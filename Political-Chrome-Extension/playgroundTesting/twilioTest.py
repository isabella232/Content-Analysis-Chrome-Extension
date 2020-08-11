# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from twilio.rest import Client

# Find these values at https://twilio.com/user/account
account_sid = "AC7ed69f2740a5cd14793b45eab5f61d5e"
auth_token = "eebf5a01555f36ca6eccb0b98fd4ee64"

client = Client(account_sid, auth_token)

client.api.account.messages.create(
    to="+19254873772",
    from_="+14804055791",
    body="Hello there!")