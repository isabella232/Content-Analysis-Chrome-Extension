import json
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import newspaper
from newspaper import Article

key = "3836568134ba4356a6242077bd107cad"
endpoint = "https://article-analysis.cognitiveservices.azure.com/"

pos = 0
neu = 0
neg = 0
num = 0

article_content_list = []


def get_article_content_list(article_url):
    article = Article(article_url)
    article.download()
    article.parse()
    article_content_list = list(article.text.split("\n"))

    for i in article_content_list:
        if not i:
            article_content_list.remove(i)

    return article_content_list

def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

def create_new_list():
    new_list = []
    counter = 0
    items = 0

    if article_content_list:

        while (counter < 5120) and (items < 10) and (article_content_list):
            if article_content_list[0]:
                counter += len(article_content_list[0])
                items += 1
                if (counter < 5120) and (items < 10):
                    new_list.append(article_content_list[0])
                    article_content_list.pop(0)
                elif (counter > 5120) and (items == 1):
                    return new_list
                else:
                    break

            else:
                article_content_list.pop(0)
    return new_list


def analyse_article(client, document, i):
    global pos
    global neu
    global neg
    global num

    num += 1

    response = client.analyze_sentiment(documents = document)[i]

    print(response.sentiment)

    pos += response.confidence_scores.positive
    neu += response.confidence_scores.neutral
    neg += response.confidence_scores.negative

def get_sentiment():
    if (pos > neg) and (pos > neu):
        return "Positive"
    elif ((neg > pos) and (neg > neu)):
        return "Negative"
    else:
        return "Neutral"

def get_json_results():
    python_results = {
        "sentiment": get_sentiment(),
        # "positive": pos/num,
        # "neutral": neu/num,
        # "negative": neg/num
    }
    return json.dumps(python_results)

def update_url_name(url_name):
    global article_content_list 
    article_content_list = get_article_content_list(url_name)

def find_sentiment():
    while article_content_list:
        document = create_new_list()
        client = authenticate_client()
        for i in range (0, len(document)):
            analyse_article(client, document, i)
    return get_json_results()
