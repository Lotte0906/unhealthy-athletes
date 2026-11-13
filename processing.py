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
    """Parse Wikidata date strings while preserving invalid/missing values.

    errors='coerce' turns unparseable dates into NaT. This is convenient, but
    it can also turn legitimate very old dates into missing values on pandas
    versions using nanosecond timestamps.
    """
    df = df.copy()

    for column in ("birthdate", "deathdate"):
        try:
            # Parse to Python date objects so historical dates outside pandas'
            # nanosecond timestamp range can be represented.
            def parse_date(value):
                if pd.isna(value) or value == "":
                    return None
                if isinstance(value, str):
                    # Wikidata values usually look like '+1875-03-14T00:00:00Z'.
                    cleaned = value.lstrip("+")
                    return pd.Timestamp(cleaned[:10]).date()
                return pd.Timestamp(value).date()

            df[column] = df[column].map(parse_date)
        except Exception as e:
            print(f"convert_dates failed for column '{column}': {type(e).__name__}: {e}")
            raise

    return df


def calculate_age_per_row(row: pd.Series, currentdate) -> int | None:
    """Calculate completed years of age, or None when birthdate is missing."""
    try:
        birthdate = row["birthdate"]
        deathdate = row["deathdate"]

        if pd.isna(birthdate):
            return None

        end_date = deathdate if pd.notna(deathdate) else currentdate
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
