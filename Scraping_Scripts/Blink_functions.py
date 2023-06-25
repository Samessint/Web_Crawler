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


# Functions reference

import Functions_And_Driver as fd


# --- Menu crawling ---


# Obtains links from Blink's navbar

def blink_menu_crawl(main_URL, menu_items_list) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(1)

        # Open menu
        dropdown_menu = driver.find_element(By.XPATH, '//a[@id="category__parent"]')
        time.sleep(1)
        dropdown_menu.click()
        time.sleep(1)

        HTML_master_block = []

        # Open first link
        actions = ActionChains(driver)
        for link in menu_items_list:
            product_link = driver.find_element(By.XPATH, f'//span[text()="{link}"]')
            time.sleep(1)
            actions.move_to_element(product_link).perform()
            time.sleep(1)
            product_sub_menu = driver.find_element_by_xpath(f'//li[@class="categ" and .//span[text()="{link}"]]')
            html_content = driver.execute_script("return arguments[0].innerHTML;", product_sub_menu)
            HTML_master_block.append(str(BeautifulSoup(html.unescape(html_content), 'html.parser')))

        driver.quit()

        # HTML parsing
        HTML_master = ' '.join(HTML_master_block)
        HTML_list = list(set(fd.extract_links(fd.extract_anchor_contents(HTML_master),'subcateg-name')))

        return HTML_list
    
    except Exception:
        print(Exception)


# Custom filter

def filter_blink(blink_list, category_list) -> list:
    
    condition_list = [";", "--", "?", "GB", "/Index"]
    filtered_list = [link for link in blink_list if all(condition not in link for condition in condition_list)]
    double_filtered_list = [link for link in filtered_list if all(condition not in link for condition in category_list)]
    triple_filtered_list = [link for link in double_filtered_list if "blink.com" in link]
    
    return triple_filtered_list


# --- Product parsing ---


# Backend


# Filters graves matching Blinks's product class inheritance

def blink_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to Blink's product div convention
    filtered_graves = []
    for grave in graveyard:
        if 'data-ng-repeat="product in ProductListList"' in grave:
            filtered_graves.append(f"<div class='items'{grave}")

    return filtered_graves
    
    
# Functional

    
# Creates a grave for a specific page

def blink_grave_list(crawl_URL) -> list:
    
    try:
        random_time = round(random.uniform(1, 2), 2)

        # Create site instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
        time.sleep(random_time + 1)

        # Handling checked or unchecked "Exclude sold-out"
        try:
            Exclude_button = driver.find_element(By.XPATH, '//span[text()="Exclude sold-out"]')

            found_stock = driver.find_element_by_css_selector('div.alignright.ng-binding')
            found_stock_int_1 = int(found_stock.text.split(' ')[0])
            Exclude_button.click()
            time.sleep(3)

            found_stock = driver.find_element_by_css_selector('div.alignright.ng-binding')
            found_stock_int_2 = int(found_stock.text.split(' ')[0])
            time.sleep(3)

            if found_stock_int_1 > found_stock_int_2:
                Exclude_button.click()
                time.sleep(random_time+2)

        except Exception as error:
            pass

        # Declare content array [first page]
        try:
            html_content = [driver.page_source]
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        # Loop through subpages until last page
        js_code = "arguments[0].scrollIntoView(true); window.scrollBy(0, -200);"

        while True:

            try:
                next_page = driver.find_element_by_css_selector('a[data-ng-click="setPage(pager.currentPage + 1)"]')
                driver.execute_script(js_code, next_page)
                time.sleep(random_time+1)
                next_page.click()
                time.sleep(random_time+2)
                html_content.append(driver.page_source)
                if fd.check_last_elements(html_content):
                    html_content = html_content[:-1]
                    print(f'{crawl_URL} page end detected')
                    break

            except Exception as error:
                print(f'{crawl_URL} page end detected')
                pass
                break

        driver.quit()

        html_content = ' '.join(html_content)

        list_graves = list(set(str(BeautifulSoup(html.unescape(html_content), 'html.parser')).split('<div class="items"')))

        return list_graves
    
    except Exception:
        print(Exception)


# Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def blink_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the Blink_links_filtered list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = []
    for link in listed_links:
        filtered_graveyard.append(blink_filter_graves(blink_grave_list(link)))
    
    return filtered_graveyard
    

# Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def blink_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}

    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            span_tag = soup.find('span', class_='item_name noSwipe')
            span_text = span_tag.get_text(strip=True)

            product_dictionary[span_text] = {
                'product_brand':'', 
                'product_price':'', 
                'product_discount':'', 
                'price_before_discount':'',
                'in_out_stock':'',
                'product_link':'', 
                'product_image':''
            }

            # product_brand <Might not always work>
            product_dictionary[span_text]['product_brand'] = span_text.split(' ')[0]

            # product_price [1]
            try:
                span_price_tag = soup.find('span', class_="newprice")
                span_price_text = span_price_tag.get_text(strip=True)
                product_dictionary[span_text]['product_price'] = span_price_text
            except Exception as error:
                pass

            # price_before_discount [2]
            try:   
                span_price_tag_2 = soup.find('span', class_="oldprice").find('span')
                span_price_text_2 = span_price_tag_2.get_text(strip=True)
                product_dictionary[span_text]['price_before_discount'] = span_price_text_2
            except Exception as error:
                pass

            # product_discount [1,2 -> 3]
            if product_dictionary[span_text]['product_price'] != '' and product_dictionary[span_text]['price_before_discount'] != '':
                price_discount_int = float(product_dictionary[span_text]['product_price'].split(' ')[0])
                price_original_int = float(product_dictionary[span_text]['price_before_discount'].split(' ')[0])
                product_dictionary[span_text]['product_discount'] = str(round((1-(price_discount_int / price_original_int))*100,2))+'%'

            # in_out_stock
            if soup.find('span', class_='outofstock'):
                product_dictionary[span_text]['in_out_stock'] = 'out_of_stock'
            else:
                product_dictionary[span_text]['in_out_stock'] = 'in_stock'

            # product_link
            try:
                for a_tag in soup.find_all('a'):
                    if 'product.SelectedCatalog.ProductName' in str(a_tag):
                        href_link = a_tag['href']
                product_dictionary[span_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                src_link = soup.find_all('img')[0]['src']
                product_dictionary[span_text]['product_image'] = src_link
            except Exception as error:
                pass

    return product_dictionary
