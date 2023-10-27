"""
Creation:
    Author: Martin Grunnill
    Date: 2023-01-27
Description: Figure of detected, hospitalised and ICU COVID-19 cases around the world cup.
    
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta
from PIL import Image # For conversion of eps files to tiff for publication.
import os

#%% Load Qatari government data
url_qatari_gov= "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets/covid-19-cases-in-qatar/exports/csv?lang=en&timezone=America%2FNew_York&use_labels=true&csv_separator=%3B"
covid_qatar_gov_data = pd.read_csv(url_qatari_gov, sep=';')
# check Date field is date type
print(covid_qatar_gov_data.Date.dtype)
# change to Date field to date type
covid_qatar_gov_data.Date = pd.to_datetime(covid_qatar_gov_data.Date).dt.date
# rename date



#%% Load Our world in Data data
url_owd = 'https://github.com/owid/covid-19-data/raw/master/public/data/owid-covid-data.csv'
covid_owd = pd.read_csv(url_owd)
# check Date field is date type
print(covid_owd.date.dtype)
# change to Date field to date type
covid_owd.date = pd.to_datetime(covid_owd.date).dt.date
# select Qatar
covid_owd = covid_owd[covid_owd.location=='Qatar']
covid_owd.rename(columns={'date': 'Date'},inplace=True)


#%% Setup important dates and select for around time of world cup
# Setup important dates
world_cup_start = dt.date(2022, 11, 20)
month_before_world_cup = world_cup_start - relativedelta(months=2)
last_group_stage_match = dt.date(2022, 12, 2)
end_of_last_16 = dt.date(2022, 12, 6)
quater_finals_begin = dt.date(2022, 12, 9)
quater_finals_end = dt.date(2022, 12, 10)
semi_finals_begin = dt.date(2022, 12, 13)
semi_finals_end = dt.date(2022, 12, 14)
world_cup_final = dt.date(2022, 12, 18)
month_after_world_cup = world_cup_final + relativedelta(months=1)
# select for around time of world cup
mask = (covid_qatar_gov_data['Date'] >= month_before_world_cup) & \
       (covid_qatar_gov_data['Date'] <= month_after_world_cup)
covid_around_word_cup_qatari_gov = covid_qatar_gov_data.loc[mask]
mask = (covid_owd['Date'] >= month_before_world_cup) & \
       (covid_owd['Date'] <= month_after_world_cup)
covid_around_word_cup_owd = covid_owd.loc[mask]

#%% Select what we want from both data sources and merge into one dataframe
new_cases_smoothed = covid_around_word_cup_owd[['Date','new_cases_smoothed']]
in_hospital_icu = covid_around_word_cup_qatari_gov[['Date',
                                                    #'Number of New Acute Hospital Admissions in Last 24 Hrs',
                                                    'Total Number of Acute Cases under Hospital Treatment',
                                                    #'Number of New ICU Admissions in Last 24 Hrs',
                                                    # 'Total Number of Cases under ICU Treatment'
                                                    ]]

merged_data = pd.merge(new_cases_smoothed, in_hospital_icu, on='Date', how='outer')
merged_data.rename(columns={'new_cases_smoothed':'New Cases\nSmoothed',
                            'Total Number of Acute Cases under Hospital Treatment':'Hospital\nTreatment',
                            # 'Total Number of Cases under ICU Treatment': 'ICU\nTreatment'
                            },
                   inplace=True)
# merged_data.set_index('Date', inplace=True)
#%% Plotting figures
merged_data_long_form = pd.melt(merged_data, id_vars='Date')

plt.figure()
fig = sns.relplot(
    data=merged_data_long_form,
    x='Date', y='value',
    row='variable',
    # hue='variable',
    kind="line",
    aspect=2,
    facet_kws={'sharey':False})
fig.set_titles(row_template="")
fig.set_xticklabels(rotation=45)
# plt.axvline(world_cup_start)
line_width = 1
fig.refline(x = world_cup_start,
            color = "gold",
            linewidth=line_width)
fig.refline(x = world_cup_final,
            color = "gold",
            linewidth=line_width)
fig.refline(x = last_group_stage_match,
            color = "firebrick",
            linewidth=line_width)
fig.refline(x = quater_finals_begin,
            color = "firebrick",
            linewidth=line_width)
fig.axes[0,0].set_ylabel('New Cases Smoothed')
fig.axes[1,0].set_ylabel('Total in Hospital')
plt.tight_layout()
plt.savefig('Covid cases around world.eps')

