import os
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError("TAVILY_API_KEY is missing in .env")

client = TavilyClient(api_key=api_key)


TRUSTED_DOMAINS = [
    "reuters.com",
    "bbc.com",
    "apnews.com",
    "thehindu.com",
    "indianexpress.com",
    "ndtv.com",
    "timesofindia.indiatimes.com",
    "hindustantimes.com",
    "theprint.in",
    "tribuneindia.com",
    "telegraphindia.com",
    "economictimes.indiatimes.com",
    "gov.in",
    "nic.in",
    "ox.ac.uk",
    "nitp.ac.in"
]


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text


def is_trusted_source(url):

    try:
        hostname = urlparse(url).netloc.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        for domain in TRUSTED_DOMAINS:

            if hostname == domain or hostname.endswith("." + domain):
                return True

    except Exception:
        pass

    return False


def detect_claim_type(claim):

    text = claim.lower()

    if any(x in text for x in [
        "dead", "died", "death", "killed",
        "passed away", "assassinated"
    ]):
        return "DEATH"

    if any(x in text for x in [
        "cm", "chief minister", "prime minister",
        "president", "minister", "ceo",
        "is the head", "currently"
    ]):
        return "ROLE"

    if any(x in text for x in [
        "son of", "daughter of", "father of",
        "mother of", "brother of", "sister of",
        "wife of", "husband of", "married to"
    ]):
        return "RELATIONSHIP"

    if any(x in text for x in [
        "better than", "worse than",
        "greater than", "less than",
        "best", "worst", "compared to",
        "superior to", "inferior to"
    ]):
        return "COMPARISON"

    if any(x in text for x in [
        "people", "killing", "deaths",
        "percent", "%", "million", "billion",
        "rate", "number of"
    ]):
        return "STATISTIC"

    return "GENERAL"


def extract_entities(claim):

    text = claim.strip()

    patterns = [
        r"(.+?)\s+is better than\s+(.+)",
        r"(.+?)\s+is worse than\s+(.+)",
        r"(.+?)\s+is the son of\s+(.+)",
        r"(.+?)\s+is the daughter of\s+(.+)",
        r"(.+?)\s+is the father of\s+(.+)",
        r"(.+?)\s+is the mother of\s+(.+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return [
                match.group(1).strip(),
                match.group(2).strip()
            ]

    return []


def build_queries(claim):

    claim_type = detect_claim_type(claim)
    entities = extract_entities(claim)

    queries = []

    if claim_type == "COMPARISON" and len(entities) == 2:

        first = entities[0]
        second = entities[1]

        queries.extend([
            f"{first} placement statistics",
            f"{second} placement statistics",
            f"{first} academics education",
            f"{second} academics education",
            f"{first} {second} comparison"
        ])

    elif claim_type == "DEATH":

        queries.extend([
            claim,
            f"{claim} fact check",
            f"{claim} death confirmed",
            f"{claim} alive",
            f"{claim} death hoax"
        ])

    elif claim_type == "ROLE":

        queries.extend([
            claim,
            f"{claim} current position",
            f"{claim} official",
            f"{claim} fact check"
        ])

    elif claim_type == "RELATIONSHIP":

        queries.extend([
            claim,
            f"{claim} family",
            f"{claim} relationship",
            f"{claim} fact check"
        ])

    elif claim_type == "STATISTIC":

        queries.extend([
            claim,
            f"{claim} latest statistics",
            f"{claim} official data",
            f"{claim} fact check"
        ])

    else:

        queries.extend([
            claim,
            f"{claim} fact check",
            f"{claim} verified",
            f"{claim} confirmed"
        ])

    return list(dict.fromkeys(queries))


def calculate_relevance(query, title, content):

    query_words = set(
        word for word in clean_text(query).split()
        if len(word) > 2
    )

    if not query_words:
        return 0

    title_words = set(clean_text(title).split())
    content_words = set(clean_text(content).split())

    title_matches = len(query_words & title_words)
    content_matches = len(query_words & content_words)

    score = (
        title_matches * 3 +
        content_matches
    ) / (len(query_words) * 4)

    return min(score, 1)


def search_web(claim):

    queries = build_queries(claim)

    all_results = []
    seen_urls = set()

    for query in queries:

        try:

            response = client.search(
                query=query,
                search_depth="basic",
                max_results=5
            )

        except Exception:
            continue

        for item in response.get("results", []):

            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            trusted = is_trusted_source(url)

            relevance = calculate_relevance(
                query,
                title,
                content
            )

            result = {
                "title": title,
                "url": url,
                "content": content,
                "trusted": trusted,
                "relevance": round(relevance * 100, 2)
            }

            all_results.append(result)

    all_results.sort(
        key=lambda x: (
            x["trusted"],
            x["relevance"]
        ),
        reverse=True
    )

    trusted_results = [
        item for item in all_results
        if item["trusted"] and item["relevance"] >= 10
    ]

    if not trusted_results:

        trusted_results = [
            item for item in all_results
            if item["trusted"]
        ][:10]

    return {
        "claim_type": detect_claim_type(claim),
        "queries": queries,
        "results": all_results[:20],
        "trusted_results": trusted_results[:10]
    }


if __name__ == "__main__":

    claim = input("Enter news or claim: ")

    result = search_web(claim)

    print("\nClaim Type:", result["claim_type"])

    print(
        "Trusted Sources:",
        len(result["trusted_results"])
    )

    for i, source in enumerate(
        result["trusted_results"],
        start=1
    ):

        print("\n", i)
        print("Title:", source["title"])
        print("URL:", source["url"])
        print("Relevance:", source["relevance"])