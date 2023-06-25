#!/usr/bin/env python
# coding: utf-8


# Dependencies

import html
import re

import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


# Deep crawler (individual product link visits)

def Crawl_deep(product_link_list):
    
    opts = ChromeOptions()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    
    for crawl_link in product_link_list:
        driver.get(crawl_link)
        
        

# Deep product category


