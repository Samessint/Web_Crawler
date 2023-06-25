# coding: utf-8
# Invented by Faris Alquaddoomi (really?)


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


# Obtains links from Xcite's navbar

def Xcite_menu_crawl(main_URL, menu_items_list) -> list:

    try:
        # Create driver instance
        opts = ChromeOptions()
        opts.add_argument("--window-size=600,1000")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        driver.get(main_URL)
        time.sleep(1)

        HTML_master_block = []

        # Open menu
        dropdown_menu = driver.find_element_by_class_name("w-6")
        time.sleep(1)
        dropdown_menu.click()
        time.sleep(1)

        # Crawl through menu by h5 header and snapshot each page
        for category in menu_items_list:
            li_link = driver.find_element_by_xpath(f"//h5[text()='{category}']")
            time.sleep(1)
            li_link.click()
            time.sleep(1)
            div_content = driver.find_elements_by_xpath("//a[div[contains(@class, 'typography-default-strong')]]")
            time.sleep(1)
            for element in div_content:
                html_content = element.get_attribute("outerHTML")
                HTML_master_block.append(str(BeautifulSoup(html.unescape(html_content), 'html.parser')))
            dropdown_menu.click()
            time.sleep(1)

        driver.quit()

        HTML_master = ' '.join(HTML_master_block)

        pattern = r'href="([^"]+)"'
        matches = re.findall(pattern, HTML_master)
        HTML_list = list(set(matches))

        return HTML_list
    
    except Exception:
        print(Exception)


# --- Product parsing ---

# Backend


# Filters graves matching Xcite's product class inheritance

def Xcite_filter_graves(graveyard) -> list:
    
    # Step 2: Function to filter out only graves conforming to Xcite products class inheritance (ProductList_tileWrapper__cV7B_)
    filtered_graves = []
    for grave in graveyard:
        if 'ProductList_tileWrapper__cV7B_' in grave:
            filtered_graves.append(f"<li class{grave}")

    return filtered_graves


# Functional


# Creates a grave for a specific page

def Xcite_grave_list(crawl_URL) -> list:
    
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
                show_more = driver.find_element_by_css_selector('button.button.secondaryOnLight span')
                time.sleep(random_time)
                driver.execute_script(js_code, show_more)
                time.sleep(random_time)
                show_more.click()
                time.sleep(random_time)
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


# Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>

def Xcite_link_crawl(listed_links) -> list(list()):
    
    # Step 3: For each link in the Xcite_links_filtered list, perform grave_list splitting, filtering, and store in graveyard
    filtered_graveyard = []
    for link in listed_links:
        filtered_graveyard.append(Xcite_filter_graves(Xcite_grave_list(link)))
    
    return filtered_graveyard


# Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary

def Xcite_cemetary_product_parse(filtered_cemetary) -> dict:
    
    # Step 4: Parse information to build the product dictionary
    product_dictionary = {}
    
    for graveyard in filtered_cemetary:
        for filtered_grave in graveyard:

            soup = BeautifulSoup(filtered_grave, 'html.parser')

            # product_name
            p_tag = soup.find('p')
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
                h5_tag = soup.find('h5')
                h5_text = h5_tag.get_text(strip=True)
                product_dictionary[p_text]['product_brand'] = h5_text
            except Exception as error:
                pass

            # product_price
            try:
                span_tag = soup.find('span', 'text-2xl text-functional-red-800 block mb-2')
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
                span_tag2 = soup.find('span', 'text-base bg-functional-red-600 text-white px-2 py-[3px] leading-1 align-text-top inline-block font-normal')
                span2_text = span_tag2.get_text(strip=True)
                product_dictionary[p_text]['product_discount'] = span2_text
            except Exception as error:
                pass

            # price_before_discount
            try:
                span_tag3 = soup.find('span', 'text-base line-through')
                span3_text = span_tag3.get_text(strip=True)
                product_dictionary[p_text]['price_before_discount'] = span3_text
            except Exception as error:
                pass
            
            # in_out_stock
            if 'disabled="" type="button">' in str(soup):
                product_dictionary[p_text]['in_out_stock'] = 'out_of_stock'
            else:
                product_dictionary[p_text]['in_out_stock'] = 'in_stock'

            # product_link
            try:
                a_tag = soup.find('a')
                href_link = a_tag['href']
                product_dictionary[p_text]['product_link'] = href_link
            except Exception as error:
                pass

            # product_image
            try:
                img_tags = soup.find_all('img')
                if len(img_tags) >= 2:
                    img_tag2 = img_tags[1]
                    src_link = img_tag2['src']
                else:
                    src_link = img_tags['src']
                product_dictionary[p_text]['product_image'] = src_link
            except Exception as error:
                pass

    return product_dictionary
