#-*- coding: utf-8 -*-
import sys
import socket
import ssl
import json
import requests
import urllib # https://docs.python.org/3/library/urllib.parse.html
import uuid
import re
from bs4 import BeautifulSoup
from util import *

import config

### DEFAULTS
request_timeout = config.http_request_timeout
googlePageSpeedApiKey = config.googlePageSpeedApiKey

def check_four_o_four(url):
    """
    Only work on a domain-level. Returns tuple with decimal for grade and string with review
    """

    points = 0
    review = ''
    result_dict = {}

    ## kollar koden
    o = urllib.parse.urlparse(url)
    url = '{0}://{1}/{2}-{3}.html'.format(o.scheme, o.netloc, 's1d4-f1nns-1nt3', get_guid(5))
    headers = {'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    request = requests.get(url, allow_redirects=False, headers=headers, timeout=request_timeout)
    code = request.status_code
    if code == 404:
        points += 2
    else:
        review = review + '* Fel statuskod. Fick {0} när 404 vore korrekt.\n'.format(request.status_code)

    result_dict['status_code'] = code

    soup = BeautifulSoup(request.text, 'lxml')
    try:
        result_dict['page_title'] = soup.title.text
    except:
        print('Error!\nMessage:\n{0}'.format(sys.exc_info()[0]))

    try:
        result_dict['h1'] = soup.find('h1').text
    except:
        print('Error!\nMessage:\n{0}'.format(sys.exc_info()[0]))

    #print(code)

    ## kollar innehållet
    four_o_four_strings = []
    four_o_four_strings.append('saknas')
    four_o_four_strings.append('finns inte')
    four_o_four_strings.append('inga resultat')
    four_o_four_strings.append('inte hittas')
    four_o_four_strings.append('inte hitta')
    four_o_four_strings.append('kunde inte')
    four_o_four_strings.append('kunde ej')
    four_o_four_strings.append('hittades inte')
    four_o_four_strings.append('hittar inte')
    four_o_four_strings.append('hittade vi inte')
    four_o_four_strings.append('hittar vi inte')
    four_o_four_strings.append('hittades tyvärr inte')
    four_o_four_strings.append('tagits bort')
    four_o_four_strings.append('fel adress')
    four_o_four_strings.append('trasig')
    four_o_four_strings.append('inte hitta')
    four_o_four_strings.append('ej hitta')
    four_o_four_strings.append('ingen sida')
    four_o_four_strings.append('borttagen')
    four_o_four_strings.append('flyttad')
    four_o_four_strings.append('inga resultat')
    four_o_four_strings.append('inte tillgänglig')
    four_o_four_strings.append('inte sidan')
    four_o_four_strings.append('kontrollera adressen')
    four_o_four_strings.append('kommit utanför')
    four_o_four_strings.append('gick fel')
    four_o_four_strings.append('blev något fel')
    four_o_four_strings.append('kan inte nås')
    four_o_four_strings.append('gammal sida')
    four_o_four_strings.append('hoppsan')
    four_o_four_strings.append('finns inte')
    four_o_four_strings.append('finns ej')
    four_o_four_strings.append('byggt om')
    four_o_four_strings.append('inte finns')
    four_o_four_strings.append('inte fungera')
    four_o_four_strings.append('ursäkta')
    four_o_four_strings.append('uppstått ett fel')
    four_o_four_strings.append('gick fel')

    #print(four_o_four_strings)
    text_from_page = request.text.lower()
    found_match = False

    #print(text_from_page)

    for item in four_o_four_strings:
        if item in text_from_page:
            points += 1.5
            found_match = True
            break

    if found_match == False:
        review = review + '* Verkar sakna text som beskriver att ett fel uppstått (på svenska).\n'
    
    ## hur långt är inehållet
    soup = BeautifulSoup(request.text, 'html.parser')
    if len(soup.get_text()) > 150:
        points += 1.5
    else:
        review = review + '* Information är under 150 tecken, vilket tyder på att användaren inte vägleds vidare.\n'

    if len(review) == 0:
        review = '* Inga anmärkningar.'

    if points == 0:
      points = 1

    return (points, review, result_dict)
