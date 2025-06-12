import requests
from bs4 import BeautifulSoup

def scrape_data(event=None, context=None):
    url = "https://u.today/search/node?keys=bitcoin"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Request failed: {e}"
        }

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("div", class_="news__item")

    if not articles:
        return {
            "statusCode": 200,
            "body": "No articles found on the page"
        }

    results = []
    for article in articles:
        title_tag = article.find("div", class_="news__item-title")
        date_tag = article.find("div", class_="humble")
        author_tag = article.find("div", class_="humble humble--author")
        link_tag = title_tag.find("a") if title_tag else None

        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        date = date_tag.get_text(strip=True) if date_tag else "N/A"
        author = author_tag.get_text(strip=True) if author_tag else "N/A"
        link = "https://u.today" + link_tag['href'] if link_tag else "N/A"

        results.append({
            "date": date,
            "title": title,
            "author": author,
            "link": link
        })

    return {
        "statusCode": 200,
        "body": results
    }
