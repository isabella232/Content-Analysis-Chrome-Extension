import newspaper
from newspaper import Article

def get_article_content_list(article_url):
    article = Article(article_url)
    article.download()
    article.parse()
    article_content_list = list(article.text.split("\n"))

    for i in article_content_list:
        if not i:
            article_content_list.remove(i)

    return article_content_list