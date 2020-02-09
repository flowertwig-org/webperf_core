from util import *
from check404 import *
from checkCss import *
from checkGooglePagespeed import *
from checkHtml import *
from checkWebbkoll import *

"""
If file is executed on itself then call a definition, mostly for testing purposes
"""
if __name__ == '__main__':
    print(check_google_pagespeed('https://webperf.se'))