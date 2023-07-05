#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8


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


# --- Menu crawling ---


# [0] Obtains links from navbar

def i2_menu_crawl(main_URL, menu_items_list) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(1)

        # Open menu
        menu_div = driver.find_element_by_class_name("tt-header-holder")
        time.sleep(1)

        html_content = menu_div.get_attribute("innerHTML")
        
        HTML_master = BeautifulSoup(html_content, 'html.parser')

        driver.quit()
        
        # Link parsing
        
        HREF_list = [
            anchor.get('href') for anchor in HTML_master.find_all('a') if any(category in str(anchor) for category in menu_items_list)
        ]

        return HREF_list
    
    except Exception:
        print(Exception)


# --- Product parsing ---


# Backend


# [A] Filters graves matching product class inheritance

def i2_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to product div convention
    filtered_graves = [grave for grave in graveyard if 'product photo product-item-photo' in grave]

    return filtered_graves

# Functional


# [1] Creates a grave for a specific page

def i2_grave_list(crawl_URL) -> list:
    
    try:
        # Step 1: Pull page source and split into list items (products) graves; return as a grave list
        random_time = round(random.uniform(1, 2),2)

        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
        time.sleep(random_time)
        
        option_30 = driver.find_element_by_xpath("//option[@value='30']")
        option_30.click()
        time.sleep(random_time)
        
        try:
            product_div = driver.find_element_by_css_selector("div.products.wrapper.grid.products-grid")
            html_content = [product_div.get_attribute("innerHTML")]
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        while True:

            try:
                
                next_page = driver.find_element_by_css_selector("a.action.next")
                next_page_href = next_page.get_attribute("href")
                driver.get(next_page_href)
                time.sleep(random_time)
                product_div = driver.find_element_by_css_selector("div.products.wrapper.grid.products-grid")
                html_content.append(product_div.get_attribute("innerHTML"))

            except Exception as error:
                print(f'{crawl_URL} page end detected')
                break

        driver.quit()

        html_content = ' '.join(html_content)
        list_graves = list(set(str(BeautifulSoup(html.unescape(html_content), 'html.parser')).split('<div class="item product product-item')))

        return list_graves
    
    except Exception:
        print(Exception)


# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def i2_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = [i2_filter_graves(i2_grave_list(link)) for link in listed_links]
    
    return filtered_graveyard

# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def i2_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}
    
    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            h2_tag = soup.find('h2', class_='tt-title')
            a_tag = h2_tag.find('a')
            a_text = a_tag.get_text(strip=True)

            product_dictionary[a_text] = {
                'product_brand':'', 
                'product_price':'', 
                'product_discount':'', 
                'price_before_discount':'',
                'in_out_stock':'',
                'product_link':'', 
                'product_image':''
            }

            # product_brand [will not always work]
            try:
                product_dictionary[a_text]['product_brand'] = a_text.split(' ')[0]
            except Exception as error:
                pass

            # product_price
            try:
                span_tag = soup.find('span', class_='price')
                span_text = span_tag.get_text(strip=True)
                product_dictionary[a_text]['product_price'] = span_text
            except Exception as error:
                pass


            # product_discount [cannot retrieve this from image]
            try:
                product_dictionary[a_text]['product_discount'] = ''
            except Exception as error:
                pass

            # price_before_discount [cannot retrieve this from image]
            try:
                product_dictionary[a_text]['price_before_discount'] = ''
            except Exception as error:
                pass
            
            # in_out_stock
            if '<span>ADD To Cart</span>' in str(soup):
                product_dictionary[a_text]['in_out_stock'] = 'in_stock'
            else:
                product_dictionary[a_text]['in_out_stock'] = 'out_of_stock'

            # product_link
            try:
                product_dictionary[a_text]['product_link'] = a_tag['href']
            except Exception as error:
                pass

            # product_image
            try:
                img_tag = soup.find('img', class_='product-image-photo')
                product_dictionary[a_text]['product_image'] = img_tag['src']
            except Exception as error:
                pass

    return product_dictionary
