from src.appConfig import getAppConfigDict, loadAppConfig
from flask import Flask, request, jsonify, render_template
from src.report_generation.reportGeneration import generateReport
# from flask_cors import CORS, cross_origin
from waitress import serve
from datetime import datetime as dt, timedelta
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
# cors = CORS(app)

# get application config
configDict = loadAppConfig()
app.config['SECRET_KEY'] = configDict['flaskSecret']
# app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def home():
    return "This port is used for background service to generate forecasting report."

@app.route('/createForecastingReport',  methods=['POST'])
# @cross_origin()
def createForecastingReport():
    reqData = request.get_json()
    report_date = reqData['reportDate']
    try:
         targetReportDate = dt.strptime(report_date, '%Y-%m-%d')
    except Exception as ex:
        return jsonify({'message': 'Unable to parse report date of this request body'}), 400
    targetReportDate = targetReportDate.replace(hour=0, minute=0, second=0, microsecond=0)

    modelName = reqData['modelName'].lower()
    if modelName not in ['dfm1','dfm2','dfm3', 'dfm4']:
        return jsonify({'message': 'Model Name is Invalid'}), 400
  
    # call generate report function
    isReportGenerated = generateReport(targetReportDate, modelName, configDict)
    # isReportGenerated = False
    if isReportGenerated:
        return jsonify({
            'message' : "Report Generation Successfull",
            'reportDate':targetReportDate.date()})
    else : 
        return jsonify(
            {
            'message' :"Report Generation UnSuccessfull"}
        ), 500

if __name__ == '__main__':
    serverMode: str = configDict['mode']
    if serverMode.lower() == 'd':
        app.run(host="localhost", port=int(configDict['flaskPort']), debug=True)
    else:
        serve(app, host='0.0.0.0', port=int(
            configDict['flaskPort']),  threads=1)