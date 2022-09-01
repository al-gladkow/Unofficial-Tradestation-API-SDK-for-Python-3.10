# Unofficial Tradestation API SDK for Python 3.10

[BY CLONING THIS REPO YOU AGREE TO THESE TERMS.](https://github.com/al-gladkow/Unofficial-Tradestation-API-SDK-for-Python-3.10/blob/main/warning.txt)

## Description
This module provides functionality for interfacing with the [Tradestation API (V3)](https://www.tradestation.com/platforms-and-tools/trading-api/) to access account information, market data, and trading functionalities. **It is intended to be used for testing purposes and is not complete**. No copyright infringement was intended; please contact the repository owner for any inquiries and/or complaints regarding this.

**Using this module requires an account with Tradestation and with an active API key.**

## Dependencies

* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [pytz](https://pypi.org/project/pytz/)
* [requests](https://pypi.org/project/requests/)

*For auto login functionality:*<br>

* [Google Chrome](https://www.google.com/chrome/index.html)
* [Chrome Web Driver](https://sites.google.com/chromium.org/driver/downloads)
* [Splinter](https://splinter.readthedocs.io/en/latest/install.html)

## Usage

[Read the Official API documentaion](https://api.tradestation.com/docs/) for more information about authentication, response structures.. etc.

*To use as a Jupyter Notebook:*
* Run all cells under 'Setup' and 'Authentication'
* Call `open_session` and save the returned session info to a variable (you will need this often)
* Complete authentication
* Pass session info you saved to the desired API functions
  * Returns or streams response json

*To use as a Python Script:*

`import ts.py`<br>
`sesh = open_session()`<br>
`get_bars(sesh, 'MSFT')`

See `main.py` for an example script

For more detailed descriptions of how to use the module, see the notes included in `TradestationAPI.ipynb`<br>

## License
GNU GPLv3. [Here.](https://github.com/al-gladkow/Unofficial-Tradestation-API-SDK-for-Python-3.10/blob/main/LICENSE)