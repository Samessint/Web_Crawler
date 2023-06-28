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


# [0] Obtains links from navbar

def Gait_menu_crawl(main_URL) -> list:

    try:
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get('https://gait.com.kw/g_kw_en')
        time.sleep(1)

        # Scraper header menu
        header_menu = driver.find_element_by_xpath('//div[contains(@class, "headerbottom")]//span[contains(@class, "action") and contains(@class, "nav-toggle")][1]/ancestor::div[1]')
        time.sleep(1)

        html_content = header_menu.get_attribute("innerHTML")

        driver.quit()

        HTML_master = str(BeautifulSoup(html.unescape(html_content), 'html.parser'))

        # Pre-processing

        HTML_master = HTML_master.split('<a')

        HTML_master_filtered = ['<a'+anchor_like for anchor_like in HTML_master if 'class="level-top"' in anchor_like]

        # Find href

        pattern = r'<a[^>]*\bhref="([^"]*)"[^>]*>'
        matches = re.findall(pattern, ' '.join(HTML_master_filtered))
        HTML_list = list(set(matches))

        # Filter

        HTML_list_filtered = [link for link in HTML_list if 'catalog' not in link]

        return HTML_list_filtered
    
    except Exception:
        print(Exception)


# --- Product parsing ---


# Backend


# [A] Filters graves matching product class inheritance

def Gait_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to Xcite products class inheritance (ProductList_tileWrapper__cV7B_)

    filtered_graves = [str(grave) for grave in graveyard if 'product-item-info' in str(grave)]

    return filtered_graves


# Functional


# [1] Creates a grave for a specific page

def Gait_grave_list(crawl_URL) -> list:
    
    try:
        random_time = round(random.uniform(1, 2), 2)

        # Create site instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
        time.sleep(random_time)
        
        try:
            show_48 = driver.find_element_by_xpath('//option[@value="48"]')
            show_48.click()
            WebDriverWait(driver, 15).until(EC.staleness_of(show_48))
            time.sleep(random_time)
        except Exception:
            print(Exception)

        # Declare content array [first page]
        try:
            html_content = [driver.page_source]
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        # Loop through subpages until last page
        
        chunk_list = []
        
        while True:
            try:
                next_page = driver.find_element_by_class_name("action.next")
                driver.get(next_page.get_attribute("href"))
                time.sleep(random_time)
                html_content.append(driver.page_source)
                
                if len(html_content) == 5:
                    chunk_list.append(html_content)
                    html_content = []
                    
            except:
                if html_content != []:
                    chunk_list.append(html_content)
                print(f'Generated {len(chunk_list)} chunks')
                print(f'{crawl_URL} page end detected')
                break

        driver.quit()
        
        # Processing

        soup_list = []

        if chunk_list == []:
            
            html_content = ' '.join(html_content)
            soup = BeautifulSoup(html_content, 'html.parser')
            list_graves = soup.find_all('li', class_=lambda value: value and 'item product product-item' in value)
            
            return list_graves
        
        else:
            
            for index, chunk in enumerate(chunk_list):
                chunk = ' '.join(chunk)
                soup_list.append(BeautifulSoup(chunk, 'html.parser'))

        chunk_graves = [soup_.find_all('li', class_=lambda value: value and 'item product product-item' in value) for soup_ in soup_list]
        list_graves = [item for sublist in chunk_graves for item in sublist]

        return list_graves

    
    except Exception:
        print(traceback.format_exc())


# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def Gait_link_crawl(listed_links) -> list(list()):
    
    filtered_graveyard = [Gait_filter_graves(Gait_grave_list(link)) for link in listed_links]
    
    return filtered_graveyard


# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def Gait_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}

    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            a_tag = soup.find('a', class_='product-item-link')
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

            # product_brand <Generally will not work>
            product_dictionary[a_text]['product_brand'] = a_text.split(' ')[0]

            # product_price [1]
            try:
                first_span = soup.select('span[id^="product-price-"]')[0]
                span_descendant = first_span.select('span.price')[0]
                span_price_text = span_descendant.get_text(strip=True)
                product_dictionary[a_text]['product_price'] = span_price_text
            except Exception as error:
                pass

            # price_before_discount [2]
            try:   
                first_span_2 = soup.select('span[id^="old-price-"]')[0]
                span_descendant_2 = first_span_2.select('span.price')[0]
                span_price_text_2 = span_descendant_2.get_text(strip=True)
                product_dictionary[a_text]['price_before_discount'] = span_price_text_2
            except Exception as error:
                pass

            # product_discount [1,2 -> 3]
            if product_dictionary[a_text]['product_price'] != '' and product_dictionary[a_text]['price_before_discount'] != '':
                price_discount_int = float(product_dictionary[a_text]['product_price'].split(' ')[1])
                price_original_int = float(product_dictionary[a_text]['price_before_discount'].split(' ')[1])
                product_dictionary[a_text]['product_discount'] = str(round((1-(price_discount_int / price_original_int))*100,2))+'%'

            # in_out_stock
            if soup.find('span', text='Buy Now'):
                product_dictionary[a_text]['in_out_stock'] = 'in_stock'
            else:
                product_dictionary[a_text]['in_out_stock'] = 'out_of_stock'

            # product_link
            try:
                href_link = a_tag['href']
                product_dictionary[a_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                src_link = soup.find('img', class_='product-image-photo')['src']
                product_dictionary[a_text]['product_image'] = src_link
            except Exception as error:
                pass

    return product_dictionary

