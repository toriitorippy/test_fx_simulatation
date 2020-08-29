from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments

accountID = "101-009-15065836-001"
access_token = ' 8ec2523da72b0e7d818764094c98cc74-3c1036b692b3c82e3e46847a895641ed'

api = API(access_token=access_token, environment="practice")

params = { "instruments": "EUR_USD,EUR_JPY,USD_JPY" }
import oandapyV20.endpoints.accounts as accounts
r = accounts.AccountInstruments(accountID=accountID, params=params)
api.request(r)

