from recommender import get_recommendation


test_scores = [
    90,
    75,
    60,
    40
]


print("\n====================================")
print("       RECOMMENDATION TEST")
print("====================================")


for score in test_scores:

    recommendation = get_recommendation(
        score
    )

    print(
        f"Score: {score}%"
        f" → {recommendation}"
    )


print("====================================")