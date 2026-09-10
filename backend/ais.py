import re
import pandas as pd
from collections import Counter

THRESHOLD = 0.10

def clean_news(news):
    news = str(news).lower()
    news = re.sub(r"[^\w\s]", "", news)
    return news.split()

def get_phrases(news):
    words = clean_news(news)

    phrases = []

    for i in range(len(words) - 1):
        phrase = words[i] + " " + words[i + 1]
        phrases.append(phrase)

    return phrases


stop_words = {
    "your", "really", "something", "says", "himself",
    "course", "actually", "doing", "ever", "nothing",
    "thing", "went", "would", "could", "there", "their",
    "about", "after", "before", "which", "while", "where",
    "what", "when", "with", "from", "this", "that",
    "have", "has", "been", "were", "they", "them",
    "into", "than", "then", "also", "just", "more"
}


from collections import Counter

def generate_detectors(fake_news, real_news):
    fake_count = Counter()
    real_count = Counter()

    for news in fake_news:
        for word in clean_news(news):
            if len(word) > 3 and word not in stop_words:
                fake_count[word] += 1

    for news in real_news:
        for word in clean_news(news):
            if len(word) > 3 and word not in stop_words:
                real_count[word] += 1

    detectors = []

    for word, count in fake_count.most_common():
        if count >= 3 and count > real_count[word]:
            detectors.append(word)

        if len(detectors) == 100:
            break

    return detectors


def negative_selection(detectors, fake_news, real_news):

    valid_detectors = []

    total_fake_articles = len(fake_news)
    total_real_articles = len(real_news)

    for detector in detectors:

        fake_matches = 0
        real_matches = 0

        for news in fake_news:
            words = set(clean_news(news))

            if detector in words:
                fake_matches += 1

        for news in real_news:
            words = set(clean_news(news))

            if detector in words:
                real_matches += 1

        fake_ratio = fake_matches / total_fake_articles
        real_ratio = real_matches / total_real_articles

        if fake_ratio >= 0.05 and real_ratio < 0.05:
            valid_detectors.append(detector)

    return valid_detectors
def calculate_affinity(news, detectors):

    words = set(clean_news(news))

    matches = 0

    for detector in detectors:
        if detector in words:
            matches += 1

    if len(detectors) == 0:
        return 0

    return matches / len(detectors)

def get_matched_detectors(news, detectors):
    words = set(clean_news(news))

    matched = []

    for detector in detectors:
        if detector in words:
            matched.append(detector)

    return matched


def classify_news(news, detectors):

    affinity = calculate_affinity(
        news,
        detectors
    )
    if affinity >= THRESHOLD:
        result = "FAKE"
    else:
        result = "REAL"

    ais_score  = affinity * 100

    return result, ais_score 


fake_data = pd.read_csv("Fake.csv")
real_data = pd.read_csv("True.csv")


fake_news = fake_data["text"].dropna().head(500).tolist()
real_news = real_data["text"].dropna().head(500).tolist()


candidate_detectors = generate_detectors(
    fake_news,
    real_news
)


valid_detectors = negative_selection(
    candidate_detectors,
    fake_news,
    real_news
)

if __name__ == "__main__":

    print("Fake articles:", len(fake_news))
    print("Real articles:", len(real_news))
    print("Candidate detectors:", len(candidate_detectors))
    print("Valid detectors:", len(valid_detectors))
    print("Valid detectors:", valid_detectors)

    print("\nTesting Fake News:")

    fake_test = fake_data["text"].dropna().iloc[0]

    result, ais_score = classify_news(
        fake_test,
        valid_detectors
    )

    print("Result:", result)
    print("AIS Score:", ais_score, "%")

    print("\nTesting Real News:")

    real_test = real_data["text"].dropna().iloc[0]

    result, ais_score = classify_news(
        real_test,
        valid_detectors
    )

    matched = get_matched_detectors(
        real_test,
        valid_detectors
    )

    print("Result:", result)
    print("AIS Score:", ais_score, "%")
    print("Matched Detectors:", matched)
    print("Matches:", len(matched), "/", len(valid_detectors))
