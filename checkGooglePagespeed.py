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

def check_google_pagespeed(url, strategy='mobile'):
    """Checks the Pagespeed Insights with Google
    In addition to the 'mobile' strategy there is also 'desktop' aimed at the desktop user's preferences
    Returns a dictionary of the results.

    attributes: check_url, strategy
    """
    check_url = url.strip()

    # urlEncodedURL = parse.quote_plus(check_url)	# making sure no spaces or other weird characters f*cks up the request, such as HTTP 400
    pagespeed_api_request = 'https://www.googleapis.com/pagespeedonline/v4/runPagespeed?url={}&strategy={}&key={}'.format(check_url, strategy, googlePageSpeedApiKey)
    #print('HTTP request towards GPS API: {}'.format(pagespeed_api_request))

    get_content = ''

    try:
        get_content = httpRequestGetContent(pagespeed_api_request)
        get_content = BeautifulSoup(get_content, "html.parser")
        get_content = str(get_content.encode("ascii"))
    except:  # breaking and hoping for more luck with the next URL
        print(
            'Error! Unfortunately the request for URL "{0}" failed, message:\n{1}'.format(
                check_url, sys.exc_info()[0]))
        pass
    # try:
    get_content = get_content[2:][:-1]  # removes two first chars and the last one
    get_content = get_content.replace('\\n', '\n').replace("\\'",
                                                           "\'")  # .replace('"', '"') #.replace('\'', '\"')
    get_content = get_content.replace('\\\\"', '\\"').replace('""', '"')

    json_content = ''
    try:
        json_content = json.loads(get_content)
    except:  # might crash if checked resource is not a webpage
        print('Error! JSON failed parsing for the URL "{0}"\nMessage:\n{1}'.format(
            check_url, sys.exc_info()[0]))
        pass

    return_dict = {}
    try:
        # overall score
        for key in json_content['ruleGroups'].keys():
            # print('Key: {0}, value {1}'.format(key, json_content['ruleGroups'][key]['score']))
            return_dict[key] = json_content['ruleGroups'][key]['score']

        # page statistics
        for key in json_content['pageStats'].keys():
            # print('Key: {0}, value {1}'.format(key, json_content['pageStats'][key]))
            return_dict[key] = json_content['pageStats'][key]

        # page potential
        for key in json_content['formattedResults']['ruleResults'].keys():
            # print('Key: {0}, value {1}'.format(key, json_content['formattedResults']['ruleResults'][key]['ruleImpact']))
            return_dict[key] = json_content['formattedResults']['ruleResults'][key]['ruleImpact']

        g_pagespeed = return_dict["SPEED"]
        if  g_pagespeed >= 84:
            points = 5
            review = '* Webbplatsen är riktigt snabb!\n'
        elif g_pagespeed >= 76:
            points = 4
            review = '* Webbplatsen är snabb.\n'
        elif g_pagespeed >= 70:
            points = 3
            review = '* Genomsnittligt men inte så värst bra.\n'
        elif g_pagespeed >= 60:
            points = 2
            review = '* Webbplatsen är rätt långsam.\n'
        elif g_pagespeed < 60:
            points = 1
            review = '* Webbplatsen har väldigt dåliga prestanda enligt Google Pagespeed!\n'

        review += '* Antal resurser: {} st\n'.format(return_dict["numberResources"])
        review += '* Antal värdar: {} st\n'.format(return_dict["numberHosts"])
        review += '* Storlek på förfrågan: {} bytes\n'.format(return_dict["totalRequestBytes"])
        review += '* Statiska filer: {} st\n'.format(return_dict["numberStaticResources"])
        review += '* Storlek på HTML: {} bytes\n'.format(return_dict["htmlResponseBytes"])
        review += '* Storlek på sidvisning: {} bytes\n'.format(return_dict["overTheWireResponseBytes"])
        review += '* Storlek på CSS: {} bytes\n'.format(return_dict["cssResponseBytes"])
        review += '* Storlek på bilder: {} bytes\n'.format(return_dict["imageResponseBytes"])
        review += '* Storlek på Javascript: {} bytes\n'.format(return_dict["javascriptResponseBytes"])
        review += '* Antal Javascriptfiler: {} st\n'.format(return_dict["numberJsResources"])
        review += '* Antal CSS-filer: {} st\n'.format(return_dict["numberCssResources"])

        # potential
        review += '* Antal roundtrips: {} st\n'.format(return_dict["numTotalRoundTrips"])
        review += '* Antal blockerande roundtrips: {} st\n'.format(return_dict["numRenderBlockingRoundTrips"])
        review += '* Undvik hänvisningar: {}\n'.format("Ok" if int(return_dict["AvoidLandingPageRedirects"]) < 2 else "Behöver förbättras")
        review += '* Aktivera GZIP-komprimering: {}\n'.format("Ok" if int(return_dict["EnableGzipCompression"]) < 2 else "Behöver förbättras")
        review += '* Använd webbläsarens cache: {}\n'.format("Ok" if int(return_dict["LeverageBrowserCaching"]) < 2 else "Behöver förbättras")
        review += '* Är webbservern snabb: {}\n'.format("Ok" if int(return_dict["MainResourceServerResponseTime"]) < 2 else "Behöver förbättras")
        review += '* Behöver CSS-filer minimeras: {}\n'.format("Ok" if int(return_dict["MinifyCss"]) < 2 else "Behöver förbättras")
        review += '* Behöver HTML-filen minimeras: {}\n'.format("Ok" if int(return_dict["MinifyHTML"]) < 2 else "Behöver förbättras")
        review += '* Behöver Javascript-filer minimeras: {}\n'.format("Ok" if int(return_dict["MinifyJavaScript"]) < 2 else "Behöver förbättras")
        review += '* Blockeras sidvisningen: {}\n'.format("Ok" if int(return_dict["MinimizeRenderBlockingResources"]) < 2 else "Behöver förbättras")
        review += '* Behöver bilderna optimeras för webben: {}\n'.format("Ok" if int(return_dict["OptimizeImages"]) < 2 else "Behöver förbättras")
        review += '* Behöver synligt innehåll prioriteras: {}\n'.format("Ok" if int(return_dict["PrioritizeVisibleContent"]) < 2 else "Behöver förbättras")

    except:
        print('Error! Request for URL "{0}" failed.\nMessage:\n{1}'.format(check_url, sys.exc_info()[0]))
        pass

    return (points, review, return_dict)
