#!python3
import requests
import json
from pymongo import MongoClient
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import datetime
import pymongo


class weather:
    '''This class is used extensively for the weather related 
        activities like downloading weather   etc'''


    def getWeather(place):
        ''' Get weather forecast '''
        pass
        weather.getThreeForecast(place)
        #weather.getSixForecast(place)

    def weatherMap():
        ''' get weather map download '''
        API_key =  'ac86e7c4eeb0e07bcee04378ac06cc98'
        url = 'https://tile.openweathermap.org/map/temp_new/1/1/1.png?appid={}'.format(API_key)
        try:
            r = requests.get(url)
            weatherdatabase.saveImg(r.content, datetime.datetime.now())
        except Exception as e:
            print("Wrong Place",e)
        pass


    def makeApiCall(url):
        ''' function to make api call'''
        pass
        try:
            r = requests.get(url)
            return [True,r.json()]
        except Exception as e:
            print("Wrong Place",e)
            return [False,[]]


    def getThreeForecast(place):
        ''' get the three hour forecast'''
        pass
        API_key =  'ac86e7c4eeb0e07bcee04378ac06cc98'
        url = 'http://api.openweathermap.org/data/2.5/forecast?q={},us&appid={}'.format(place, API_key)
        result, raw_data = weather.makeApiCall(url)
        if result:
            clean_data = weather.cleanThree(raw_data, place)
            weatherdatabase.storeThree(clean_data)
        else:
            pass


    def cleanThree(raw_data, place):
        ''' clean up the three hour forecast data'''
        temp = raw_data['list']
        temp_list = []
        for i in temp:
            datee = i['dt_txt'].split()[0]
            temp_list.append({"Date": datee, "Datetime": i['dt_txt'], "temp": i['main']['temp'],
                              "weat": i['weather'][0]['main'], "Place": place})
        return temp_list
        pass
    

    def getSixForecast(place):
        pass
        API_key =  'ac86e7c4eeb0e07bcee04378ac06cc98'
        url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q={},us&appid={}'.format(place, API_key)
        print(url)
        weather.makeApiCall(url)


class weatherdatabase:
    ''' this class is used for the database'''

    def saveImg(content,datetime):
        ''' persist imae data to db'''
        pass
        print("Storing Image")
        client = MongoClient('localhost', 27017)
        db = client.Image
        try:
            db.WeatherImage.insert_one({
                "Datetime": datetime,
                "data": content
                })
            print("Image Saved")
        except Exception as e:
            print("failed because: ",e)


    def genImg(dat):
        ''' generate the picture'''
        i = Image.open(BytesIO(dat))
        i.show()
        pass


    def getImg():
        ''' get the latest picture'''
        print("getting Image")
        client = MongoClient('localhost', 27017)
        db = client.Image
        try:
            qry = db.WeatherImage.find().sort('Datetime', pymongo.DESCENDING).limit(1)
            for val in qry:
                weatherdatabase.genImg(val['data'])
        except Exception as e:
            print("failed because: ",e)
        pass

    def storeThree(data):
        ''' store forecast data'''
        pass
        print("Storing data")
        client = MongoClient('localhost', 27017)
        db = client.ThreeDay
        try:
            db.WeatherThree.insert_many(data)
            print("data Sucessfully stored for threeday forecast")
        except Exception as e:
            print("failed because: ",e)


    def getTenDay(place):
        ''' get last 10 days data'''
        pass
        print("getting ten days data")
        dates = weatherdatabase.getDatesTen()
        ten_data = []
        for x in dates:
            ten_data.append(weatherdatabase.getSummary(x, place))
        #print(ten_data)
        weatherdatabase.plotgraph(ten_data, place, dates)
        


    def getSummary(datex, place):
        ''' get summary fo 10 days'''
        pass
        client = MongoClient('localhost', 27017)
        db = client.ThreeDay
        count = 0
        summ = 0.0
        try:
            pass
            myquery = {"Date": datex, "Place": place}
            result = db.WeatherThree.find(myquery)
            for val in result:
                summ = summ + val['temp']
                count = count + 1
        except Exception as e:
            print("failed because: ",e)
            return 0
        return summ / count if count > 0 else 0


    def getNotifyData(place):
        ''' get the data for notifications'''
        pass
        print("getting the cold/rain data fr a place")
        client = MongoClient('localhost', 27017)
        db = client.ThreeDay
        return_list = []
        try:
            pass
            myquery = {"$or": [ {"weat": "Rain"}, {"weat": "Snow"},
                                {"temp": {"$lt": 273}}], "Place": place}
            result = db.WeatherThree.find(myquery)
            for val in result:
                return_list.append([val['Date'], val['temp'],
                                    val['weat'], val['Place']])
        except Exception as e:
            print("failed because: ",e)
        return return_list


    def getDatesTen():
        ''' get ten dates'''
        pass
        date_list = []
        today = date.today()
        date_list.append(today.strftime('%Y-%m-%d'))
        for i in range(1,10):
            newday = date.today() - timedelta(days=i)
            date_list.append(newday.strftime('%Y-%m-%d'))
        return date_list


    def plotgraph(data, place, dates):
        ''' function to plot a graph'''
        pass
        print(dates)
        yaxis = data[::-1]
        xaxis = tuple(dates[::-1])
        #print(xaxis,yaxis)
        y_pos = np.arange(len(xaxis))
        plt.bar(y_pos, yaxis, color=(0.2, 0.4, 0.6, 0.6))
        plt.xlabel('Temperature Vs Dates', fontweight='bold', color = 'orange',
                   fontsize='17', horizontalalignment='center')
        plt.xticks(y_pos, xaxis, color='orange', rotation=45, fontweight='bold',
                   fontsize='10', horizontalalignment='right')
        plt.show()


if __name__ == "__main__":
    pass
    #weather.getWeather("Dallas")
    #weatherdatabase.getNotifyData("Austin")
    #weatherdatabase.getTenDay("Austin")
    #weather.weatherMap()
    #weatherdatabase.getImg()
