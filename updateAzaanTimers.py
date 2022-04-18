#!/usr/bin/env python3

import datetime
import time
import sys
from os.path import dirname, abspath, join as pathjoin
import argparse
import requests, json

root_dir = dirname(abspath(__file__))
sys.path.insert(0, pathjoin(root_dir, 'crontab'))

from praytimes import PrayTimes
PT = PrayTimes()

from crontab import CronTab
system_cron = CronTab(user='pi')

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
    parser.add_argument('--method', choices=['Diyanet','MWL', 'ISNA', 'Egypt', 'Makkah', 'Karachi', 'Tehran', 'Jafari'],
                        dest='method',
                        help='Method of calculation')
    parser.add_argument('--fajr-azaan-volume', type=int, dest='fajr_azaan_vol',
                        help='Volume for fajr azaan in millibels, 1500 is loud and -30000 is quiet (default 0)')
    parser.add_argument('--azaan-volume', type=int, dest='azaan_vol',
                        help='Volume for azaan (other than fajr) in millibels, 1500 is loud and -30000 is quiet (default 0)')
    return parser

def mergeArgs(args):
    file_path = pathjoin(root_dir, '.settings')
    # load values
    lat = lng = method = fajr_azaan_vol = azaan_vol = None
    try:
        with open(file_path, 'rt') as f:
            lat, lng, method, fajr_azaan_vol, azaan_vol = f.readlines()[0].split(',')
    except:
        print('No .settings file found')
    # merge args
    if args.lat:
        lat = args.lat
    if lat:
        lat = float(lat)
    if args.lng:

        lng = args.lng
    if lng:
        lng = float(lng)
    if args.method:
        method = args.method
    if args.fajr_azaan_vol:
        fajr_azaan_vol = args.fajr_azaan_vol
    if fajr_azaan_vol:
        fajr_azaan_vol = int(fajr_azaan_vol)
    if args.azaan_vol:
        azaan_vol = args.azaan_vol
    if azaan_vol:
        azaan_vol = int(azaan_vol)
    # save values
    with open(file_path, 'wt') as f:
        f.write('{},{},{},{},{}'.format(lat or '', lng or '', method or '',
                fajr_azaan_vol or 0, azaan_vol or 0))
    return lat or None, lng or None, method or None, fajr_azaan_vol or 0, azaan_vol or 0

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
lat, lng, method, fajr_azaan_vol, azaan_vol = mergeArgs(args)
print(lat, lng, method, fajr_azaan_vol, azaan_vol)
#Complain if any mandatory value is missing
if not lat or not lng or not method:
    parser.print_usage()
    sys.exit(1)

#Set calculation method, utcOffset and dst here
#By default system timezone will be used
#--------------------
PT.setMethod(method)
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst


now = datetime.datetime.now()
#strPlayFajrAzaanMP3Command = 'curl --data "p0=play&p1=mixer&p2=volume&p3=30&p4=playlist&p5=play&p6=/home/pi/adhan/mp3/Adhan-fajr.mp3&player=aa:aa:00:00:00:00&start=0" http://localhost:9000/status.html'

strVolumeFajr = "curl -d '{\"id\":0,\"params\":[\"aa:aa:00:00:00:00\",[\"mixer\",\"volume\",\"30\"]],\"method\":\"slim.request\"}' http://localhost:9000/jsonrpc.js"
strPlayFajrAzaanMP3Command = "curl -d '{\"id\":0,\"params\":[\"aa:aa:00:00:00:00\",[\"playlist\",\"play\",\"/home/pi/adhan/mp3/Adhan-Makkah.mp3\"]],\"method\":\"slim.request\"}' http://localhost:9000/jsonrpc.js"


strVolumeAdhan = "curl -d '{\"id\":0,\"params\":[\"aa:aa:00:00:00:00\",[\"mixer\",\"volume\",\"60\"]],\"method\":\"slim.request\"}' http://localhost:9000/jsonrpc.js"
#strPlayAzaanMP3Command = "curl -d '{\"id\":0,\"params\":[\"aa:aa:00:00:00:00\",[\"playlist\",\"play\",\"/home/pi/adhan/mp3/Adhan-Makkah.mp3\"]],\"method\":\"slim.request\"}' http://localhost:9000/jsonrpc.js"
strPlayAzaanMP3Command = '{}/playAzaan.sh {}/Adhan-Madinah.mp3 {}'.format(root_dir, root_dir, azaan_vol)

strUpdateCommand = '{}/updateAzaanTimers.py >> {}/adhan.log 2>&1'.format(root_dir, root_dir)
strClearLogsCommand = 'truncate -s 0 {}/adhan.log 2>&1'.format(root_dir)
strJobComment = 'rpiAdhanClockJob'

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
addAzaanTime('volume',times['fajr'],system_cron,strVolumeFajr)
addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('volume',times['dhuhr'],system_cron,strVolumeAdhan)
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
