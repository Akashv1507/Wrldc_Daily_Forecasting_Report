import argparse
from datetime import datetime as dt, timedelta
from src.appConfig import getAppConfigDict
from src.report_generation.reportGeneration import generateReport

configDict = getAppConfigDict()

targetReportDate = dt.now() + timedelta(days=1)
modelName = "dfm1"

# get start and end dates from command line
parser = argparse.ArgumentParser()
parser.add_argument('--report_date', help="Enter target report date in yyyy-mm-dd format",
                    default=dt.strftime(targetReportDate, '%Y-%m-%d'))
parser.add_argument(
    '--model_name', help="Enter model name in string ", default=modelName)

args = parser.parse_args()
targetReportDate = dt.strptime(args.report_date, '%Y-%m-%d')
modelName = args.model_name

targetReportDate = targetReportDate.replace(
    hour=0, minute=0, second=0, microsecond=0)

print('targetReportDate = {0}'.format(dt.strftime(
    targetReportDate, '%Y-%m-%d')), modelName)

generateReport(targetReportDate, modelName, configDict)
