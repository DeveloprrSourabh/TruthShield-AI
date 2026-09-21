from ais import classify_news, valid_detectors
from web_search import search_web
from nlp import analyze_news


def make_decision(
    ais_result,
    web_result,
    nlp_result
):

    ais_score = ais_result.get(
        "ais_score",
        0
    )

    web_score = web_result.get(
        "web_score",
        0
    )

    nlp_score = nlp_result.get(
        "nlp_score",
        0
    )

    relationship = nlp_result.get(
        "relationship",
        "UNCERTAIN"
    )

    # Strong semantic contradiction
    if (
        relationship == "CONTRADICT"
        and nlp_score >= 70
    ):
        result = "FAKE"

    # Strong semantic support
    elif (
        relationship == "SUPPORT"
        and nlp_score >= 70
    ):
        result = "REAL"

    else:
        result = "UNCERTAIN"

    return {
        "result": result,
        "ais_score": round(
            ais_score,
            2
        ),
        "web_score": round(
            web_score,
            2
        ),
        "nlp_score": round(
            nlp_score,
            2
        ),
        "relationship": relationship,
        "reason": nlp_result.get(
            "reason",
            "Insufficient evidence."
        ),
        "evidence": nlp_result.get(
            "evidence",
            ""
        ),
        "sources": web_result.get(
            "sources",
            []
        )
    }

def verify_news(news):

    # AIS
    ais_result, ais_score = classify_news(
        news,
        valid_detectors
    )

    ais_data = {
        "ais_score": ais_score,
        "result": ais_result
    }

    # Web Search
    web_result = search_web(
        news
    )

    # NLP Verification
    nlp_result = analyze_news(
        news,
        web_result.get(
            "sources",
            []
        )
    )

    # Final Decision
    return make_decision(
        ais_data,
        web_result,
        nlp_result
    )


def test_decision():

    news = input(
        "Enter news: "
    )

    result = verify_news(
        news
    )

    print(
        "\n========== TruthShield AI =========="
    )

    print(
        "Result:",
        result["result"]
    )

    print(
        "AIS Score:",
        result["ais_score"]
    )

    print(
        "Web Score:",
        result["web_score"]
    )

    print(
        "NLP Score:",
        result["nlp_score"]
    )

    print(
        "Relationship:",
        result["relationship"]
    )

    print(
        "Reason:",
        result["reason"]
    )

    print(
        "\nEvidence:"
    )

    print(
        result["evidence"]
    )

    print(
        "\nSources:"
    )

    for source in result["sources"]:

        print(
            source.get(
                "title",
                ""
            )
        )

        print(
            source.get(
                "url",
                ""
            )
        )

        print()


if __name__ == "__main__":

    test_decision()