import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

# Download necessary NLTK data
nltk.download('vader_lexicon', quiet=True)

def get_article_sentiment(url):
    """
    Perform sentiment analysis on a news article.
    
    :param url: URL of the news article
    :return: Sentiment scores (compound, positive, negative, neutral)
    """
    try:
        # Fetch article content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article text (this is a simplified approach)
        article_text = ' '.join([p.text for p in soup.find_all('p')])
        
        # Perform sentiment analysis
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(article_text)
        
        return sentiment_scores
    except Exception as e:
        print(f"Error analyzing sentiment for {url}: {str(e)}")
        return None

def analyze_news_sentiment(news_articles):
    """
    Analyze sentiment for a list of news articles.
    
    :param news_articles: List of news article dictionaries
    :return: List of news articles with sentiment scores
    """
    for article in news_articles:
        sentiment = get_article_sentiment(article['url'])
        if sentiment:
            article['sentiment'] = sentiment
    
    return news_articles
