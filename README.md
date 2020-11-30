# Automating reservations for Ikon-operated ski resorts.

Because of the ongoing pandemic, most ski resorts are now requiring reservations to manage crowds. Ikon-owned and operated ski hills have their weekend days fully booked up months in advance, leaving weekend warriors with two options: hitting refresh every minute in the hope of snagging an elusive spot as a result of cancellations, or using this script to do the work for them.

### Tired of hitting refresh in the hope of getting a reservation to your favourite ski resort? Use this bot! 

Given a desired reservation date and ski resort, as well as the username and password of a particular Ikon pass holder, this script will launch a chrome web browser and look for availability on that given date. If no slots are available for that day, the browser will exit, and this process will repeat itself once every minute until the given date, or until availability for that slot is found, whichever comes first.

Important note: The current implementation only works for ski resorts that are using the Ikon-operated reservations system, i.e. Arapahoe Basin, Big Sky, Brighton, The Summit at Snoqualmie, and Crystal Mountain Resort. 

### Let's go! 

This python script has a few dependencies, which need to be installed to ensure smooth sailing.

Requirements: 
* Python3.x (tested with python3.7)
* [`selenium`](https://pypi.org/project/selenium/)
* [`schedule`](https://schedule.readthedocs.io/en/stable/)
* [`chromedriver`](https://chromedriver.chromium.org/downloads). Make sure you specify the absolute path to your chromedriver executable file in the `ikon_reservations.py` file. On ubuntu, Install the chrome driver using the following command: `sudo apt-get install chromium-chromedriver`. Your chromedriver will then be located at the following location: `/usr/bin/chromedriver`.
* [`pytz`](https://pypi.org/project/pytz/). This is to ensure that the script runs on your timezone. The current implementation assumes that you're on LA time. If that is not the case, look up your relevant timezone [here](https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones), and pass that to the `local_tz` variable in the `ikon_reservations.py` script.

To specify the desired reservation dates, fill in the information for every reservation desired using the `mock_credentials.py` file. You can have the script running and looking for multiple reservations at the same time, but for the booking to actually happen, you you can't already be holding 10 reserved days, or the website won't let you through with another booking. Yes, this system requires you to store your password in plain text –– use at your own risk. Finally, change the name of that file to `credentials.py`, and then the script can be run using the following command: `python3.x ikon_reservations.py`. Once the desired slot is booked, the script will automatically stop, and Ikon will send you an email confirming your reservation! 

You will need to leave your local machine running until all the desired slots are booked, which is why I recommend setting up a [free server](https://www.oracle.com/cloud/free/#always-free) and running this script on there. Note that an oracle Always Free ubuntu server will require installation of python and the dependencies listed above. Assuming all of the dependencies have been installed, the script can be run indefinitely using the `nohup python3.x -u ikon_reservations.py &` command, which will prevent the process from crashing when you disconnect from the server.





# LOGIN FUNCTION DOESN'T HAVE A CHECK TO SEE IF LOGIN WAS SUCCESSFUL. IF LOGIN ISN'T SUCCESSFUL, THE NEXT FUNCTION THROWS AN EXCEPTION. NEED TO FIX THAT.
