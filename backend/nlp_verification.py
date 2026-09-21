from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def detect_claim_type(claim):

    text = claim.lower()

    if any(x in text for x in [
        "dead", "died", "death",
        "killed", "passed away",
        "assassinated"
    ]):
        return "DEATH"

    if any(x in text for x in [
        "cm", "chief minister",
        "prime minister", "president",
        "minister", "ceo"
    ]):
        return "ROLE"

    if any(x in text for x in [
        "son of", "daughter of",
        "father of", "mother of",
        "brother of", "sister of",
        "wife of", "husband of"
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
        "percent", "%", "million",
        "billion", "number", "rate"
    ]):
        return "STATISTIC"

    return "GENERAL"


def similarity_score(claim, evidence):

    try:

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2)
        )

        vectors = vectorizer.fit_transform(
            [claim, evidence]
        )

        score = cosine_similarity(
            vectors[0],
            vectors[1]
        )[0][0]

        return score

    except Exception:
        return 0


def find_phrases(text, phrases):

    text = text.lower()

    found = []

    for phrase in phrases:

        if phrase in text:
            found.append(phrase)

    return found


def relationship_for_death(text):

    contradiction = [
        "is alive",
        "alive and well",
        "still alive",
        "death hoax",
        "death rumor",
        "death rumour",
        "false death",
        "false report of death",
        "not dead",
        "death claim is false",
        "reports of his death are false"
    ]

    support = [
        "was killed",
        "was assassinated",
        "was murdered",
        "was pronounced dead",
        "death confirmed",
        "death was confirmed",
        "has died",
        "passed away",
        "died on"
    ]

    if find_phrases(text, contradiction):
        return "CONTRADICT"

    if find_phrases(text, support):
        return "SUPPORT"

    return "UNCERTAIN"


def relationship_for_role(text):

    contradiction = [
        "is not the",
        "was not the",
        "not currently",
        "no longer",
        "former",
        "replaced by",
        "succeeded by"
    ]

    support = [
        "is the",
        "currently serves as",
        "currently holds",
        "appointed as",
        "serves as",
        "elected as",
        "officially"
    ]

    if find_phrases(text, contradiction):
        return "CONTRADICT"

    if find_phrases(text, support):
        return "SUPPORT"

    return "UNCERTAIN"


def relationship_for_relationship(text):

    contradiction = [
        "not the son of",
        "not his son",
        "not her son",
        "not the daughter of",
        "not his daughter",
        "not her daughter",
        "unrelated to",
        "no relation"
    ]

    support = [
        "son of",
        "daughter of",
        "father of",
        "mother of",
        "brother of",
        "sister of",
        "wife of",
        "husband of"
    ]

    if find_phrases(text, contradiction):
        return "CONTRADICT"

    if find_phrases(text, support):
        return "SUPPORT"

    return "UNCERTAIN"


def relationship_for_general(text):

    contradiction = [
        "false",
        "fact check",
        "incorrect",
        "not true",
        "untrue",
        "fake",
        "hoax",
        "denied",
        "debunked",
        "misleading"
    ]

    support = [
        "confirmed",
        "verified",
        "official statement",
        "officially",
        "according to",
        "reported by"
    ]

    if find_phrases(text, contradiction):
        return "CONTRADICT"

    if find_phrases(text, support):
        return "SUPPORT"

    return "UNCERTAIN"


def analyze_evidence(claim, source):

    title = source.get("title", "")
    content = source.get("content", "")

    evidence = title + " " + content

    claim_type = detect_claim_type(claim)

    if claim_type == "DEATH":

        relationship = relationship_for_death(
            evidence
        )

    elif claim_type == "ROLE":

        relationship = relationship_for_role(
            evidence
        )

    elif claim_type == "RELATIONSHIP":

        relationship = relationship_for_relationship(
            evidence
        )

    else:

        relationship = relationship_for_general(
            evidence
        )

    similarity = similarity_score(
        claim,
        evidence
    )

    priority = similarity * 100

    if relationship == "CONTRADICT":
        priority += 30

    elif relationship == "SUPPORT":
        priority += 20

    if "fact check" in title.lower():
        priority += 30

    if "official" in title.lower():
        priority += 20

    return {
        "source": source,
        "relationship": relationship,
        "similarity": similarity,
        "priority": priority
    }


def analyze_news(claim, trusted_results):

    if not trusted_results:

        return {
            "nlp_score": 0,
            "relationship": "UNCERTAIN",
            "reason": "No trusted web evidence was found.",
            "evidence": None,
            "claim_type": detect_claim_type(claim)
        }

    analyses = []

    for source in trusted_results:

        analyses.append(
            analyze_evidence(
                claim,
                source
            )
        )

    contradictions = [
        item for item in analyses
        if item["relationship"] == "CONTRADICT"
    ]

    supports = [
        item for item in analyses
        if item["relationship"] == "SUPPORT"
    ]

    if contradictions:

        best = max(
            contradictions,
            key=lambda x: x["priority"]
        )

        relationship = "CONTRADICT"

    elif supports:

        best = max(
            supports,
            key=lambda x: x["priority"]
        )

        relationship = "SUPPORT"

    else:

        best = max(
            analyses,
            key=lambda x: x["priority"]
        )

        relationship = "UNCERTAIN"

    score = best["similarity"] * 100

    if relationship == "CONTRADICT":

        reason = (
            "Relevant trusted web evidence "
            "contradicts the claim."
        )

    elif relationship == "SUPPORT":

        reason = (
            "Relevant trusted web evidence "
            "supports the claim."
        )

    else:

        reason = (
            "Trusted web evidence was found, "
            "but it does not clearly support "
            "or contradict the claim."
        )

    return {
        "nlp_score": round(score, 2),
        "relationship": relationship,
        "reason": reason,
        "evidence": best["source"],
        "claim_type": detect_claim_type(claim)
    }


if __name__ == "__main__":

    from web_verification import search_web

    claim = input("Enter news or claim: ")

    web_result = search_web(claim)

    result = analyze_news(
        claim,
        web_result["trusted_results"]
    )

    print("\nClaim Type:", result["claim_type"])
    print("NLP Score:", result["nlp_score"])
    print("Relationship:", result["relationship"])
    print("Reason:", result["reason"])

    if result["evidence"]:
        print(
            "Evidence:",
            result["evidence"]["title"]
        )