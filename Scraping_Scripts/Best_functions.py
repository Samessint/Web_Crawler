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

def best_menu_crawl(main_URL, menu_items_list) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(3)

        # Open menu
        dropdown_menu = driver.find_element(By.XPATH, "//span[text()='All Categories']")
        time.sleep(1)
        dropdown_menu.click()
        time.sleep(1)

        HTML_master_block = []

        # Open first link and obtain inner HTML
        actions = ActionChains(driver)
        list_class = "dropdown-item ng-star-inserted"
        for category in menu_items_list:
            category_obj = driver.find_element_by_xpath(f"//cx-generic-link[contains(.//a, '{category}')]")
            actions.move_to_element(category_obj).perform()
            list_item = driver.find_element_by_xpath(f"//li[contains(@class, '{list_class}')]//a[contains(., '{category}')]/ancestor::li")
            html_content = list_item.get_attribute("innerHTML")
            HTML_master_block.append(BeautifulSoup(html_content, 'html.parser'))

        driver.quit()

        # HTML sub-category parsing
        HREF_list = []
        for HTML_soup in HTML_master_block:
            HTML_soup_links = HTML_soup.find_all('h3')
            for h3_link in HTML_soup_links:
                HREF_list.append(h3_link.find('a')['href'])

        return HREF_list
    
    except Exception:
        print(Exception)


# --- Product parsing ---


# Backend


# Filters graves matching Blinks's product class inheritance

def best_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to Blink's product div convention
    filtered_graves = []
    for grave in graveyard:
        if 'class="cx-product-name"' in grave:
            filtered_graves.append(f"<best-product-grid-item{grave}")

    return filtered_graves
    
    
# Functional

    
# Step 1: Creates a grave for a specific page

    
def best_grave_list(crawl_URL) -> list:
    
    try:
        random_time = round(random.uniform(1, 2), 2)

        # Create site instance [best site loading error handle]
        site = 'unloaded'
        max_tries = 1

        while max_tries < 4:

            try:
                opts = ChromeOptions()
                opts.add_argument("--start-maximized")
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
                driver.get(crawl_URL)
                time.sleep(random_time+4)
                # Throws exception if below element is not loaded
                driver.find_element_by_xpath("//img[@alt='Best Al Yousufi']")
                site = 'loaded'
                break

            except Exception:
                max_tries += 1
                print('Site not loaded')
                print(max_tries)
                driver.quit()

                if max_tries == 3:
                    print(f'Could not obtain site resources: {crawl_URL}')
                    break

        # Declare content array [first page]
        if site == 'loaded':
            html_content = [driver.page_source]

            # Loop through subpages until last page
            js_code = "arguments[0].scrollIntoView(true); window.scrollBy(0, -200);"

            while True:

                try:
                    next_page = driver.find_element_by_xpath("//a[@aria-label='next page']")
                    driver.execute_script(js_code, next_page)
                    time.sleep(2)
                    next_page.click()
                    time.sleep(random_time)
                    html_content.append(driver.page_source)

                except Exception as error:
                    print(f'{crawl_URL} page end detected')
                    break

            driver.quit()

            html_content = ' '.join(html_content)

            list_graves = list(set(str(BeautifulSoup(html.unescape(html_content), 'html.parser')).split('<best-product-grid-item')))

        else:
            return [f'Could not obtain site resources: {crawl_URL}']

        return list_graves
    
    except Exception:
        print(Exception)


# Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def best_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the Blink_links_filtered list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = []
    for link in listed_links:
        filtered_graveyard.append(best_filter_graves(best_grave_list(link)))
    
    return filtered_graveyard


# Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def best_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}

    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

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

            # product_brand <Might not always work>
            product_dictionary[a_text]['product_brand'] = a_text.split(' ')[0]

            # product_price [1]
            try:
                div_price = float(soup.find('div', class_="cx-product-price").get_text(strip=True).split('KD')[1].strip())
                product_dictionary[a_text]['product_price'] = div_price
            except Exception as error:
                pass
            
            # price_before_discount [2]
            try:
                div_price_list = soup.find('div', class_="cx-product-price").get_text(strip=True).split('KD')
                if len(div_price_list) == 3:
                    product_dictionary[a_text]['price_before_discount'] = float(div_price_list[2].strip())
            except Exception as error:
                pass
            
            # product_discount [1,2 -> 3]
            if product_dictionary[a_text]['product_price'] != '' and product_dictionary[a_text]['price_before_discount'] != '':
                price_discount_int = float(product_dictionary[a_text]['product_price'])
                price_original_int = float(product_dictionary[a_text]['price_before_discount'])
                product_dictionary[a_text]['product_discount'] = str(round((1-(price_discount_int / price_original_int))*100,2))+'%'
    
            # in_out_stock
            if soup.find(lambda tag: tag.name == 'div' and tag.text.strip() == 'Out Of Stock'):
                product_dictionary[a_text]['in_out_stock'] = 'out_of_stock'
            else:
                product_dictionary[a_text]['in_out_stock'] = 'in_stock'
                
            # product_link
            try:
                href_link = f"https://best.com.kw{a_tag['href']}"
                product_dictionary[a_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                src_link = soup.find('img', class_='ng-star-inserted')['src']
                product_dictionary[a_text]['product_image'] = src_link
            except Exception as error:
                pass
    
    return product_dictionary
