from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import datetime as dt
import time
import os
from selenium.webdriver.chrome.options import Options
import subprocess
import sqlite3
import eel
from gtts import gTTS 
from playsound import playsound
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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



@eel.expose
def login_to_google():
    if os.path.exists("c:\\Program Files\\Google\\Chrome\\Application"):
        x=subprocess.Popen('c: & cd c:\\Program Files\\Google\\Chrome\\Application & .\chrome.exe --remote-debugging-port=8989 --user-data-dir="C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium"',shell=True)    
    if os.path.exists("c:\\Program Files (x86)\\Google\\Chrome\\Application"):
        x=subprocess.Popen('c: & cd c:\\Program Files (x86)\\Google\\Chrome\\Application & .\chrome.exe --remote-debugging-port=8989 --user-data-dir="C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium"',shell=True)    
    opt=Options()
    opt.add_argument("start-maximized")
    opt.add_experimental_option("debuggerAddress","localhost:8989")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
    # driver=webdriver.Chrome(executable_path=".\\chromedriver.exe",options=opt)
    driver.get("https://accounts.google.com/signin/v2/identifier?ltmpl=meet&continue=https%3A%2F%2Fmeet.google.com%3Fhs%3D193&&o_ref=https%3A%2F%2Fmeet.google.com%2F_meet%2Fwhoops%3Fsc%3D232%26alias%3Dmymeetingraheel&_ga=2.262670348.1240836039.1604695943-1869502693.1604695943&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
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
    getTiming(currDay)

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



def StartEel():
    eel.init('web')

    eel.start('index.html')


threat = Thread(target=StartEel)
threat.start()






def is_port_in_use():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', 8989)) == 0

def open(meeting_link):
    print("im in open function")
    try:
        if is_port_in_use()==False:
            print("im in try if is_port_in_use()==False")
            if os.path.exists("c:\\Program Files\\Google\\Chrome\\Application"):
                x=subprocess.Popen('c: & cd c:\\Program Files\\Google\\Chrome\\Application & .\chrome.exe --remote-debugging-port=8989 --user-data-dir="C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium"',shell=True)    
            if os.path.exists("c:\\Program Files (x86)\\Google\\Chrome\\Application"):
                x=subprocess.Popen('c: & cd c:\\Program Files (x86)\\Google\\Chrome\\Application & .\chrome.exe --remote-debugging-port=8989 --user-data-dir="C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium"',shell=True)    
            opt=Options()
            opt.add_argument("start-maximized")
            opt.add_experimental_option("debuggerAddress","localhost:8989")
    
            # driver=webdriver.Chrome(executable_path=".\\chromedriver.exe",options=opt)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
            print("im in false")
            no_of_tabs=len(driver.window_handles)
            
            driver.get(meeting_link)
            join(driver)

        else:
            print("im in is_port_in_use == True")
            opt=Options()
            opt.add_experimental_option("debuggerAddress","localhost:8989")
            
            opt.add_argument("start-maximized")
            #driver=webdriver.Chrome(executable_path=".\\chromedriver.exe",options=opt)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
            no_of_tabs=len(driver.window_handles)
            
            driver.execute_script("window.open('about:blank', 'tab{}');".format(no_of_tabs+1))
            driver.switch_to.window('tab{}'.format(no_of_tabs+1))
            driver.get(meeting_link)
            join(driver)
    except Exception as e: 
        print(e)   
def join(driver):
    driver.maximize_window()
    audioWait = WebDriverWait(driver, 50)
    audioElement = audioWait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div")))
    videoWait = WebDriverWait(driver, 50)
    videoElement = videoWait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div")))
    joinWait = WebDriverWait(driver, 50)
    joinElement = joinWait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/span")))
    # audioWait = WebDriverWait(driver, 50).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div"))
    # )
    # videoWait = WebDriverWait(driver, 50).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div"))
    # )
    # joinWait = WebDriverWait(driver, 50).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/span"))
    # )
    audio_btn=driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div")
    audio_btn.click()
    aval = audio_btn.get_attribute("data-is-muted")
    print("Audio Muted : "+aval)
    video_btn=driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div")
    video_btn.click()
    vval = video_btn.get_attribute("data-is-muted")
    print("Video Muted : "+vval)
    # join_btn = driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/span")
    # join_btn.click()
    iterating_var=0
    while iterating_var!=5:
        aval = audio_btn.get_attribute("data-is-muted")
        vval = video_btn.get_attribute("data-is-muted")
        time.sleep(2)
        if aval=="false":
            audio_btn=driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div")
            audio_btn.click()
            aval = audio_btn.get_attribute("data-is-muted")
        if vval=="false":
            video_btn=driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div")
            video_btn.click()
            vval = video_btn.get_attribute("data-is-muted")
        print("attempt no."+str(iterating_var))
        try:
            if aval == "true" and vval=="true":
                print("isAudioMuted:"+str(aval))
                print("isVideoMuted:"+str(vval))
                join_btn = driver.find_element_by_xpath("//*[@id=\"yDmH0d\"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/span")
                join_btn.click()
                time.sleep(2)
                break
            else:
                iterating_var+=1
                driver.implicitly_wait(1)
                continue
        except:
            if iterating_var!=5:
                driver.implicitly_wait(1)
                continue
            elif iterating_var==5:
                break


def isLoggedin():
    try:
        time.sleep(1)
        # chat_btn=driver.find_element_by_xpath("//*[@id=\"ow3\"]/div[1]/div/div[9]/div[3]/div[1]/div[3]/div/div[2]/div[3]/span/span")         
        end_btn=driver.find_element_by_xpath("//*[@id=\"ow3\"]/div[1]/div/div[9]/div[3]/div[10]/div[2]/div/div[7]/span/button")         
        print("Im inside the meeting")
    except :
        isLoggedin()

def getTimingNonUI(day):
    val = connection.execute('SELECT * FROM TIMING WHERE DAY = {};'.format(day))
    ret = []
    for x in val:
        ret.append(x[1])
    return ret

def getSubjectForDay(day):
    val = connection.execute('SELECT * FROM TIMING WHERE DAY = {};'.format(day))
    ret = []
    for x in val:
        ret.append(x[3])
    return ret

def getLink(sub):
    val = connection.execute('SELECT * FROM SUBJECT')
    for x in val:
        if x[0]==sub:
            return x[1]

# def initFunction():
while True:
    language = 'en-us'
    day = dt.date.today().isoweekday()+1
    if day==8:
        day=1
    startArray=getTimingNonUI(day)
    subjectArray=getSubjectForDay(day)


    time2 = dt.datetime.now()
    time2 = time.strftime("%H:%M")

    print('time : ' + time2)
    print('start array : ' + repr(startArray))
    try:
        time_index=startArray.index(time2)
        subjectName=subjectArray[time_index]
        print("subject - "+subjectName)
        print("Link - "+getLink(subjectName))
        myobj = gTTS(text="Joining "+subjectName+" class", lang=language, slow=False)
        myobj.save("class.mp3")
        playsound("class.mp3")
        os.remove("class.mp3")
        open(getLink(subjectName))   
    except ValueError:
        pass
    time.sleep(50)
# ------------------- 
# eelThread=Thread(target=eelStart)
# initThread=Thread(target=initFunction)
# initThread.start()
# eelThread.start()
# eelThread.join()    
# ---------------------

# print(startArray)
# print(subjectArray)
# print(getLink(subjectArray[0]))
# open("https://meet.google.com/doe-oskc-rsu")
