
from src.context_creator.contextCreator import ContextCreator
import datetime as dt
from docxtpl import DocxTemplate
from src.fetchers.dayAheadForecastPlotFetcher import ForecastedDemandFetchForPlotRepo
from src.fetchers.intraday_error_actualPlotFetcher import IntradayErrorActualDemandFetchForPlotRepo
from src.fetchers.rmseMapeFetchers import RevisionwiseRmseMapeFetchRepo
from src.typeDefs.mapeRmseContext import  IRmseMapeDetails
from src.context_creator.contextCreator import ContextCreator
from src.fetchers.intradayForVsActualFetcher import IntradayForecastVsActualFetchRepository



def generateReport(targetReportDate: dt.datetime, modelName: str, configDict: dict) -> None:
    """function that generate daily forecasting Report

    Args:
        targetReportDate (dt.datetime):Target Date of Forecasting Report
        modelName(str) : model name dfm1, dfm2, dfm3.
        configDict (dict): app configuration dictionary
    """

    con_string = configDict['con_string_mis_warehouse']
    dminus2Date = targetReportDate- dt.timedelta(days=2)
    plotsDumpPath = configDict['plots_dumps_path']

    # initialization regarding tempalte
    definedTemplatePath = configDict['raw_template_path'] + '\\forecasting_report_raw_template.docx'
    templateSavePath = configDict['report_dumps_path'] + f"\\{modelName.upper()} WR Day Ahead Load Forecast for {targetReportDate.date()} and Comparison for {dminus2Date.date()}.docx"
    docTpl = DocxTemplate(definedTemplatePath)

    # creating instance of each classes
    obj_contextCreator = ContextCreator(plotsDumpPath, targetReportDate.date(), dminus2Date.date())
    objPlot_fetchR0aForecast = ForecastedDemandFetchForPlotRepo(con_string, targetReportDate.date(), modelName)
    objPlot_fetchR16ErrorForecast = IntradayErrorActualDemandFetchForPlotRepo(con_string, dminus2Date.date(), modelName)
    obj_fetchRmseMape = RevisionwiseRmseMapeFetchRepo(con_string, modelName)
    obj_fetchIntVsActual = IntradayForecastVsActualFetchRepository(con_string, modelName)

    objPlot_fetchR0aForecast.fetchForecastedDemand(targetReportDate, targetReportDate)
    objPlot_fetchR16ErrorForecast.fetchForecastedDemand(dminus2Date, dminus2Date)
    rmseMapeContextDict:IRmseMapeDetails = obj_fetchRmseMape.fetchRevisionwiseRmseMapeError(dminus2Date, dminus2Date)
    foreVsActContext =obj_fetchIntVsActual.fetchForVsActualData(dminus2Date, dminus2Date)
    reportContext = obj_contextCreator.createReportContext(rmseMapeContextDict, foreVsActContext, modelName, configDict, docTpl)

    docTpl.render(reportContext)
    docTpl.save(templateSavePath)
