"""This file perform data clean to target & features dataframe"""
import pandas as pd


def replace_null_values(dataset):
    """Replace values identified as null with the mean"""
    # replacing null values with the mean
    cols = list(dataset.columns)
    for c in cols:
        dataset.loc[dataset[c].isin([-9999, -2222, -2222.2, -2, -1111.1, -1111, -1]), c] = None
        mean = dataset[c].mean()
        dataset[c].fillna(value=mean, inplace=True)
    return dataset


def create_fips_columns(dataset):
    """Create FIPS columns in Features dataframe, this is used for choropleth"""
    dataset['State_FIPS_Code'] = dataset['State_FIPS_Code'].astype(int).astype(str)
    dataset['County_FIPS_Code'] = dataset['County_FIPS_Code'].astype(int).astype(str)
    dataset['FIPS'] = dataset['State_FIPS_Code'].apply(lambda x: x.zfill(2)) + dataset['County_FIPS_Code'].apply(lambda x: x.zfill(3))
    return dataset


def drop_cols(dataset):
    """Drop features that will not be used in modeling"""
    dataset = dataset.drop(columns=['Premature', 'Toxic_Chem', 'Pap_Smear', 'Proctoscopy', 'Flu_Vac', 'Pneumo_Vax', 'Mammogram', 'State_FIPS_Code', 'County_FIPS_Code', 'Population_Size', 'Sev_Work_Disabled'])
    return dataset


def drop_invalid(dataset):
    """dropping invalid values from Target dataframe"""
    idy_nan = dataset.loc[dataset['ALE'].isin([-9999, -2222, -2222.2, -2, -1111.1, -1111, -1])].index
    dataset.drop(index=idy_nan, inplace=True)
    return dataset


def change_to_percentage(dataset):
    """Change to percentages those feature columns that are not"""
    list_ratios = ['Prim_Care_Phys_Rate', 'Dentist_Rate']
    for r in list_ratios:
        dataset[r] = round((dataset[r]/1000), 2)
    list_totals = ['No_HS_Diploma', 'Unemployed', 'Sev_Work_Disabled', 'Major_Depression', 'Recent_Drug_Use', 'Uninsured', 'Elderly_Medicare', 'Disabled_Medicare', 'MVA']
    for l in list_totals:
        if [dataset['Population_Size'] - dataset[l] < 0]:
            dataset = dataset.loc[dataset['Population_Size'] - dataset[l] > 0]
        dataset[l] = round(((dataset[l]/dataset['Population_Size'])*100), 2)
    return dataset


def match_records(dataset_x, dataset_y):
    """This function validates the row count is the same for features and target dataframes"""
    x_train_idx = list(dataset_x.index.values)
    y_train_idx = list(dataset_y.index.values)
    drop_from_y = list(set(y_train_idx) - set(x_train_idx))
    drop_from_x = list(set(x_train_idx) - set(y_train_idx))
    dataset_x.drop(index=drop_from_x, inplace=True)
    dataset_y.drop(index=drop_from_y, inplace=True)
    print(dataset_x.shape[0], dataset_y.shape[0])
    return dataset_x, dataset_y


def create_fips_df(dataset_train, dataset_test):
    """This function merges test & train sets, then drops the FIPS column from features dataframe"""
    full_data = pd.concat([dataset_train, dataset_test])
    if "FIPS" in list(dataset_test.columns):
        dataset_test.drop(columns='FIPS', inplace=True)
        dataset_train.drop(columns='FIPS', inplace=True)
    return dataset_train, dataset_test, full_data


def data_clean(dataset_x, dataset_y):
    """First parameter must be features dataframe, second paramenter must be target dataframe"""
    dataset_x = create_fips_columns(dataset_x)
    dataset_x = replace_null_values(dataset_x)
    dataset_x = change_to_percentage(dataset_x)
    dataset_x = drop_cols(dataset_x)
    dataset_y = drop_invalid(dataset_y)
    dataset_x, dataset_y = match_records(dataset_x, dataset_y)
    return dataset_x, dataset_y
