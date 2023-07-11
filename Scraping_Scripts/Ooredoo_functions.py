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


# --- Product parsing ---


# [1] Creates a grave for a specific page

def ooredoo_grave_list(main_URL):
    
    opts = ChromeOptions()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(main_URL)

    div_product_box = driver.find_element_by_css_selector('div.product-grid div.item-grid')
    html_content = div_product_box.get_attribute("innerHTML")

    product_soup = BeautifulSoup(html_content, 'html.parser')
    product_master_list = [product_soup.find_all('div', class_='item-box')]

    while True:

        try:

            next_page = driver.find_element_by_xpath("//li[@class='next-page']")
            next_page.click()
            time.sleep(2)

            div_product_box = driver.find_element_by_css_selector('div.product-grid div.item-grid')
            html_content    = div_product_box.get_attribute("innerHTML")

            product_soup = BeautifulSoup(html_content, 'html.parser')
            product_master_list.append(product_soup.find_all('div', class_='item-box'))

        except Exception:
            driver.quit()
            break

    list_graves = [item_box for products_div in product_master_list for item_box in products_div]
    
    return list_graves


# [1.1] Rips product links for use in data enrichment later

def ooredoo_rip_links(main_URL):
    
    opts = ChromeOptions()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(main_URL)

    div_product_box = driver.find_element_by_css_selector('div.product-grid div.item-grid')
    anchor_bucket = div_product_box.find_elements_by_xpath("//h2[@class='product-title']//a")

    link_list_list = [[(anchor.get_attribute("href"), anchor.text) for anchor in anchor_bucket]]

    while True:
        try:
            next_page = driver.find_element_by_xpath("//li[@class='next-page']")
            next_page.click()
            time.sleep(2)

            div_product_box = driver.find_element_by_css_selector('div.product-grid div.item-grid')
            anchor_bucket = div_product_box.find_elements_by_xpath("//h2[@class='product-title']//a")
            
            link_list_list.append([(anchor.get_attribute("href"), anchor.text) for anchor in anchor_bucket])

        except Exception:
            driver.quit()
            break

    link_list = list(set([link for sublist in link_list_list for link in sublist]))

    return link_list


# [2] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def ooredoo_grave_product_parse(grave_list):

    product_dictionary = {}

    for product_div in grave_list:

        soup = BeautifulSoup(str(product_div), 'html.parser')

        # product_name
        h2_tag = soup.find('h2', class_='product-title')
        a_text = h2_tag.find('a').text

        product_dictionary[a_text] = {
            'product_brand':'', 
            'product_price':'',
            'price_type':'',
            'price_period':'',
            'in_out_stock':'',
            'other_label':'',
            'product_link':'',
            'product_image':''
        }

        # product_brand
        try:
            product_dictionary[a_text]['product_brand'] = a_text.split(' ')[0]
        except:
            pass

        # product_price
        try:
            span_tag = soup.find('span', class_='price actual-price')
            span_text = span_tag.text
            product_dictionary[a_text]['product_price'] = span_text.strip(' Starting from  ')
        except:
            pass

        # price_type
        # instantiated in enrichment
        
        # price_period
        # instantiated in enrichment

        # in_out_stock
        # the rest is intantiated in enrichment
        try:
            label_tag = soup.find('label', class_='ribbon-image-text')
            label_text= label_tag.text
            if label_text == 'out of Stock':
                product_dictionary[a_text]['in_out_stock'] = 'out_of_stock'
            else:
                product_dictionary[a_text]['other_label'] = label_text
        except:
            product_dictionary[a_text]['in_out_stock'] = 'in_stock'
            pass

        # product_link
        # instantiated from ooredoo_rip_links

        # product_image
        try:
            img_tag = soup.find('img', class_='picture-img')
            src_link = img_tag['data-lazyloadsrc']
            product_dictionary[a_text]['product_image'] = src_link
        except:
            pass
        
    return product_dictionary


# [2.1] zips ripped links to product_dictionary

def ooredoo_link_rip_zip(product_links, product_dictionary) -> dict():
    
    ooredoo_product_dictionary_lower = {}
    dictionary_bridge = {}

    for key in product_dictionary:
        lower_key = key.lower().replace(' ','').replace('\xa0','')
        ooredoo_product_dictionary_lower[lower_key] = key

    for product in product_links:
        dictionary_bridge[product[1].lower().replace(' ','')] = product[0]

    for key in dictionary_bridge:
        product_dictionary[ooredoo_product_dictionary_lower[key]]['product_link'] = dictionary_bridge[key]
    
    return product_dictionary


# Data enrichment: Search in page


def ooredoo_enhance_dictionary(product_dictionary) -> dict():

    for product in product_dictionary:

        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(product_dictionary[product]['product_link'])
        time.sleep(5)

        try:
            # Check page type
            type_2_info = driver.find_element_by_css_selector("div.product-info-main")

        except:
            #Type 1 page

            # Enhance stock (in_out_stock)
            try:
                driver.find_element_by_xpath("//span[text()='Sold out']")
                product_dictionary[product]['in_out_stock'] = 'out_of_stock'
            except:
                product_dictionary[product]['in_out_stock'] = 'in_stock'
                pass

            # Enhance payment_type- FIX THIS
            try:
                
                select_element = driver.find_element_by_css_selector("select.valid")

                selected_option = select_element.find_elements_by_css_selector("option[selected='selected']")
                
                options_list = [option.text for option in selected_options]

                for value in options_list:
                    
                    if 'Cash' in str(select_element.get_attribute("innerHTML")):
                        cash_option = selected_option.find_element_by_xpath('//select//option[text()="Cash"]')
                        cash_option.click()
                        time.sleep(1)
                        cash_price = driver.find_element_by_xpath("//div[@class='product-price']/span")
                        product_dictionary[product]['product_price'] = cash_price.text

                select_element = driver.find_element_by_css_selector("select.valid")

                selected_option = select_element.find_elements_by_css_selector("option[selected='selected']")
                
                options_list = [option.text for option in selected_options]               
                
                for value in options_list:
                    
                    if 'Monthly' in value:
                        product_dictionary[product]['price_type'] = value
                    elif 'ADD' in value:
                        product_dictionary[product]['price_type'] = value
                    elif 'Months' in value:
                        product_dictionary[product]['price_period'] = value

            except:
                pass

        else:
            # Type 2 page

            # Enhance stock
            try:
                type_2_info.find_element_by_xpath("//span[text()='In stock']")
                product_dictionary[product]['in_out_stock'] = 'in_stock'
            except:
                product_dictionary[product]['in_out_stock'] = 'out_of_stock'
                pass

            pass

            # Enhance payment type

            try:
                cash_div = type_2_info.find_element_by_xpath("//div[text()='Cash']")
                time.sleep(1)
                cash_div.click()
                time.sleep(1)
                price_div = type_2_info.find_element_by_xpath("//div[@class='custom_price_wrap']/span[@class='price']")
                time.sleep(1)
                product_dictionary[product]['product_price'] = price_div.text

                drop_downs = type_2_info.find_elements_by_xpath("//div[@data-option-type='drop_down']")
                selected_icons = [icon.get_attribute('innerHTML') for icon in drop_downs if 'selected' in str(icon.get_attribute('outerHTML'))]

            except:

                drop_downs = type_2_info.find_elements_by_xpath("//div[@data-option-type='drop_down']")
                selected_icons = [icon.get_attribute('innerHTML') for icon in drop_downs if 'selected' in str(icon.get_attribute('outerHTML'))]

            try:
                product_dictionary[product]['price_type'] = selected_icons[0]
            except:
                pass

            try:
                product_dictionary[product]['price_period'] = selected_icons[1]
            except:
                pass
        
        driver.quit()
        print(f'Successfully enhanced: {product}')
    
    return product_dictionary
