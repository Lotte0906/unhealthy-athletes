import pandas as pd
from dateutil.relativedelta import relativedelta


def convert_dict_to_pd_df(list_of_dicts: list[dict]) -> pd.DataFrame:
    """Convert a list of person dictionaries into a DataFrame."""
    try:
        return pd.DataFrame(list_of_dicts)
    except Exception as e:
        print(f"convert_dict_to_pd_df failed: {type(e).__name__}: {e}")
        raise



def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Left-merge Olympic rows with biography data using athlete IDs."""
    try:
        df = df1.merge(
            df2,
            on="ID",
            how="left",
            validate="many_to_one"
        )
    except Exception as e:
        print(f"merge_dataframes failed: {type(e).__name__}: {e}")
        raise

    if "name" in df.columns:
        df = df.drop(columns=["name"])

    return df



def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Wikidata dates, preserving originals and recording date issues."""
    import re
    from datetime import date, datetime

    df = df.copy()

    def parse_date(value):
        if value is None or value == "":
            return None, None

        if not isinstance(value, str):
            if pd.isna(value):
                return None, None
            if isinstance(value, (date, datetime)):
                return value.date() if isinstance(value, datetime) else value, None
            return None, "Unsupported date type"

        match = re.fullmatch(
            r"([+-]?\d+)-(\d{2})-(\d{2})(?:T.*)?",
            value,
        )

        if not match:
            return None, "Unexpected date format"

        year, month, day = map(int, match.groups())

        if not 1 <= year <= 9999:
            return None, "Unsupported year"

        issues = []

        if month == 0:
            issues.append("Missing month")
            month = 1
        elif not 1 <= month <= 12:
            issues.append("Invalid month")
            month = 1

        if day == 0:
            issues.append("Missing day")
            day = 1
        else:
            try:
                date(year, month, day)
            except ValueError:
                issues.append("Invalid day")
                day = 1

        return date(year, month, day), "; ".join(issues) or None

    for column in ("birthdate", "deathdate"):
        df[f"{column}_original"] = df[column]

        parsed = df[column].map(parse_date)

        df[column] = parsed.map(lambda result: result[0])
        df[f"{column}_date_issue"] = parsed.map(lambda result: result[1])

    return df



def calculate_age_per_row(row: pd.Series, currentdate) -> int | None:
    """Calculate age using birthdate, deathdate, and known life status."""
    try:
        birthdate = row["birthdate"]
        deathdate = row["deathdate"]
        status = row.get("status")

        if pd.isna(birthdate):
            return None

        if pd.notna(deathdate):
            end_date = deathdate

        elif status == "Alive":
            end_date = currentdate

        else:
            # Dead with no usable deathdate, or unknown life status.
            return None

        return relativedelta(end_date, birthdate).years

    except Exception as e:
        name = row.get("Name", "<unknown>")
        print(
            f"calculate_age_per_row failed for {name}: "
            f"{type(e).__name__}: {e}"
        )
        raise



def add_age(df: pd.DataFrame, currentdate) -> pd.DataFrame:
    """Add an integer age column; retain missing ages as pandas nullable integers."""
    df = df.copy()
    try:
        df["age"] = df.apply(
            lambda row: calculate_age_per_row(row, currentdate),
            axis=1,
        )
        df["age"] = df["age"].astype("Int64")
    except Exception as e:
        print(f"add_age failed: {type(e).__name__}: {e}")
        raise

    return df
