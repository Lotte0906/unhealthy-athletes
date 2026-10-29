MEDAL_TYPES = ("Bronze", "Silver", "Gold")


def get_medal_winners(
    data: pd.DataFrame,
    medal_types: tuple[str, ...] = MEDAL_TYPES,
) -> pd.DataFrame:
    """Return rows where an athlete won one of the specified medals."""
    invalid_types = set(medal_types) - set(MEDAL_TYPES)
    if invalid_types:
        raise ValueError(
            f"Invalid medal types: {sorted(invalid_types)}. "
            f"Choose from {MEDAL_TYPES}."
        )

    return data[data[list(medal_types)].any(axis=1)].copy()


def filter_by_year_range(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """Return rows within an inclusive year range."""
    if start_year > end_year:
        raise ValueError("start_year must be <= end_year.")

    return data[data["Year"].between(start_year, end_year)].copy()

