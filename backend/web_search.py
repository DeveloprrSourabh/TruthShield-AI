import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

API_KEY = os.getenv("TAVILY_API_KEY")

if not API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file")

client = TavilyClient(api_key=API_KEY)


TRUSTED_DOMAINS = {
    "reuters.com",
    "bbc.com",
    "apnews.com",

    "thehindu.com",
    "indianexpress.com",
    "ndtv.com",
    "timesofindia.indiatimes.com",
    "hindustantimes.com",
    "theprint.in",

    "gov.in",
    "nic.in",

    "nasa.gov",
    "noaa.gov",
    "esa.int",
    "who.int",
    "nih.gov",
    "cdc.gov",

    "nature.com",
    "science.org",
    "britannica.com"
}


def get_domain(url):

    try:
        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


def is_trusted_source(url):

    domain = get_domain(url)

    for trusted in TRUSTED_DOMAINS:

        if domain == trusted or domain.endswith("." + trusted):
            return True

    return False


def search_web(claim):

    if not claim or not claim.strip():

        return {
            "web_score": 0,
            "evidence": "",
            "sources": []
        }

    queries = [
        claim,
        f'"{claim}" fact check',
        f'"{claim}" evidence'
    ]

    all_results = []
    seen_urls = set()

    for query in queries:

        try:

            response = client.search(
                query=query,
                search_depth="basic",
                max_results=8
            )

            results = response.get(
                "results",
                []
            )

            for result in results:

                url = result.get("url", "")

                if not url:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                all_results.append({
                    "title": result.get("title", ""),
                    "url": url,
                    "content": result.get("content", ""),
                    "score": float(
                        result.get("score", 0) or 0
                    ),
                    "trusted": is_trusted_source(url)
                })

        except Exception as e:

            print("Tavily search error:", e)

    all_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    trusted_results = [
        result
        for result in all_results
        if result["trusted"] and result["score"] >= 0.20
    ]

    trusted_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not trusted_results:

        return {
            "web_score": 0,
            "evidence": "",
            "sources": all_results
        }

    best_score = trusted_results[0]["score"]

    source_count = min(
        len(trusted_results),
        5
    )

    web_score = min(
        100,
        (best_score * 50) + (source_count * 10)
    )

    return {
        "web_score": round(web_score, 2),
        "evidence": trusted_results[0]["content"],
        "sources": trusted_results
    }


def test_web_search():

    claim = input("Enter news claim: ")

    result = search_web(claim)

    print("\nWeb Score:", result["web_score"])

    print("\nEvidence:")
    print(result["evidence"])

    print("\nSources:")

    for source in result["sources"]:

        print("\nTitle:", source["title"])
        print("URL:", source["url"])
        print("Score:", source["score"])


if __name__ == "__main__":
    test_web_search()