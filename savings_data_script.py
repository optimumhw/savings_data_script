
__author__ = 'hal'

import requests
import json
import os
import sys


class TeslaHelperClass():

    def __init__(self, host, username, password):

        self.tesla_host = host
        self.tesla_user = username
        self.tesla_password = password

        print
        self.tesla_password

    def setToken(self):
        url = self.tesla_host + "/v1/oauth/token"

        headers = {}
        headers['content-type'] = 'application/json'

        dict = {}
        dict['grantType'] = 'password'
        dict['email'] = self.tesla_user
        dict['password'] = self.tesla_password

        payload = json.dumps(dict)
        payload = json.loads(payload)

        try:
            resp = requests.post(url, json=payload, headers=headers)
            dict = json.loads(resp.text)

        except Exception, e:
            print
            e

        if resp.status_code != 200:
            msg = "Can't get token! host= " + self.tesla_host
            self.fatalError(msg, resp)

        self.tok = dict['accessToken']



    def getHistory(self, historyRequest ):
        headers = {}
        headers['Accept'] = 'application/json'
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.tok

        url = self.tesla_host + '/v1/data/query'

        payload = json.dumps(historyRequest)
        payload = json.loads(payload)

        resp = requests.post(url, json=payload, headers=headers)


        if resp.status_code != 200:
            print "Could not get history"
            exit(1)

        history = json.loads(resp.text)

        stuff = json.dumps(history)
        print stuff

        return history


    def combineHistory(self, hourlyHistory, fiveMinuteHistory):


        pointNames = []
        for pointObj in fiveMinuteHistory:
            pointNames.append( pointObj['name'])
        for pointObj in hourlyHistory:
            pointNames.append(pointObj['name'])

        timestamps = []
        for pointObj in fiveMinuteHistory:
            for ts in pointObj["timestamps"]:
                if not ts in timestamps:
                    timestamps.append(ts)

        for pointObj in hourlyHistory:
            for ts in pointObj["timestamps"]:
                if not ts in timestamps:
                    timestamps.append(ts)

        tsToValues = {}
        for ts in timestamps:
            valuesArray = []
            for name in pointNames:
                valuesArray.append("filler")
            tsToValues[ts] = valuesArray

        pointIndex = 0
        for pointObj in fiveMinuteHistory:
            tsIndex = 0
            for ts in pointObj["timestamps"]:
                valuesAtTimstamp = tsToValues.get(ts)
                valuesAtTimstamp[pointIndex] = pointObj["values"][tsIndex]
                tsToValues[ts] = valuesAtTimstamp
                tsIndex += 1
            pointIndex += 1

        for pointObj in hourlyHistory:
            tsIndex = 0
            for ts in pointObj["timestamps"]:
                valuesAtTimstamp = tsToValues.get(ts)
                valuesAtTimstamp[pointIndex] = pointObj["values"][tsIndex]
                tsToValues[ts] = valuesAtTimstamp
                tsIndex += 1
            pointIndex += 1


        return pointNames, timestamps, tsToValues


    def makeCsv(self, reportPath, pointNames, timestamps, tsToValues):

        print 'creating: ' + reportPath
        csvFile = open(reportPath, 'w')

        headerRow = "timestamp"
        for pointName in pointNames:
            headerRow += "," + pointName
        csvFile.write(headerRow + '\n')

        for ts in timestamps:
            csvRow = ts

            values = tsToValues[ts]
            for pointValue in values:
                if pointValue is None:
                    strVal = ''
                else:
                    strVal = str(pointValue)
                csvRow += ',' + strVal

            csvFile.write(csvRow + '\n')

        csvFile.close()

        return True


# =================================================================
def logError(msg='error'):
    print
    msg
    exit()


if __name__ == '__main__':

    tesla_host = os.environ['SAVINGS_HOST']
    tesla_user = os.environ['SAVINGS_USER']
    tesla_password = os.environ['SAVINGS_PASSWORD']
    tesla_stationId = os.environ['SAVINGS_STATION_ID']
    reportPath = os.environ['SAVINGS_REPORT_PATH']

    try:
        '''
        "America/Phoenix"
        2019-06-01T00.00.00.000-07.00
        2019-06-01T00.00.00.000-07.00
        '''
        start_Date = sys.argv[1]
        end_Date = sys.argv[2]
        timezone = sys.argv[3]

    except Exception, e:
        print e
        print 'usage: python savings_data_script.py 2019-06-01T00.00.00.000-07.00 2019-06-01T00.00.00.000-07.00 "America/Phoenix" '
        exit(1)

    '''
    TotalkWh	    hour	    5a12611f-bee1-4b7e-94b2-eb1765e06c5e
    BaselinekWh	    hour	    90fdc01f-19dd-415a-b3c7-a5bd12a5e0d9

    BaselinekW	    fiveMinute	df0d8adf-852b-496b-b4fb-4265df67f0a9
    BaselinekWTon	fiveMinute	f39e786a-3bcb-40f9-a59f-9d095b2a25be
    OAT	            fiveMinute	708ea72d-0ea3-45dd-b907-adbc74e014f5
    OAWB	        fiveMinute	7f0f2aa3-3d1e-4120-8ba9-1a08269124bc
    TotalkW	        fiveMinute	135facba-bb9e-4931-8220-60c1420e891e
    TotalTon	    fiveMinute	52d0b2ee-3f41-4ea9-8037-ffc6080bd193
    '''

    #hourly points
    TotalkWh = '5a12611f-bee1-4b7e-94b2-eb1765e06c5e'
    BaselinekWh = '90fdc01f-19dd-415a-b3c7-a5bd12a5e0d9'

    pointIds_hour = []
    pointIds_hour.append(TotalkWh)
    pointIds_hour.append(BaselinekWh)

    history_request_hour = {}
    history_request_hour["startAt"] = start_Date
    history_request_hour["endAt"] = end_Date
    history_request_hour["timeZone"] = timezone
    history_request_hour["resolution"] = "hour"
    history_request_hour["ids"] = pointIds_hour

    #fivemin points
    BaselinekW = 'df0d8adf-852b-496b-b4fb-4265df67f0a9'
    BaselinekWTon = 'f39e786a-3bcb-40f9-a59f-9d095b2a25be'
    OAT = '708ea72d-0ea3-45dd-b907-adbc74e014f5'
    OAWB = '7f0f2aa3-3d1e-4120-8ba9-1a08269124bc'
    TotalTon = '52d0b2ee-3f41-4ea9-8037-ffc6080bd193'

    pointIds_five_minute = []
    pointIds_five_minute.append(BaselinekW)
    pointIds_five_minute.append(BaselinekWTon)
    pointIds_five_minute.append(OAT)
    pointIds_five_minute.append(OAWB)
    pointIds_five_minute.append(TotalTon)

    history_request_five_minute = {}
    history_request_five_minute["startAt"] = start_Date
    history_request_five_minute["endAt"] = end_Date
    history_request_five_minute["timeZone"] = timezone
    history_request_five_minute["resolution"] = "fiveMinute"
    history_request_five_minute["ids"] = pointIds_five_minute

    # =====================================================================


    print 'Getting auth token from tesla...'
    teslaHelper = TeslaHelperClass( tesla_host, tesla_user, tesla_password)
    teslaHelper.setToken()

    print 'Getting hourly data...'
    hourly_history = teslaHelper.getHistory(history_request_hour)

    print 'Getting five minute data...'
    five_minute_history = teslaHelper.getHistory(history_request_five_minute)

    print 'Combining History...'
    pointNames, timestamps, tsToValues = teslaHelper.combineHistory(hourly_history,five_minute_history )

    print 'Making csv...'
    filePath = os.path.join(reportPath, "history.csv")
    status = teslaHelper.makeCsv(filePath, pointNames, timestamps, tsToValues)

    'Done.'

