from bs4 import BeautifulSoup
from io import StringIO
from PIL import Image
import json
import base64
import re
import requests
from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import os
import cssutils
from utils.helpers import searchFlagInResources, searchFlagInText
from utils.helpers import CHARS
from utils.helpers import random_string_generator, random_sql_injection
from utils.crawler import Crawler

from html import escape

BASE_URL = 'https://unruffled-kilby-c5894d.netlify.app/'

foundFlagsFile = 'moderate3_flags_found.txt'
flags_list = []
url_visited = []

if os.path.exists(foundFlagsFile):
    text_file = open(foundFlagsFile, "r")
    flags_list = text_file.readlines()
    text_file.close()


def searchIndexingpages():
    subpages = ['login', 'page', 'edit', '']
    for subpage in subpages:
        url = BASE_URL + '/'+subpage
        searchFlagInResources(
            url, True, False, url_visited, flags_list, hackattemptInput)
        for index in range(1, 10):
            url = url + '/' + str(index)
            searchFlagInResources(
                url, True, False, url_visited, flags_list, hackattemptInput)


def hackattemptInput(url, name):

    function_list = [random_string_generator(
        200, CHARS), random_sql_injection()]
    for function in function_list:
        # Data dict
        payload = "title="+name+"&body="+function+"&undefined="+function
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print("hacked? ", response.headers)

        searchFlagInText(response.text, flags_list)


def buildXMLSiteMap():
    """
    I'm going to build the XMLSiteMap
    """
    dict_arg = {
        "domain": BASE_URL,
        "skipext":	[
            "pdf",
            "xml"
        ],
        "parserobots": True,
        "images": False,
        "debug": True,
        "output": "sitemap.xml",
        "exclude":	[
            "action=edit"
        ]
    }
    crawl = Crawler(**dict_arg)
    crawl.run()

    crawl.make_report()


if __name__ == "__main__":
    url = BASE_URL

    buildXMLSiteMap()

    # searchIndexingpages()

    #url = BASE_URL + '/' + 'favicon.ico'
    # searchFlagInResources(url)

    # based on previous assignment
    #url = BASE_URL + '/' + 'background.png'
    # searchFlagInResources(url)

    text_file = open(foundFlagsFile, "w")
    text_file.writelines(flags_list)
    text_file.close()