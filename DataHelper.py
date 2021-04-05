import numpy as np
import pandas as pd


def get_trip_record_from_dataframe_by_starting_and_end_time(df, starting_time, end_time):
    df_result = df.loc[(df['rider earliest departure time'] >= starting_time) & (df['rider earliest departure time'] <= end_time)]
    # print(df_result)
    return df_result