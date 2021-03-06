#
# screenshot.py
#
# kevinabrandon@gmail.com
#

import sys
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser

# Read the configuration file for this application.
parser = ConfigParser()
parser.read('config.ini')

# Assign AboveTustin variables.
abovetustin_image_width = int(parser.get('abovetustin', 'image_width'))
abovetustin_image_height = int(parser.get('abovetustin', 'image_height'))

#  Check for Crop settings
if parser.has_section('crop'):
    do_crop = parser.getboolean('crop', 'do_crop')
    crop_x = parser.getint('crop', 'crop_x')
    crop_y = parser.getint('crop', 'crop_y')
    crop_width = parser.getint('crop', 'crop_width')
    crop_height = parser.getint('crop', 'crop_height')
    if do_crop:
        try:
            from PIL import Image
            from io import BytesIO
            print('will crop')
        except ImportError:
            print('Image manipulation module "Pillow" not found, cropping disabled')
            do_crop = False
else:
    do_crop = False

# Assign dump1090 variables.
dump1090_map_url = parser.get('dump1090', 'map_url')
dump1090_request_timeout = int(parser.get('dump1090', 'request_timeout'))

def loadmap():
    '''
    loadmap()
    Creates a browser object and loads the webpage.
    It sets up the map to the proper zoom level.

    Returns the browser on success, None on fail.
    '''
    try:
        browser = webdriver.PhantomJS(desired_capabilities={'phantomjs.page.settings.resourceTimeout': '20000'})
        browser.set_window_size(abovetustin_image_width, abovetustin_image_height)

        print ("getting web page...")
        browser.get(dump1090_map_url)

        # Need to wait for the page to load
        timeout = dump1090_request_timeout
        print ("waiting for page to load...")
        wait = WebDriverWait(browser, timeout)
        element = wait.until(EC.element_to_be_clickable((By.ID,'dump1090_version')))

        print("reset map:")
        resetbutton = browser.find_elements_by_xpath("//*[contains(text(), 'Reset Map')]")
        resetbutton[0].click()

        print("zoom in 4 times:")
        zoomin = browser.find_element_by_class_name('ol-zoom-in')
        zoomin.click()
        zoomin.click()
        zoomin.click()
        zoomin.click()

        return browser
    except:
        print("exception in loadmap()")
        print (sys.exc_info()[0])
        return None


def screenshot(browser, name):
    '''
    screenshot()
    Takes a screenshot of the browser
    '''
    try:
        if do_crop:
            print('cropping screenshot')
            #  Grab screenshot rather than saving
            im = browser.get_screenshot_as_png()
            im = Image.open(BytesIO(im))

            #  Crop to specifications
            im = im.crop((crop_x, crop_y, crop_width, crop_height))
            im.save(name)
        else:
            browser.save_screenshot(name)
        print("success saving screnshot: %s" % name)
    except:
        print("exception in screenshot()")
        print(sys.exc_info()[0])


def clickOnAirplane(browser, text):
    '''
    clickOnAirplane()
    Clicks on the airplane with the name text, and then takes a screenshot
    '''
    try:
        element = browser.find_elements_by_xpath("//td[text()='%s']" % text)
        print("number of elements found: %i" % len(element))
        if len(element) > 0:
            print("click!")
            element[0].click()
            time.sleep(0.5) # if we don't wait a little bit the airplane icon isn't drawn.
            screenshot(browser, 'tweet.png')
            return True
        else:
            print("couldn't find the object")
    except:
        print("exception in clickOnAirplane()")
        print (sys.exc_info()[0])

    return False
