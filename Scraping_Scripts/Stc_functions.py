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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --- Menu crawling ---


# [0] Obtains links

def stc_menu_crawl(main_URL) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(driver_path, options=opts)
        driver.get(main_URL)
        time.sleep(1)

        # STC category links
        category_anchors = driver.find_elements_by_xpath("//a[text()='See all']")
        
        category_links   = [anchor.get_attribute('href') for anchor in category_anchors]
        
        driver.quit()

        return category_links
    
    except Exception:
        print(Exception)


# --- Product parsing ---


# Functional


# [1] Creates a grave for a specific page #WIP

def stc_grave_list(crawl_URL) -> list:
    
    try:
        # Open page
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(driver_path, options=opts)
        driver.get(Stc_URL)
        
        strip_crawl = crawl_URL.strip('https://www.stc.com.kw')
        link = driver.find_element_by_xpath(f"//a[@href='/{strip_crawl}']")
        link = link.get_attribute('href')
        driver.get(link)
        
        time.sleep(5)
        
        js_down = "window.scrollTo(0, document.body.scrollHeight);"
        js_clik = "arguments[0].click();"

        while True:

            try:
                driver.execute_script(js_down)
                load_more = driver.find_element_by_xpath("//button[.//span[contains(text(), 'Load More')]]")
                driver.execute_script(js_clik, load_more)
            except Exception as error:
                print(f'{crawl_URL} page end detected')
                break
                
        html_content = driver.find_elements_by_xpath("//div[contains(@class, 'col-12') and contains(@class, 'col-md-4') and contains(@class, 'col-lg-3')]")

        list_graves = [div_content.get_attribute('innerHTML') for div_content in html_content] 
        
        driver.quit()

        return list_graves
    
    except Exception:
        print(Exception)
        
        
# [1.1] Grave enhancement


def enhance_grave():
    --


# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def stc_link_crawl(listed_links) -> list(list()):
    
    # stc_grave_list on each link
    graveyard = [stc_grave_list(link) for link in stc_links]
    
    return graveyard


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
