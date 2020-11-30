# Tired of hitting refresh hoping to get a reservation to your ski resort? Use this bot! 

The idea behind this script is to automate the tiresome (and often stressful) process that involves getting a reservation to your favourite ski resort during this "new normal". 

Given a desired reservation date, the username and password of a particular user, as well as the preferred ski resort, this script will launch a chrome web browser and look for availability on that given date. If no slots are available for that day, the browser will exit, and this process will repeat itself once every minute, until availability for that slot is found, or the current date is in the past, whichever comes first. 

# Let's go! 

This python script has a few dependencies, which need to be installed for the script to run properly. 

Requirements: 
* Python 3.x (tested with python3.7)
* [`selenium`](https://pypi.org/project/selenium/)
* [`schedule`](https://schedule.readthedocs.io/en/stable/)
* [`chromedriver`](https://chromedriver.chromium.org/downloads). Make sure you specify the absolute path to your chromedriver executable file in the ikon_reservations.py file. On ubuntu, Install the chrome driver using the following command: `sudo apt-get install chromium-chromedriver`. Your chromedriver will then be located at the following location: `/usr/bin/chromedriver`.



# Ikon reservations


* Arapahoe Basin, Big Sky, Brighton, The Summit at Snoqualmie. 

