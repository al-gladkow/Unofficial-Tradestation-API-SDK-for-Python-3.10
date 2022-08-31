#!/bin/python3

# WARNING!!! FILES AND PROGRAMS CONTAINED IN THIS REPOSITORY ARE ACTIVELY DEVELOPED AND MAY CONTAIN SEVERE AND/OR DAMAGING BUGS.
# DO NOT DOWNLOAD OR USE ANY FILES UNLESS YOU KNOW WHAT YOU ARE DOING AND YOU HAVE READ & AGREE TO THE FOLLOWING CONDITIONS:

# * The User acknowledges that any files or programs contained herein should NOT be considered fully functional and may damage the User's system.
# * The User acknowledges that errors within any files or programs contained herein and/or incorrect usage by the User MAY CAUSE A LOSS OF FUNDS.
# * The User accepts all responsibility for any loss of funds, system damage, or other consequence(s) that may arise from usage of any files or programs contained in this repository.
# * The User understands that the creator(s) or any files or programs contained herein is(are) IN NO WAY ASSOCIATED with TradeStation Securities, TradeStation Crypto, TradeStation Technologies, TradeStation Group Inc., or any of its subsidiaries.

# BY CLONING THIS REPOSITORY, THE USER ACKNOWLEDGES THAT THEY HAVE READ AND AGREE TO THE CONDITIONS OUTLINED ABOVE.

# Imports
# --------------------------------
import string
import random


def make_url(strings):

    # Creates URL from list of strings joined by '&'

    url = ''
    for _string in strings[1:-1]:
        url = url + _string + '&'
    url = strings[0] + url + strings[-1]
    return url


def random_state():

    # Create random alphanumeric string for authorization state

    char_list = list(string.ascii_letters + string.digits)
    _state = ''

    for i in range(16):
        _state += random.choice(char_list)

    return _state
