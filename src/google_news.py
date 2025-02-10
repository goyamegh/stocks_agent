import requests
from bedrock_claude import summarize_news_with_claude

def build_news_article(item):
    """
    Constructs a detailed article representation from a Google Custom Search API result item.
    Combines the source, title, and snippet into one string.
    """
    source = item.get('displayLink', 'News')
    title = item.get('title', 'No title')
    snippet = item.get('snippet', '')
    # Combine into a detailed article text.
    article = f"Source: {source}\nTitle: {title}\nDetails: {snippet}"
    return article

def fetch_google_news(query, api_key, cx, num=3):
    """
    Fetches the top 'num' news articles for a given query using the Google Custom Search API.
    Returns a list of detailed news articles.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': num,
        'sort': 'date'  # sorted by date if supported by your CSE
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        articles = []
        if 'items' in results:
            for item in results['items']:
                articles.append(build_news_article(item))
        return articles
    except Exception as exc:
        print(f"Google News API error for query '{query}':", exc)
        return []

def fetch_google_news_summary(query, api_key, cx, num=3, model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0", temperature=0.7):
    """
    Fetches detailed news articles using the Google Custom Search API, and then for each article
    uses the Claude model via Amazon Bedrock to generate a concise one-line summary. The individual
    summaries are combined into a single string, with each summary on a new line.

    Parameters:
      - query: The search query (for example, a stock ticker)
      - api_key: Your Google API key
      - cx: Your Custom Search Engine ID
      - num: Number of articles to fetch (default is 3)
      - model_id: The identifier for your Claude model
      - temperature: The temperature setting for the model generation

    Returns:
      A string containing individual summaries for each article, separated by newlines.
    """
    articles = fetch_google_news(query, api_key, cx, num)
    if articles:
        summaries = []
        # Process each article individually.
        for article in articles:
            summary = summarize_news_with_claude([article], model_id=model_id, temperature=temperature)
            summaries.append(summary)
        # Combine individual summaries into one string.
        final_summary = "\n".join(summaries)
        return final_summary
    return "No relevant news found." 