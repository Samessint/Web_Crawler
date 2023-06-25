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


# [0] Obtains links from Zain's navbar


# --- Product parsing ---


# Backend


# [A] Filters graves matching Blinks's product class inheritance


# Functional


# [1] Creates a grave for a specific page


# [2] Crawls through a list of links and creates product class filtered graves for each webpage: HEAVY OPERATION <ONLY RUN WHEN 100% SURE>


# [3] Crawls through a graveyard of product class filtered graves and parses product information into a product dictionary


