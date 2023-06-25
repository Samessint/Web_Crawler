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


# [0] Obtains links from navbar

def zain_menu_crawl(main_URL) -> list:

    # Create driver instance
    try:
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(1)

        # Ensure english site
        try:
            driver.find_element_by_xpath('//a[text()="العربية"]')
        except:
            english_site = driver.find_element_by_xpath('//a[text()="english"]')
            english_site.click()
            time.sleep(1)

        # Open menu
        dropdown_menu = driver.find_element_by_link_text("Shop")
        time.sleep(1)
        dropdown_menu.click()
        time.sleep(1)

        # Obtain all links in devices
        device_links_div = driver.find_element_by_xpath('//div[h3[text()="Devices"]]')
        html_content = device_links_div.get_attribute("innerHTML")

        driver.quit()

        HTML_master = str(BeautifulSoup(html_content, 'html.parser'))

        pattern = r'href="(.*?)"'
        matches = re.findall(pattern, HTML_master)
        HTML_list = list(set(matches))
        
        return HTML_list
        
    except Exception:
        print(Exception)


# --- Product parsing ---


# Backend


# [A] Filters graves matching Blinks's product class inheritance

def Zain_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to Xcite products class inheritance (ProductList_tileWrapper__cV7B_)
    filtered_graves = []
    for grave in graveyard:
        if 'product-name' in grave:
            filtered_graves.append(f'''<div class= "products-grid-item{grave}''')

    return filtered_graves


# Functional


# [1] Creates a grave for a specific page

def Zain_grave_list(crawl_URL) -> list:
    
    try:
        # Step 1: Pull page source and split into list items (products) graves; return as a grave list
        random_time = round(random.uniform(1, 2),2)
        
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(crawl_URL)
    
        # Ensure english site
        try:
            driver.find_element_by_xpath('//a[text()="العربية"]')
        except:
            english_site = driver.find_element_by_xpath('//a[text()="english"]')
            english_site.click()
            time.sleep(1)
    
        try:
            html_content = [driver.page_source]
        except:
            print(f'Could not obtain site resources: {crawl_URL}')

        js_code = "arguments[0].scrollIntoView(true); window.scrollBy(0, -200);"

        while True:

            try:
                next_page = driver.find_element_by_xpath('//span[@title="Next Page"]')
                time.sleep(random_time)
                driver.execute_script(js_code, next_page)
                time.sleep(random_time)
                next_page.click()
                time.sleep(random_time)
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
        list_graves = list(set(str(BeautifulSoup(html.unescape(html_content), 'html.parser')).split('<div class="products-grid-item')))
        
        return list_graves
    
    except Exception:
        print(Exception)



# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def Zain_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the Blink_links_filtered list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = []
    for link in listed_links:
        filtered_graveyard.append(Zain_filter_graves(Zain_grave_list(link)))
    
    return filtered_graveyard


# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def Zain_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}
    
    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            try:
                h3_element = soup.find('h3', class_='product-name')
                a_text = h3_element.a.get_text(strip=True)
            except Exception:
                return None

            # ADD IN_OUT_STOCK
            # ENRICH DATA
            product_dictionary[a_text] = {
                'product_brand':'', 
                'product_price_cash':'',
                'product_price_zain_plus':'', 
                'product_price_plan':'',
                'product_discount':'', 
                'product_link':'', 
                'product_image':''
            }

            # product_brand
            try:
                p_tag = soup.find('p', class_='brand-name')
                p_text = p_tag.get_text(strip=True)
                product_dictionary[a_text]['product_brand'] = p_text
            except Exception as error:
                pass

            # product_price_cash
            try:
                h2_element = soup.find('h2', text='Cash Deals')
                span_element = h2_element.find_next_sibling('h4').find('span', class_='product-price')
                span_text = span_element.get_text(strip=True)
                product_dictionary[a_text]['product_price_cash'] = span_text
            except Exception as error:
                pass

            
            # product_price_zain_plus
            try:
                h2_element = soup.find('h2', text='Zain Plus')
                span_element = h2_element.find_next_sibling('h4').find('span', class_='product-price')
                span_text = span_element.get_text(strip=True)
                product_dictionary[a_text]['product_price_zain_plus'] = f"{span_text} /Month"
            except Exception:
                pass
            
            # product_price_plan
            try:
                h2_element = soup.find('h2', text='Plan')
                span_element = h2_element.find_next_sibling('h4').find('span', class_='product-price')
                span_text = span_element.get_text(strip=True)
                product_dictionary[a_text]['product_price_plan'] = f"{span_text} /Month"
            except Exception:
                pass

            # product_discount
            try:
                label_element = soup.find('label', class_='kd-lablel sm-label')
                label_text = label_element.get_text(strip=True)
                product_dictionary[a_text]['product_discount'] = label_text.split(' ')[2]
            except Exception as error:
                pass

            # product_link
            try:
                h3_element = soup.find('h3', class_='product-name')
                a_element = h3_element.find('a')
                href_link = a_element['href']
                product_dictionary[a_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                div_element = soup.find('div', class_='product-image')
                img_element = div_element.find('img')
                src_link = img_element['src']
                product_dictionary[a_text]['product_image'] = f"https://www.kw.zain.com{src_link}"
            except Exception as error:
                pass

    return product_dictionary
                      
