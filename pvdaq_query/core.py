# -*- coding: utf-8 -*-
from pvdaq_query.utilities import progress

from time import time
import requests
from io import StringIO
import pandas as pd
import numpy as np
from datetime import timedelta


def get_pvdaq_data(sysid=2, api_key = 'DEMO_KEY', year=2011):
    """
    This fuction queries one or more years of raw PV system data from NREL's PVDAQ data service:
            https://maps.nrel.gov/pvdaq/
    """
    # Force year to be a list of integers
    ti = time()
    try:
        year = int(year)
    except TypeError:
        year = [int(yr) for yr in year]
    else:
        year = [year]
    # Each year must queries separately, so iterate over the years and generate a list of dataframes.
    df_list = []
    it = 0
    for yr in year:
        progress(it, len(year), 'querying year {}'.format(year[it]))
        req_params = {
            'api_key': api_key,
            'system_id': sysid,
            'year': yr
        }
        base_url = 'https://developer.nrel.gov/api/pvdaq/v3/data_file?'
        param_list = [str(item[0]) + '=' + str(item[1]) for item in req_params.items()]
        req_url = base_url + '&'.join(param_list)
        response = requests.get(req_url)
        if int(response.status_code) != 200:
            print('\n error: ', response.status_code)
            return
        df = pd.read_csv(StringIO(response.text))
        df_list.append(df)
        it += 1
    tf = time()
    progress(it, len(year), 'queries complete in {:.1f} seconds       '.format(tf - ti))
    # concatenate the list of yearly data frames
    df = pd.concat(df_list, axis=0)
    # convert index to timeseries
    df['Date-Time'] = pd.to_datetime(df['Date-Time'])
    df.set_index('Date-Time', inplace=True)
    # standardize the timeseries axis to a regular frequency over a full set of days
    diff = (df.index[1:] - df.index[:-1]).seconds
    freq = int(np.median(diff))                  # the number of seconds between each measurement
    start = df.index[0]
    end = df.index[-1]
    time_index = pd.date_range(start=start.date(), end=end.date() + timedelta(days=1), freq='{}s'.format(freq))[:-1]
    df = df.reindex(index=time_index, method='nearest')
    return df.fillna(value=0)

def make_D(df, key='dc_power'):
    if df is not None:
        n_steps = int(24 * 60 * 60 / df.index.freq.n)
        D = df[key].values.reshape(n_steps, -1, order='F')
        return D
    else:
        return

def plot_D(D, figsize=(12, 6)):
    if D is not None:
        import matplotlib.pyplot as plt
        import seaborn as sns

        with sns.axes_style("white"):
            fig, ax = plt.subplots(nrows=1, figsize=figsize)
            foo = ax.imshow(D, cmap='hot', interpolation='none', aspect='auto', vmin=0)
            ax.set_title('Measured power')
            plt.colorbar(foo, ax=ax, label='kW')
            ax.set_xlabel('Day number')
            ax.set_yticks([])
            ax.set_ylabel('Time of day')
        return fig
    else:
        return