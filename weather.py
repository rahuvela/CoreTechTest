#!python3
import requests
import json
from pymongo import MongoClient
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import datetime
import pymongo
import time
from PIL import Image
import threading


class Work:

    
    def __init__(self, place):
        self.place = place
        self.API_key = 'ac86e7c4eeb0e07bcee04378ac06cc98'
        self.url = 'https://tile.openweathermap.org/map/temp_new/1/1/1.png?appid={}'.format(self.API_key)
        self.place_url = 'http://api.openweathermap.org/data/2.5/forecast?q={},us&appid={}'.format(place, self.API_key)
        self.client = MongoClient('localhost', 27017)


    def threaders(self):
        '''
        This function sets each place thread to begin all the thread processes for each
        requirement
        '''
        t1 = threading.Timer(10.0, self.getWeather) #thread to et and store weather
        t2 = threading.Timer(10.0, self.weatherMap) # thread to download weather map
        t3 = threading.Timer(10.0, self.getImg) # thread to get weather map image
        t4 = threading.Timer(10.0, self.getNotifyData) #thread for notification
        t5 = threading.Timer(10.0, self.getTenDay) # thread for 10 day plot
        return [t1,t2,t3,t4,t5]


    def startfunc(self):
        for thread in self.threaders():
            thread.start()
            print("working here")
            thread.join()


    def getWeather(self):
        ''' Get weather forecast given place this function invokes
            the respective functions to store forecast details'''
        self.getThreeForecast()
        # getSixForecast(place)


    def weatherMap(self):
        ''' get weather map download , this function is used
            to download the weathermap alyer'''
        try:
            r = requests.get(self.url)
            self.saveImg(r.content, datetime.datetime.now())
        except Exception as e:
            print("Wrong Place", e)
            pass


    def makeCall(self):
        '''function determines if data exists , so that a
               call is not made unnecessarily'''
        today = date.today()
        now = today.strftime('%Y-%m-%d')
        db = self.client.ThreeDay
        count = 0
        try:
            pass
            qury = db.WeatherThree.find({"Date": now, "Place": self.place})
            for val in qury:
                count = count + 1
        except Exception as e:
            print("failed because: ", e)
            return False
        return False if count > 0 else True


    def makeApiCall(self):
        ''' function to make api call'''
        pass
        try:
            r = requests.get(self.place_url)
            return [True, r.json()]
        except Exception as e:
            print("Wrong Place", e)
            return [False, []]


    def getThreeForecast(self):
        ''' get the three hour forecast, clean it and store it'''
        if self.makeCall():
            result, raw_data = self.makeApiCall()
            if result:
                clean_data = self.cleanThree(raw_data)
                self.storeThree(clean_data)


    def cleanThree(self,raw_data):
        ''' clean up the three hour forecast data'''
        print(raw_data, self.place)
        temp = raw_data['list']
        temp_list = []
        for i in temp:
            datee = i['dt_txt'].split()[0]
            temp_list.append({"Date": datee, "Datetime": i['dt_txt'], "temp": i['main']['temp'],
                              "weat": i['weather'][0]['main'], "Place": self.place})
        return temp_list


    def getSixForecast(self):
        ''' placeholder function for 16day'''
        self.makeApiCall()


    def saveImg(self, content, datetime):
        ''' persist image data to db'''
        pass
        print("Storing Image")
        db = self.client.Image
        try:
            db.WeatherImage.insert_one({"Datetime": datetime, "data": content})
            print("Image Saved")
        except Exception as e:
            print("failed because: ", e)


    @staticmethod
    def genImg(dat):
        ''' generate the picture'''
        i = Image.open(BytesIO(dat))
        i.show()
        pass


    def getImg(self):
        ''' get the latest picture'''
        print("getting Image")
        db = self.client.Image
        try:
            qry = db.WeatherImage.find().sort('Datetime', pymongo.DESCENDING).limit(1)
            for val in qry:
                Work.genImg(val['data'])
        except Exception as e:
            print("failed because: ", e)
            pass


    def storeThree(self, data):
        ''' store forecast data'''
        pass
        print("Storing data")
        db = self.client.ThreeDay
        try:
            db.WeatherThree.insert_many(data)
            print("data Sucessfully stored for threeday forecast")
        except Exception as e:
            print("failed because: ", e)


    def getTenDay(self):
        ''' get last 10 days data'''
        pass
        print("getting ten days data")
        dates = Work.getDatesTen()
        ten_data = []
        for x in dates:
            ten_data.append(self.getSummary(x))
        self.plotgraph(ten_data, dates)


    def getSummary(self, datex):
        ''' get summary fo 10 days'''
        pass
        db = self.client.ThreeDay
        count = 0
        summ = 0.0
        try:
            pass
            myquery = {"Date": datex, "Place": self.place}
            result = db.WeatherThree.find(myquery)
            for val in result:
                summ = summ + val['temp']
                count = count + 1
        except Exception as e:
            print("failed because: ", e)
            return 0
        return summ / count if count > 0 else 0


    def getNotifyData(self):
        ''' get the data for notifications'''
        print("getting the cold/rain data")
        db = self.client.ThreeDay
        return_list = []
        try:
            myquery = {"$or": [{"weat": "Rain"}, {"weat": "Snow"},
                               {"temp": {"$lt": 273}}], "Place": self.place}
            result = db.WeatherThree.find(myquery)
            for val in result:
                return_list.append([val['Date'], val['temp'],
                                    val['weat'], val['Place']])
        except Exception as e:
            print("failed because: ", e)
            return []
        return return_list


    @staticmethod
    def getDatesTen():
        ''' get ten dates'''
        date_list = []
        today = date.today()
        date_list.append(today.strftime('%Y-%m-%d'))
        for i in range(1, 10):
            newday = date.today() - timedelta(days=i)
            date_list.append(newday.strftime('%Y-%m-%d'))
        return date_list


    def plotgraph(self,data,dates):
        ''' function to plot a graph'''
        yaxis = data[::-1]
        xaxis = tuple(dates[::-1])
        y_pos = np.arange(len(xaxis))
        plt.bar(y_pos, yaxis, color=(0.2, 0.4, 0.6, 0.6))
        plt.xlabel('Temperature Vs Dates', fontweight='bold', color='orange',
                   fontsize='17', horizontalalignment='center')
        plt.xticks(y_pos, xaxis, color='orange', rotation=45, fontweight='bold',
                   fontsize='10', horizontalalignment='right')
        fig = plt.gcf()
        today = date.today()
        now = today.strftime('%Y%m%d')
        fig.savefig('plot/{}{}.png'.format(self.place, now))
        plt.show()
        plt.close()


if __name__ == "__main__":
    now = time.time()
    conti = True
    dataold = []
    while conti:
        if  (time.time() - now) > 30.0: #Read the textfile every 30 seconds
            pass
            now = time.time()
            with open("places.txt") as f:
                content = f.readlines()
            datanew = [x.split() for x in content]
            print(datanew == dataold)
            if datanew == dataold: #same places
                pass #do nothing
            else:
                dataold = datanew
                print("New data")
                for h in datanew[0]: #for each place create a new thread
                    x = Work(h)
                    t = threading.Timer(3.0, x.startfunc)
                    t.start()
                    print("Working for ", h)
                    t.join()
        else:
            pass
