# get household size info, create median_size col of zeros, then loop through each row to create list(x * int(col_name) + ...), then get median of list
# sum up income col to just 4 in terms of fpl


# fpl guidelines https://familiesusa.org/product/federal-poverty-guidelines

import pandas as pd
import statistics


def aggregate_ward_demographics():
    hhd_size_df = pd.read_csv('data/ACS_2017_household_size/ACS_17_5YR_B11016_with_ann.csv')
    race_df = pd.read_csv('data/ACS_2017_race/ACS_17_5YR_B02001_with_ann.csv')
    income_df = pd.read_csv('data/ACS_2017_income/ACS_17_5YR_B19001_with_ann.csv')
    fpl_df = pd.read_csv('data/federal_poverty_guidelines.csv')
    bg_ward_mapping = pd.read_csv('block_group_ward_mapping.csv')
    ward_boundaries = pd.read_csv('data/ward_boundaries.csv')
    ward_boundaries.drop(columns = ['SHAPE_Leng', 'SHAPE_Area'], inplace = True)
    ward_boundaries.columns = ['the_geom', 'Ward', ]

    hhd_size_df = hhd_size_df[['GEO.id2', 'HD02_VD01', 'HD01_VD03', 'HD01_VD04',
        'HD01_VD05', 'HD01_VD06', 'HD01_VD07', 'HD01_VD08', 'HD01_VD10', 'HD01_VD11',
        'HD01_VD12', 'HD01_VD13', 'HD01_VD14', 'HD01_VD15', 'HD01_VD16']]
    # combine data for family and non-family hhds
    hhd_size_df['Household-2 person'] = hhd_size_df['HD01_VD03'] + hhd_size_df['HD01_VD11']
    hhd_size_df['Household-3 person'] = hhd_size_df['HD01_VD04'] + hhd_size_df['HD01_VD12']
    hhd_size_df['Household-4 person'] = hhd_size_df['HD01_VD05'] + hhd_size_df['HD01_VD13']
    hhd_size_df['Household-5 person'] = hhd_size_df['HD01_VD06'] + hhd_size_df['HD01_VD14']
    hhd_size_df['Household-6 person'] = hhd_size_df['HD01_VD07'] + hhd_size_df['HD01_VD15']
    hhd_size_df['Household-7 or more person'] = hhd_size_df['HD01_VD08'] + hhd_size_df['HD01_VD16']
    hhd_size_df.drop(columns = ['HD01_VD03', 'HD01_VD04', 'HD01_VD05', 'HD01_VD06', 'HD01_VD07',
        'HD01_VD08', 'HD01_VD11', 'HD01_VD12', 'HD01_VD13', 'HD01_VD14', 'HD01_VD15', 'HD01_VD16'], inplace = True)
    hhd_size_df.rename(index = str, columns = {'GEO.id2': 'bg_id', 'HD02_VD01': 'Household-Total',
        'HD01_VD10': 'Household-1 person'}, inplace = True)

    race_df = race_df[['GEO.id2', 'HD01_VD01', 'HD01_VD02', 'HD01_VD03', 'HD01_VD04', 
        'HD01_VD05', 'HD01_VD06', 'HD01_VD07', 'HD01_VD08', 'HD01_VD09', 'HD01_VD10']]
    # combine data for American Indian, Native Hawaiian, Some other race, Two or more races
    # REDO COMBINATION- TOO MUCH AGGREG.
    race_df['Race-Other'] = (race_df['HD01_VD04'] + race_df['HD01_VD06'] + race_df['HD01_VD07'] +
        race_df['HD01_VD08'] + race_df['HD01_VD09'] + + race_df['HD01_VD10'])
    race_df.drop(columns = ['HD01_VD04', 'HD01_VD06', 'HD01_VD07', 'HD01_VD08',
        'HD01_VD09', 'HD01_VD10'], inplace = True)
    race_df.rename(index = str, columns = {'GEO.id2': 'bg_id', 'HD01_VD01': 'Race-Total',
        'HD01_VD02': 'Race-White alone', 'HD01_VD03': 'Race-Black alone',
        'HD01_VD05': 'Race-Asian alone'}, inplace = True)

    income_df = income_df[['GEO.id2', 'HD01_VD01', 'HD01_VD02', 'HD01_VD03', 'HD01_VD04',
        'HD01_VD05', 'HD01_VD06', 'HD01_VD07', 'HD01_VD08', 'HD01_VD09', 'HD01_VD10',
        'HD01_VD11', 'HD01_VD12', 'HD01_VD13', 'HD01_VD14', 'HD01_VD15', 'HD01_VD16', 'HD01_VD17']]
    # need to rename col and do in terms of FPL


    # aggregate block group level data by ward
    ward_demo_df = hhd_size_df.merge(race_df, how = 'inner', on = 'bg_id')
    # ward_demo_df = ward_demo_df.merge(income_df, how = 'inner', on = 'bg_id')
    ward_demo_df.drop(ward_demo_df.index[0], inplace = True) # first line is documentation
    ward_demo_df = ward_demo_df.astype(int)
    ward_demo_df = ward_demo_df.merge(bg_ward_mapping, how = 'inner', on = 'bg_id')
    # inner join b/c ACS data is for all block groups within Cook County,
    # some of which may not be in Chicago
    ward_demo_df = ward_demo_df.groupby('ward_id').sum().reset_index().drop(columns = ['bg_id'])
    ward_demo_df.rename(index = str, columns = {'ward_id': 'Ward'}, inplace = True)

    # calculate median household size of all wards for FPL income cutoffs
    ward_demo_df['median_hhd_size'] = 0

    for i in range(ward_demo_df.shape[0]):
        hhd_sizes = []
        for col in ('Household-1 person', 'Household-2 person', 'Household-3 person',
            'Household-4 person', 'Household-5 person', 'Household-6 person',
            'Household-7 or more person'):
            hhd_sizes.extend([int(col[10])] * ward_demo_df.iloc[i][col])
        ward_demo_df.at[ward_demo_df.index[i], 'median_hhd_size'] = int(statistics.median(hhd_sizes) + 0.5) # round up


    for df in (income_df, race_df):
        for col in df.columns[3:]: # convert counts to percentages
            df[col] = df[col] / df['HD01_VD01'] * 100 # 'HD01_VD01' is total count col



    ward_boundaries = ward_boundaries.merge(ward_demo_df, how = 'left', on = 'Ward')

    return ward_boundaries


if __name__ == '__main__':
    pass

