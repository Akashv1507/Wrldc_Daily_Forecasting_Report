import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple, Union
from src.typeDefs.mapeRmseContext import IRmseDetails, IMapeDetails, IMapeRow, IRmseMapeDetails, IRmseRow


class RevisionwiseRmseMapeFetchRepo():
    """revision wise RMSE Mape error fetch repository
    """

    def __init__(self, con_string, modelName):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
            modelName : Name of forecasting model
        """
        self.connString = con_string
        self.modelName = modelName
        self.dataDict:IRmseMapeDetails = {'mapeContextDict':{}, 'rmseContextDict':{}}
    

    def toContextDict(self, df:pd.core.frame.DataFrame, errorName:str, errorPercentageName:str ):
        """set datadict(IRmseMapeDetails)

        Args:
            df (pd.core.frame.DataFrame): input dataframe
            errorName (str): name of error (mae, rmse)
            errorPercentageName (str): name of error percentage(mape, Rmse_percentage)
        """        
        if errorName == 'MAE':
            labelError = "MAE"
            labelErrorPercentage= 'MAPE %'
        else:
            labelError = "RMSE"
            labelErrorPercentage= 'RMSE %'

        # replacing entity_tag with constituents name
        replace_values = {"WRLDCMP.SCADA1.A0047000":"WR","WRLDCMP.SCADA1.A0046980": "Maharastra", "WRLDCMP.SCADA1.A0046957":"Gujarat", "WRLDCMP.SCADA1.A0046978":"Madhya Pradesh", "WRLDCMP.SCADA1.A0046945":"Chattisgarh", "WRLDCMP.SCADA1.A0046962":"Goa", "WRLDCMP.SCADA1.A0046948":"DD", "WRLDCMP.SCADA1.A0046953":"DNH"}
        df = df.replace({"ENTITY_TAG": replace_values})
        colName = df['ENTITY_TAG'].unique()

        r0aErrorDf =df[df['REVISION_NO']=='R0A'][['ENTITY_TAG',errorName]].reset_index( drop = True)
        r0aErrorPercentageDf =df[df['REVISION_NO']=='R0A'][['ENTITY_TAG',errorPercentageName]].reset_index( drop = True)
        r16ErrorDf =df[df['REVISION_NO']=='R16'][['ENTITY_TAG',errorName]].reset_index( drop = True)
        r16ErrorPercentageDf =df[df['REVISION_NO']=='R16'][['ENTITY_TAG',errorPercentageName]].reset_index( drop = True)
        
        r0aErrorRow = {'label': f'DayAhead(R0A) {labelError}', 'values': r0aErrorDf[errorName].round(0).astype(int).tolist()}
        r0aErrorPercentageRow = {'label': f'DayAhead(R0A) {labelErrorPercentage}', 'values': r0aErrorPercentageDf[errorPercentageName].round(2).tolist()}
        r16ErrorRow = {'label': f'Intraday(R16) {labelError}', 'values': r16ErrorDf[errorName].round(0).astype(int).tolist()}
        r16ErrorPercentageRow = {'label': f'Intraday(R16) {labelErrorPercentage}', 'values': r16ErrorPercentageDf[errorPercentageName].round(2).tolist()}
        
        if errorName == 'MAE':
            mapeContextDict:IMapeDetails={'colNames': colName, 'tblContents':[r0aErrorRow, r0aErrorPercentageRow, r16ErrorRow, r16ErrorPercentageRow]}
            self.dataDict['mapeContextDict'] = mapeContextDict
        else:
            rmseContextDict:IRmseDetails={'colNames': colName, 'tblContents':[r0aErrorRow, r0aErrorPercentageRow, r16ErrorRow, r16ErrorPercentageRow]}
            self.dataDict['rmseContextDict'] = rmseContextDict
        

    def fetchRevisionwiseRmseMapeError(self, startTime: dt.datetime, endTime: dt.datetime) ->IRmseMapeDetails:
        """fetch revisionwise rmse/mape error and return context
        Args:
            startTime (dt.datetime): start time
            endTime (dt.datetime): end time   
        Returns:
            IRmseMapeDetails: rmse mape context dict
            
        """ 
        revErrorTableName ="revisionwise_error_store"
        if  self.modelName == 'dfm2'  :
            revErrorTableName ="dfm2_revisionwise_error_store"     
        elif self.modelName == 'dfm3':
             revErrorTableName ="dfm3_revisionwise_error_store"
        elif self.modelName == 'dfm4':
             revErrorTableName ="dfm4_revisionwise_error_store"        
        try:
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)

        else:
            try:
                cur = connection.cursor()
                # fetch MAE, MAPE and create context dict
                fetch_sql = f"""SELECT entity_tag, revision_no, mae,mape FROM {revErrorTableName} 
                WHERE date_key BETWEEN TO_DATE(:start_time,'YYYY-MM-DD') and TO_DATE(:end_time,'YYYY-MM-DD') 
                and revision_no in ('R0A', 'R16') ORDER BY entity_tag,revision_no"""
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD' ")
                mapeDf = pd.read_sql(fetch_sql, params={'start_time': startTime, 'end_time': endTime}, con=connection)
                mapeContextDict = self.toContextDict(mapeDf, "MAE", "MAPE")

                # fetch RMSE, RMSE% and create context dict
                fetch_sql = f"""SELECT entity_tag, revision_no, rmse, rmse_percentage FROM {revErrorTableName} 
                WHERE date_key BETWEEN TO_DATE(:start_time,'YYYY-MM-DD') and TO_DATE(:end_time,'YYYY-MM-DD') 
                and revision_no in ('R0A', 'R16') ORDER BY entity_tag,revision_no"""
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD' ")
                rmseDf = pd.read_sql(fetch_sql, params={'start_time': startTime, 'end_time': endTime}, con=connection)
                rmseContextDict = self.toContextDict(rmseDf, "RMSE", "RMSE_PERCENTAGE")
            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
        return self.dataDict
        