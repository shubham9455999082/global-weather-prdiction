import pandas as pd
import numpy as np

GRID_SIZE = 514
tmax = 'gt-contest_tmax-14d.txt'
tmin = 'gt-contest_tmin-14d.txt'
prec = 'gt-contest_precip-14d.txt'
climat = 'gt-climate_regions.txt'
delta_train = 14

def read_df(name_df):
    df = pd.read_csv(name_df)
    date = df[df['lon'].isnull()]['start_date / lat'].tolist()
    df = df.dropna()
    col_date = []
    for d in date:
        col_date += [d] * GRID_SIZE
    df['start_date'] = col_date
    df.columns = ['lat'] + df.columns.tolist()[1:]
    df['lon'] = df['lon'].astype('int')
    df['lat'] = df['lat'].astype('int')
    return df

def create_df(df_tmax, df_tmin, df_prec, full_df = -1, flag = False):
    df_taver = df_tmax[['lat', 'lon', 'start_date']].copy()
    df_taver['tmax'] = df_tmax['tmax']
    df_taver['tmin'] = df_tmin['tmin']
    df_taver['taver'] = (df_tmax['tmax'] + df_tmin['tmin']) / 2
    if not flag:
        df_taver = df_taver[(df_taver['start_date'] >= '2010-01-01')]
        df_prec = df_prec[(df_prec['start_date'] >= '2010-01-01')]
    df_taver['precip'] = df_prec['precip'].values
    df_taver = df_taver.sort_values(['lat', 'lon', 'start_date'])
    if flag:
        full_df = pd.concat([full_df, df_taver]).reset_index(drop=True)
        return full_df
    else:
        return df_taver

df_tmax = read_df(tmax)
df_tmin = read_df(tmin)
df_prec = read_df(prec)

full_df = create_df(df_tmax, df_tmin, df_prec)

full_df['month_day'] = [x[5:] for x in full_df.start_date]
full_df['lat_lon'] = full_df['lat'].astype('str') + '_' + full_df['lon'].astype('str')
full_df['mean_tmp'] = (full_df['tmax'] + full_df['tmin']) / 2
tmp_new = full_df[full_df.month_day == '03-17']
mean_tmp = (tmp_new.groupby('lat_lon').mean_tmp.mean()).reset_index()
mean_tmp['lat'] = [int(x.split('_')[0]) for x in mean_tmp['lat_lon'].values]
mean_tmp['lon'] = [int(x.split('_')[1]) for x in mean_tmp['lat_lon'].values]
mean_tmp['temp34'] = mean_tmp['mean_tmp'] + 0.5

tmp_new = full_df[full_df.month_day == '03-31']
mean_tmp_new = (tmp_new.groupby('lat_lon').mean_tmp.mean())
mean_tmp['temp56'] = mean_tmp['lat_lon'].map(mean_tmp_new) + 0.5

tmp_new = full_df[full_df.month_day == '03-17']
mean_tmp_new = (tmp_new.groupby('lat_lon').precip.mean())
mean_tmp['prec34'] = mean_tmp['lat_lon'].map(mean_tmp_new) + 0.5

tmp_new = full_df[full_df.month_day == '03-31']
mean_tmp_new = (tmp_new.groupby('lat_lon').precip.mean())
mean_tmp['prec56'] = mean_tmp['lat_lon'].map(mean_tmp_new) + 0.5

mean_tmp = mean_tmp[mean_tmp.columns[2:]]
mean_tmp.to_csv('2020-03-03.csv', index = None)