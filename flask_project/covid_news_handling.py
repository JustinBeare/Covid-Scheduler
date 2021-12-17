import requests
import json

with open("./static/config.json") as file:
    data = json.load(file)

''' This function will get all the news articles from the api '''
def news_API_request(covid_terms = "Covid COVID-19 coronavirus"):
    api_key = data["apiKeys"]["covid19ApiKey"]
    ''' Loads the data from the api with the api key found in the config file '''
    url = "https://newsapi.org/v2/top-headlines?country=gb&apiKey=" + api_key
    news = requests.get(url).json()
    articles = news["articles"]
    my_articles = []
    my_news = ""
    covid_terms_split = covid_terms.split()
    ''' Checks if the articles have any of the terms such as covid in their title '''
    for article in articles:
        for term in covid_terms_split:
            if term.lower() in article["title"].lower():
                my_articles.append(article)
                break
    return my_articles

    
    
news_API_request()
#def update_news()

