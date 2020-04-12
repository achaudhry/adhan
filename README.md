# Raspberry Pi Adhan Clock
This projects uses a python script which automatically calculates [adhan](https://en.wikipedia.org/wiki/Adhan){:target="_blank" rel="noopener"} times every day and plays all five adhans with Logitech Media Server and Airplay Speakers at their scheduled time using cron.

## Prerequisites
1. Raspberry Pi running Raspbian
  1. I would stay away from Raspberry Pi zero esp if you're new to this stuff since it doesn't come with a built in audio out port.
  2. Also, if you haven't worked with raspberry pi before, I would highly recommend using [these](https://www.raspberrypi.org/documentation/installation/noobs.md){:target="_blank" rel="noopener"} instructions to get it up and running: https://www.raspberrypi.org/documentation/installation/noobs.md
2. Airplay Speakers ([GGMM](https://amzn.to/2RwiA4B){:target="_blank" rel="noopener"}, [Sonos](https://amzn.to/2XqB4al){:target="_blank" rel="noopener"})
3. Logitech Media Server

## Instructions
1. Update at first
    * `$ sudo apt-get update && sudo apt-get dist-upgrade`
2. Install necessary libraries & tools
    * `$ sudo apt-get install -y libsox-fmt-all libflac-dev libfaad2 libmad0 git`
3. Clone repo: Clone this repository on your raspberry pi in your `home` directory. (Tip: run `$ cd ~` to go to your home directory)
    * `$ git clone git@github.com:semaf/adhan.git`
    * After doing that you should see an `adhan` direcotry in your `home` directory.
4. Install LMS (Logitech Media Server): Download lastest [Logitech Media Server](http://downloads.slimdevices.com/LogitechMediaServer_v7.9.2/logitechmediaserver_7.9.2_arm.deb){:target="_blank" rel="noopener"} Debian Package for Raspberry Pi.
    * `$ wget http://downloads.slimdevices.com/LogitechMediaServer_v7.9.2/logitechmediaserver_7.9.2_arm.deb`
    * `$ sudo dpkg -i logitechmediaserver_7.9.2_arm.deb`
5. Open LMS on browser, setup LMS and connect your Airplay Speakers.
    * URL to LMS https://my_server_ip:9000 (if port 9000 is not available, LMS will change port to 9001 or 9002 or ...)
    * On Web Gui of LMS go to Settings > Plugins and install `AirPlay bridge`. After installation go to Settings of `AirPlay bridge`.
    * Tick `Start the Bridge > Running`
    * Select Binary `squeeze2raop-armv6hf-static` and apply on bottom right
    * Close settings and get back to main GUI back and select your AirPlay Speaker Name.
5. Now go back to commandline and into `adhan` directory: `$cd adhan`
6. Open `updateAzaanTimers.py` in your favorite editor. For instance, `nano` is a simple one: `$ nano updateAzaanTimers.py`. Change the port (9000 or 9001 or ...) to that is used on your Server

## Configuration
The original python script is super configurable. Please see the [manual](http://praytimes.org/manual){:target="_blank" rel="noopener"} for advanced instructions. However, below are the three basic things you'll need to change to get it up and running.

* Set the latitude and longitude so it can calculate accurate prayer times for that location. Modify the following lines:
```
#Set latitude and longitude here
#--------------------
lat = 42.3601
long = -71.0589
```
* Set adhan time [calculation method](http://praytimes.org/manual#Set_Calculation_Method){:target="_blank" rel="noopener"}. Modify the following line:
```
PT.setMethod('ISNA')
```
Save your changes by pressing `Control X` and then `Y`.

## Run it for to get output on Logitech Media Server
Run this command `$ python /home/pi/adhan/updateAzaanTimers.py`. If everythig worked, your output will look something like this:
```
04:24 Fajr
06:04 Sunrise
13:00 Dhuhr
16:43 Asr
19:46 Maghrib
21:15 Isha
24 4 * * * curl --data "p0=playlist&p1=play&p2=/home/pi/adhan/mp3/Sabah-Ezani.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9000/status.html # rpiAdhanClockJob
0 13 * * * curl --data "p0=playlist&p1=play&p2=/home/pi/adhan/mp3/Ezan.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9000/status.html # rpiAdhanClockJob
43 16 * * * curl --data "p0=playlist&p1=play&p2=/home/pi/adhan/mp3/Ezan.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9000/status.html # rpiAdhanClockJob
46 19 * * * curl --data "p0=playlist&p1=play&p2=/home/pi/adhan/mp3/Ezan.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9000/status.html # rpiAdhanClockJob
15 21 * * * curl --data "p0=playlist&p1=play&p2=/home/pi/adhan/mp3/Ezan.mp3&player=00:00:00:18:70:c8&start=0" http://localhost:9000/status.html # rpiAdhanClockJob
15 3 * * * python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1 # rpiAdhanClockJob
@monthly truncate -s 0 /home/pi/adhan/adhan.log 2>&1 # rpiAdhanClockJob
Script execution finished at: 2020-04-12 13:20:26.870908
```

If you look at the last few lines, you'll see that 5 adhan times have been scheduled. Then there is another line at the end which makes sure that at 1am every day the same script will run and calculate adhan times for that day. And lastly, there is a line to clear logs on a monthly basis so that your log file doesn't grow too big.

VOILA! You're done!! Plug in your speakers and enjoy!

## Tips:
1. You can see your currently scheduled jobs by running `crontab -l`
2. The output of the job that runs at 1am every night is being captured in `/home/pi/adhan/adhan.log`. This way you can keep track of all successful runs and any potential issues. This file will be truncated at midnight on the forst day of each month. To view the output type `$ cat /home/pi/adhan/adhan.log`

### Credits
I have made modifications / bug fixes but I've used the following as starting point:
* Main Source of this code is by [achaudhry https://github.com/achaudhry/adhan](https://github.com/achaudhry/adhan){:target="_blank" rel="noopener"}
* Python code to calculate adhan times: http://praytimes.org/code/
* Basic code to turn the above into an adhan clock: http://randomconsultant.blogspot.co.uk/2013/07/turn-your-raspberry-pi-into-azaanprayer.html
* Cron scheduler: https://pypi.python.org/pypi/python-crontab/
