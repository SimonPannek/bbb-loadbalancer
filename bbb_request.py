import concurrent.futures
import operator
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

import config

# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")


def get_user_count(room_id):
    with webdriver.Chrome(options=chrome_options) as driver:
        # Connect to site
        wait = WebDriverWait(driver, 100)
        driver.get(config.url + room_id)

        # Input name
        try:
            name_input = driver.find_element(By.NAME, "/{}[join_name]".format(room_id))
            name_input.send_keys("Load-balancer" + Keys.RETURN)
        except NoSuchElementException:
            # Could not find username input, probably wrong link
            return room_id, -1

        # Check if meeting has started
        if driver.find_elements(By.XPATH,
                                "//div[@room = '{}']//h3[contains(text(), 'started yet')]".format(
                                    room_id)):
            # Meeting hasn't started yet
            return room_id, -1

        # Try to get user count
        try:
            user_field = wait.until(
                presence_of_element_located((By.XPATH, "//div[contains(@class, 'userListColumn')]//h2")))
            field_value = user_field.get_attribute("textContent")
            field_value = re.findall(r'\d+', field_value)

            if field_value:
                # Remove load balancer from users
                return room_id, int(field_value[0]) - 1
            else:
                # Could not parse user count, probably connection problems
                return room_id, -1
        except TimeoutException:
            # Could not find field for user count, the meeting probably hasn't started yet
            return room_id, -1


def get_least_visited(room_ids):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = list()

        # Request user count for each room in list
        for current_room in room_ids:
            future = executor.submit(get_user_count, current_room)
            future_list.append(future)

        # Wait for futures to resolve
        resolved = map(lambda fut: fut.result(5000), future_list)

        # Filter only successful requests
        filtered = filter(lambda x: x[1] >= 0, resolved)

        # Get a room with a minimum count of users
        result = min(filtered, key=operator.itemgetter(1), default=None)

        return result
