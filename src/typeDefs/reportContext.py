from typing import TypedDict, List
import datetime as dt
from src.typeDefs.mapeRmseContext import IRmseDetails, IMapeDetails
from src.typeDefs.r16MaxMinAvgStats import IR16MaxMinAvgStatsContext

class IReportContext(TypedDict):
    mae:IMapeDetails
    rmse:IRmseDetails 
    foreVsAct : IR16MaxMinAvgStatsContext
    r0aPlots: List
    r16Plots: List
    targetDate: str
    dminus2Date: str