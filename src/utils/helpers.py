import random
import string
import re
import requests
import base64
import json
from urllib.request import Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from urllib.request import urlopen

CHARS = string.ascii_letters + string.punctuation
SIZE = 8

def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

def random_sql_injection():
    return '1 OR 1=1'

def searchSemanticsTag(url, recursive=False, print_dom=False, url_visited={}, flags_list=[]):
    return ""

def searchFlagInText(text, flags_list):
    flag = re.search('FLAG(.*?)FLAG', text)
    if flag != None:
        for findings in flag.groups():
            if findings not in flags_list:
                print("Flag found: " , findings )
                flags_list.append(findings)

def searchFlahInImage(link, flags_list):
    print("Searching flag in IMG: " + link['src'] )
    try:
        img_response = requests.get(link['src'])
    except HTTPError as e:
        # do something
        print('Error code: ', e.code)
    except URLError as e:
        # do something
        print('Reason: ', e.reason)
    else:
        str_img = base64.b64encode(img_response.content)
        searchFlagInText(str_img.decode('ASCII'), flags_list)

def searchFlagInResources(url, recursive=False, print_dom=False, url_visited={}, flags_list=[], func_hack=None ):

    if url in url_visited:
        print('alrady visited... jumping')
        return
    url_visited.append(url)

    BASE_URL = url

    request = Request(url)
    session = requests.Session()
    print("Searching Flag in url: " + url)
    try:
        http_request = urlopen(request)
    except HTTPError as e:
        # do something
        print('Error code: ', e.code)
        #if e.code != 404:
        print("Searching Flag in headers while a server error")
        headers = e.headers
        searchFlagInText(json.dumps(headers._headers), flags_list)
    except URLError as e:
        # do something
        print('Reason: ', e.reason)
    else:
        # do something
        soup = BeautifulSoup(http_request, "lxml")
        if print_dom:
            print(" String ", soup.prettify())
        plain_text = soup.get_text()
        print("Searching Flag in body")      
        searchFlagInText(plain_text, flags_list)
        print("Searching Flag in headers")
        headers = http_request.getheaders()
        searchFlagInText(json.dumps(headers), flags_list)

        print("Searching Flag in cookies")
        cookies = session.cookies.get_dict()
        searchFlagInText(json.dumps(cookies), flags_list)

        if recursive:
            # Search in HREF tags
            links = soup.find_all('a')
            for link in links:
                temp_url = link['href']
                #FOR THIS CMS instead relative path are all absolutes
                url_link = BASE_URL + '/' + temp_url
                recursive = True
                print_dom = False
                if re.search('http(.*?)', temp_url) != None:
                    #avoid searching on github
                    if re.search('github(.*?)', temp_url) != None:
                        print('Jump github')
                        continue
                    url_link = temp_url
                    recursive = False
                    print_dom = False
                # FOR THIS CMS if we are in page whatever any href will be BASE_URL/page/<href> as typical Drupal  
                elif re.search('page(.*?)', url) != None:
                    url_link = BASE_URL + '/page/' + temp_url

                searchFlagInResources(url_link, recursive, print_dom, url_visited, flags_list, func_hack)

            # External resources as IMG
            img_links = soup.find_all('img')
            for link in img_links:
                searchFlahInImage(link, flags_list)
            
            input_links = soup.find_all('input')
            for link in input_links:
                if 'text' in link.attrs:
                    print("Hackeable content input ", soup.prettify(), " In URL ", url, " entry" , link['name'])
                
                elif 'value' in link.attrs:
                        if link['value'] == 'submit':
                            func_hack(url,link['name'])
                        elif link['value'] == 'Create':
                             func_hack(url,random_string_generator(SIZE, CHARS))
                             func_hack(BASE_URL,random_string_generator(SIZE, CHARS))
                             func_hack(BASE_URL, random_sql_injection())
              
