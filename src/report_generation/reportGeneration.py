
from src.context_creator.contextCreator import ContextCreator
import datetime as dt
from typing import List, Tuple
from docxtpl import DocxTemplate
from src.fetchers.dayAheadForecastPlotFetcher import ForecastedDemandFetchForPlotRepo


def generateReport(targetReportDate: dt.datetime, modelName: str, configDict: dict) -> None:
    """function that generate weekly Mis Report

    Args:
        targetReportDate (dt.datetime):Target Date of Forecasting Report
        modelName(str) : model name dfm1, dfm2, dfm3.
        configDict (dict): app configuration dictionary
    """

    con_string = configDict['con_string_mis_warehouse']

    # creating instance of each classes
    # obj_dictMerger = ContextCreator(year, week_number, startDate, endDate)
    obj_fetchR0aForecast = ForecastedDemandFetchForPlotRepo(con_string, targetReportDate.date(), modelName)
    obj_fetchR0aForecast.fetchForecastedDemand(targetReportDate, targetReportDate)
    # definedTemplatePath = configDict['template_path'] + \
    #     '\\freq_volt_profile_raw_template.docx'
    # templateSavePath = configDict['template_path'] + \
    #     '\\07-- sept-2020_weekly-report.docx'
    # doc = DocxTemplate(definedTemplatePath)
    # doc.render(context)
    # doc.save(templateSavePath)
