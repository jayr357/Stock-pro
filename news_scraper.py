import requests
from bs4 import BeautifulSoup

def get_news_articles(symbol):
    """
    Scrape news articles related to the given stock symbol.
    """
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for item in soup.find_all('div', class_='Ov(h) Pend(44px) Pstart(25px)'):
            title = item.find('h3').text if item.find('h3') else ''
            link = item.find('a')['href'] if item.find('a') else ''
            description = item.find('p').text if item.find('p') else ''

            if title and link:
                articles.append({
                    'title': title,
                    'url': f"https://finance.yahoo.com{link}",
                    'description': description
                })

        return articles
    except Exception as e:
        print(f"Error scraping news: {e}")
        return []
