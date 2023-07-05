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


# [0] Obtains span links from navbar

def span_crawl_text(main_URL, menu_items_list) -> list:
    
    # Open webpage
    opts = ChromeOptions()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(main_URL)
    time.sleep(1)
    
    # Open menu
    css_selector = "span.ml-2.text-gray-90 span.ec.ec-arrow-down-search"
    dropdown_menu = driver.find_element_by_css_selector(css_selector)
    dropdown_menu.click()
    time.sleep(1)

    link_list = []
    actions = ActionChains(driver)

    for category in menu_items_list:

        # Locate category
        category_obj = driver.find_element_by_xpath(f"//span[text()='{category}']")
        category_obj.click()
        time.sleep(1)
        
        link_list.append(driver.current_url)
                
        # Open menu
        css_selector = "span.ml-2.text-gray-90 span.ec.ec-arrow-down-search"
        dropdown_menu = driver.find_element_by_css_selector(css_selector)
        dropdown_menu.click()
        time.sleep(1)

    driver.quit()
    
    return link_list


# --- Product parsing ---


# Functional


# [1] Creates a grave for a specific page [already filtered]

def switch_grave_list(crawl_URL) -> list:
    
    try:
        # Step 1: Pull page source and split into list items (products) graves; return as a grave list
        random_time = round(random.uniform(1, 2),2)

        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
        time.sleep(random_time)
        
        # Infinite scroll

        js_scroll_bottom = "window.scrollTo(0, document.body.scrollHeight)"

        while True:
            driver.execute_script(js_scroll_bottom)
            try:
                driver.find_element_by_xpath("//div[text()=' BACK TO TOP ']")
            except:
                pass
            else:
                break            
        
        try:
            div_content = driver.find_element_by_xpath("//div[@class='cx-product-container']")
            html_content = div_content.get_attribute('innerHTML')
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        driver.quit()

        list_graves = BeautifulSoup(html_content, 'html.parser').find_all('div', class_='product-item__body pb-xl-2')

        return list_graves
    
    except Exception:
        print(Exception)


# [2] Crawls through a list of links and creates product class graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def switch_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the list, perform grave_list splitting and store in graveyard
    filtered_graveyard = [switch_grave_list(link) for link in listed_links]
    
    return filtered_graveyard

# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def switch_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}

    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(str(filtered_grave), 'html.parser')

            # product_name
            a_tag = soup.find('a', class_='cx-product-name')
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

            # product_brand [might not always work]
            try:
                product_dictionary[a_text]['product_brand'] = a_text.split(' ')[0]
            except:
                pass

            # product_price
            try:
                div_tag = soup.find('div', class_='text-gray-100')
                div_text= div_tag.get_text(strip=True)
                product_dictionary[a_text]['product_price'] = div_text
            except:
                try:
                    app_tag = soup.find('app-transform-arabic-number')
                    app_text = app_tag.get_text(strip=True)
                    product_dictionary[a_text]['product_price'] = app_text
                except:
                    pass

            # price_before_discount
            try:
                del_tag = soup.find('del', class_='font-size-12 tex-gray-6 position-absolute bottom-100')
                del_text= del_tag.get_text(strip=True)
                product_dictionary[a_text]['price_before_discount'] = del_text
            except:
                pass

            # product_discount
            if product_dictionary[a_text]['product_price'] != '' and product_dictionary[a_text]['price_before_discount'] != '':
                price_discount_int = float(product_dictionary[a_text]['product_price'].replace(',',''))
                price_original_int = float(product_dictionary[a_text]['price_before_discount'].split(' ')[0].replace(',',''))
                product_dictionary[a_text]['product_discount'] = str(round((1-(price_discount_int / price_original_int))*100,2))+'%'

            # in_out_stock
            if ' Add To Cart ' in str(soup):
                product_dictionary[a_text]['in_out_stock'] = 'in_stock'
            else:
                product_dictionary[a_text]['in_out_stock'] = 'out_of_stock'

            # product_link
            try:
                href_link = a_tag['href']
                product_dictionary[a_text]['product_link'] = f'https://switch.com.kw{href_link}'
            except:
                pass

            # product_image
            try:
                img_tags = soup.find('img')
                src_link = img_tags['src']
                product_dictionary[a_text]['product_image'] = src_link
            except:
                pass 

    return product_dictionary

