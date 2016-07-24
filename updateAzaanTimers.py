#!/usr/bin/env python

import datetime
from praytimes import PrayTimes


#Set latitude and longitude here
#--------------------
lat = 42.288788
long = -71.551678

now = datetime.datetime.now()



PT = PrayTimes() 
#Set calculation method and timezone here
#--------------------
PT.setMethod('ISNA')
times = PT.getTimes((now.year,now.month,now.day), (lat, long), -5,1) 

print times['fajr']
print times['dhuhr']
print times['asr']
print times['maghrib']
print times['isha']


#Update Crontab with Prayer Times
#---------------------------------

from crontab import CronTab


#Function to add azaan time to cron
def addAzaanTime (strPrayerName, strPrayerTime, objCronTab, strCommand):

  job = objCronTab.new(command=strCommand,comment=strPrayerName)
  
  timeArr = strPrayerTime.split(':')

  hour = timeArr[0]
  min = timeArr[1]

  job.minute.on(int(min))
  job.hour.on(int(hour))

  print job

  return


def addUpdateCronJob (objCronTab, strCommand):

  job = objCronTab.new(command=strCommand)

  job.minute.on(0)
  job.hour.on(1)

  print job

  return

def addClearLogsCronJob (objCronTab, strCommand):

  job = objCronTab.new(command=strCommand)

  job.day.on(1)
  job.minute.on(0)
  job.hour.on(0)

  print job

  return


system_cron = CronTab()
strPlayFajrAzaanMP3Command = 'omxplayer -o local /home/pi/adhan/Adhan-Makkah-Fajr.mp3 > /dev/null 2>&1'
strPlayAzaanMP3Command = 'omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1'
strUpdateCommand = 'python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1'
strClearLogsCommand = 'truncate -s 0 /home/pi/adhan/adhan.log 2>&1'

jobs = system_cron.find_command(strPlayAzaanMP3Command)

print jobs

for j in jobs:
  system_cron.remove(j) 

addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('dhuhr',times['dhuhr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('asr',times['asr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('maghrib',times['maghrib'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('isha',times['isha'],system_cron,strPlayAzaanMP3Command)
addUpdateCronJob(system_cron, strUpdateCommand)
addClearLogsCronJob(system_cron,strClearLogsCommand)
system_cron.write_to_user(user='pi')
print 'Script execution finished at: ' + str(now)
