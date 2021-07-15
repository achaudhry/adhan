# Raspberry Pi Adhan Clock
This projects uses a python script which automatically calculates [adhan](https://en.wikipedia.org/wiki/Adhan) times every day and plays all five adhans at their scheduled time using cron. 

## Prerequisites
1. Raspberry Pi running Raspbian
  1. I would stay away from Raspberry Pi zero esp if you're new to this stuff since it doesn't come with a built in audio out port.
  2. Also, if you haven't worked with raspberry pi before, I would highly recommend using [these](https://www.raspberrypi.org/documentation/installation/noobs.md) instructions to get it up and running: https://www.raspberrypi.org/documentation/installation/noobs.md
2. Speakers
3. Auxiliary audio cable

## Caution when using Bluetooth Speakers
1. Raspberry Pi's bluetooth drivers has known issues that result in intermittent disconnections. Using a wired speaker is recommended

## Instructions
1. Install git: Go to raspberry pi terminal (command line interface) and install `git`
  ```bash
  sudo apt-get install git
  ```
2. Clone repo: Clone this repository on your raspberry pi in your `home` directory. (Tip: run `$ cd ~` to go to your home directory)
  ```bash
  $ git clone <get repo clone url from github and put it here>
  ```
  * After doing that you should see an `adhan` directory in your `home` directory. 

## Run it for the first time
Run this command:

```bash
$ python3 /home/pi/adhan/updateAzaanTimers.py --lat <YOUR_LAT> --lon <YOUR_LNG> --method <METHOD>
```

Replace the arguments above with your location information and calculation method:
* Set the latitude and longitude so it can calculate accurate prayer times for that location.
* Set adhan time [calculation method](http://praytimes.org/manual#Set_Calculation_Method).

### Calculation Methods available
```json
{
   "MWL":{
      "name":"Muslim World League",
      "params":{"fajr":18, "isha":17}
   },
   "ISNA":{
      "name":"Islamic Society of North America (ISNA)",
      "params":{"fajr":15, "isha":15}
   },
   "Egypt":{
      "name":"Egyptian General Authority of Survey",
      "params":{"fajr":19.5, "isha":17.5}
   },
   "Makkah":{
      "name":"Umm Al-Qura University, Makkah",
      "params":{"fajr":18.5, "isha":"90 min"}
   },
   "Karachi":{
      "name":"University of Islamic Sciences, Karachi",
      "params":{"fajr":18, "isha":18}
   },
   "Tehran":{
      "name":"Institute of Geophysics, University of Tehran",
      "params":{"fajr":17.7, "isha":14, "maghrib":4.5, "midnight":"Jafari"}
   },
   "Jafari":{
      "name":"Shia Ithna-Ashari, Leva Institute, Qum",
      "params":{"fajr":16, "isha":14, "maghrib":4, "midnight":"Jafari"}
   }
}
```


If everythig worked, your output will look something like this:
```
---------------------------------
Co-ordinates provided
---------------------------------
Latitude: 28.479250699999998, Longitude: 77.535747, Method: Karachi
---------------------------------

---------------------------------
Prayer Times
---------------------------------
Fajr:    04:08 hrs
Dhuhr:   12:16 hrs
Asr:     15:50 hrs
Maghrib: 18:59 hrs
Isha:    20:25 hrs
---------------------------------

---------------------------------
Crob jobs scheduled
---------------------------------
8 4 * * * omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/Adhan-fajr.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
16 12 * * * omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/Adhan-Makkah1.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
50 15 * * * omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/Adhan-Makkah1.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
59 18 * * * omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/Adhan-Makkah1.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
25 20 * * * omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/Adhan-Makkah1.mp3 > /dev/null 2>&1 # rpiAdhanClockJob
0 8 * * 5 omxplayer --vol 0 -o local /home/pi/Desktop/Github/adhan/media/002-surah-baqarah-mishary.mp3 > /dev/null 2>&1 # Surah Baqarah
---------------------------------

```

If you look at the last few lines, you'll see that 5 adhan times have been scheduled. Then there is another line at the end which makes sure that at 1am every day the same script will run and calculate adhan times for that day. And lastly, there is a line to clear logs on a monthly basis so that your log file doesn't grow too big.


Note that for later runs you do not have to supply any arguments as they are saved in `/home/pi/adhan/settings.ini`.

## Play Surah Baqrah on Fridays
If you notice the output above, it has a line item with comment "# Surah Baqarah". This is disabled by default, but can be turned on by editing settings.ini and updating "FRIDAY" section
```
[FRIDAY]
playsurahbaqarah = True
surahvolume = 0
```

VOILA! You're done!! Plug in your speakers and enjoy!

Please see the [manual](http://praytimes.org/manual) for advanced configuration instructions. 

There are 2 additional arguments that are optional, you can set them in the first run or
further runs: `--fajr-azaan-volume` and `azaan-volume`. You can control the volume of the Azaan
by supplying numbers in millibels. To get more information on how to select the values, run the command with `-h`.

## Configuring custom actions before/after adhan

Sometimes it is needed to run custom commands either before, after or before
and after playing adhan. For example, if you have
[Quran playing continuously](https://github.com/LintangWisesa/RPi_QuranSpeaker),
you would want to pause and resume the playback. Another example, is to set your
status on a social network, or a calendar, to block/unblock the Internet
using [pi.hole rules](https://docs.pi-hole.net/), ... etc.

You can easily do this by adding scripts in the following directories:
- `before-hooks.d`: Scripts to run before adhan playback
- `after-hooks.d`: Scripts to run after adhan playback

### Example:
To pause/resume Quran playback if using the
[RPi_QuranSpeaker](https://github.com/LintangWisesa/RPi_QuranSpeaker) project, place
the following in 2 new files under the above 2 directories:

```bash
# before-hooks.d/01-pause-quran-speaker.sh
#!/usr/bin/env bash
/home/pi/RPi_QuranSpeaker/pauser.py pause
```

```bash
# after-hooks.d/01-resume-quran-speaker.sh
#!/usr/bin/env bash
/home/pi/RPi_QuranSpeaker/pauser.py resume
```

Do not forget to make the scripts executable:
```bash
chmod u+x ./before-hooks.d/01-pause-quran-speaker.sh
chmod u+x ./after-hooks.d/01-resume-quran-speaker.sh
```

## Tips:
1. You can see your currently scheduled jobs by running `crontab -l`
2. The output of the job that runs at 1am every night is being captured in `/home/pi/adhan/adhan.log`. This way you can keep track of all successful runs and any potential issues. This file will be truncated at midnight on the forst day of each month. To view the output type `$ cat /home/pi/adhan/adhan.log`

## Credits
I have made modifications / bug fixes but I've used the following as starting point:
* Python code to calculate adhan times: http://praytimes.org/code/ 
* Basic code to turn the above into an adhan clock: http://randomconsultant.blogspot.co.uk/2013/07/turn-your-raspberry-pi-into-azaanprayer.html
* Cron scheduler: https://pypi.python.org/pypi/python-crontab/ 
