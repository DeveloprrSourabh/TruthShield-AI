import pandas as pd

from ais import classify_news, valid_detectors


fake_data = pd.read_csv("Fake.csv")
real_data = pd.read_csv("True.csv")

fake_news = fake_data["text"].dropna().iloc[500:1000].tolist()
real_news = real_data["text"].dropna().iloc[500:1000].tolist()


thresholds = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]


for threshold in thresholds:

    TP = 0
    TN = 0
    FP = 0
    FN = 0

    for news in fake_news:

        result, score = classify_news(
            news,
            valid_detectors
        )

        if score >= threshold * 100:
            TP += 1
        else:
            FN += 1


    for news in real_news:

        result, score = classify_news(
            news,
            valid_detectors
        )

        if score >= threshold * 100:
            FP += 1
        else:
            TN += 1


    total = TP + TN + FP + FN

    accuracy = (TP + TN) / total * 100

    precision = TP / (TP + FP) * 100 if (TP + FP) != 0 else 0

    recall = TP / (TP + FN) * 100 if (TP + FN) != 0 else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) != 0
        else 0
    )


    print("\nThreshold:", threshold)

    print("TP:", TP)
    print("TN:", TN)
    print("FP:", FP)
    print("FN:", FN)

    print("Accuracy :", round(accuracy, 2), "%")
    print("Precision:", round(precision, 2), "%")
    print("Recall   :", round(recall, 2), "%")
    print("F1-Score :", round(f1, 2), "%")