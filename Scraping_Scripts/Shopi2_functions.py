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

def #_menu_crawl(main_URL, menu_items_list) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(3)

        # Open menu
        dropdown_menu = #
        time.sleep(1)
        dropdown_menu.click()
        time.sleep(1)

        HTML_master_block = []

        # Open first link and obtain inner HTML
        actions = ActionChains(driver)

        for category in menu_items_list:
            category_obj = #
            actions.move_to_element(category_obj).perform()
            list_item = #
            html_content = list_item.get_attribute("innerHTML")
            HTML_master_block.append(BeautifulSoup(html_content, 'html.parser'))

        driver.quit()

        # HTML sub-category parsing
        HREF_list = []
        for HTML_soup in HTML_master_block:
            HTML_soup_links = #
            for h3_link in HTML_soup_links:
                """"""

        return HREF_list
    
    except Exception:
        print(Exception)


# --- Product parsing ---


# Backend


# [A] Filters graves matching product class inheritance

def #_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to product div convention
    filtered_graves = [grave for grave in graveyard if '' in grave]

    return filtered_graves

# Functional


# [1] Creates a grave for a specific page

def #_grave_list(crawl_URL) -> list:
    
    try:
        # Step 1: Pull page source and split into list items (products) graves; return as a grave list
        random_time = round(random.uniform(1, 2),2)

        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
        time.sleep(random_time)
        
        try:
            html_content = [driver.page_source]
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        js_code = "arguments[0].scrollIntoView(true); window.scrollBy(0, -200);"

        while True:

            try:

                driver.execute_script(js_code, show_more)
                time.sleep(random_time)
 
                # ...
                html_content.append(driver.page_source)

            except Exception as error:
                print(f'{crawl_URL} page end detected')
                break

        driver.quit()

        html_content = ' '.join(html_content)
        list_graves = list(set(str(BeautifulSoup(html.unescape(html_content), 'html.parser')).split('<li class')))

        return list_graves
    
    except Exception:
        print(Exception)


# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def #_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = [_filter_graves(_grave_list(link)) for link in listed_links]
    
    return filtered_graveyard

# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def #_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}
    
    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            p_tag = #
            p_text = p_tag.get_text(strip=True)

            product_dictionary[p_text] = {
                'product_brand':'', 
                'product_price':'', 
                'product_discount':'', 
                'price_before_discount':'',
                'in_out_stock':'',
                'product_link':'', 
                'product_image':''
            }

            # product_brand
            try:
                h5_tag = soup.find(
                h5_text = h5_tag.get_text(strip=True)
                product_dictionary[p_text]['product_brand'] = h5_text
            except Exception as error:
                pass

            # product_price
            try:
                span_tag = soup.find(
                span_text = span_tag.get_text(strip=True)
                product_dictionary[p_text]['product_price'] = span_text
            except Exception as error:
                try:
                    h4_tag = soup.find('h4')
                    h4_text = h4_tag.get_text(strip=True)
                    product_dictionary[p_text]['product_price'] = h4_text
                except Exception as error:
                    pass


            # product_discount
            try:
                span_tag2 = soup.find(
                span2_text = span_tag2.get_text(strip=True)
                product_dictionary[p_text]['product_discount'] = span2_text
            except Exception as error:
                pass

            # price_before_discount
            try:
                span_tag3 = soup.find(
                span3_text = span_tag3.get_text(strip=True)
                product_dictionary[p_text]['price_before_discount'] = span3_text
            except Exception as error:
                pass
            
            # in_out_stock
            if '' in str(soup):
                product_dictionary[p_text]['in_out_stock'] = 'out_of_stock'
            else:
                product_dictionary[p_text]['in_out_stock'] = 'in_stock'

            # product_link
            try:
                a_tag = soup.find(
                href_link = a_tag['href']
                product_dictionary[p_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                img_tags = soup.find(
                product_dictionary[p_text]['product_image'] = src_link
            except Exception as error:
                pass

    return product_dictionary
