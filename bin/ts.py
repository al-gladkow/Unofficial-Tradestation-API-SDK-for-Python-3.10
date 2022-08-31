# %% [markdown]
# ## Unofficial Tradestation API SDK for Python 3.10
# ---
# **Version 0.0.1**
# <br>
# *Alec Gladkowski*

# %%
# WARNING!!! FILES AND PROGRAMS CONTAINED IN THIS REPOSITORY ARE ACTIVELY DEVELOPED AND MAY CONTAIN SEVERE AND/OR DAMAGING BUGS.
# DO NOT DOWNLOAD OR USE ANY FILES UNLESS YOU KNOW WHAT YOU ARE DOING AND YOU HAVE READ & AGREE TO THE FOLLOWING CONDITIONS:

# * The User acknowledges that any files or programs contained herein should NOT be considered fully functional and may damage the User's system.
# * The User acknowledges that errors within any files or programs contained herein and/or incorrect usage by the User MAY CAUSE A LOSS OF FUNDS.
# * The User accepts all responsibility for any loss of funds, system damage, or other consequence(s) that may arise from usage of any files or programs contained in this repository.
# * The User understands that the creator(s) or any files or programs contained herein is(are) IN NO WAY ASSOCIATED with TradeStation Securities, TradeStation Crypto, TradeStation Technologies, TradeStation Group Inc., or any of its subsidiaries.

# BY CLONING THIS REPOSITORY, THE USER ACKNOWLEDGES THAT THEY HAVE READ AND AGREE TO THE CONDITIONS OUTLINED ABOVE.

# %%
# TODO:
#  * Random state checking 
#  * Complete Trading functionality
#  * Complete Options functionality
#  * Add more docstrings and examples
#  * Session timeout tracking
#  * Automatic session refresh without refresh token

# %%
# Install dependencies if needed
# Must have Google Chrome and ChromeDriver installed on the system for automatic logins
# To install ChromeDriver visit: https://sites.google.com/chromium.org/driver/downloads
# ----------------------------------------------------

# %pip install python-dotenv
# %pip install datetime
# %pip install pytz
# %pip install requests
# %pip install splinter

# %%
# Imports
# ----------------------------------------------------

# Local Modules
from HelperFunctions import make_url, random_state

# System
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from pytz import timezone

# Network
import requests as req
from urllib import parse
import webbrowser
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

# Debugging
# import warnings
# import pdb

# %% [markdown]
# ### Setup

# %%
# Load environment variables
# Create an environment variable first or add your credentials to an exisiting one
# Hard-coding sensitive information is dangerous and not recommended!!
# ----------------------------------------------------

def load_env():

    env_loaded = load_dotenv(find_dotenv())

    try:
        if env_loaded is False:
            raise ValueError('Environment was not loaded correctly')
    except ValueError as ve:
        print(ve)
        exit()

load_env()

TRADESTATION_KEY = os.getenv('TRADESTATION_KEY')
TRADESTATION_SECRET = os.getenv('TRADESTATION_SECRET')

# Only needed for auto login
TRADESTATION_USER = os.getenv('TRADESTATION_USER')
TRADESTATION_PASS = os.getenv('TRADESTATION_PASS')

# %%
# Set Globals/Options
# ----------------------------------------------------

LIVE_TRADING = 'https://api.tradestation.com'
SIM_TRADING = 'https://sim.api.tradestation.com'

# Choose live trading account or sim
API_URL = SIM_TRADING

# Don't change these unless you know what you're doing
REDIRECT_URI = 'redirect_uri=http://localhost:80'
CLIENT_ID = f'client_id={TRADESTATION_KEY}'
CLIENT_SECRET = f'client_secret={TRADESTATION_SECRET}'

# Choose available scopes
# Options: MarketData, ReadAccount, Trade, Crypto, OptionSpreads, offline_access, profile, email
# NOTE: "offline_access" requied for refresh tokens. 'openid' is always required
# No default account authorization: Crypto, OptionSpreads, Trade - speak with TradeStation to change this
SCOPES = ['openid', 'MarketData', 'ReadAccount', 'profile']

# Set your timezone
TIMEZONE = timezone('US/Central')
TODAY = TIMEZONE.localize(datetime.now()).replace(microsecond=0).isoformat()

# %% [markdown]
# ### Authentication

# %%
# Build URL for redirection
# ----------------------------------------------------

def make_auth_url():

    auth_url= 'https://signin.tradestation.com/authorize?'
    response_type = 'response_type=code'
    _state = f'state={random_state()}'
    
    scope_list = parse.quote_plus(" ".join(SCOPES))
    _scope = f'scope={scope_list}'

    audience = f'audience={LIVE_TRADING}'

    full_url = make_url([auth_url, response_type, CLIENT_ID, REDIRECT_URI, audience, _state, _scope])

    return full_url

# %%
# Get Authorization Code with manual login
# ----------------------------------------------------
# NOTE INSTRUCTIONS:
# After successful login, browser will redirect to a blank page.
# Look in the url and copy the 'code=' portion
# E.g. -> http://localhost:80/...code=ABCD1234EFGH5678...
# Copy the portion between '...' and paste into the prompt

def get_auth_manual():
    
    # Opens URL in browser for authentication
    webbrowser.open_new(make_auth_url())

    # Manually enter authorization code from browser redirection URL
    return input('Please enter the authorization code from the url: ')

# %%
# Get Authorization Code with automatic login
# ----------------------------------------------------
# NOTE: WORKING

def get_auth_auto():
    
    # Login automatically
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    browser.visit(make_auth_url())

    browser.find_by_id('username').fill(TRADESTATION_USER)
    browser.find_by_id('password').fill(TRADESTATION_PASS)

    button = browser.find_by_id('btn-login')
    button.click()
    
    code_field = browser.find_by_id('code')
    print('Please enter your one-time password.')
    code_field.fill(input('OTP: '))
    
    button = browser.find_by_name('action')
    button.click()

    # After logging in, extract the url and the parts from it
    browser_url = browser.url
    browser.quit()
    
    code = browser_url.split(sep="?")[1].split(sep="&")[0]
    
    return code

# %%
# Retrieve access token
# ----------------------------------------------------
# NOTE: WORKING

def get_access_token(auth_code):
    
    # Build URL
    token_url = 'https://signin.tradestation.com/oauth/token'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    grant_type = 'grant_type=authorization_code'

    # Build data dict
    data = {}
    for item in [grant_type,CLIENT_ID,CLIENT_SECRET,auth_code,REDIRECT_URI]:
        split = item.split('=')
        data[split[0]] = split[1]

    # Post request
    res = req.post(url=token_url,headers=headers,data=data)
    
    # NOTE: Response 400 can be the result of an incorrect OTP login code
    if res.status_code != 200: print(res)
    
    # Return session info dict
    else: return res.json()

# %%

# Open a Session
# ----------------------------------------------------
# NOTE: WORKING

def open_session(mode='auto'):

    session_info = None
    
    if mode.lower() == 'auto':
        auth_code = get_auth_auto()
    elif mode.lower() == 'manual':
        auth_code = get_auth_manual()

    # Get the access token
    session_info = get_access_token(auth_code)

    if session_info is not None:
        print('Successfully opened new login session.')
        
        # Compute, store, & print the session expiration time
        expire_time = datetime.now() + timedelta(seconds=session_info['expires_in'])
        session_info['expire_time'] = expire_time
        print(f'Session expires at: {expire_time.replace(microsecond=0)}.')
        
        return session_info
    
    else:
        print('Authentication unsuccessful.')
        
# sesh = open_session()
# sesh = open_session(mode='manual')

# %%
# Refresh session with refresh token
# This allow you to keep the session open indefinitely.
# Default session timeout is 20mins
# NOTE WARNING: refresh tokens are valid until deactivated by
# talking with Tradestation. Use them at your own discretion and
# keep them secure if you choose to.
# NOTE: Must have 'offline_access' included in scope
# ----------------------------------------------------
# NOTE: WORKING???

def refresh_session(session_info):
    
    # Build URL
    token_url = 'https://signin.tradestation.com/oauth/token'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    grant_type = 'grant_type=refresh_token'
    refresh_token = f'refresh_token={session_info["refresh_token"]}'

    # Build data dict
    data = {}
    for item in [grant_type, CLIENT_ID, CLIENT_SECRET, refresh_token]:
        split = item.split('=')
        data[split[0]] = split[1]

    # Post request
    res = req.post(url=token_url, headers=headers, data=data)

    if res.status_code != 200: print(res)

    # Return session info dict
    else:
        print('Successfully refreshed the session.')
        
        session_info = res.json()
        
        # Compute, store, & print the session expiration time
        expire_time = datetime.now() + timedelta(seconds=session_info['expires_in'])
        session_info['expire_time'] = expire_time
        print(f'Session expires at: {expire_time.replace(microsecond=0)}.')
        
        return session_info
    
# sesh = refresh_session(sesh)

# %% [markdown]
# ### Market Data Requests

# %%
# Get Bars
# ----------------------------------------------------
# Fetches marketdata bars for the given symbol, interval, and timeframe.
# NOTE: WORKING

def get_bars(session_info, symbol, interval='1', unit='Daily', barsback='5', start=TODAY):
    
    endpoint = '/v3/marketdata/barcharts/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + symbol + '?'

    _interval = f'interval={interval}'
    _unit = f'unit={unit}'
    _barsback = f'barsback={barsback}'
    _start = f'startdate={start}'

    full_url = make_url([full_url,_interval,_unit,_barsback,_start])

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)
    
    return res.json()

# get_bars(sesh, 'AMZN')

# %%
# Stream Bars
# ----------------------------------------------------
# Streams marketdata bars for the given symbol, interval, and timeframe.
# NOTE: WORKING

def stream_bars(session_info, symbol, interval='1', unit='Daily', barsback='5'):
    
    endpoint = '/v3/marketdata/stream/barcharts/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + symbol + '?'
    
    _interval = f'interval={interval}'
    _unit = f'unit={unit}'
    _barsback = f'barsback={barsback}'
    
    full_url = make_url([full_url,_interval,_unit,_barsback])
    
    res = req.get(url = full_url, headers=headers, stream=True)
    
    if res.status_code != 200: print(res)
    
    for line in res.iter_lines():
        if line:
            print(line)
            
# stream_bars(sesh, 'BTCUSD')

# %%
# Get Quote Snapshots
# ----------------------------------------------------
# Fetches a full snapshot of the latest Quote for the given Symbols. For realtime Quote updates, users should use the Quote Stream endpoint.
# NOTE: WORKING

def get_quote_snapshots(session_info, symbols):
    
    endpoint = '/v3/marketdata/quotes/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url +  ','.join(symbols)
    
    res = req.get(url = full_url, headers=headers)

    if res.status_code != 200: print(res)
    
    return res.json()

# get_quote_snapshots(sesh, ['AMZN', 'BTCUSD'])

# %%
# Stream Quotes
# ----------------------------------------------------
# Streams Quote changes for one or more symbols.
# NOTE: WORKING

def stream_quotes(session_info, symbols):
    
    endpoint = '/v3/marketdata/stream/quotes/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + ','.join(symbols)
    
    res = req.get(url = full_url, headers=headers, stream=True)
    
    if res.status_code != 200: print(res)
    
    for line in res.iter_lines():
        if line:
            print(line)
            
# stream_quotes(sesh, ['BTCUSD', 'ETHUSD'])

# %%
# Get Crypto Symbol Names
# ----------------------------------------------------
# Fetches all crypto Symbol Names information.
# NOTE: WORKING

def get_crypto_symbol_names(session_info):
    
    endpoint = '/v3/marketdata/symbollists/cryptopairs/symbolnames'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url
    
    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# get_crypto_symbol_names(sesh)

# %%
# Get Symbol Details
# ----------------------------------------------------
# Fetches symbol details and formatting information for one or more symbols and relevant errors, if any. Use provided formatting objects to display provided prices and quantities from other API endpoints.
# NOTE: WORKING

def get_symbol_details(session_info, symbols):

    endpoint = '/v3/marketdata/symbols/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + ','.join(symbols)

    res = req.get(url = full_url, headers=headers)

    if res.status_code != 200: print(res)

    return res.json()

# get_symbol_details(sesh, ['AMZN', 'BTCUSD'])

# %%
# Get Interest Rates
# ----------------------------------------------------
# A public route that returns cryptocurrency interest rates.

def get_interest_rates(session_info):
    
    endpoint = '/v3/marketdata/crypto/interestrates'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url
    
    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# get_interest_rates(sesh)

# %%
# Get Option Expirations
# ----------------------------------------------------
# Get the available option contract expiration dates for the underlying symbol.

def get_option_expirations(session_info, underlying, strike=None):
    
    endpoint = '/v3/marketdata/options/expirations/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    
    if strike is None:
        full_url = url + underlying
    else:
        full_url = url + underlying + f'?strikePrice={strike}'
    
    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# get_option_expirations(sesh, 'AMZN')

# %%
# TODO
# Get Option Risk Reward
# ----------------------------------------------------
# Analyze the risk vs. reward of a potential option trade. This endpoint is not applicable for option spread types with different expirations, such as Calendar and Diagonal.

def get_options_risk_reward():
    
    pass

# %%
# Get Option Spread Types
# ----------------------------------------------------
# Get the available spread types for option chains.

def get_option_spread_types(session_info):
    
    endpoint = '/v3/marketdata/options/spreadtypes'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url
    
    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# get_option_spread_types(sesh)

# %%
# Get Option Strikes
# ----------------------------------------------------
# Get the available strike prices for a spread type and expiration date.
    
def get_option_strikes(session_info, underlying, spreadType='Single', strikeInterval=1, expiration=None, expiration2=None):
    
    endpoint = '/v3/marketdata/options/strikes/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + underlying + '?'
    
    _spreadType = f'spreadType={spreadType}'
    _strikeInterval = f'strikeInterval={strikeInterval}'

    url_maker = [full_url, _spreadType, _strikeInterval]
    
    if expiration is not None:
        _expiration = f'expiration={expiration}'
        url_maker.append(_expiration)
    if expiration2 is not None:
        _expiration2 = f'expiration2={expiration2}'
        url_maker.append(_expiration2)
    
    full_url = make_url(url_maker)
    
    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)
    
    # print(res.json())
    
    return res.json()

# get_option_strikes(sesh, 'AMZN')

# %%
# Stream Option Chain
# ----------------------------------------------------
# Stream a chain of option spreads for a given underlying symbol, spread type, and expiration. A maximum of 10 concurrent streams is allowed.

def stream_option_chain(session_info, underlying, strikeProximity=5, spreadType='Single', strikeInterval=1, enableGreeks=True,
                        strikeRange='All', optionType='All', riskFreeRate=None, priceCenter=None, expiration=None, expiration2=None):
    
    endpoint = '/v3/marketdata/stream/options/chains/'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + underlying + '?'
    
    _strikeProximity = f'strikeProximity={strikeProximity}'
    _spreadType = f'spreadType={spreadType}'
    _strikeInterval = f'strikeInterval={strikeInterval}'
    _enableGreeks = f'enableGreeks={str(enableGreeks)}'
    _strikeRange = f'strikeRange={strikeRange}'
    _optionType = f'optionType={optionType}'
    
    url_maker = [full_url, _strikeProximity, _spreadType, _strikeInterval, _enableGreeks, _strikeRange, _optionType]
    
    if riskFreeRate is not None:
        _riskFreeRate = f'riskFreeRate={riskFreeRate}'
        url_maker.append(_riskFreeRate)
    if priceCenter is not None: 
        _priceCenter = f'priceCenter={priceCenter}'
        url_maker.append(_priceCenter)
    if expiration is not None:
        _expiration = f'expiration={expiration}'
        url_maker.append(_expiration)
    if expiration2 is not None:
        _expiration2 = f'expiration2={expiration2}'
        url_maker.append(_expiration2)
    
    full_url = make_url(url_maker)
    
    res = req.get(url = full_url, headers=headers, stream=True)
    
    if res.status_code != 200: print(res)
    
    return res.json()

# stream_option_chain(sesh, 'AMZN')

# %%
# TODO
# Stream Option Quotes
# ----------------------------------------------------
# Stream price quotes and greeks for the specified option spread. A maximum of 10 concurrent streams is allowed. Leg indexes are expected to be sequential starting at zero. For example, if there are three legs, the legs in the request should contain Legs[0], Legs[1], and Legs[2]. Note that there is no required order for the Legs in the query parameters. For example, if there are 2 legs, Legs[0].Symbol, Legs[0].Ratio, Legs[1].Symbol, and Legs[1].Ratio can be in any order in the query parameters.

def stream_option_quotes(session_info, underlying):
    
    endpoint = '/v3/marketdata/stream/options/quotes'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + underlying + '?'
    
    pass

# stream_option_quotes(sesh, 'AMZN')

# %% [markdown]
# ### Brokerage Requests

# %%
# Get Accounts
# ----------------------------------------------------
# Fetches the list of Brokerage Accounts available for the current user.
# NOTE: WORKING

def get_accounts(session_info):

    endpoint = '/v3/brokerage/accounts'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# get_accounts(sesh)

# %%
# Get Balances
# ----------------------------------------------------
# Fetches the brokerage account Balances for one or more given accounts. Request valid for Cash, Margin, Futures, and DVP account types.

def get_balances(session_info, accounts):
    
    _accounts = ','.join(accounts)
    
    endpoint = f'/v3/brokerage/accounts/{_accounts}/balances'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# account = get_accounts(sesh)['Accounts'][0]['AccountID']
# get_balances(sesh, account)

# %%
# Get Balances BOD
# ----------------------------------------------------
# Fetches the Beginning of Day Balances for the given Accounts. Request valid for Cash, Margin, Futures, and DVP account types.

def get_balances_bod(session_info,accounts):
    
    _accounts = ','.join(accounts)
    
    endpoint = f'/v3/brokerage/accounts/{_accounts}/bodbalances'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)
    
    return res.json()

# account = get_accounts(sesh)['Accounts'][0]['AccountID']
# get_balances_bod(sesh, account)

# %%
# Get Historical Orders
# ----------------------------------------------------
# Fetches Historical Orders for the given Accounts, sorted in descending order of time placed for open and time executed for closed. Request valid for all account types.

def get_historical_orders(session_info,accounts,since):
    
    _accounts = ','.join(accounts)
    _since = f'?since={since}'
    
    endpoint = f'/v3/brokerage/accounts/{_accounts}/historicalorders'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + _since

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Get Orders
# ----------------------------------------------------
# Fetches today's orders for the given Accounts, sorted in descending order of time placed for open and time executed for closed. Request valid for all account types.

def get_orders(session_info, accounts):
    
    _accounts = ','.join(accounts)
    
    endpoint = f'/v3/brokerage/accounts/{_accounts}/orders'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Get Positions
# ----------------------------------------------------
# Fetches positions for the given Accounts. Request valid for Cash, Margin, Futures, and DVP account types.

def get_positions(session_info, accounts):
    
    _accounts = ','.join(accounts)
    
    endpoint = f'/v3/brokerage/accounts/{_accounts}/positions'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Get Wallets
# ----------------------------------------------------
# Fetches wallet information. Request valid for Crypto account types.

def get_wallets(session_info, account):
    
    endpoint = f'/v3/brokerage/accounts/{account}/wallets'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Stream Wallets
# ----------------------------------------------------
# Streams wallet information. Request valid for Crypto account types.

def stream_wallets(session_info, account):
    
    endpoint = f'/v3/brokerage/stream/accounts/{account}/wallets'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %% [markdown]
# ### Order Execution Requests

# %%
# Confirm Order
# ----------------------------------------------------
# Returns estimated cost and commission information for an order without the order actually being placed. Request valid for Market, Limit, Stop Market, Stop Limit, Options, and Order Sends Order (OSO) order types. All Crypto market orders, excluding USDCUSD, must have Day duration (TimeInForce). The fields that are returned in the response depend on the order type. The following shows the different fields that will be returned.

def confirm_order(session_info):
    
    pass
    

# %%
# Confirm Group Order
# ----------------------------------------------------
# Creates an Order Confirmation for a group order. Request valid for all account types. Request valid for Order Cancels Order (OCO) and Bracket (BRK) order types as well as grouped orders of other types (NORMAL). All Crypto market orders, excluding USDCUSD, must have Day duration (TimeInForce).

def confirm_group_order(session_info):
    
    pass
    

# %%
# Place Group Order
# ----------------------------------------------------
# Submits a group order. Request valid for all account types. Request valid for Order Cancels Order (OCO) and Bracket (BRK) order types as well as grouped orders of other types (NORMAL). All Crypto market orders, excluding USDCUSD, must have Day duration (TimeInForce).

def place_group_order(session_info):
    
    pass

# %%
# Place Order
# ----------------------------------------------------
# Creates a new brokerage order. Request valid for all account types. Request valid for Market, Limit, Stop Market, Stop Limit, Options and Order Sends Order (OSO) order types. All Crypto market orders, excluding USDCUSD, must have Day duration (TimeInForce).

def place_order(session_info):
    
    pass

# %%
# Replace Order
# ----------------------------------------------------
# Replaces an active order with a modified version of that order. You cannot update an order that has been filled. Request valid for Cash, Margin, Futures, and DVP account types.

def replace_order(session_info, orderID, order):
    
    endpoint = f'/v3/orderexecution/orders'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + orderID

    res = req.put(url = full_url, headers=headers, json=order)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Cancel Order
# ----------------------------------------------------
# Cancels an active order. Request valid for all account types.

def cancel_order(session_info, orderID):
    
    endpoint = f'/v3/orderexecution/orders'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url + orderID

    res = req.delete(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Get Activation Triggers
# ----------------------------------------------------
# To place orders with activation triggers, a valid TriggerKey must be sent with the order. This resource provides the available trigger methods with their corresponding key.

def get_activation_triggers(session_info):
    
    endpoint = f'/v3/orderexecution/activationtriggers'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()

# %%
# Get Routes
# ----------------------------------------------------
# Returns a list of valid routes that a client can specify when posting an order.

def get_routes(session_info):
    
    endpoint = f'/v3/orderexecution/routes'
    headers = {'Authorization': f'Bearer {session_info["access_token"]}'}
    url = API_URL + endpoint
    full_url = url

    res = req.get(url = full_url, headers=headers)
    
    if res.status_code != 200: print(res)

    return res.json()


