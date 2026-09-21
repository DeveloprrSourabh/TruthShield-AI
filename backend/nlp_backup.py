from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from web_search import search_news


def get_claim_keywords(claim):

    stop_words = {
        "the", "a", "an", "is", "was", "were",
        "in", "on", "of", "to", "and", "for"
    }

    words = claim.lower().split()

    keywords = []

    for word in words:
        word = word.strip(".,!?")

        if word not in stop_words:
            keywords.append(word)

    return keywords


def calculate_similarity(claim, evidence):

    documents = [claim, evidence]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(vectors[0], vectors[1])

    return similarity[0][0]


def classify_relationship(claim, evidence, similarity_score):

    claim_lower = claim.lower()
    evidence_lower = evidence.lower()

    support_words = {
        "won": ["won", "defeated", "beat", "victory", "champions"],
        "increased": ["increased", "rose", "grew", "higher"],
        "approved": ["approved", "accepted", "cleared"],
        "launched": ["launched", "introduced", "released"]
    }

    contradiction_words = {
        "won": ["lost", "failed", "did not win"],
        "increased": ["decreased", "fell", "dropped", "declined"],
        "approved": ["rejected", "denied", "not approved"],
        "launched": ["cancelled", "not launched"]
    }

    for claim_word, words in contradiction_words.items():

        if claim_word in claim_lower:

            for word in words:

                if word in evidence_lower:
                    return "CONTRADICT"

    for claim_word, words in support_words.items():

        if claim_word in claim_lower:

            for word in words:

                if word in evidence_lower:
                    return "SUPPORT"

    if similarity_score >= 0.5:
        return "UNCERTAIN"

    return "UNCERTAIN"


def compare_with_evidence(claim, trusted_results):

    best_score = 0
    best_evidence = None
    best_relationship = "UNCERTAIN"

    for result in trusted_results:

        evidence = result["content"]

        score = calculate_similarity(
            claim,
            evidence
        )

        relationship = classify_relationship(
            claim,
            evidence,
            score
        )

        if score > best_score:

            best_score = score
            best_evidence = result
            best_relationship = relationship

    return best_score, best_evidence, best_relationship


def analyze_news(claim, trusted_results):

    if not trusted_results:

        return {
            "nlp_score": 0,
            "relationship": "UNCERTAIN",
            "reason": "No trusted evidence was found.",
            "evidence": None
        }

    score, best_evidence, relationship = compare_with_evidence(
        claim,
        trusted_results
    )

    if relationship == "SUPPORT":

        reason = "The evidence supports the claim."

    elif relationship == "CONTRADICT":

        reason = "The evidence contradicts the claim."

    else:

        reason = "The evidence is related to the claim but does not clearly support or contradict it."

    return {
        "nlp_score": round(score * 100, 2),
        "relationship": relationship,
        "reason": reason,
        "evidence": best_evidence
    }


if __name__ == "__main__":

    claim = input("Enter news or claim: ")

    results, trusted_results = search_news(claim)

    print("\nTrusted sources found:", len(trusted_results))

    result = analyze_news(
        claim,
        trusted_results
    )

    print("\n========== NLP RESULT ==========")
    print("NLP Score:", result["nlp_score"])
    print("Relationship:", result["relationship"])
    print("Reason:", result["reason"])

    if result["evidence"]:

        print("\n========== BEST EVIDENCE ==========")
        print("Title:", result["evidence"]["title"])
        print("URL:", result["evidence"]["url"])
        print("Content:", result["evidence"]["content"])