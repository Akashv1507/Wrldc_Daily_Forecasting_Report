import cx_Oracle
import pandas as pd
import datetime as dt
from src.typeDefs.r16MaxMinAvgStats import ISingleColData, IR16MaxMinAvgStatsContext

class IntradayForecastVsActualFetchRepository():
    """ Intraday Forecast Vs Actual Fetch  repository
    """

    def __init__(self, con_string, modelName):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
            modelName : Name of forecasting model
        """
        self.connString = con_string
        self.modelName = modelName
    
    def toContextDict(self, dataDf:pd.core.frame.DataFrame)->IR16MaxMinAvgStatsContext:
        """retutn min, max, avg stats context of forecast and actual demand

        Args:
            dataDf (pd.core.frame.DataFrame): dataframe with columns [MAX_DEMAND, MIN_DEMAND, AVG_DEMAND, MAX_FORECAST, MIN_FORECAST, AVG_FORECAST] with index entity_tag

        Returns:
            IR16MaxMinAvgStatsContext: context data
        """        
               
        # handling in case of dfm2,3,4 becoz max, min, avg forecast of goa, dd, dnh is null
        dataDf = dataDf[dataDf['MAX_FORECAST'].notnull()]
        dataDf.reset_index(inplace = True)
        # replacing entity_tag with constituents name
        replace_values = {"WRLDCMP.SCADA1.A0047000":"WR","WRLDCMP.SCADA1.A0046980": "Maharastra", "WRLDCMP.SCADA1.A0046957":"Gujarat", "WRLDCMP.SCADA1.A0046978":"MP", "WRLDCMP.SCADA1.A0046945":"Chattisgarh", "WRLDCMP.SCADA1.A0046962":"Goa", "WRLDCMP.SCADA1.A0046948":"DD", "WRLDCMP.SCADA1.A0046953":"DNH"}
        dataDf = dataDf.replace({"ENTITY_TAG": replace_values})
        colName = dataDf['ENTITY_TAG']
        contextData:IR16MaxMinAvgStatsContext = []
        for col in colName:
            filteredDf = dataDf[dataDf['ENTITY_TAG']== col].reset_index( drop = True)
            singleColObj:ISingleColData = {'colName': col, 'maxFor': filteredDf['MAX_FORECAST'][0].round(0).astype(int), 'maxDem':filteredDf['MAX_DEMAND'][0].round(0).astype(int),
            'minFor': filteredDf['MIN_FORECAST'][0].round(0).astype(int), 'minDem':filteredDf['MIN_DEMAND'][0].round(0).astype(int),
            'avgFor':filteredDf['AVG_FORECAST'][0].round(0).astype(int), 'avgDem':filteredDf['AVG_DEMAND'][0].round(0).astype(int) }
            contextData.append(singleColObj)
        
        return contextData

        

    def fetchForVsActualData(self, startTime: dt.datetime, endTime: dt.datetime)-> IR16MaxMinAvgStatsContext:
        """ fetch  Intraday Forecast Vs Actual dataand return IR16MaxMinAvgStatsContext
        Args:
            startTime (dt.datetime): start time
            endTime (dt.datetime): end time   
        Returns:
            IR16MaxMinAvgStatsContext: context data
        """
        forecastRevTableName = "forecast_revision_store"
        actualDemanTableName = "derived_blockwise_demand"

        if self.modelName == 'dfm2':
            forecastRevTableName = "dfm2_forecast_revision_store"
            actualDemanTableName = "interpolated_blockwise_demand"
        elif self.modelName == 'dfm3':
            forecastRevTableName = "dfm3_forecast_revision_store"
            actualDemanTableName = "interpolated_blockwise_demand"
        elif self.modelName == 'dfm4':
            forecastRevTableName = "dfm4_forecast_revision_store"
            actualDemanTableName = "interpolated_blockwise_demand"

        start_time_value = startTime
        end_time_value = endTime + dt.timedelta(hours=23, minutes=59)

        try:
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)

        else:
            try:
                cur = connection.cursor()
                forecast_fetch_sql = f"""SELECT entity_tag, MAX(forecasted_demand_value) as Max_Forecast, MIN(forecasted_demand_value) as Min_Forecast, AVG(forecasted_demand_value) as Avg_Forecast 
                FROM {forecastRevTableName} WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and 
                TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and revision_no =:revNo GROUP BY entity_tag ORDER BY entity_tag"""

                actual_fetch_sql = f"""SELECT entity_tag, MAX(demand_value) as Max_Demand, MIN(demand_value) as Min_Demand, AVG(demand_value) as Avg_Demand 
                FROM {actualDemanTableName} WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and 
                TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') GROUP BY entity_tag ORDER BY entity_tag"""
               
                cur.execute(
                    "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                r16ForecastDf = pd.read_sql(forecast_fetch_sql, params={
                                            'start_time': start_time_value, 'end_time': end_time_value, 'revNo': 'R16'}, con=connection)
                actualDemandDf = pd.read_sql(actual_fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value}, con=connection)
                
                actualDemandDf.set_index('ENTITY_TAG', inplace=True)
                r16ForecastDf.set_index('ENTITY_TAG', inplace=True)
                dataDf = pd.concat([actualDemandDf, r16ForecastDf], axis=1)

            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
        contextData:IR16MaxMinAvgStatsContext = self.toContextDict(dataDf)
        return contextData
