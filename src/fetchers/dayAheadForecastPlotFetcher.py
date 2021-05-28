import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple, TypedDict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import seaborn as sns

class ForecastedDemandFetchForPlotRepo():
    """fethc forecasted demand and plot a graph
    """

    def __init__(self, con_string, reportDate, modelName):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string
        self.reportDate =reportDate
        self.modelName = modelName

    def plotGraph(self, forecastedDemandDf:pd.DataFrame, entityObj:dict):
        """plot grpah for a particular  entity

        Args:
            forecastedDemandDf (pd.DataFrame): forecasted demand df
            entityObj (dict): [{'tag': 'WRLDCMP.SCADA1.A0047000', 'name': 'WR'}]
        """        
        
        if not forecastedDemandDf.empty:           
            constituentName = entityObj['name']
            fig, ax = plt.subplots(figsize=(12, 6))
            line, = ax.plot(forecastedDemandDf['TIME_STAMP'] , forecastedDemandDf['FORECASTED_DEMAND_VALUE'] , color='red', linewidth=3.0)
            
            # setting label and title
            ax.set_title(label= f'{constituentName} Day Ahead Load Forecast For {self.reportDate}', fontdict={'fontsize': '14','fontweight' :'bold'})
            ax.set_ylabel('-Forecast(MW)-', fontdict={'fontsize': '12','fontweight' :'bold'})
            ax.set_xlabel('-Time-', fontdict={'fontsize': '12','fontweight' :'bold'})
            line.set_label("Day Ahead Forecast(R0)")
           
            # setting x limit
            ax.set_xlim(xmin= forecastedDemandDf['TIME_STAMP'][0], xmax=forecastedDemandDf['TIME_STAMP'][95] )
            
            # configuring ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

            # configuring ticks size, rotation and ticks label
            ax.tick_params(axis='x',labelrotation=90, labelsize=9, pad=1,colors='black',length=3, width=5)
            ax.tick_params(axis='y', labelsize=10, colors='black',length=5, width=5) 

            # showing grid, legend and finally saving
            ax.grid(axis='y')
            ax.legend()
            fig.savefig(f'plots_dumps/{self.modelName}_{self.reportDate}_{constituentName}.png')
     
    def fetchForecastedDemand(self, startDate: dt.datetime, endDate: dt.datetime):
        """fetch forecasted demand of R0A

        Args:
            startDate (dt.datetime): start date
            endDate (dt.datetime): end date

        Returns:
            generate plots only
        """

        forecastRevTableName ="forecast_revision_store"
        if  self.modelName == 'dfm2'  :
            forecastRevTableName ="dfm2_forecast_revision_store"     
        elif self.modelName == 'dfm3':
             forecastRevTableName ="dfm3_forecast_revision_store"
        elif self.modelName == 'dfm4':
             forecastRevTableName ="dfm4_forecast_revision_store"  

        listOfEntityObj = [{'tag': 'WRLDCMP.SCADA1.A0047000', 'name': 'WR'},
                           {'tag': 'WRLDCMP.SCADA1.A0046980', 'name': 'Maharashtra'},
                           {'tag': 'WRLDCMP.SCADA1.A0046957', 'name': 'Gujarat'},
                           {'tag': 'WRLDCMP.SCADA1.A0046978', 'name': 'Madhya Pradesh'},
                           {'tag': 'WRLDCMP.SCADA1.A0046945', 'name': 'Chattisgarh'},
                           {'tag': 'WRLDCMP.SCADA1.A0046962', 'name': 'Goa'},
                           {'tag': 'WRLDCMP.SCADA1.A0046948', 'name': 'DD'}, 
                           {'tag': 'WRLDCMP.SCADA1.A0046953', 'name': 'DNH'}]

        start_time_value = startDate
        end_time_value = endDate + dt.timedelta(hours=23, minutes=59)
        try:
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)
        else:
            try:
                cur = connection.cursor()
                for entityObj in listOfEntityObj:
                    fetch_sql = f"SELECT time_stamp, forecasted_demand_value FROM {forecastRevTableName} WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag=:entityTag and revision_no = 'R0A' ORDER BY entity_tag, time_stamp"
                    cur.execute(
                        "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                    forecastedDemandDf = pd.read_sql(fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value,'entityTag': entityObj['tag']}, con=connection)
                    self.plotGraph(forecastedDemandDf, entityObj)
            except Exception as err:
                print('error while creating a cursor/plotting graph', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
