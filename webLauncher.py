import eel
import sqlite3
import subprocess
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys



connection = sqlite3.connect('database.db',check_same_thread=False)

#better way is just to create a bloody primary key
connection.execute('''CREATE TABLE IF NOT EXISTS SUBJECT
         (
         NAME    TEXT    NOT NULL,
         URL     TEXT    NOT NULL,
         PRIMARY KEY('NAME')
         );''')

#connection.execute('''ALTER TABLE SUBJECT ADD UNIQUE INDEX(NAME, URL);''')
#foreign key reference is useless
connection.execute('''CREATE TABLE IF NOT EXISTS TIMING
         (
         DAY      INT    NOT NULL,
         STIME    TEXT   NOT NULL,
         ETIME    TEXT   NOT NULL,
         SUBJECT  TEXT   NOT NULL,
         UNIQUE(DAY, STIME, ETIME, SUBJECT)
         FOREIGN KEY('SUBJECT') REFERENCES 'SUBJECT'('NAME') ON DELETE CASCADE
         );''')

#only 1 value ffs
connection.execute('''CREATE TABLE IF NOT EXISTS ACCOUNT
         (
            EMAIL     TEXT   NOT NULL,
            PASSWORD  TEXT   NOT NULL
         );''')

connection.commit()

eel.init('web')


@eel.expose
def login_to_google():
    x=subprocess.Popen('cd c:\\Program Files\\Google\\Chrome\\Application & .\chrome.exe --remote-debugging-port=8989 --user-data-dir="C:\\Users\\shara\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium"',shell=True)
    opt=Options()
    opt.add_argument("start-maximized")
    opt.add_experimental_option("debuggerAddress","localhost:8989")
    driver=webdriver.Chrome(executable_path="chromedriver.exe",options=opt)
    driver.get("https://accounts.google.com/signin/v2/identifier?ltmpl=meet&continue=https%3A%2F%2Fmeet.google.com%3Fhs%3D193&&o_ref=https%3A%2F%2Fmeet.google.com%2F_meet%2Fwhoops%3Fsc%3D232%26alias%3Dmymeetingraheel&_ga=2.262670348.1240836039.1604695943-1869502693.1604695943&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
    driver.minimize_window()  
    driver.maximize_window()  
    # driver.minimize_window()  
    # driver.maximize_window() 



@eel.expose
def getSubject():
    val = connection.execute('SELECT * FROM SUBJECT')
    ret = []    
    for x in val:
        obj = {}
        obj['name'] = x[0]
        obj['url'] = x[1]
        ret.append(obj)
    eel.updateSubject(ret)

@eel.expose
def addSubject(subject):
    connection.execute('INSERT OR IGNORE INTO SUBJECT VALUES (\'{}\',\'{}\');'.format(subject['name'],subject['url']))
    connection.commit()
    getSubject()

@eel.expose
def deleteSubject(subject):
    connection.execute('DELETE FROM SUBJECT WHERE NAME = \'{}\' AND URL = \'{}\';'.format(subject['name'],subject['url']))
    connection.commit()
    deleteAllTimingOfaSubject(subject['name'])
    getSubject()
    
@eel.expose
def updateSubject(new, old):
    connection.execute('UPDATE SUBJECT SET NAME = \'{}\' , URL = \'{}\' WHERE NAME = \'{}\' AND URL = \'{}\''.format(new['name'], new['url'], old['name'], old['url']))
    connection.commit()
    editAllTimingOfaSubject(new['name'], old['name'])
    getSubject()


currDay = 1

@eel.expose
def getTiming(day):
    val = connection.execute('SELECT * FROM TIMING WHERE DAY = {};'.format(day))
    ret = []
    for x in val:
        obj = {}
        obj['day'] = x[0]
        obj['start_time'] = x[1]
        obj['end_time'] = x[2]
        obj['subject'] = x[3]
        ret.append(obj)
    currDay = day
    eel.updateTiming(ret)


@eel.expose
def addTiming(timing):
    connection.execute('INSERT OR IGNORE INTO TIMING VALUES ({},\'{}\',\'{}\',\'{}\');'.format(timing['day'],timing['start_time'],timing['end_time'], timing['subject']))
    connection.commit()
    currDay = timing['day']
    getTiming(timing['day'])

@eel.expose
def deleteTiming(timing):
    connection.execute('DELETE FROM TIMING WHERE DAY = \'{}\' AND STIME = \'{}\' AND ETIME = \'{}\' AND SUBJECT = \'{}\';'.format(timing['day'],timing['start_time'],timing['end_time'], timing['subject']))
    connection.commit()
    currDay = timing['day']
    getTiming(timing['day'])
    
    
@eel.expose
def updateTiming(new, old):
    connection.execute('UPDATE TIMING SET DAY = \'{}\' , STIME = \'{}\', ETIME = \'{}\' , SUBJECT = \'{}\' WHERE DAY = \'{}\' AND STIME = \'{}\' AND ETIME = \'{}\' AND SUBJECT = \'{}\';  '.format(new['day'],new['start_time'],new['end_time'], new['subject'],old['day'],old['start_time'],old['end_time'], old['subject']))
    connection.commit()
    currDay = new['day']
    getTiming(new['day'])
    

def deleteAllTimingOfaSubject(subject):
    connection.execute('DELETE FROM TIMING WHERE SUBJECT = \'{}\''.format(subject))
    connection.commit()
    getTiming(currDay)


def editAllTimingOfaSubject(new, old):
    connection.execute('UPDATE TIMING SET SUBJECT = \'{}\' WHERE SUBJECT = \'{}\';  '.format(new, old))
    connection.commit()
    getTiming(currDay)


eel.start('index.html')


