# Raspberry Pi Adhan Clock
This projects uses a python script which automatically calculates [adhan](https://en.wikipedia.org/wiki/Adhan) times every day and plays all five adhans at their scheduled time using cron. 

## Prerequisites
1. Raspberry Pi running Raspbian
  1. I would stay away from Raspberry Pi zero esp if you're new to this stuff since it doesn't come with a built in audio out port.
  2. Also, if you haven't worked with raspberry pi before, I would highly recommend using [these](https://www.raspberrypi.org/documentation/installation/noobs.md) instructions to get it up and running: https://www.raspberrypi.org/documentation/installation/noobs.md
2. Speakers
3. Auxiliary audio cable

## Instructions
1. Install git: Go to raspberry pi terminal (command line interface) and install `git`
  * `$ sudo apt-get install git`
2. Clone repo: Clone this repository on your raspberry pi in your `home` directory. (Tip: run `$ cd ~` to go to your home directory)
  * `$ git clone <get repo clone url from github and put it here>`
  * After doing that you should see an `adhan` direcotry in your `home` directory. 

## Run it for the first time
Run this command:

```bash
$ python /home/pi/adhan/updateAzaanTimers.py --lat <YOUR_LAT> --lng <YOUR_LNG> --method <METHOD>`.
```

Replace the arguments above with your location information and calculation method:
* Set the latitude and longitude so it can calculate accurate prayer times for that location.
* Set adhan time [calculation method](http://praytimes.org/manual#Set_Calculation_Method).

If everythig worked, your output will look something like this:
```
20 60 Egypt
05:51
11:52
14:11
16:30
17:53
51 5 * * * omxplayer -o local /home/pi/adhan/Adhan-fajr.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
52 11 * * * omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
11 14 * * * omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
30 16 * * * omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
53 17 * * * omxplayer -o local /home/pi/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
0 1 * * * python /home/pi/adhan/updateAzaanTimers.py >> /home/pi/adhan/adhan.log 2>&1 # rpiAdhanClockJob
@monthly truncate -s 0 /home/pi/adhan/adhan.log 2>&1 # rpiAdhanClockJob
Script execution finished at: 2017-01-06 21:22:31.512667
```

If you look at the last few lines, you'll see that 5 adhan times have been scheduled. Then there is another line at the end which makes sure that at 1am every day the same script will run and calculate adhan times for that day. And lastly, there is a line to clear logs on a monthly basis so that your log file doesn't grow too big.

Note that for later runs you do not have to supply any arguments as they are saved in `/home/pi/adhan/.settings`.

VOILA! You're done!! Plug in your speakers and enjoy!

Please see the [manual](http://praytimes.org/manual) for advanced configuration instructions. 

## Tips:
1. You can see your currently scheduled jobs by running `crontab -l`
2. The output of the job that runs at 1am every night is being captured in `/home/pi/adhan/adhan.log`. This way you can keep track of all successful runs and any potential issues. This file will be truncated at midnight on the forst day of each month. To view the output type `$ cat /home/pi/adhan/adhan.log`

### Credits
I have made modifications / bug fixes but I've used the following as starting point:
* Python code to calculate adhan times: http://praytimes.org/code/ 
* Basic code to turn the above into an adhan clock: http://randomconsultant.blogspot.co.uk/2013/07/turn-your-raspberry-pi-into-azaanprayer.html
* Cron scheduler: https://pypi.python.org/pypi/python-crontab/ 

