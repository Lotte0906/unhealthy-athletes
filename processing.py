import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def convert_dict_to_pd_df(list_of_dicts):
    return pd.DataFrame(list_of_dicts)

def merge_dataframes(df1, df2):
    df = df1.merge(
        df2,
        left_on = 'Name',
        right_on = 'name',
        how = 'left'
    )
    df = df.drop(['name'], axis = 1)
    return df

def convert_dates(df):
    df['birthdate'] = pd.to_datetime(df['birthdate'], format="+%Y-%m-%dT%H:%M:%SZ").dt.date
    df['deathdate'] = pd.to_datetime(df['deathdate'], format="+%Y-%m-%dT%H:%M:%SZ").dt.date
    return df

def calculate_age_per_row(row, currentdate):
    if pd.notna(row['birthdate']) and pd.notna(row['deathdate']):
        age = relativedelta(row['deathdate'], row['birthdate']).years
    elif pd.notna(row['birthdate']):
        age = relativedelta(currentdate, row['birthdate']).years
    else:
        age = None
    return age

def add_age(df, currentdate):
    df["age"] = df.apply(lambda row: calculate_age_per_row(row, currentdate), axis=1)
    df["age"] = df["age"].astype("Int64")
    return df