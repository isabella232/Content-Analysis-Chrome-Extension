import logging
import azure.functions as func
import json
import requests
from twilio.rest import Client

subscription_key = "acaa102d183f4260965c782bc60e2199"
search_url = "https://api.cognitive.microsoft.com/bing/v7.0/news/search"

account_sid = "AC7ed69f2740a5cd14793b45eab5f61d5e"
auth_token = "eebf5a01555f36ca6eccb0b98fd4ee64"
temp_twilio_num = "+14804055791"

receiver_num = ""

counter = 1
search_term = ""

value_data_list = []

twilio_success = False

headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
params  = {"q": search_term, "count": counter}


def main(req: func.HttpRequest) -> func.HttpResponse:
    global search_terms
    global counter
    global value_data_list
    global receiver_num


    logging.info('Python HTTP trigger function processed a request.')

    phrases = req.params.get('phrases')
    url = req.params.get('url')
    receiver = req.params.get('receiver')

    count = req.params.get('count')
    if not phrases:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            phrases = req_body.get('phrases')
    if count:
        counter = count

    if phrases and url and receiver:
        search_terms = phrases
        receiver_num = receiver

        data_dict = create_data_dict()
        set_data_list(data_dict)
        check_for_initial(url)

        for data in value_data_list:
            twilio_message("Article Name: " + data["name"])
            twilio_message("Article URL: " + data["url"])
            twilio_message("Article Description: " + data["description"])

        return func.HttpResponse(get_json_results())
    else:
        return func.HttpResponse(
             "test"
        )

def create_data_dict():
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = json.dumps(response.json())
    return json.loads(search_results)

def set_data_list(data_dict):
    global value_data_list
    for i in range(0, counter):
        temp_data_dict = {}
        temp_data_dict["name"] = data_dict["value"][i]["name"]
        temp_data_dict["url"] = data_dict["value"][i]["url"]
        temp_data_dict["description"] = data_dict["value"][i]["description"]
        value_data_list.append(temp_data_dict)

def check_for_initial(url):
    global value_data_list
    for data in value_data_list:
        if data["url"] == url:
            value_data_list.remove(data)

def get_json_results():
    python_results = { "success" : twilio_success }
    reset_values()
    return json.dumps(python_results)

def reset_values():
    global counter
    global search_term
    global value_data_list
    global twilio_success
    global receiver_num

    receiver_num = ""
    
    counter = 1
    search_term = ""

    value_data_list = []

    twilio_success = False

def twilio_message(body_message):
    global twilio_success

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to="+1" + receiver_num,
        from_=temp_twilio_num,
        body=body_message)

    twilio_success = True