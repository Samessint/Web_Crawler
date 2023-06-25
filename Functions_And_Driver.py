# coding: utf-8
# Invented by Faris Alquaddoomi (really?)

# Web Crawl Functions and Driver


# Dependencies

import html
import random
import re
import time

import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


# Back-end (function input)


# Function to assert self-similarity [used in Blink_grave_list as a condition to break While loop] - currently used in blink_grave_list

def check_last_elements(lst) -> bool:
    if len(lst) >= 2:
        last_element = lst[-1]
        second_to_last_element = lst[-2]
        if last_element == second_to_last_element:
            return True
        else:
            return False
    else:
        return False


# Currently being used in HTML_grab_links_dynamic

def extract_anchor_contents(html_in) -> list:
    anchor_contents = []
    start_tag = '<a'
    end_tag = '>'
    index = 0

    while index < len(str(html_in)):
        start_index = str(html_in).find(start_tag, index)
        if start_index == -1:
            break

        end_index = str(html_in).find(end_tag, start_index)
        if end_index == -1:
            break

        anchor_content = str(html_in)[start_index + len(start_tag):end_index].strip()
        anchor_contents.append(anchor_content)

        index = end_index + 1

    return anchor_contents


# Currently being used in Blink_menu_crawl

def extract_links(html_list, condition=None) -> list:
    links = []
    pattern = r'href=\\?"([^"]*?)(?<!\\)"'

    for anchor_link in html_list:
        match = re.search(pattern, anchor_link)
        if match:
            link = match.group(1)
            if condition:
                if condition in anchor_link:
                    links.append(link)
            else:
                links.append(link)

    return links


# Currently being used in HTM_grab_links_dynamic

def dynamic_extract_links(html_string) -> list:
    links = []
    pattern = r'href=\\?"([^"]*?\\)"'

    for character in html_string:
        match = re.search(pattern, character)
        if match:
            link = match.group(1)
            links.append(link)

    return links


# Functional (user-input)


# Just grabs the static HTML from a webpage

def HTML_grab_links_static(main_URL) -> list:
    rand_float = random.uniform(1.0, 3.0)
    time.sleep(rand_float)

    request = requests.get(main_URL)
    soup = BeautifulSoup(request.content, 'html.parser')

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    return links


# Grabs some dynamic HTML content from a webpage (Works for Blink and Best)

def HTML_grab_links_dynamic(main_URL) -> list:

    # Implement later: check if installed; if so, just declare; if not, install and declare
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(main_URL)
    
    # For <hamburger-box> in Best.com
    try:
        dropdown_menu = driver.find_element_by_class_name('hamburger-box')
        time.sleep(5)
        dropdown_menu.click()
        time.sleep(3)
    except Exception as error:
        print(f'No hamburger box because: {error}')
    
    html_content = driver.page_source
    HTML_soup = BeautifulSoup(html.unescape(html_content), 'html.parser')
 
    driver.quit()

    links = dynamic_extract_links(extract_anchor_contents(HTML_soup))

    return links


# Filters links based on a specified condition that the link has at its ending

def filter_c(listed_links, condition, index_end) -> list:
    filtered_links = []
    for link in listed_links:
        if link[index_end:] == condition:
            filtered_links.append(link)

    return filtered_links


# Filters links based on a specified condition that the link has within it

def filter_if_in(listed_links, condition) -> list:
    filtered_list = []
    for link in listed_links:
        if condition in link:
            filtered_list.append(link)

    return filtered_list


# Filters links based on their match with a condition list filter

def filter_devices(listed_links, condition_list) -> list:
    
    filtered_list = []
    for list_item in listed_links:
        for filter_item in condition_list:
            if filter_item.lower() in list_item.lower():
                filtered_list.append(list_item)
    
    return filtered_list
