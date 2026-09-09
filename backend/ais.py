import re
import pandas as pd
from collections import Counter


def clean_news(news):
    news = str(news).lower()
    news = re.sub(r"[^\w\s]", "", news)
    return news.split()


from collections import Counter

def generate_detectors(fake_news, real_news):
    fake_count = Counter()
    real_count = Counter()

    for news in fake_news:
        for word in clean_news(news):
            if len(word) > 3:
                fake_count[word] += 1

    for news in real_news:
        for word in clean_news(news):
            if len(word) > 3:
                real_count[word] += 1

    detectors = []

    for word, count in fake_count.most_common():
        if count >= 3 and count > real_count[word]:
            detectors.append(word)

        if len(detectors) == 100:
            break

    return detectors


def negative_selection(detectors, real_news):
    return detectors


def calculate_affinity(news, detectors):

    words = set(clean_news(news))

    matches = 0

    for detector in detectors:
        if detector in words:
            matches += 1

    if matches == 0:
        return 0

    return matches / len(words)


def classify_news(news, detectors):

    affinity = calculate_affinity(
        news,
        detectors
    )

    if affinity >= 0.12:
        result = "FAKE"
    else:
        result = "REAL"

    confidence = affinity * 100

    return result, confidence


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
    real_news
)


print("Fake articles:", len(fake_news))
print("Real articles:", len(real_news))
print("Candidate detectors:", len(candidate_detectors))
print("Valid detectors:", len(valid_detectors))

print("\nTesting Fake News:")
fake_test = fake_data["text"].dropna().iloc[0]

result, confidence = classify_news(
    fake_test,
    valid_detectors
)

print("Result:", result)
print("Confidence:", confidence, "%")


print("\nTesting Real News:")
real_test = real_data["text"].dropna().iloc[0]

result, confidence = classify_news(
    real_test,
    valid_detectors
)

print("Result:", result)
print("Confidence:", confidence, "%")