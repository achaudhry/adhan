#!/usr/bin/env python

import datetime
import time
import sys
sys.path.insert(0, '/home/pi/adhan/crontab')

from praytimes import PrayTimes
PT = PrayTimes()

from crontab import CronTab
system_cron = CronTab(user='pi')

now = datetime.datetime.now()

# Set Azaan MP3 source
strPlayFajrAzaanMP3Command = 'curl --data "p0=mixer&p1=volume&p2=30&p3=playlist&p4=play&p5=/home/pi/adhan/mp3/Adhan-fajr.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9002/status.html'
strPlayAzaanMP3Command = 'curl --data "p0=mixer&p1=volume&p2=50&p3=playlist&p4=play&p5=/home/pi/adhan/mp3/Adhan-Makkah.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9002/status.html'

strUpdateCommand = 'python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1'
strClearLogsCommand = 'truncate -s 0 /home/pi/adhan/adhan.log 2>&1'
strJobComment = 'rpiAdhanClockJob'

# Set latitude and longitude here
#--------------------
lat = 42.288788
long = -71.551678

# Set calculation method, utcOffset and dst here
# By default system timezone will be used
#--------------------
PT.setMethod('Diyanet')
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst


# HELPER FUNCTIONS
# ---------------------------------
# ---------------------------------
# Function to add azaan time to cron
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
  job.minute.on(15)
  job.hour.on(3)
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
# ---------------------------------
# ---------------------------------
# HELPER FUNCTIONS END

# Remove existing jobs created by this script
system_cron.remove_all(comment=strJobComment)

# Calculate prayer times
times = PT.getTimes((now.year,now.month,now.day), (lat, long), utcOffset, isDst)
print times['fajr'], 'Fajr'
print times['sunrise'], 'Sunrise'
print times['dhuhr'], 'Dhuhr'
print times['asr'], 'Asr'
print times['maghrib'], 'Maghrib'
print times['isha'], 'Isha'

# Add times to crontab
addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('dhuhr',times['dhuhr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('asr',times['asr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('maghrib',times['maghrib'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('isha',times['isha'],system_cron,strPlayAzaanMP3Command)

# Run this script again overnight
addUpdateCronJob(system_cron, strUpdateCommand)

# Clear the logs every month
addClearLogsCronJob(system_cron,strClearLogsCommand)

system_cron.write_to_user(user='pi')
print 'Script execution finished at: ' + str(now)
