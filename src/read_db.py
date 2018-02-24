import pandas as pd
import os
import numpy as np

CSV_DIR = '../input/database/raw'
SAVE_DIR = '../input/database'
def parse_csv_db(filepath):

    df = pd.read_csv(filepath)
    df.columns = ['name', 'observed', 'ritz']
    df = df.drop(['observed'], axis=1)
    df.columns = ['name', 'nm']

    df = df.applymap(lambda x: x.strip())
    df = df.applymap(lambda x: np.nan if x == '' else x)
    df = df.dropna(axis=0, how='all')

    df['nm'] = df['nm'].apply(lambda x: x.split('+')[0])

    return df


al = parse_csv_db(os.path.join(CSV_DIR, 'database_Al.csv'))
cu = parse_csv_db(os.path.join(CSV_DIR, 'database_Cu.csv'))
fe = parse_csv_db(os.path.join(CSV_DIR, 'database_Fe.csv'))

al.to_csv(os.path.join(SAVE_DIR, 'database_Al.csv'), index=False)
cu.to_csv(os.path.join(SAVE_DIR, 'database_Cu.csv'), index=False)
fe.to_csv(os.path.join(SAVE_DIR, 'database_Fe.csv'), index=False)