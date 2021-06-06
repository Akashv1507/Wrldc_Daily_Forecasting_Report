import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple, TypedDict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import seaborn as sns

class IntradayErrorActualDemandFetchForPlotRepo():
    """fetch intraday forecasted demand, blockwise error, actual demand, day ahead forecast and plot a graph
    """

    def __init__(self, con_string, reportDate, modelName):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string
        self.reportDate =reportDate
        self.modelName = modelName

    def plotGraph(self, plotDf:pd.DataFrame, entityObj:dict):
        """plot grpah for a particular  entity

        Args:
            plotDf (pd.DataFrame):plot df columns ->['ACTUAL_DEMAND', 'R0A_FORECAST', 'R16_FORECAST', 'PERCENTAGE_MW_ERROR']
            entityObj (dict): [{'tag': 'WRLDCMP.SCADA1.A0047000', 'name': 'WR'}]
        """    
        # checking plotdf is not empty as weel as any columns not null    
        if (not plotDf.empty) and (not plotDf['R0A_FORECAST'].isnull().values.any()):         
            constituentName = entityObj['name']
            fig, ax = plt.subplots(figsize=(8, 6))

            actualDemandLine, = ax.plot(plotDf.index.values , plotDf['ACTUAL_DEMAND'] , color='green', linewidth=3.0)
            actualDemandLine.set_label("Actual Load")
            r0aForecastLine, = ax.plot(plotDf.index.values , plotDf['R0A_FORECAST'] , color='red', linewidth=3.0)
            r0aForecastLine.set_label("Day Ahead Forecast(R0)")
            r16ForecastLine, = ax.plot(plotDf.index.values , plotDf['R16_FORECAST'] , color='blue', linewidth=3.0)
            r16ForecastLine.set_label("Intraday Forecast(R16)")
            # plotting blockwise error on secondary axis
            ax_twin = ax.twinx()
            blockwiseErroLine = ax_twin.bar(plotDf.index.values , plotDf['PERCENTAGE_MW_ERROR'] , width =0.003, color='purple')
            blockwiseErroLine.set_label("Error % (R16)")
           
            # setting label and title
            ax.set_title(label= f'{constituentName} Load Forecast Vs Actual For {self.reportDate}', fontdict={'fontsize': '14','fontweight' :'bold'})
            ax.set_ylabel('-Forecast/Actual(MW)-', fontdict={'fontsize': '10','fontweight' :'bold'})
            ax_twin.set_ylabel('-Error (%)-', fontdict={'fontsize': '10','fontweight' :'bold'})
            ax.set_xlabel('-Time-', fontdict={'fontsize': '12','fontweight' :'bold'})
            
            # setting x limit
            ax.set_xlim(xmin= plotDf.index.tolist()[0], xmax=plotDf.index.tolist()[95] )
            # setting seconday y axis  limit
            ax_twin.set_ylim(ymin= -20, ymax= 20)
            # drawing xaxis line for secondary y axis at y=0
            ax_twin.axhline(y=0, linewidth=0.7, color='grey')
 
            # configuring ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

            # configuring ticks size, rotation and ticks label
            ax.tick_params(axis='x',labelrotation=90, labelsize=9, pad=1,colors='black',length=3, width=5)
            ax.tick_params(axis='y', labelsize=10, pad=0, colors='black',length=2, width=5) 
            ax_twin.tick_params(axis='y', labelsize=10, pad=0, colors='black',length=2, width=5)

            # ask matplotlib for the plotted objects and their labels, and combining legends
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax_twin.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc=0)

            # showing grid, legend and finally saving
            ax.grid(axis='y')
            fig.savefig(f'plots_dumps/R16_{self.modelName}_{self.reportDate}_{constituentName}.png', bbox_inches='tight')
     
    def fetchForecastedDemand(self, startDate: dt.datetime, endDate: dt.datetime):
        """fetch intraday forecasted demand, blockwise error, actual demand, day ahead forecast and plot a graph

        Args:
            startDate (dt.datetime): start date
            endDate (dt.datetime): end date

        Returns:
            generate plots only
        """

        forecastRevTableName ="forecast_revision_store"
        blockwiseErrorTableName = "mw_error_store"
        if  self.modelName == 'dfm2'  :
            forecastRevTableName ="dfm2_forecast_revision_store"
            blockwiseErrorTableName = "dfm2_mw_error_store"     
        elif self.modelName == 'dfm3':
             forecastRevTableName ="dfm3_forecast_revision_store"
             blockwiseErrorTableName = "dfm3_mw_error_store"
        elif self.modelName == 'dfm4':
             forecastRevTableName ="dfm4_forecast_revision_store"
             blockwiseErrorTableName = "dfm4_mw_error_store"  

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
                actualDemand_fetch_sql = f"SELECT time_stamp, demand_value FROM derived_blockwise_demand WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag=:entityTag ORDER BY time_stamp"
                forecast_fetch_sql = f"SELECT time_stamp, forecasted_demand_value FROM {forecastRevTableName} WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag=:entityTag and revision_no =:revNo ORDER BY time_stamp"
                blockwiseError_fetch_sql = f"SELECT time_stamp, percentage_mw_error FROM {blockwiseErrorTableName} WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag=:entityTag and revision_no =:revNo ORDER BY time_stamp"
                cur = connection.cursor()
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")

                # fetching actual demand, R0a,R16 forecast, and blockwise error for each entity and then ploting graph
                for entityObj in listOfEntityObj:
                    actualDemandDf = pd.read_sql(actualDemand_fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value,'entityTag': entityObj['tag']}, con=connection)
                    r0aForecastDf = pd.read_sql(forecast_fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value,'entityTag': entityObj['tag'] , 'revNo': 'R0A'}, con=connection)
                    r16ForecastDf = pd.read_sql(forecast_fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value,'entityTag': entityObj['tag'] , 'revNo': 'R16'}, con=connection)
                    blockwiseErrorDf = pd.read_sql(blockwiseError_fetch_sql, params={
                        'start_time': start_time_value, 'end_time': end_time_value,'entityTag': entityObj['tag'], 'revNo': 'R16'}, con=connection)
                    
                    # setting index and then concatenating vertically
                    actualDemandDf.set_index('TIME_STAMP', inplace=True)
                    r0aForecastDf.set_index('TIME_STAMP', inplace=True)
                    r16ForecastDf.set_index('TIME_STAMP', inplace=True)
                    blockwiseErrorDf.set_index('TIME_STAMP', inplace=True)
                    plotDf = pd.concat([actualDemandDf, r0aForecastDf, r16ForecastDf, blockwiseErrorDf], axis=1)
                    plotDf.columns = ['ACTUAL_DEMAND', 'R0A_FORECAST', 'R16_FORECAST', 'PERCENTAGE_MW_ERROR']
                    # plotting graphs
                    self.plotGraph(plotDf, entityObj)
            except Exception as err:
                print('error while creating a cursor/plotting graph', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
