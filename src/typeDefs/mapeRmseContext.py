from typing import TypedDict, List
import datetime as dt

class IRmseRow(TypedDict):
    label: str
    values: List[float]

class IRmseDetails(TypedDict):
    colName:List[str]
    tblCOntents:IRmseRow

class IMapeRow(TypedDict):
    label: str
    values: List[float]

class IMapeDetails(TypedDict):
    colName:List[str]
    tblCOntents:IMapeRow

class IRmseMapeDetails(TypedDict):
    mapeContextDict:IMapeDetails
    rmseContextDict: IRmseDetails

