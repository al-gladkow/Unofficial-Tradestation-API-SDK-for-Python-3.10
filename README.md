# Unofficial Tradestation API SDK for Python 3.10
**Version 0.0.1**
<br>
*Alec Gladkowski*

[Please read before cloning this repo.](https://github.com/al-gladkow/Unofficial-Tradestation-API-SDK-for-Python-3.10/blob/main/warning.txt)

## Description
This module provides functionality for interfacing with the [Tradestation](https://www.tradestation.com/) API to access account information, market data, and trading functionalities. It is not intended for corporate use and was created as a personal project. No copyright infringement was intended; please contact the repository owner for any inquiries and/or complaints regarding this.

Using this module requires an account with Tradestation and API key activated for the account. For more information on how to acquire this, speak with your Tradestation representative.

## Dependencies
*For auto login functionality:*
<br>
* [Google Chrome](https://www.google.com/chrome/index.html)
* [Chrome Web Driver](https://sites.google.com/chromium.org/driver/downloads)
* [Splinter](https://splinter.readthedocs.io/en/latest/install.html)

*For regular use:*
<br>
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [pytz](https://pypi.org/project/pytz/)
* [requests](https://pypi.org/project/requests/)

## Usage

*To use as a Jupyter Notebook:*
* Step 1: Install dependencies (only equired before first use) 
* Step 2: Import dependencies
* Step 3: Run all cells under 'Setup' and 'Authentication'
* Step 4: Call `open_session` and save the returned session info to a variable (you will need this often)
* Step 5: Complete authentication steps (Optional, see the end of this section)
* Step 6: Pass session info you saved to the desired API functions
  * Example: `get_bars(sesh, 'MSFT')`
  * Returns or streams request json - see Tradestation API Docs for more info on the format   

*To use as a Python Script:*
* Install dependencies, import `ts.py` and skip to Step 4 above

<p>For a more detailed description of how to authenticate your account, see the notes included in `TradestationAPI.ipynb`*</p>
<p>See `TradestationAPI.ipynb` for more notes on usage and how the program works or to get started using the SDK.
Also see `main.py` for an example script.</p>

[LICENSE](https://github.com/al-gladkow/Unofficial-Tradestation-API-SDK-for-Python-3.10/blob/main/LICENSE)