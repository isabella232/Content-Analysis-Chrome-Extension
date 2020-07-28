import logging
import azure.functions as func
import json
import newspaper
import nltk
import re
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from newspaper import Article

key = "3836568134ba4356a6242077bd107cad"
endpoint = "https://article-analysis.cognitiveservices.azure.com/"

pos = 0
neu = 0
neg = 0
num = 0

cycle = 0

syllables = 0
sentences = 0
words = 0

continue_running = True
article_content_list = []

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    name = req.params.get('name')
    cycle = req.params.get('cycle')

    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get(f'name')

    if name:
        update_name_and_cycle(name, cycle)
        return func.HttpResponse(get_analytics()) 

    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
    return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
    )

def update_name_and_cycle(url_name, current_cycle):
    global article_content_list 
    global cycle

    cycle = current_cycle
    article_content_list = get_article_content_list(url_name)

def get_article_content_list(article_url):
    article = Article(article_url)
    article.download()
    article.parse()
    article_content_list = list(article.text.split("\n"))

    for i in article_content_list:
        if not i:
            article_content_list.remove(i)

    return article_content_list

def get_analytics():
    global continue_running
    global num

    client = authenticate_client()
    document = create_new_list()
    
    if len(document) != 0:
        for i in range (0, len(document)):
            analyse_reading(document, i)
            analyse_sentiment(client, document, i)
    else:
        final_cycle_configurations()
    return get_json_results()

def final_cycle_configurations():
    global continue_running
    global num
    global sentences
    global words 

    num = 1
    continue_running = False
    sentences = 1
    words = 1

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
        temp_list = list_after_cycle()
        print(len(temp_list))
        while (counter < 5120) and (items < 10) and (temp_list) and (items < len(temp_list)):
            if temp_list[items]:
                counter += len(temp_list[items])
                if (counter < 5120) and (items < 10):
                    new_list.append(article_content_list[items])
                    items += 1
                elif (counter > 5120) and (items == 0):
                    return new_list
                else:
                    break
    return new_list

def list_after_cycle():
    global article_content_list

    counter = 0
    items = 0

    temp_list = article_content_list

    cycle_num = int(cycle)

    if (cycle_num != 0):
        for _ in range(0, cycle_num):
            while (counter < 5120) and (items < 10) and (temp_list):
                if temp_list[0]:
                    counter += len(temp_list[0])
                    items += 1
                    if (counter < 5120) and (items < 10):
                        del temp_list[0]
                    else:
                        break
                else:
                    del temp_list[0]
            counter = 0
            items = 0
    return temp_list

def analyse_reading(document, i):
    global syllables
    global words
    global sentences

    text = document[i]
    sentence_list = split_into_sentences(text)
    sentences += len(sentence_list)
    for sentence in sentence_list:
        word_list = sentence.split()
        words += len(word_list)
        for w in word_list:
            syllables += syllable_count(w)

def analyse_sentiment(client, document, i):
    global pos
    global neu
    global neg
    global num

    num += 1

    response = client.analyze_sentiment(documents = document)[i]

    pos += response.confidence_scores.positive
    neu += response.confidence_scores.neutral
    neg += response.confidence_scores.negative

def get_json_results():
    python_results = {
        "sentiment_analysis": {
            "sentiment": get_sentiment(),
            "positive": pos/num,
            "neutral": neu/num,
            "negative": neg/num,
        },
        "difficulty_analysis": {
            "asl": words/sentences,
            "asw": syllables/words,
            "flesch_reading_score": get_flesch_reading_score(),
        }, 
        "continue": continue_running
    }
    resetValues()
    return json.dumps(python_results)

def get_sentiment():
    if check_for_mixed():
        return "Mixed"
    elif (pos > neg) and (pos > neu):
        return "Positive"
    elif ((neg > pos) and (neg > neu)):
        return "Negative"
    else:
        return "Neutral"

def check_for_mixed():
    return (pos/num < 0.45) and (neu/num < 0.45) and (neg/num < 0.45)

def syllable_count(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

def get_flesch_reading_score():
    asl = words/sentences
    asw = syllables/words
    return 206.835 - (1.015 * asl) - (84.6 * asw)

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def resetValues():
    global pos
    global neu
    global neg
    global num
    global cycle
    global syllables
    global sentences
    global words
    global continue_running
    global article_content_list

    pos = 0
    neu = 0
    neg = 0
    num = 0

    cycle = 0

    syllables = 0
    sentences = 0
    words = 0

    continue_running = True
    article_content_list = []