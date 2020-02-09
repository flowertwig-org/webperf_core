#-*- coding: utf-8 -*-
from flask import Flask
import datetime

from util import *
from checks import *

import config

app = Flask(__name__)

def testsites(test_type=None, only_test_untested_last_hours=24, order_by='title ASC'):
    """
    Executing the actual tests.
    Attributes:
    * test_type=num|None to execute all available tests
    """

    # TODO: implementera test_type=None

    print("###############################################")

    i = 1

    items = list()
    items.append([0, "https://polisen.se/"])
    #items.append([1, "https://purecss.flowertwig.org/"])

    print('Webbadresser som testas:', len(items))

    for item in items:
        site_id = item[0]
        website = item[1]
        print('{}. Testar adress {}'.format(i, website))
        the_test_result = None

        try:
            if test_type == 2:
                the_test_result = check_four_o_four(website)
            elif test_type == 6:
                the_test_result = check_w3c_valid(website)
            elif test_type == 7:
                the_test_result = check_w3c_valid_css(website)
            elif test_type == 20:
                the_test_result = check_privacy_webbkollen(website)
            elif test_type == 0:
                the_test_result = check_google_pagespeed(website)

            if the_test_result != None:
                print('Rating: ', the_test_result[0])
                #print('Review: ', the_test_result[1])

                json_data = ''
                try:
                    json_data = the_test_result[2]
                except:
                    json_data = ''
                    pass

                checkreport = str(the_test_result[1]).encode('utf-8') # för att lösa encoding-probs
                jsondata = str(json_data).encode('utf-8') # --//--

                the_test_result = None # 190506 för att inte skriva testresultat till sajter när testet kraschat. Måste det sättas till ''?
        except Exception as e:
            print('FAIL!', website, '\n', e)
            pass

        i += 1

def testing():
    print('### {0} ###'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    ##############
    print('###############################\nKör test: 0 - Google Pagespeed')
    testsites(test_type=0)
    print('###############################\nKör test: 2 - 404-test')
    testsites(test_type=2)
    print('###############################\nKör test: 6 - HTML')
    testsites(test_type=6)
    print('###############################\nKör test: 7 - CSS')
    testsites(test_type=7)
    print('###############################\nKör test: 20 - Webbkoll')
    testsites(test_type=20)

"""
If file is executed on itself then call a definition, mostly for testing purposes
"""
if __name__ == '__main__':
    print('###############################')
    testing()
