import time
from datetime import datetime, timedelta
from pytz import timezone
import schedule
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import credentials
import send_emails

# Change this variable to your timezone. See README for more info
local_tz = timezone('America/Los_Angeles')


class Automate_reservation:
    def __init__(self, booking_details):
        """
        Creates the class variables required to book a slot.
        Contained in the credentials.py file.
        """
        self.date = datetime(booking_details['year'],
                            booking_details['month'],
                            booking_details['day'])
        self.email = booking_details['email']
        self.password = booking_details['password']
        self.resort = booking_details['resort']

    def main(self, test_mode=True):
        """
        Creates a new browser instance, navigates the browser through login,
        checks if the desired slot (as defined in the credentials.py file) is
        available and if so, books it.

        When done testing code and ready to run, toggle test_mode
        to False. test_mode goes through the whole process but
        does not submit the form.
        """

        # This is the timezone defined outside of the class, which allows the
        # scheduler to sync with the machine's internal clock.
        global local_tz

        # The check belows tells the scheduler to cancel the job
        # if we're past the desired reservation date.
        if datetime.now().astimezone(local_tz) > \
                    self.date.astimezone(local_tz) + timedelta(days=1):
            print("Returning schedule.CancelJob, since we're past the date of the desired reservation.")
            return schedule.CancelJob


        try:
            # Create new browser
            browser = self.new_browser_instance(
                                test_mode=test_mode
                                                )
            print('Created a new browser')
            time.sleep(5)

            # Login using the credentials specified in the credentials.py file
            self.login(browser)
            print('Managed to login')
            time.sleep(5)

            # find_slot() will return True if the slot is available.
            # otherwise, it will raise an exception.
            print("Now looking for availability for date:",
                    self.date)
            is_available = self.find_slot(browser, self.date)
            time.sleep(2)

            if is_available:
                # book_slot() will return True if the process goes smoothly,
                # otherwise raise an exception.
                print('Found the slot, will now try to book it...')
                is_booked = self.book_slot(browser,
                                            test_mode=test_mode)

                if is_booked:
                    print('Slot booked, now cancelling this job!')
                    browser.quit()
                    # send_emails.email(
                             # 'thomatou@hotmail.com',
                             # 'Slot booked for user ' + self.email,
                             # 'Hopefully some good skiing on: ' + self.date.strftime('%a %b %d %Y') + ' at ' + self.resort
                             #     )
                    return schedule.CancelJob

        except Exception as ex:
            print("Going to quit this browser because of exception:", ex)
            time.sleep(5)

        # Need to check if memory allocated to variables that go out of scope
        # are automatically cleaned up in Python
        try:
            browser.quit()
        except Exception:
            pass

    def new_browser_instance(self, test_mode=True):
        """
        Creates a Selenium chrome browser instance, which is made headless
        when not in test mode.
        Make sure that the path to the chromedriver executable is the correct
        one for your machine.
        """

        chrome_options = Options()

        if not test_mode:
            chrome_options.add_argument("--headless")

        browser = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

        return browser

    def login(self, browser):
        """
        Uses a browser instance, along with the credentials (email/password)
        given in the eponymous file to identify the user with their ikon
        account. Will raise an exception if login is unsuccessful.
        """

        try:
            # Log in address
            browser.get('https://account.ikonpass.com/en/login')
            time.sleep(2)

            # Wait until page is loaded fully
            WebDriverWait(browser, 3).until(EC.presence_of_element_located(
                                        (By.XPATH, '//*[@id="email"]')))

            # Enter your login details
            browser.find_element_by_xpath('//*[@id="email"]').send_keys(
                                self.email)

            browser.find_element_by_xpath(
                            '//*[@id="sign-in-password"]'
                                        ).send_keys(self.password)

            time.sleep(1)

            # Deal with the banners for cookies. Turns out there are three of
            # those superimposed on top of each other, which block access to
            # the reservation buttons.
            buttons = browser.find_elements_by_class_name('cc-btn.cc-dismiss')
            for i in range(len(buttons)-1, -1, -1):
                buttons[i].click()
                time.sleep(1)

            # Submit your login info
            browser.find_element_by_class_name('submit').click()

            # Check that hitting submit redirects you to
            # "https://account.ikonpass.com/en/myaccount", indicating success.
            # Else: raise an error.

            time.sleep(1)
            if browser.current_url != 'https://account.ikonpass.com/en/myaccount':
                raise Exception("Invalid credentials.")

        except Exception as ex:
            raise Exception("Login failed.", ex)

    def find_slot(self, browser, date):
        """
        Given a browser instance that has logged in successfully, will check if
        the slot of interest is available.
        Date has to be a datetime object containg year, month and day.
        Returns True if the desired slot is available, otherwise raises an
        exception.
        """

        # Assuming you're logged in, go to reservations page
        browser.get(
                'https://account.ikonpass.com/en/myaccount/add-reservations/'
                    )

        # Wait until page is loaded fully
        WebDriverWait(browser, 3).until(EC.presence_of_element_located(
                                    (By.CLASS_NAME, 'sc-pRStN')))

        # Input the name of the resort
        browser.find_element_by_class_name('sc-pRStN').send_keys(self.resort)

        time.sleep(1)

        # Select the first choice in the list that comes up
        # Current implementation requires that you have self.resort
        # selected as a favourite in your ikon account.

        browser.find_element_by_xpath(
        '//*[@id="react-autowhatever-resort-picker-section-1-item-0"]'
                                    ).click()

        # Uncomment the next 3 lines if self.resort is not a favourite (and
        # comment out the one above)

        # browser.find_element_by_xpath(
        # '//*[@id="react-autowhatever-resort-picker-section-0-item-0"]'
                                    # ).click()

        # Click continue to get to the calendar
        browser.find_element_by_class_name(
                                    'sc-AxjAm.jxPclZ'
                                            ).click()

        time.sleep(1)

        # If the reservation is not for the current month,
        # toggle calendar to the correct one.

        # First let's format our datetime object to match the website's format
        # for month
        # Website's format for month at top of calendar is "DECEMBER 2020"
        month_year = date.strftime('%B %Y').upper()

        # Check what month we are currently looking at
        counter = 0

        while month_year != browser.find_element_by_class_name('sc-pckkE.goPjwB').text:

        # Add one month to the calendar if we're not looking at the correct one
            browser.find_element_by_class_name('amp-icon.icon-chevron-right').click()
            counter += 1
            # If we've gone through too many iterations, there might be an
            # error with formatting of calendar month, so raise an exception
            # here to avoid getting stuck in infinite loop.
            if counter > 10:
                raise Exception(
                "The desired date is not available for booking yet"
                                )

        # The actual calendar dates are stored in the format 'Thu Dec 10 2020'
        # Let's convert our desired reservation date into that format
        calendar_date = date.strftime('%a %b %d %Y')

        # Click on the desired calendar date
        browser.find_element_by_css_selector(
                        "[aria-label=" + "\"" + calendar_date + "\"" + "]"
                                            ).click()

        # See if the button to reserve is there.
        # If so, return True. If not, raise an exception.
        slot_found = False
        time.sleep(2)

        try:
            WebDriverWait(browser, 3).until(EC.element_to_be_clickable(
                            (By.CLASS_NAME, 'sc-AxjAm.jxPclZ.sc-pAArZ.lkoEyq')))

            button = browser.find_element_by_class_name(
                                'sc-AxjAm.jxPclZ.sc-pAArZ.lkoEyq'
                                                        )
            button.click()
            slot_found = True

        except TimeoutException:
            raise Exception('This slot is currently not available.')

        return slot_found

    def book_slot(self, browser, test_mode=True):
        """
        Given a browser instance that has been logged in and found the desired
        slot as done using the find_slot() function, this function will book
        said slot and return True. If it runs into an issue, it will raise
        an exception.
        In test_mode, the function will run through the motions but not hit
        submit.
        """

        # Click on "Review my reservations" button once it's clickable.
        try:
            WebDriverWait(browser, 3).until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'sc-AxjAm.jxPclZ.sc-pAKSZ.dHRKUJ')
                                                                    ))

            browser.find_element_by_class_name(
                                'sc-AxjAm.jxPclZ.sc-pAKSZ.dHRKUJ'
                                            ).click()

            # Tick the checkbox
            browser.find_element_by_class_name('input').click()
            # Submit the form (if not in test_mode)
            # If in test_mode, want to leave the browser open so can inspect
            # that everything has been done correctly.

            if not test_mode:
                browser.find_element_by_class_name('sc-AxjAm.jxPclZ').click()
                print('Booked the desired slot, for date:', self.date)

            return True

        except Exception as ex:
            raise Exception("Ran into an issue booking the slot", ex)

for booking_number in credentials.booking:
    schedule.every(10).seconds.do(
                Automate_reservation(credentials.booking[booking_number]).main,
                test_mode=False
                              )

while schedule.jobs:
    schedule.run_pending()
    time.sleep(1)
    print(datetime.now().astimezone(local_tz).strftime("%c"))
