from flask import Flask, render_template, jsonify
from flask_cors import CORS
from sassutils.wsgi import SassMiddleware
import sass
import json
import requests
#from binance.client import Client
import os.path
import csv
import pandas as pd

import time
import datetime
 

current_date_unix_timestamp = int((datetime.datetime.timestamp(datetime.datetime.now(datetime.timezone.utc))*1000))
d30_ago_date_unix_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=30))*1000)



def download_data(currency,interval,start,end):
    url = 'https://api.binance.com/api/v3/klines'
    
    par = {'symbol': currency, 'interval': interval, 'startTime': start, 'endTime': end}
    #print(requests.get(url, params= par).text)
    data = json.loads(requests.get(url, params= par).text) 
    return data

def prepare_data_to_charts(data):
    ready_data=[]
    for candle in data:
        candlestick = { 
            "time": int(candle[0]) / 1000, 
            "open": candle[1],
            "high": candle[2], 
            "low": candle[3], 
            "close": candle[4]
        }
        ready_data.append(candlestick)
    return ready_data
front_charts=[]

if os.path.exists("user_config.json")==True:
    file = open("user_config.json", "r")
    config =json.loads(file.read())
    charts= config['Charts'] 
    for chart in charts:       
        front_charts.append({"currency":chart['currency'],"interval":chart['interval']})
        
        file_path="data/"+chart['currency']+"_"+chart['interval']+".csv"
        chart['file_path']=file_path
        if os.path.exists(chart['file_path'])==True:
            chart_data=[]            
            f =open(chart['file_path'], 'r+', newline='')
            #get last price time
            chart_data=list(csv.reader(f))
            last_row=chart_data[-1]
            last_price_time=last_row[6]    
            #download data from last time to current time
            new_chart_data=download_data(chart['currency'],chart['interval'],last_price_time,current_date_unix_timestamp)
            print(new_chart_data)
            #save data
            if new_chart_data:
                candlewriter = csv.writer(f, delimiter=',')
                for candle in new_chart_data:                   
                    candlewriter.writerow(candle)
                    chart_data.append(candle)
            
            else:
                print("thre is no new data")
            f.close()
        else:
            chart_data=[]   
            f =open(chart['file_path'], 'w', newline='')
            candlewriter = csv.writer(f, delimiter=',')
        
            chart_data = download_data(chart['currency'],chart['interval'],d30_ago_date_unix_timestamp,current_date_unix_timestamp)
            #print(hour4_data)
            for candle in chart_data:
                candlewriter.writerow(candle)

            f.close()  


else:
    print("there is no config file!")

app = Flask(__name__)
CORS(app)
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'app': ('static/sass', 'static/css', '/static/css')
})
sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')

@app.route('/')
def index():
    #zwrot ilosci wykresow wedlug configa
    return render_template('home.html',charts=front_charts)


@app.route('/data/history', methods=['GET'])
def history():
    #zwrot danych wedlug cofiga
    charts_to_return=[]
    for chart in charts:
        web_stream_url=config['BinnanceStreamUrl']+chart['currency']+"@kline_"+chart['interval']
        if os.path.exists(chart['file_path'])==True:
            chart_data=[]            
            f =open(chart['file_path'], 'r+', newline='')
            #get last price time
            chart_data=list(csv.reader(f))
            last_row=chart_data[-1]
            last_price_time=last_row[6]    
            #download data from last time to current time
            new_chart_data=download_data(chart['currency'],chart['interval'],last_price_time,current_date_unix_timestamp)
            print(new_chart_data)
            #save data
            if new_chart_data:
                
                for candle in new_chart_data:                   
                    
                    chart_data.append(candle)
            
            else:
                print("thre is no new data")
            f.close()
            
        else:
            chart_data=[]   
            f =open(chart['file_path'], 'w', newline='')
            candlewriter = csv.writer(f, delimiter=',')
        
            chart_data = download_data(chart['currency'],chart['interval'],d30_ago_date_unix_timestamp,current_date_unix_timestamp)
            #print(hour4_data)
            for candle in chart_data:
                candlewriter.writerow(candle)

            f.close()
        chart_data=prepare_data_to_charts(chart_data)
        charts_to_return.append({"name":chart['currency']+"_"+chart['interval'],
         "data":chart_data,"stream_url":web_stream_url,
         "currency":chart['currency'].lower(),
         "interval":chart['interval']})
        
    response = jsonify(charts_to_return)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route('/data/update')
def updatedata():
    #update danych
    pass
if __name__ == '__main__' :
    app.run(debug=True)