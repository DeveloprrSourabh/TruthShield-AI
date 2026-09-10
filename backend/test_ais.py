import pandas as pd

from ais import classify_news, valid_detectors


fake_data = pd.read_csv("Fake.csv")
real_data = pd.read_csv("True.csv")


fake_news = fake_data["text"].dropna().iloc[500:600].tolist()
real_news = real_data["text"].dropna().iloc[500:600].tolist()


TP = 0
TN = 0
FP = 0
FN = 0


# Test Fake News
for news in fake_news:

    result, score = classify_news(
        news,
        valid_detectors
    )

    if result == "FAKE":
        TP += 1
    else:
        FN += 1


# Test Real News
for news in real_news:

    result, score = classify_news(
        news,
        valid_detectors
    )

    if result == "FAKE":
        FP += 1
    else:
        TN += 1


total = TP + TN + FP + FN

accuracy = (TP + TN) / total * 100


print("========== AIS MODEL EVALUATION ==========")

print("Fake News Tested :", len(fake_news))
print("Real News Tested :", len(real_news))

print("\nConfusion Matrix:")
print("TP:", TP)
print("FN:", FN)
print("FP:", FP)
print("TN:", TN)

print("\nAccuracy:", accuracy, "%")