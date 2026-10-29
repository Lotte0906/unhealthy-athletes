import pandas as pd

def get_first_n_names(data: pd.DataFrame,n: int = 20) -> list[str]:
    """Return the first n unique names in order of appearance."""
    if n < 0:
        raise ValueError("n must be non-negative.")

    return data["Name"].drop_duplicates().head(n).tolist()


def filter_by_names(data: pd.DataFrame, names: list[str]|int) -> pd.DataFrame:
    """Return rows belonging to the specified names."""
    if isinstance(names, int):
        names = get_first_n_names(data, names)
        
    return data[data["Name"].isin(names)].copy()