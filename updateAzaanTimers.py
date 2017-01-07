#!/usr/bin/env python

import datetime
import time

from praytimes import PrayTimes
PT = PrayTimes() 

from crontab import CronTab
system_cron = CronTab(user='pi')

now = datetime.datetime.now()
strPlayFajrAzaanMP3Command = 'omxplayer -o local /home/pi/adhan/Adhan-Makkah-Fajr.mp3 > /dev/null 2>&1'
strPlayAzaanMP3Command = 'omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1'
strUpdateCommand = 'python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1'
strClearLogsCommand = 'truncate -s 0 /home/pi/adhan/adhan.log 2>&1'
strHdmiOff = '30 22 * * * sh /home/pi/prayer_times/static/rpi-hdmi.sh off'
strHdmiOn = '00 5 * * * sh /home/pi/prayer_times/static/rpi-hdmi.sh on'
strJobComment = 'rpiAdhanClockJob'

#Set latitude and longitude here
#--------------------
lat = 42.288788
long = -71.551678

#Set calculation method, utcOffset and dst here
#By default system timezone will be used
#--------------------
PT.setMethod('ISNA')
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst

times = PT.getTimes((now.year,now.month,now.day), (lat, long), utcOffset, isDst) 

print times['fajr']
print times['dhuhr']
print times['asr']
print times['maghrib']
print times['isha']


#Update Crontab with Prayer Times
#---------------------------------

#Function to add azaan time to cron
def addAzaanTime (strPrayerName, strPrayerTime, objCronTab, strCommand):
  job = objCronTab.new(command=strCommand,comment=strPrayerName)  
  timeArr = strPrayerTime.split(':')
  hour = timeArr[0]
  min = timeArr[1]
  job.minute.on(int(min))
  job.hour.on(int(hour))
  job.set_comment(strJobComment)
  print job
  return


def addUpdateCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.minute.on(0)
  job.hour.on(1)
  job.set_comment(strJobComment)
  print job
  return

def addClearLogsCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.day.on(1)
  job.minute.on(0)
  job.hour.on(0)
  job.set_comment(strJobComment)
  print job
  return

def addToggleHDMI (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.minute.on(0)
  job.hour.on(0)
  print job
  return

#jobs = system_cron.find_comment(strJobComment)
#for j in jobs:
#  print j

system_cron.remove_all(comment=strJobComment)

addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('dhuhr',times['dhuhr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('asr',times['asr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('maghrib',times['maghrib'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('isha',times['isha'],system_cron,strPlayAzaanMP3Command)
addUpdateCronJob(system_cron, strUpdateCommand)
addClearLogsCronJob(system_cron,strClearLogsCommand)
#addToggleHDMI(system_cron, strHdmiOff)
#addToggleHDMI(system_cron, strHdmiOn)
system_cron.write_to_user(user='pi')
print 'Script execution finished at: ' + str(now)
