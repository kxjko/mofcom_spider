import pandas as pd

if __name__ == '__main__':
    df1 = pd.read_excel('data/价格.xls', dtype={'子目HS2002': str})
    for i, row in df1.iterrows():
        if len(row['子目HS2002']) < 6:
            df1.loc[i, '子目HS2002'] = '0' + row['子目HS2002']
    df2 = pd.read_excel('data/2002-2012.xlsx', dtype={'HS 2012': str, 'HS 2002': str})
    df3 = pd.read_excel('data/原产地.xls', dtype={'HS2012': str})
    for i, row in df3.iterrows():
        if row['v1'] < 10:
            df3.loc[i, 'HS2012'] = '0' + row['HS2012']
    df4 = pd.merge(left=df1, right=df2, left_on='子目HS2002', right_on='HS 2002', how='left')
    df5 = pd.merge(left=df4, right=df3, left_on='HS 2012', right_on='HS2012', how='left')
    # for (k1, k2, k3, k4), group in df5.groupby(['时间', '出口国', '进口国', '子目HS2002']):
    #     print(group)
    for i, row in df5.loc[(~pd.isnull(df5['HS 2012']) & pd.isnull(df5['HS2012']))].iterrows():
        for key, value in df3.loc[df3['HS2012'] == row['HS 2012'][:4]].iloc[0].items():
            df5.loc[i, key] = value

    df5.drop_duplicates(subset=['时间', '出口国', '进口国', '子目HS2002', 'roo', 'index'], keep='first', inplace=True)
    print(df5.to_excel('res.xlsx'))
