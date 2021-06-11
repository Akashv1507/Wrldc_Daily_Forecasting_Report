from typing import TypedDict, List
import datetime as dt

class ISingleColData(TypedDict):
    colName:str
    maxFor:int
    maxDem: int
    minFor:int
    minDem: int
    avgFor:int
    avgDem: int

class IR16MaxMinAvgStatsContext(TypedDict):
    statsContextData:List[ISingleColData]
