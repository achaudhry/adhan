#!/usr/bin/env python

import datetime
import time
import sys
from os.path import dirname, abspath, join as pathjoin
import argparse

root_dir = dirname(abspath(__file__))
sys.path.insert(0, pathjoin(root_dir, 'crontab'))

from praytimes import PrayTimes
PT = PrayTimes() 

from crontab import CronTab
system_cron = CronTab(user='pi')

now = datetime.datetime.now()
strPlayFajrAzaanMP3Command = 'omxplayer --vol 1200 -o local {}/Adhan-fajr.mp3 > /dev/null 2>&1'.format(root_dir)
strPlayAzaanMP3Command = 'omxplayer --vol 1800 -o local {}/Adhan-Madinah.mp3 > /dev/null 2>&1'.format(root_dir)
strUpdateCommand = 'python {}/updateAzaanTimers.py >> {}/adhan.log 2>&1'.format(root_dir, root_dir)
strClearLogsCommand = 'truncate -s 0 {}/adhan.log 2>&1'.format(root_dir)
strJobComment = 'rpiAdhanClockJob'

#HELPER FUNCTIONS
#---------------------------------
#---------------------------------
#Function to add azaan time to cron
def parseArgs():
    parser = argparse.ArgumentParser(description='Calculate prayer times and install cronjobs to play Adhan')
    parser.add_argument('--lat', type=float, dest='lat',
                        help='Latitude of the location, for example 30.345621')
    parser.add_argument('--lng', type=float, dest='lng',
                        help='Longitude of the location, for example 60.512126')
    parser.add_argument('--method', choices=['MWL', 'ISNA', 'Egypt', 'Makkah', 'Karachi', 'Tehran', 'Jafari'],
                        dest='method',
                        help='Method of calculation')
    return parser

def mergeArgs(args):
    file_path = pathjoin(root_dir, '.settings')
    # load values
    lat = lng = method = None
    try:
        with open(file_path, 'rt') as f:
            lat, lng, method = f.readlines()[0].split(',')
    except:
        print('No .settings file found')
    # merge args
    if args.lat:
        lat = args.lat
    if args.lng:
        lng = args.lng
    if args.method:
        method = args.method
    # save values
    with open(file_path, 'wt') as f:
        f.write('{},{},{}'.format(lat or '', lng or '', method or ''))
    return float(lat) or None, float(lng) or None, method or None

def addAzaanTime (strPrayerName, strPrayerTime, objCronTab, strCommand):
  job = objCronTab.new(command=strCommand,comment=strPrayerName)  
  timeArr = strPrayerTime.split(':')
  hour = timeArr[0]
  min = timeArr[1]
  job.minute.on(int(min))
  job.hour.on(int(hour))
  job.set_comment(strJobComment)
  print(job)
  return

def addUpdateCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.minute.on(15)
  job.hour.on(3)
  job.set_comment(strJobComment)
  print(job)
  return

def addClearLogsCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.day.on(1)
  job.minute.on(0)
  job.hour.on(0)
  job.set_comment(strJobComment)
  print(job)
  return
#---------------------------------
#---------------------------------
#HELPER FUNCTIONS END

#Parse arguments
parser = parseArgs()
args = parser.parse_args()
#Merge args with saved values if any
lat, lng, method = mergeArgs(args)
print(lat, lng, method)
#Complain if any value is missing
if not lat or not lng or not method:
    parser.print_usage()
    sys.exit(1)

#Set calculation method, utcOffset and dst here
#By default system timezone will be used
#--------------------
PT.setMethod(method)
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst

# Remove existing jobs created by this script
system_cron.remove_all(comment=strJobComment)

# Calculate prayer times
times = PT.getTimes((now.year,now.month,now.day), (lat, lng), utcOffset, isDst) 
print(times['fajr'])
print(times['dhuhr'])
print(times['asr'])
print(times['maghrib'])
print(times['isha'])

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
print('Script execution finished at: ' + str(now))
