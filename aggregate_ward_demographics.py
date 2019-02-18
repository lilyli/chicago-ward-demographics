import pandas as pd


def aggregate_ward_demographics():
    race_df = pd.read_csv('data/ACS_2017_race/ACS_17_5YR_B02001_with_ann.csv')
    ethnicity_df = pd.read_csv('data/ACS_2017_ethnicity/ACS_17_5YR_B03003_with_ann.csv')
    income_df = pd.read_csv('data/ACS_2017_income/ACS_17_5YR_B19001_with_ann.csv')
    bg_ward_mapping = pd.read_csv('block_group_ward_mapping.csv')
    ward_boundaries = pd.read_csv('data/ward_boundaries.csv')
    ward_boundaries.drop(columns = ['SHAPE_Leng', 'SHAPE_Area'], inplace = True)
    ward_boundaries.columns = ['the_geom', 'Ward', ]

    # first line of csvs is documentation
    race_df.drop(race_df.index[0], inplace = True)
    ethnicity_df.drop(ethnicity_df.index[0], inplace = True)
    income_df.drop(income_df.index[0], inplace = True)

    race_df = race_df[['GEO.id2', 'HD01_VD01', 'HD01_VD02', 'HD01_VD03', 'HD01_VD05']]
    race_df = race_df.astype(int) # convert columns to int for merging later
    race_df.rename(index = str, columns = {'GEO.id2': 'bg_id', 'HD01_VD01': 'Race-Total',
        'HD01_VD02': 'Race-White', 'HD01_VD03': 'Race-Black', 'HD01_VD05': 'Race-Asian'}, inplace = True)

    ethnicity_df = ethnicity_df[['GEO.id2', 'HD01_VD01', 'HD01_VD03']]
    ethnicity_df = ethnicity_df.astype(int)
    ethnicity_df.rename(index = str, columns = {'GEO.id2': 'bg_id', 'HD01_VD01': 'Ethnicity-Total',
        'HD01_VD03': 'Ethnicity-Hispanic'}, inplace = True)

    income_df = income_df[['GEO.id2', 'HD01_VD01', 'HD01_VD02', 'HD01_VD03', 'HD01_VD04',
        'HD01_VD05', 'HD01_VD06', 'HD01_VD07', 'HD01_VD08', 'HD01_VD09', 'HD01_VD10',
        'HD01_VD11', 'HD01_VD12', 'HD01_VD13', 'HD01_VD14', 'HD01_VD15', 'HD01_VD16', 'HD01_VD17']]
    income_df = income_df.astype(int) # convert columns to int for accurate summing
    income_df['Income-24999_minus'] = income_df['HD01_VD02'] + income_df['HD01_VD03'] + income_df['HD01_VD04'] + \
        income_df['HD01_VD05']
    income_df['Income-25000-49999'] = income_df['HD01_VD06'] + income_df['HD01_VD07'] + income_df['HD01_VD08'] + \
        income_df['HD01_VD09'] + income_df['HD01_VD10']
    income_df['Income-50000-99999'] = income_df['HD01_VD11'] + income_df['HD01_VD12'] + income_df['HD01_VD13']
    income_df['Income-100000-149999'] = income_df['HD01_VD14'] + income_df['HD01_VD15']
    income_df['Income-150000_plus'] = income_df['HD01_VD16'] + income_df['HD01_VD17']
    income_df.drop(columns = ['HD01_VD02', 'HD01_VD03', 'HD01_VD04', 'HD01_VD05', 'HD01_VD06',
        'HD01_VD07', 'HD01_VD08', 'HD01_VD09', 'HD01_VD10', 'HD01_VD11', 'HD01_VD12',
        'HD01_VD13', 'HD01_VD14', 'HD01_VD15', 'HD01_VD16', 'HD01_VD17'], axis = 1, inplace = True)
    income_df.rename(index = str, columns = {'GEO.id2': 'bg_id', 'HD01_VD01': 'Income-Total'}, inplace = True)

    # aggregate block group level data by ward
    ward_demo_df = ethnicity_df.merge(race_df, how = 'inner', on = 'bg_id')
    ward_demo_df = ward_demo_df.merge(income_df, how = 'inner', on = 'bg_id')
    ward_demo_df = ward_demo_df.merge(bg_ward_mapping, how = 'inner', on = 'bg_id')
    # inner join b/c ACS data is for all block groups within Cook County,
    # some of which may not be in Chicago
    ward_demo_df = ward_demo_df.groupby('ward_id').sum().reset_index().drop(columns = ['bg_id'])

    # convert counts to %s
    for col in ['Race-White', 'Race-Black', 'Race-Asian']:
        ward_demo_df[col + '_pct'] = round(ward_demo_df[col] / ward_demo_df['Race-Total'] * 100, 2)
    ward_demo_df['Ethnicity-Hispanic_pct'] = round(ward_demo_df['Ethnicity-Hispanic'] / ward_demo_df['Ethnicity-Total'] * 100, 2)
    for col in ['Income-24999_minus', 'Income-25000-49999', 'Income-50000-99999', 'Income-100000-149999', 'Income-150000_plus']:
        ward_demo_df[col + '_pct'] = round(ward_demo_df[col] / ward_demo_df['Income-Total'] * 100, 2)
    
    ward_demo_pct_df = ward_demo_df[['ward_id', 'Race-White_pct', 'Race-Black_pct', 'Race-Asian_pct',
        'Ethnicity-Hispanic_pct', 'Income-24999_minus_pct', 'Income-25000-49999_pct', 'Income-50000-99999_pct',
        'Income-100000-149999_pct', 'Income-150000_plus_pct']]
    ward_demo_pct_df.rename(index = str, columns = {'ward_id': 'Ward'}, inplace = True)
    ward_demo_pct_df.to_csv('ward_demographics.csv')
    ward_boundaries = ward_boundaries.merge(ward_demo_pct_df, how = 'left', on = 'Ward')

    return ward_boundaries


if __name__ == '__main__':
    ward_demo = aggregate_ward_demographics()
    ward_demo.to_csv('ward_demographics_boundaries.csv')

