def get_top_candidates(
    ranking_df,
    top_n=3
):
    """
    Return the top N candidates based on
    Final Score.
    """

    if ranking_df.empty:
        return ranking_df

    # Make sure highest scores come first
    ranking_df = ranking_df.sort_values(
        by="Final Score",
        ascending=False
    )

    # Select top N
    top_candidates = ranking_df.head(
        top_n
    ).copy()

    # Reset ranking
    top_candidates = top_candidates.reset_index(
        drop=True
    )

    # Make sure Rank is correct
    if "Rank" in top_candidates.columns:

        top_candidates["Rank"] = (
            top_candidates.index + 1
        )

    return top_candidates