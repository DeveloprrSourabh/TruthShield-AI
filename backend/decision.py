from ais import classify_news, valid_detectors
from web_search import search_news
from nlp import analyze_news


def make_decision(ais_score, trusted_results, nlp_result):

    relationship = nlp_result["relationship"]
    web_sources = len(trusted_results)

    if web_sources == 0:

        result = "UNCERTAIN"
        reason = "No trusted web evidence was found."

    elif relationship == "CONTRADICT":

        result = "FAKE"
        reason = "Trusted web evidence contradicts the claim."

    elif relationship == "SUPPORT":

        if ais_score < 10:
            result = "REAL"
            reason = "Trusted web evidence supports the claim and AIS found low suspicious-pattern matching."
        else:
            result = "UNCERTAIN"
            reason = "Web evidence supports the claim, but AIS found suspicious patterns."

    else:

        if ais_score >= 10:
            result = "FAKE"
            reason = "The evidence is uncertain and AIS found suspicious patterns."
        else:
            result = "UNCERTAIN"
            reason = "The available evidence is not sufficient for a clear decision."

    return {
        "result": result,
        "ais_score": ais_score,
        "web_sources": web_sources,
        "nlp_score": nlp_result["nlp_score"],
        "relationship": relationship,
        "reason": reason,
        "sources": trusted_results
    }

def verify_news(news):

    # AIS verification
    _, ais_score = classify_news(
        news,
        valid_detectors
    )

    # Web verification
    results, trusted_results = search_news(news)

    # NLP verification
    nlp_result = analyze_news(
        news,
        trusted_results
    )

    # Final decision
    final_result = make_decision(
        ais_score,
        trusted_results,
        nlp_result
    )

    return final_result


if __name__ == "__main__":

    news = input("Enter news or claim: ")

    result = verify_news(news)

    print("\n========== FINAL RESULT ==========")
    print("Result:", result["result"])
    print("AIS Score:", result["ais_score"])
    print("Web Sources:", result["web_sources"])
    print("NLP Score:", result["nlp_score"])
    print("Relationship:", result["relationship"])
    print("Reason:", result["reason"])