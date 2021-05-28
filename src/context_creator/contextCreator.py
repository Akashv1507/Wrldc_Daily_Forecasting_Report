import datetime as dt
from typing import List, Tuple

class ContextCreator():
    """class that creates context for template 
    """    

    def __init__(self,year :int,weekNo :int, startDate: dt.datetime, endDate: dt.datetime):
        """constructor method

        Args:
            year (int): year
            weekNo (int): week no
            startDate (dt.datetime): start date
            endDate (dt.datetime): end date
        """        
        self.year=year
        self.weekNo = weekNo
        self.startDate = startDate.strftime("%Y-%m-%d")
        self.endDate =  endDate.strftime("%Y-%m-%d")
    
    def contextCreator(self,rowsFreqProfile:List[dict],weeklyFDI:int,rows400Kv:List[dict], rows765Kv:List[dict],voltValuesTable1:List[dict],voltValuesTable2:List[dict],voltValuesTable3:List[dict],voltValuesTable4:List[dict]) -> dict:
        """create context for template

        Args:
            rowsFreqProfile (List[dict]): rows in form of dictionary 
            weeklyFDI (int)             : weekly FDI
            rows400Kv (List[dict])      : rows that belongs to 400Kv nodes     
            rows765Kv (List[dict])      : rows that belongs to 765Kv nodes 
            voltValuesTable1 (List[dict]): derived voltage value for table 1 in report template.
            voltValuesTable2 (List[dict]): derived voltage value for table 2 in report template.
            voltValuesTable3 (List[dict]): derived voltage value for table 3 in report template.
            voltValuesTable4 (List[dict]): derived voltage value for table 4 in report template.

        Returns:
            dict: context dictionary that we render in template.

            """          
       
        context = {
                  'year_str' : self.year,
                  'week_no'  : self.weekNo,
                  'start_dt' : self.startDate,
                  'end_dt'   : self.endDate,
                  'weekVDI'  : "{:0.2f}".format(weeklyFDI),
                  'derFreqList' : rowsFreqProfile,
                  'rows400Kv' : rows400Kv,
                  'rows765Kv'  : rows765Kv,
                  'voltTable1' : voltValuesTable1,
                  'voltTable2' : voltValuesTable2,
                  'voltTable3' : voltValuesTable3,
                  'voltTable4' : voltValuesTable4        
        }
        
        return context