import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=api_key)


trusted_domains = [
    "reuters.com",
    "bbc.com",
    "thehindu.com",
    "indianexpress.com",
    "apnews.com",
    "ndtv.com",
    "tribuneindia.com",
    "gov.in",
    "nic.in"
]


def is_trusted_source(url):

    for domain in trusted_domains:

        if domain in url:
            return True

    return False


def search_news(query, max_results=5):

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=max_results
    )

    results = []
    trusted_results = []

    for item in response["results"]:

        trusted = is_trusted_source(item["url"])

        result = {
            "title": item["title"],
            "url": item["url"],
            "content": item["content"],
            "trusted": trusted
        }

        results.append(result)

        if trusted:
            trusted_results.append(result)

    return results, trusted_results


if __name__ == "__main__":

    news = input("Enter news or claim to search: ")

    results, trusted_results = search_news(news)
    print("\n========== TRUSTED EVIDENCE ==========")

    if len(trusted_results) == 0:

        print("No trusted source found.")

    else:

        for i, result in enumerate(trusted_results, start=1):

            print("\nEvidence", i)
            print("Source:", result["title"])
            print("URL:", result["url"])
            print("Content:", result["content"][:500])