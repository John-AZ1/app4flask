from tinydb import TinyDB, Query, where
import json
from flask import Flask
import datetime
import requests
from bs4 import BeautifulSoup
import mechanize
app = Flask(__name__)

tinydb = TinyDB('files/db.json')
query = Query()

def update(user, password):
        try:
                print("update starting")
                def browse():
                        br = mechanize.Browser()
                        url = "http://{{ school name }}.app4.ws/"
                        br.open(url)
                        print(br.title())
                        br.select_form(nr=0)
                        br["txtLoginUserID"] = user
                        br["txtLoginPassword"] = password
                        br.submit()
                        print(br.title())
                        br.open(url + str("app4.ws/portal/timetable.php"))
                        soup = BeautifulSoup(br.response().read(), "lxml")
                        classes = soup.find_all('td', {"width": '18%'})
                        timetablelist = []
                        #find the tag holding th classes and get the text
                        for i in classes:
                                classes = i.find_all('span', {"class": "ttsub"})
                                for i in classes:
                                        timetablelist.append(i.text.strip())
                        return timetablelist
                timetablelist = browse()
                # use x and y to break the the main into into smaller lists of days
                def daylist(x,y,list):
                        daylist = []
                        for i in range(x,y):
                                daylist.append(list[i])
                        return daylist
                # insert data into database
                def inset(x, y, z, list, user):
                        session = 1
                        print(y,z)
                        classes = daylist(x, y,list)
                        for i in classes:
                                tinydb.insert({'Day':z, 'Session':session, 'class': i,"user": user})
                                session += 1
                z = 1
                x = 0
                y = 9
                # add classes to database

                while z <= 10:

                        inset(x, y, z, timetablelist, user)
                        z += 1
                        x += 9
                        y += 9

                print("database updated")

        except requests.exceptions.ConnectionError:
                print("connection unreliable")
                pass

def get(day, session, user):
        jsonstr = tinydb.get((where('Day') == day) & (where('Session') == session) & (where('user') == user))
        print jsonstr
        parse = jsonstr["class"]
        return parse

@app.route('/<studentnum>/<password>/list')
def show_post(studentnum, password):
        try:
                today = datetime.datetime.today().weekday()
                classes = []
                for i in range(1, 10):
                        classes.append("<item>" + str(get(today, i, studentnum)) + "</item>")
                        timetablefordaylist = ''.join(classes)
                        return timetablefordaylist

                return timetablefordaylist
        # if there not in the database this except gets raised and updates the timetable
        except TypeError:
                update(studentnum, password)
                return "please stand by"


app.run()