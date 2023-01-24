"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-01
Description: Getting prevelance data for world cup teams.
    
"""
import copy
import pandas as pd
import datetime

schedule_df = pd.read_csv('data_extraction/Fifa 2022 Group stages matches with venue capacity.csv')
covid_data = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
population_df = pd.read_csv('data_extraction/Population estimates world bank.csv',header=2, index_col='Country Name') # downloaded from https://data.worldbank.org/indicator/SP.POP.TOTL https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv

# need to change covid_data to datetime type
covid_data.date = pd.to_datetime(covid_data.date)

date_to = datetime.datetime(2022, 11, 18)
covid_data = covid_data[covid_data.date<=date_to]

#%%
# select data for only countries in the world cup
countries = set(schedule_df['Team A'].unique().tolist() +
                schedule_df['Team B'].unique().tolist()) 

# looking at the data set (https://covid.ourworldindata.org/data/owid-covid-data.csv) new cases smoothed
# for England and Wales is pooled under United Kingdom
proxies = copy.deepcopy(countries)
proxies.add('United Kingdom')
proxies.remove('England')
proxies.remove('Wales')
covid_data = covid_data[covid_data.location.isin(proxies)]
# sense check to make sure we have selected the right places
selected_proxies = covid_data.location.unique()
len(proxies)==len(selected_proxies)
#%% Selecting most recent available data for new_cases_smoothed
# remove missing data
covid_data.new_cases_smoothed = covid_data.new_cases_smoothed.replace({0:None})
covid_data = covid_data[pd.notnull(covid_data.new_cases_smoothed)]
prevelance_records = []
for country in countries:
    if country in ['England', 'Wales']:
        proxy = 'United Kingdom'
    else:
        proxy = country
    # select proxie
    location_data = covid_data[covid_data.location==proxy]
    # latest date for which we have information
    latest_date = location_data.date.max()
    latest_date_data = location_data[location_data.date==latest_date]
    cases_smoothed = latest_date_data.new_cases_smoothed.iloc[0]
    if proxy=='South Korea':
        population = population_df.loc['Korea, Rep.', '2021']
    elif proxy == 'Iran':
        population = population_df.loc['Iran, Islamic Rep.', '2021']
    else:
        population = population_df.loc[proxy,'2021']

    entry = {'country': country,
             'proxy': proxy,
             'date': latest_date,
             'case_prevalence': cases_smoothed/population,
             }

    prevelance_records.append(entry)

prevelance_df = pd.DataFrame(prevelance_records)
#%% Adding data on infection to detection ratio

# Getting data frame
# location of zip file downloaded from https://ghdx.healthdata.org/sites/default/files/record-attached-files/HME_COVID_19_IES_2019_2021_RATIOS.zip
zip_file = 'data_extraction/HME_COVID_19_IES_2019_2021_RATIOS.zip'
# read file
detection_raio_df = pd.read_csv(zip_file)
# Selecting detections/infections
detection_raio_df.measure_name.unique()
detection_raio_df = detection_raio_df[detection_raio_df.measure_name=='Cumulative infection-detection ratio']
# change date to date
detection_raio_df['date'] = pd.to_datetime(detection_raio_df['date'])
detection_raio_df = detection_raio_df[detection_raio_df.date==detection_raio_df.date.max()]
detection_raio_df.location_name = detection_raio_df.location_name.replace({'USA':'United States','UK':'United Kingdom'})

values_list = ['value_mean','value_lower','value_upper']
# Change percent to raw number
for column in values_list:
    detection_raio_df[column] = detection_raio_df[column]/100
detection_raio_df.metric_name = 'raw'
# invert values so they are now infections/detected cases.
for column in values_list:
    detection_raio_df[column] = detection_raio_df[column]**-1


to_merge = detection_raio_df[detection_raio_df.location_name.isin(proxies)]
to_merge = to_merge[['location_name']+values_list]

prevelance_df = prevelance_df.merge(to_merge, left_on='proxy', right_on='location_name')
prevelance_df.rename(columns={'value_lower': 'ratio_upper',
                              'value_mean': 'ratio_mean',
                              'value_upper': 'ratio_lower'},
                     inplace=True)

prevelance_df['infection_prevalence_lower'] = prevelance_df.case_prevalence*prevelance_df.ratio_lower
prevelance_df['infection_prevalence_mean'] = prevelance_df.case_prevalence*prevelance_df.ratio_mean
prevelance_df['infection_prevalence_upper'] = prevelance_df.case_prevalence*prevelance_df.ratio_upper
# host min and max
host_min = prevelance_df[prevelance_df.country=='Qatar']['infection_prevalence_lower'].tolist()[0]
host_max = prevelance_df[prevelance_df.country=='Qatar']['infection_prevalence_upper'].tolist()[0]

# Everybody elses min max
visior_min = prevelance_df[prevelance_df.country!='Qatar']['infection_prevalence_lower'].min()
visior_max = prevelance_df[prevelance_df.country!='Qatar']['infection_prevalence_upper'].max()

