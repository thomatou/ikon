current_tzimport time
from datetime import datetime, timedelta
from pytz import timezone
import schedule
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import credentials


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
        Creates a new browser instance, navigates the browser through identification, checks if the desired slot (as defined in the
        booking_details.py file) is available and if so, books it.

        When done testing code and ready to run, toggle test_mode to False.
        test_mode goes through the whole process but does not submit the form.
        """

        global local_tz

        # We need to cancel this scheduled job if we're past the booking date
        # E.g., if we're trying to book a slot for 06/26 and it's 06/27
        # let's cancel the job. Can probably make that dependent on the exact
        # time of booking.
        # The server runs in UTC time so have to convert to pacific time first
        # local_tz = timezone('America/Los_Angeles')

        if datetime.now().astimezone(local_tz) > \
                    self.date.astimezone(local_tz) + timedelta(days=1):
            print("Returning schedule.CancelJob, since we're past the date of the desired reservation.")
            return schedule.CancelJob

        try:
            browser = self.new_browser_instance(test_mode=test_mode)

            time.sleep(5)
            print('Created a new browser')

            # self.login() does not need to return anything if runs successfully
            # because browser instance gets modified

            # new_browser = self.login(browser)
            self.login(browser)
            print('Managed to login')
            time.sleep(5)
            print("Now looking for availability for date:", self.date)

            is_available = self.find_slot(browser, self.date)

            # if not is_available:
            #     raise Exception("Slot is not available.")
            # Suggestion by Stephen:
            # isAvailable = self.find_slot(browser, self.date)


            time.sleep(2)
            # Suggestion by Stephen:
            # if (isAvailable)
                # self.book_slot(browser, self.date, test_mode=test_mode)
            # have find_slot() raise an exception if it fails instead of
            # passing the contents to variable browser.

            # if is_available:
            #

            if is_available:
                print('Found the slot, will now try to book it...')
                is_booked = self.book_slot(browser, test_mode=test_mode)

                if is_booked:
                    print('Slot booked, now cancelling this job!')
                    browser.quit()
                    return schedule.CancelJob
            # Suggestion by stephen
            # TODO: Move browser.quit() to outside of except statement so that
            # you only write it once.

        except Exception as ex:
            print("Going to quit this browser because of exception:", ex)
            time.sleep(5)
            browser.quit()


    def new_browser_instance(self, test_mode=True):
        """
        Creates a Selenium browser instance, which is made headless
        when not in test mode (uses less resources).
        """

        chrome_options = Options()

        if not test_mode:
            chrome_options.add_argument("--headless")

        browser = webdriver.Chrome(executable_path='/Users/tchavas/chromedriver', options=chrome_options)

        return browser

    def login(self, browser):
        """
        Uses a browser instance, along with the credentials (email/password)
        given in the eponymous file to identify the user with their ikon
        account.
        Need to check if the login has actually worked, because current
        implementation does not throw an exception if login isn't successful.
        """

        # Log in address
        try:
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

            # Deal with the banners for cookies. Turns out there are three of those
            # superimposed on top of each other.

            # TODO: Current implementation to deal with them is not ideal, will
            # need to formalise it at some point. Currently works.

            buttons = browser.find_elements_by_class_name('cc-btn.cc-dismiss')
            for i in range(len(buttons)-1, -1, -1):
                buttons[i].click()
                time.sleep(1)

            # Submit your login info
            browser.find_element_by_class_name('submit').click()

        except Exception:
            raise Exception("Login did not go as planned")

    def find_slot(self, browser, date):
        """
        Uses a browser instance to check if the slot of interest is available.
        By default, has one participant in the booking.
        Date has to be a datetime object containg year, month and day.
        Returns the browser once the slot has been selected.
        """

        # Once you're logged in, go to reservations page
        browser.get(
                'https://account.ikonpass.com/en/myaccount/add-reservations/'
                    )

        # Wait until page is loaded fully
        WebDriverWait(browser, 3).until(EC.presence_of_element_located(
                                    (By.CLASS_NAME, 'sc-pAXKH')))

        # Input the name of the resort
        browser.find_element_by_class_name('sc-pAXKH').send_keys(self.resort)

        time.sleep(1)

        # Select the first choice in the list that comes up
        browser.find_element_by_xpath(
        '//*[@id="react-autowhatever-resort-picker-section-0-item-0"]'
                                    ).click()

        # Click continue to get to the calendar
        browser.find_element_by_class_name(
                            'sc-AxjAm.jxPclZ.sc-prpXb.hoYObS'
                                            ).click()

        time.sleep(1)

        # If the month of reservation is not the current month,
        # toggle calendar to the correct month
        month_year = date.strftime('%B %Y').upper()

        # Check what month we are looking at
        while month_year != browser.find_element_by_class_name('sc-pZMVu.hgRLdf').text:

        # Add one month to the calendar if we're not looking at the correct one
            browser.find_element_by_class_name('amp-icon.icon-chevron-right').click()

        # The dates are stored in the format 'Thu Dec 10 2020'
        # Let's convert our desired reservation date into that format
        calendar_date = date.strftime('%a %b %d %Y')

        # Click on the desired calendar date
        browser.find_element_by_css_selector(
                        "[aria-label=" + "\"" + calendar_date + "\"" + "]"
                                            ).click()

        # See if the button to reserve is there, if not, bubble that information
        # back up to the main function
        slot_found = False

        try:
            browser.find_element_by_class_name(
                        'sc-AxjAm.jxPclZ.sc-qPNpY.fZKxnA'
                                            ).click()
            slot_found = True

        # except NoSuchElementException:
        except Exception as ex:
            raise Exception('This slot is currently not available.', ex)
            # print(, ex)
            # browser.quit()

        return slot_found

    def book_slot(self, browser, test_mode=True):
        """
        This function is called only if find_slot() has found the slot
        that the desired slot is available.
        """

        # Click on review my reservations button
        # TODO: NEED TO PUT A WAIT FOR ELEMENT TO BE CLICKABLE
        # This should work, let's see
        try:
            WebDriverWait(browser, 3).until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'sc-AxjAm.jxPclZ.sc-qOubn.cugtRd')
                                                                    ))

            browser.find_element_by_class_name(
                                'sc-AxjAm.jxPclZ.sc-qOubn.cugtRd'
                                            ).click()

            # Tick the checkbox
            browser.find_element_by_class_name('input').click()

            # Submit the form
            # If in test_mode, want to leave the browser open so can inspect that
            # everything has been done correctly.

            if not test_mode:
                browser.find_element_by_class_name('sc-AxjAm.jxPclZ').click()
                print('Booked the desired slot, for date:', self.date)

            # If we booked the desired slot we can stop the scheduler from
            # scheduling that job again
            # return schedule.CancelJob
            return True

        except Exception as ex:
            raise Exception("Ran into an issue booking the slot", ex)
            return False


for booking_number in credentials.booking:
    schedule.every(10).seconds.do(
                Automate_reservation(credentials.booking[booking_number]).main,
                test_mode=True
                              )
# for booking_number in credentials.booking:
#     Automate_reservation(credentials.booking[booking_number]).main(test_mode=True)

while schedule.jobs:
    # try:
    schedule.run_pending()
    time.sleep(1)
    print(datetime.now().astimezone(local_tz).strftime("%c"))
    # except Exception as ex:
    #     print("exception caught in the scheduler loop: ", ex)
