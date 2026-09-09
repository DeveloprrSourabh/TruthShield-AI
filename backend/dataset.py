import pandas as pd

fake = pd.read_csv("Fake.csv")
real = pd.read_csv("True.csv")

print("Fake news:", len(fake))
print("Real news:", len(real))

print(fake.columns)
print(real.columns)

print(fake.head(2))
print(real.head(2))