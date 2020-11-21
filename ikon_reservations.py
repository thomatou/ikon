import time
from datetime import datetime
from pytz import timezone
import traceback
import schedule
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import credentials

pst = timezone('America/Los_Angeles')


class Automate_reservation:
    def __init__(self, booking_details):
        """
        Creates the class variables required to book a slot.
        Contained in the credentials.py file.
        """
        self.month = booking_details['month']
        self.day = booking_details['day']
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

        # We need to cancel this scheduled job if we're past the booking date
        # E.g., if we're trying to book a slot for 06/26 and it's 06/27
        # let's cancel the job. Can probably make that dependent on the exact
        # time of booking.
        # The server runs in UTC time so have to convert to pacific time first
        #pst = timezone('America/Los_Angeles')

        if datetime.now().astimezone(pst) > datetime(2020, self.month, self.day + 1).astimezone(pst):
            print('doing schedule.CancelJob')
            return schedule.CancelJob

        browser = self.new_browser_instance(test_mode=test_mode)
        #
        # time.sleep(5)
        # print("we have a new browser instance!")

        new_browser = self.login(browser)
        # print("we've logged in")
        # time.sleep(5)

        time.sleep(1)

        browser = self.find_slot(new_browser)

        # time.sleep(5)
        #
        # if browser:
        #     print('returning canceljob')
        #     return self.book_slot(browser, test_mode=test_mode)

    def new_browser_instance(self, test_mode=True):
        """
        Creates a Selenium browser instance, which is made headless
        when not in test mode (uses less resources).
        """

        options = Options()
        if test_mode:
            options.headless = False
        else:
            options.headless = True

        browser = webdriver.Firefox(
                                    options=options,
                                    executable_path='/Users/tchavas/geckodriver'
                                    )
        return browser

    def login(self, browser):
        """
        Uses a browser instance, along with the credentials (email/password)
        given in the eponymous file to identify the user with their ikon
        account.

        Returns a browser instance where the user is identified.
        """

        # Log in address
        browser.get(
        'https://account.ikonpass.com/en/myaccount/add-reservations/'
                    )

        # # Fill in your details
        browser.find_element_by_xpath(
        '//*[@id="email"]').send_keys(self.email)
        browser.find_element_by_xpath(
        '//*[@id="sign-in-password"]').send_keys(self.password)

        time.sleep(1)

        # Submit your login info
        browser.find_element_by_class_name('submit').click()

        return browser

    def find_slot(self, browser):
        """
        Uses a browser instance to check if the slot of interest is available.
        By default, has one participant in the booking.
        Returns the browser once the slot has been selected.
        Only supports booking in the current month, or the following one.
        """

        browser.get(
        'https://account.ikonpass.com/en/myaccount/add-reservations/'
                    )

        time.sleep(1)
        # Input the name of the resort

        browser.find_element_by_class_name('sc-pAXKH').send_keys(
                                                    'crystal mountain'
                                                                )
        time.sleep(1)

        # Select the first choice that comes up
        browser.find_element_by_xpath('//*[@id="react-autowhatever-resort-picker-section-0-item-0"]').click()

        # Click continue to get to the calendar
        browser.find_element_by_class_name('sc-AxjAm.jxPclZ.sc-prpXb.hoYObS').click()


    #
    #     # If the month of reservation is not the current month,
    #     # toggle calendar to the following month (assuming you won't book more
    #     # than 29 days in advance)
    #     if self.month > datetime.now().month:
    #         browser.find_element_by_xpath(
    #             '/html/body/div[1]/form/div[6]/fieldset/div/div/div/a[2]/span'
    #                                      ).click()
    #
    #     # Select the day of interest
    #     browser.find_element_by_xpath("//td[not(contains(@class,'ui-datepicker-month'))]/a[text()='" + str(self.day) + "']").click()
    #
    #     # Add one participant to the booking
    #     browser.find_element_by_xpath('/html/body/div[1]/form/div[6]/div/fieldset/table/tbody/tr/td[1]/a[2]').click()
    #
    #     # Selected is there to check if we've been able to select the slot
    #     # of interest (to know when to exit browser or return it at the end
    #     # of function)
    #     selected = False
    #
    #     # Iterate through the table containing all the slots for the day
    #     for i in range(1, 17):
    #         # This is the location of the table row containing the time of
    #         # reservation
    #         row_xpath = '/html/body/div[1]/form/fieldset/div[1]/table/tbody/tr[' + str(i) + ']/td[1]'
    #
    #         try:
    #             # Format of temp_slot is the following:
    #             # "Tue, September 29, 7 AM to 9 AM"
    #             temp_slot = browser.find_element_by_xpath(row_xpath).text
    #             temp_time = temp_slot.split(',')[-1]
    #             start_time = temp_time.split('to')[0].strip()
    #
    #             # If this is the slot desired, let's book it!
    #             # Check that the slot we're looking at starts at the time
    #             # that was specified
    #             if self.hour == start_time:
    #
    #                 # Click the button adjacent to that slot if it exists
    #                 # If not, caught by exception and quit browser.
    #                 button_xpath = '/html/body/div[1]/form/fieldset/div[1]/table/tbody/tr[' + str(i) + ']/td[4]/a'
    #                 browser.find_element_by_xpath(button_xpath).click()
    #
    #                 print('Found the reservation you were looking for!')
    #                 selected = True
    #                 break
    #
    #         except Exception as ex:
    #             print('Caught an exception:', ex)
    #             print("\n")
    #             continue
    #
    #     # If the slot is available and selected, we can then return the browser
    #     # at the end of function so that we can go on to book it.
    #     if selected:
    #         return browser
    #
    #     browser.quit()
    #
    # def book_slot(self, browser, test_mode=True):
    #     """
    #     When given a browser where the user is identified and the desired
    #     slot has been selected, this function will book the slot.
    #
    #     Test mode means that everything is filled out but the submit button
    #     isn't clicked.
    #     """
    #
    #     # This global variable lets the scheduler know when to stop looking
    #     # for the desired slot (i.e. when the slot has been booked)
    #     # global is_reserved
    #
    #     try:
    #         # Click on the profile name to autofill the form
    #         browser.find_element_by_xpath('/html/body/div[1]/form/fieldset[1]/div/div[1]/div/a').click()
    #
    #         # Give the browser a little time to autofill the form
    #         # Otherwise results in crash
    #         time.sleep(1)
    #
    #         # Confirm that all waivers have been signed
    #         browser.find_element_by_xpath('/html/body/div[1]/form/fieldset[2]/div[2]/select/option[2]').click()
    #         browser.find_element_by_xpath('/html/body/div[1]/form/fieldset[3]/div[2]/select/option[2]').click()
    #
    #         # Click continue
    #         browser.find_element_by_xpath('/html/body/div[1]/form/a[2]').click()
    #
    #         # Agree to the T&Cs
    #         browser.find_element_by_xpath('/html/body/div[1]/form/fieldset[5]/div[2]/input').click()
    #
    #         # Submit form if not in test mode, i.e. actually want to book the
    #         # slot
    #         if not test_mode:
    #             browser.find_element_by_xpath(
    #                     '//*[@id="confirm_booking_button"]').click()
    #
    #         # If we got to submit the form, it's that the slot was booked
    #         # Need to change is_reserved to True, so that the scheduler knows
    #         # to stop
    #         # is_reserved = True
    #         print('We booked the slot you were after!')
    #         time.sleep(1)
    #
    #         # If in test_mode, want to leave the browser open so can inspect
    #         # that everything has been done correctly.
    #         if not test_mode:
    #             browser.quit()
    #
    #         return schedule.CancelJob
    #
    #     except Exception as ex:
    #         print('Found desired slot but could not book slot because of error after slot selection.')
    #         print('Exception:', ex)


# for booking_number in credentials.booking:
#     schedule.every(10).seconds.do(
#                 Automate_reservation(credentials.booking[booking_number]).main,
#                 test_mode=True
#                               )
for booking_number in credentials.booking:
    Automate_reservation(credentials.booking[booking_number]).main(test_mode=True)
#
# while schedule.jobs:
#     try:
#         schedule.run_pending()
#         time.sleep(1)
#         print(datetime.now().astimezone(pst).strftime("%c"))
#     except Exception as ex:
#         print("exception caught in the scheduler loop: ", ex)


browser = webdriver.Firefox(executable_path='/Users/tchavas/geckodriver')

browser.get('https://account.ikonpass.com/en/myaccount/add-reservations/')

# # Fill in your details
browser.find_element_by_xpath('//*[@id="email"]').send_keys('thomatou@hotmail.com')
browser.find_element_by_xpath('//*[@id="sign-in-password"]').send_keys('FhF8htNLnaAeQUq')

time.sleep(1)

# Submit your login info
browser.find_element_by_class_name('submit').click()


browser.get('https://account.ikonpass.com/en/myaccount/add-reservations/')

time.sleep(1)
# Input the name of the resort

browser.find_element_by_class_name('sc-pAXKH').send_keys('crystal mountain')
time.sleep(1)

# Select the first choice that comes up
browser.find_element_by_xpath('//*[@id="react-autowhatever-resort-picker-section-0-item-0"]').click()

# Click continue to get to the calendar
browser.find_element_by_class_name('sc-AxjAm.jxPclZ.sc-prpXb.hoYObS').click()


# select a particular date – first have to toggle to correct month
browser.find_element_by_css_selector("[aria-label='Thu Nov 19 2020']").click()




# add one month to calendar
browser.find_element_by_class_name('amp-icon.icon-chevron-right').click()

# select a particular date – first have to toggle to correct month
browser.find_element_by_css_selector("[aria-label='Thu Dec 10 2020']").click()
