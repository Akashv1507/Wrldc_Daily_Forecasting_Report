import datetime as dt
import os
from typing import List, Tuple
from src.typeDefs.mapeRmseContext import IRmseMapeDetails
from docxtpl import InlineImage, DocxTemplate
from docx.shared import Mm

class ContextCreator():
    """class that creates context for template 
    """    

    def __init__(self, plotsDumpPath:str, targetReportDate:dt.datetime, dminus2Date:dt.datetime):
        self.plotsDumpPath = plotsDumpPath
        self.targetReportDate = targetReportDate
        self.dminus2Date = dminus2Date      
        
    
    def createReportContext(self,rmseMapeContextDict:IRmseMapeDetails, foreVsActContext, modelName:str, configDict: dict, docTpl ) -> dict:

        

        r0aPlotList = []
        r16PlotList = []
        # isValid flag checks which entities present in which model
        listOfEntity = [{'tag': 'WRLDCMP.SCADA1.A0047000', 'name': 'WR', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046980', 'name': 'Maharashtra', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046957', 'name': 'Gujarat', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046978', 'name': 'Madhya Pradesh', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046945', 'name': 'Chattisgarh', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046962', 'name': 'Goa', 'isValid':True},
                           {'tag': 'WRLDCMP.SCADA1.A0046948', 'name': 'DD', 'isValid':True}, 
                           {'tag': 'WRLDCMP.SCADA1.A0046953', 'name': 'DNH', 'isValid':True}]
        if modelName == 'dfm2' or modelName == 'dfm3':
            listOfEntity[5]['isValid']=listOfEntity[6]['isValid']=listOfEntity[7]['isValid'] = False
        if modelName == 'dfm4':
            listOfEntity[1]['isValid']=listOfEntity[2]['isValid']=listOfEntity[3]['isValid']=listOfEntity[4]['isValid']=listOfEntity[5]['isValid']=listOfEntity[6]['isValid']=listOfEntity[7]['isValid'] = False

        for entity in listOfEntity:    
            if entity['isValid']== True:
                imgPathR0a = os.path.join(self.plotsDumpPath,f"R0A_{modelName}_{self.targetReportDate}_{entity['name']}.png" )
                imgPathR16 = os.path.join(self.plotsDumpPath,f"R16_{modelName}_{self.dminus2Date}_{entity['name']}.png" )
                imageR0a = InlineImage(docTpl, image_descriptor=imgPathR0a, width=Mm(205), height=Mm(180))
                imageR16 = InlineImage(docTpl, image_descriptor=imgPathR16, width=Mm(205), height=Mm(180))
                r0aPlotList.append(imageR0a)
                r16PlotList.append(imageR16)
            
        reportContext = {
            'mae':rmseMapeContextDict['mapeContextDict'] ,
            'rmse':rmseMapeContextDict['rmseContextDict'] ,
            'foreVsAct' : foreVsActContext,
            'r0aPlots': r0aPlotList,
            'r16Plots': r16PlotList,
            'targetDate': f"{self.targetReportDate.strftime('%d-%B-%Y')} ({self.targetReportDate.strftime('%A')}) " ,
            'dminus2Date': f"{self.dminus2Date.strftime('%d-%B-%Y')} ({self.dminus2Date.strftime('%A')})"
        }       
        return reportContext  
        