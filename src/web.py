# All selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import common

# This is for finding the element like <div>text</div>
def generate_xpath_text(command) :
    index = "1"
    if "index" in command :
        index = command["index"]
    return "(//*[text()='{text}'])[position() = {index}]".format(text=command["args"][-1], index=index)

# Generates the XPATH of an element with any generic attribute.
def generate_xpath_for_generic_attribute(command) :
    index = "1"
    if "index" in command :
        index = command["index"]
    return "(//*[@{attribute}='{text}'])[position() = {index}]".format(text=command["args"][-1], index=index, attribute=command["attribute"])

# Specialised function to find element by placeholder. Eg. <input placeholder="text" />
def generate_xpath_placeholder(command) :
    command["attribute"] = "placeholder"
    return generate_xpath_for_generic_attribute(command)

# Specialised function to find element by name Eg. <input name="text" />
def generate_xpath_name(command) :
    return command["args"][-1].replace(" ", "")

# Specialised function to find element by value Eg. <input value="text" />
def generate_xpath_value(command) :
    command["attribute"] = "value"
    return generate_xpath_for_generic_attribute(command)

# These are the different mode in which we find an element on the screen.
# The order given here is the same order in which we search.
execute_modes = ["NAME", "PLACEHOLDER", "XPATH", "VALUE", "ATTRIBUTE"]

def find_element(driver, command) :
    # If mode is already present, then the North Remembers :p, and we remember how to get the element.
    # If we are finding the element by attribute the the mode is fixed.
    mode_index = 0
    timeout_seconds = 5
    if "mode" in command :
        mode_index = execute_modes.index(command["mode"])
        timeout_seconds = 15
    elif "attribute" in command :
        mode_index = execute_modes.index("ATTRIBUTE")
    else :
        mode_index = 0

    mode = ""
    element = ""

    # Iterate through all the modes.
    # If we don't find the element, then we move on to the next mode.
    while mode_index < len(execute_modes) :
        mode = execute_modes[mode_index]
        try :
            if mode == "NAME" :
                xpath = generate_xpath_name(command)
                element = common.find_element(driver, timeout_seconds, mode, xpath)
                break
            elif mode == "PLACEHOLDER" :
                xpath = generate_xpath_placeholder(command)
                element = common.find_element(driver, timeout_seconds, mode, xpath)
                break
            elif mode == "XPATH" :
                xpath = generate_xpath_text(command)
                element = common.find_element(driver, timeout_seconds, mode, xpath)
                break
            elif mode == "VALUE" :
                xpath = generate_xpath_value(command)
                element = find_element(driver, timeout_seconds, mode, xpath)
                break
            elif mode == "ATTRIBUTE" :
                xpath = generate_xpath_for_generic_attribute(command)
                element = common.find_element(driver, timeout_seconds, mode, xpath)
                break
            else :
                raise Exception("Invalid mode  found while parsing command", command)
        except :
            print ("Element not while searching in mode : ", mode)
            mode_index += 1
            continue

    if mode_index == len(execute_modes) :
        raise Exception("Element not found")
    return (element, mode, xpath)

def init_driver() :
    # Initialise the options.
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialise the driver.
    driver = webdriver.Chrome(chrome_options=options)
    driver.set_window_size(1920, 1080)

    return driver

def init_app(driver, program, arguments) :
    driver.get(program["url"].format(**arguments))
