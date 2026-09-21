from sentence_transformers import CrossEncoder, SentenceTransformer
import numpy as np
import re


# Stronger NLI model than MiniLM
NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-base"

# Used only for finding relevant evidence
SIMILARITY_MODEL_NAME = "all-MiniLM-L6-v2"


nli_model = CrossEncoder(
    NLI_MODEL_NAME
)

similarity_model = SentenceTransformer(
    SIMILARITY_MODEL_NAME
)


def get_label_mapping():

    labels = nli_model.model.config.id2label

    mapping = {}

    for index, label in labels.items():

        label = label.lower()

        if "entail" in label:
            mapping["SUPPORT"] = index

        elif "contrad" in label:
            mapping["CONTRADICT"] = index

        elif "neutral" in label:
            mapping["UNCERTAIN"] = index

    return mapping


LABEL_MAPPING = get_label_mapping()


def get_probabilities(prediction):

    prediction = np.array(
        prediction
    )

    exp_values = np.exp(
        prediction - np.max(prediction)
    )

    return (
        exp_values /
        exp_values.sum()
    )


def split_sentences(text):

    text = str(text)

    text = re.sub(
        r"\[\.\.\.\]",
        ".",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 20
    ]

    return sentences


def get_relevant_sentences(
    claim,
    sources
):

    candidates = []

    for source in sources[:8]:

        content = source.get(
            "content",
            ""
        )

        # IMPORTANT:
        # Do not use article titles as evidence.
        sentences = split_sentences(
            content
        )

        for sentence in sentences:

            candidates.append({
                "text": sentence,
                "source": source
            })

    if not candidates:

        return []

    claim_embedding = similarity_model.encode(
        claim,
        normalize_embeddings=True
    )

    sentence_texts = [
        item["text"]
        for item in candidates
    ]

    sentence_embeddings = (
        similarity_model.encode(
            sentence_texts,
            normalize_embeddings=True
        )
    )

    similarities = np.dot(
        sentence_embeddings,
        claim_embedding
    )

    for i, similarity in enumerate(
        similarities
    ):

        candidates[i][
            "similarity"
        ] = float(
            similarity
        )

    candidates.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return candidates[:20]


def analyze_news(
    claim,
    sources
):

    if not claim or not claim.strip():

        return {
            "nlp_score": 0,
            "relationship": "UNCERTAIN",
            "reason": "No claim provided.",
            "evidence": ""
        }

    if not sources:

        return {
            "nlp_score": 0,
            "relationship": "UNCERTAIN",
            "reason": "No web evidence available.",
            "evidence": ""
        }

    evidence_list = (
        get_relevant_sentences(
            claim,
            sources
        )
    )

    if not evidence_list:

        return {
            "nlp_score": 0,
            "relationship": "UNCERTAIN",
            "reason": "No relevant evidence found.",
            "evidence": ""
        }

    pairs = [
        (
            item["text"],
            claim
        )
        for item in evidence_list
    ]

    predictions = nli_model.predict(
        pairs
    )

    support_index = LABEL_MAPPING.get(
        "SUPPORT"
    )

    contradict_index = LABEL_MAPPING.get(
        "CONTRADICT"
    )

    uncertain_index = LABEL_MAPPING.get(
        "UNCERTAIN"
    )

    results = []

    for i, prediction in enumerate(
        predictions
    ):

        probabilities = (
            get_probabilities(
                prediction
            )
        )

        support = (
            probabilities[
                support_index
            ]
            if support_index is not None
            else 0
        )

        contradict = (
            probabilities[
                contradict_index
            ]
            if contradict_index is not None
            else 0
        )

        uncertain = (
            probabilities[
                uncertain_index
            ]
            if uncertain_index is not None
            else 0
        )

        similarity = evidence_list[
            i
        ]["similarity"]

        results.append({

            "support": float(
                support
            ),

            "contradict": float(
                contradict
            ),

            "uncertain": float(
                uncertain
            ),

            "similarity": float(
                similarity
            ),

            "text": evidence_list[
                i
            ]["text"],

            "source": evidence_list[
                i
            ]["source"]
        })

    # Ignore evidence that is only weakly
    # related to the claim.
    relevant_results = [
        item
        for item in results
        if item["similarity"] >= 0.35
    ]

    if not relevant_results:

        relevant_results = results[:5]

    # Combine NLI confidence with
    # semantic relevance.

    for item in relevant_results:

        relevance = max(
            0,
            item["similarity"]
        )

        item[
            "support_strength"
        ] = (
            item["support"]
            * relevance
        )

        item[
            "contradict_strength"
        ] = (
            item["contradict"]
            * relevance
        )

    best_support = max(
        relevant_results,
        key=lambda x:
        x["support_strength"]
    )

    best_contradict = max(
        relevant_results,
        key=lambda x:
        x["contradict_strength"]
    )

    support_strength = (
        best_support[
            "support_strength"
        ]
    )

    contradict_strength = (
        best_contradict[
            "contradict_strength"
        ]
    )

    support_valid = (
        best_support["support"] >= 0.65
        and
        best_support["similarity"] >= 0.40
    )

    contradict_valid = (
        best_contradict["contradict"] >= 0.65
        and
        best_contradict["similarity"] >= 0.40
    )

    # Strong contradiction
    if (
        contradict_valid
        and
        contradict_strength >
        support_strength
    ):

        relationship = "CONTRADICT"

        best = best_contradict

        confidence = (
            best_contradict[
                "contradict"
            ]
        )

    # Strong support
    elif (
        support_valid
        and
        support_strength >
        contradict_strength
    ):

        relationship = "SUPPORT"

        best = best_support

        confidence = (
            best_support[
                "support"
            ]
        )

    else:

        relationship = "UNCERTAIN"

        best = max(
            relevant_results,
            key=lambda x:
            x["similarity"]
        )

        confidence = max(
            best["support"],
            best["contradict"],
            best["uncertain"]
        )

    nlp_score = round(
        confidence * 100,
        2
    )

    if relationship == "SUPPORT":

        reason = (
            "The most relevant web evidence "
            "semantically supports the given claim."
        )

    elif relationship == "CONTRADICT":

        reason = (
            "The most relevant web evidence "
            "semantically contradicts the given claim."
        )

    else:

        reason = (
            "The available evidence is relevant, "
            "but it does not provide sufficiently "
            "clear semantic support or contradiction."
        )

    return {

        "nlp_score": nlp_score,

        "relationship": relationship,

        "reason": reason,

        "evidence": best["text"]
    }


def test_nlp():

    claim = input(
        "Enter claim: "
    )

    sources = [
        {
            "title": "Example Evidence",

            "content": input(
                "Enter evidence: "
            )
        }
    ]

    result = analyze_news(
        claim,
        sources
    )

    print(
        "\nNLP Score:",
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
        "Evidence:",
        result["evidence"]
    )


if __name__ == "__main__":

    test_nlp()