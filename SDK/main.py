#!/bin/python3

# WARNING!!! FILES AND PROGRAMS CONTAINED IN THIS REPOSITORY ARE ACTIVELY DEVELOPED AND MAY CONTAIN SEVERE AND/OR DAMAGING BUGS.
# DO NOT DOWNLOAD OR USE ANY FILES UNLESS YOU KNOW WHAT YOU ARE DOING AND YOU HAVE READ & AGREE TO THE FOLLOWING CONDITIONS:

# * The User acknowledges that any files or programs contained herein should NOT be considered fully functional and may damage the User's system.
# * The User acknowledges that errors within any files or programs contained herein and/or incorrect usage by the User MAY CAUSE A LOSS OF FUNDS.
# * The User accepts all responsibility for any loss of funds, system damage, or other consequence(s) that may arise from usage of any files or programs contained in this repository.
# * The User understands that the creator(s) or any files or programs contained herein is(are) IN NO WAY ASSOCIATED with TradeStation Securities, TradeStation Crypto, TradeStation Technologies, TradeStation Group Inc., or any of its subsidiaries.

# BY CLONING THIS REPOSITORY, THE USER ACKNOWLEDGES THAT THEY HAVE READ AND AGREE TO THE CONDITIONS OUTLINED ABOVE.

# Example modular usage

import ts

if __name__ == '__main__':

    sesh = ts.open_session()

    print(ts.get_bars(sesh, 'MSFT'))
