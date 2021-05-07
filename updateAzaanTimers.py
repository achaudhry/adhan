#!/usr/bin/env python

import datetime
import time
import sys
from os.path import dirname, abspath, join as pathjoin
import argparse
from configparser import ConfigParser

root_dir = dirname(abspath(__file__))
sys.path.insert(0, pathjoin(root_dir, 'crontab'))
from modules.praytimes import PrayTimes
PT = PrayTimes() 

from crontab import CronTab
system_cron = CronTab(user='pi')


# HELPER FUNCTIONS
# ---------------------------------
# ---------------------------------
# Function to add azaan time to cron
def parseArgs():
    parser = argparse.ArgumentParser(description='Calculate prayer times and install cronjobs to play Adhan')
    parser.add_argument('--lat', type=float, dest='lat',
                        help='Latitude of the location, for example 30.345621')
    parser.add_argument('--lon', type=float, dest='lon',
                        help='Longitude of the location, for example 60.512126')
    parser.add_argument('--method', choices=['MWL', 'ISNA', 'Egypt', 'Makkah', 'Karachi', 'Tehran', 'Jafari'],
                        dest='method',
                        help='Method of calculation')
    parser.add_argument('--azaan-volume', type=int, dest='default_azaan_vol',
                        help='Volume for azaan (other than fajr) in millibels, 1500 is loud and -30000 is quiet (default 0)')
    parser.add_argument('--fajr-azaan-volume', type=int, dest='fajr_azaan_vol',
                        help='Volume for fajr azaan in millibels, 1500 is loud and -30000 is quiet (default 0)')
    return parser

def getConfig():
    # Parse arguments
    parser = parseArgs()
    args = parser.parse_args()
    
    # Initialise and read config file if present
    config = ConfigParser()
    file_path = pathjoin(root_dir, 'settings.ini')
    config.read(file_path)

    lat = lon = method = fajr_azaan_vol = default_azaan_vol = surahBaqarah = surahVolume = None

    # Get mandatory data. First check args, if not present check settings.ini
    try:
        if args.lat:
            lat = float(args.lat)
            config['DEFAULT']['lat'] = str(lat)
        else:
            lat = float(config['DEFAULT']['lat'])
        
        if args.lon:
            lon = float(args.lon)
            config['DEFAULT']['lon'] = str(lon)
        else:
            lon = float(config['DEFAULT']['lon'])

        if args.method:
            method = args.method
            config['DEFAULT']['method'] = method
        else:
            method = config['DEFAULT']['method']
    except:
        print("Incorrect value or values not provided")
        lat = lon = method = None


    # Get optional data
    try:
        if args.default_azaan_vol:
            default_azaan_vol = int(args.default_azaan_vol)
        else:
            default_azaan_vol = int(config['VOLUME']['defaultAzaanVolume'])

        if args.fajr_azaan_vol:
            fajr_azaan_vol = int(args.fajr_azaan_vol)
        else:
            fajr_azaan_vol = int(config['VOLUME']['fajrAzaanVolume'])
    except:
        default_azaan_vol = 0
        fajr_azaan_vol = 0

        
    config["VOLUME"] = {
        "defaultAzaanVolume": str(default_azaan_vol), 
        "fajrAzaanVolume": str(fajr_azaan_vol)
        }


    # Setup Surah Baqarah on Fridays
    try:
        surahBaqarah = bool(config['FRIDAY']['playSurahBaqarah'])
        surahVolume = int(config['FRIDAY']['surahVolume'])
    except:
        surahBaqarah = False
        surahVolume = 0
        config["FRIDAY"] = {"playSurahBaqarah": str(surahBaqarah), "surahVolume": str(surahVolume)}
    

    # If any of the mandatory values not provided or configures in settings.ini, exit and show usage
    if not lat or not lon or not method:
        print("No values provided, please provide values as per below usage")
        parser.print_usage()
        sys.exit(1)

    # save values to settings.ini
    with open(file_path, 'w') as configfile:
        config.write(configfile)

    return lat, lon, method, fajr_azaan_vol, default_azaan_vol, surahBaqarah, surahVolume


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

def addFriday(strSurahName, objCronTab, strCommand):
  job = objCronTab.new(command=strCommand,comment=strSurahName)
  job.minute.on(0)
  job.hour.on(8)
  job.dow.on(5)
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
# ---------------------------------
# ---------------------------------
# HELPER FUNCTIONS END
# Merge args with saved values if any
lat, lon, method, fajr_azaan_vol, default_azaan_vol, surahBaqarah, surahVolume = getConfig()
# Set calculation method, utcOffset and dst here
# By default system timezone will be used
# --------------------
PT.setMethod(method)
utcOffset = -(time.timezone/float(3600))
isDst = time.localtime().tm_isdst

now = datetime.datetime.now()
strPlayFajrAzaanMP3Command = f"omxplayer --vol {fajr_azaan_vol} -o local {root_dir}/media/Adhan-fajr.mp3 > /dev/null 2>&1"
strPlayAzaanMP3Command = f"omxplayer --vol {default_azaan_vol} -o local {root_dir}/media/Adhan-Makkah1.mp3 > /dev/null 2>&1"
strUpdateCommand = f"python {root_dir}/updateAzaanTimers.py >> {root_dir}/adhan.log 2>&1"
strClearLogsCommand = f"truncate -s 0 {root_dir}/adhan.log 2>&1"
strJobComment = "rpiAdhanClockJob"
strSurahBaqarahMP3Command = f"omxplayer --vol {surahVolume} -o local {root_dir}/media/002-surah-baqarah-mishary.mp3 > /dev/null 2>&1"

# Remove existing jobs created by this script
system_cron.remove_all(comment=strJobComment)

# Calculate prayer times
times = PT.getTimes((now.year,now.month,now.day), (lat, lon), utcOffset, isDst)
print("---------------------------------")
print("Co-ordinates provided")
print("---------------------------------")
print(f"Latitude:   {lat} \nLongitude:  {lon} \nMethod:     {method}")
print("---------------------------------")
print()
print("---------------------------------")
print("Prayer Times")
print("---------------------------------")
print(f"Fajr:    {times['fajr']} hrs")
print(f"Dhuhr:   {times['dhuhr']} hrs")
print(f"Asr:     {times['asr']} hrs")
print(f"Maghrib: {times['maghrib']} hrs")
print(f"Isha:    {times['isha']} hrs")
print("---------------------------------")

# Add times to crontab
print()
print("---------------------------------")
print("Crob jobs scheduled")
print("---------------------------------")
addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('dhuhr',times['dhuhr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('asr',times['asr'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('maghrib',times['maghrib'],system_cron,strPlayAzaanMP3Command)
addAzaanTime('isha',times['isha'],system_cron,strPlayAzaanMP3Command)
if surahBaqarah == True:
    addFriday('Surah Baqarah', system_cron, strSurahBaqarahMP3Command)
print("---------------------------------")
print()
# Run this script again overnight
addUpdateCronJob(system_cron, strUpdateCommand)

# Clear the logs every month
addClearLogsCronJob(system_cron,strClearLogsCommand)

system_cron.write_to_user(user='pi')
print('Script execution finished at: ' + str(now))

