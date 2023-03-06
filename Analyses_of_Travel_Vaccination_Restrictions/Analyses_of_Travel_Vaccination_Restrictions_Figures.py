"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-30
Description: Figures showing effect of varying vaccination regimes. Simulations described in  'Analyses of Travel
             Vaccination Restrictions' section of manuscript. Figures presented and discussed in 'Effects of Proportion
             Recently Vaccinated as a COVID-19 Control Measure' section of manuscript.
    
"""

import pandas as pd
import copy
import os
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

sample_size = 10000
data_dir = 'C:/Data/World Cup Modelling'
data_dir = data_dir + '/Assesing vaccination with LH sample Size ' + str(sample_size)+'/'
fig_dir = data_dir +'/Figures'
if not os.path.exists(fig_dir):
    os.mkdir(fig_dir)
fig_dir = fig_dir +'/'

#%%
# Useful lists and variables.
outputs = ['total infections',
           'total hospitalisations',
           'peak infected',
           'peak hospitalised',
           # 'total positive tests'
           ]
output_labels = [output.title().replace(' ', '\n') for output in outputs]
just_totals_outputs = outputs[0:2]
just_totals_output_labels = output_labels[0:2]
LH_sample = pd.read_csv(data_dir+'LH sample.csv')
parameters_sampled = LH_sample.columns.to_list()
parameters_sampled.remove('Sample Number')
testing_regimes = ['Pre-travel RTPCR',
                   'Pre-travel RA',
                   'Pre-match RTPCR',
                   'Pre-match RA',
                   'Double RTPCR',
                   'Double RA',
                   'RTPCR then RA',
                   'RA then RTPCR',
                   'No Testing'
                   ]
palette = sns.color_palette()
palette_dict = {testing_regime:palette[index] for index, testing_regime in enumerate(testing_regimes)}
testing_regimes = ['Pre-travel RTPCR',
                   'Pre-match RA',
                   'RTPCR then RA',
                   'No Testing'
                   ]
testing_regimes_labels = [testing_regime.replace(' ', '\n') for testing_regime in testing_regimes]
actual_testing_regimes = copy.deepcopy(testing_regimes)
actual_testing_regimes.remove('No Testing')
actual_testing_regimes_labels = [testing_regime.replace(' ', '\n') for testing_regime in actual_testing_regimes]
correlation_types = ['spearman', 'pearson']
sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
props_effectivly_vaccinated = [0.0, 0.25, 0.5, 0.75, 1.0]
box_plot_mean_marker = {"marker":"o",
                        "markerfacecolor":"white",
                        "markeredgecolor":"white",
                        "markersize":"2.5"}

#%%
# loading data
results_file = data_dir+'/merged focused outputs.csv'
if os.path.isfile(results_file):
    results_df = pd.read_csv(results_file)
else:
    results_df = []
    for testing_regime in tqdm(testing_regimes, desc='loading data from testing regime'):
        regime_data_dir = data_dir + testing_regime + '/'
        for prop_effectivly_vaccinated in props_effectivly_vaccinated:
            prop_vaccinated_save_dir = (regime_data_dir + 'Prop Effectively vaccinated '
                                        + str(prop_effectivly_vaccinated)+ '/')
            csvs = [prop_vaccinated_save_dir+'Focused Outputs and Sample ' + str(index)+ '.csv' for index in range(sample_size)]
            df = pd.concat(map(pd.read_csv, csvs), ignore_index=True)
            df['Testing Regime'] = testing_regime
            df['Prop_Effec_Vaccinated'] = prop_effectivly_vaccinated
            results_df.append(df)

    results_df = pd.concat(results_df)
    results_df.to_csv(results_file, index=False)

#%%
results_reshaped = results_df.set_index(['Testing Regime', 'Sample Number','Prop_Effec_Vaccinated'])
results_reshaped = results_reshaped[outputs]
results_reshaped = results_reshaped.stack()
results_reshaped = results_reshaped.reset_index()
results_reshaped.rename(columns={'level_3':'Output',
                                 0:'people'},
                        inplace=True)
# Proportion vaccinated has to be a string to be seen as a boxplot catagory
results_reshaped.Prop_Effec_Vaccinated = results_reshaped.Prop_Effec_Vaccinated.astype(str)
results_pivoted = results_reshaped.pivot(index=['Sample Number','Output','Testing Regime'],
                                         columns=['Prop_Effec_Vaccinated'],
                                         values='people')

#%%
relative_diffs = {str(prop) : [] for prop in props_effectivly_vaccinated[:-1]}
control = results_pivoted.loc[(slice(None), slice(None), 'No Testing'), '1.0'] # No testing and 1.0 effectivly vaccinated.
control = control.reset_index(level=2)['1.0']
for prop in props_effectivly_vaccinated[:-1]:
    prop = str(prop)
    for testing_regime in testing_regimes:
        comparison_regime = results_pivoted.loc[(slice(None), slice(None), testing_regime), prop]
        comparison_regime = comparison_regime.reset_index(level=2)[prop]
        relative_diff = comparison_regime.subtract(control).divide(control)
        relative_diff = relative_diff.multiply(100)
        relative_diff.name = str(prop)
        relative_diff = relative_diff.to_frame()
        relative_diff['Testing Regime'] = testing_regime
        if (prop == '1.0' and testing_regime == 'No Testing'):
            relative_diff[prop] = None
        relative_diff = relative_diff.set_index('Testing Regime', append=True)
        relative_diffs[prop].append(relative_diff)

relative_diffs = {key:pd.concat(serries_list, axis=0) for key, serries_list in relative_diffs.items()}
relative_diffs = pd.concat(relative_diffs.values(), axis=1)
relative_diffs = relative_diffs.stack()
relative_diffs.name = 'people'
relative_diffs = relative_diffs.reset_index()
relative_diffs.rename(columns={'level_3':'Proportion Effectively Vaccinated'}, inplace=True)

#%%
plt.figure()
figC = sns.catplot(data=relative_diffs,
                   height=7, aspect=0.9,
                   x='people', y='Proportion Effectively Vaccinated',
                   margin_titles=False,
                   col='Output', col_order=outputs, col_wrap=2, hue='Testing Regime',
                   hue_order=testing_regimes,
                   sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = figC.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + outputs[index].title())
figC.set_titles(col_template="", row_template="")
sns.move_legend(figC, "upper left", bbox_to_anchor=(0.875, 0.55))
plt.savefig(fig_dir+'Relative Diff Boxplots testing regimes and props vaccinated.png')

# Plotting control figure
control_results = results_reshaped[(results_reshaped.Prop_Effec_Vaccinated=='1.0') &
                                   (results_reshaped['Testing Regime']=='No Testing')]
plt.figure()
figC = sns.catplot(data=control_results,
                   height=7, aspect=0.9,
                   x='people',
                   margin_titles=False, color=palette_dict['No Testing'],
                   col='Output', col_order=outputs, col_wrap=2,
                   sharex=False, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = figC.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = outputs[index].title())
figC.set_titles(col_template="", row_template="")
plt.savefig(fig_dir+'Control of Relative Diff Boxplots testing regimes and props vaccinated.png')

#%%
# plotting just Total Infections and Hospitalisations

plt.figure()
plotting_df = relative_diffs[relative_diffs['Proportion Effectively Vaccinated'].isin(['0.0','0.25'])]
figB = sns.catplot(data=plotting_df,
                   height=3, aspect=1.8,
                   x='people', y='Proportion Effectively Vaccinated',
                   margin_titles=False,legend=False,
                   col='Output', col_order=just_totals_outputs, col_wrap=2, hue='Testing Regime',
                   hue_order=testing_regimes,
                   sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = figB.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + just_totals_outputs[index].title())
figB.set_titles(col_template="", row_template="")
plt.figtext(0.025, 0.05, s='B:', fontdict={'fontsize':'xx-large',
                                           'fontweight':'bold'})
plt.savefig(fig_dir+'Relative Diff Boxplots testing regimes and props vaccinated (Totals) 1.png')
# plt.show()
plt.figure()
plotting_df = relative_diffs[relative_diffs['Proportion Effectively Vaccinated'].isin(['0.5','0.75'])]
figC = sns.catplot(data=plotting_df,
                   height=3, aspect=1.8,
                   x='people', y='Proportion Effectively Vaccinated',
                   margin_titles=False,legend=False,
                   col='Output', col_order=just_totals_outputs, col_wrap=2, hue='Testing Regime',
                   hue_order=testing_regimes,
                   sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = figC.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + just_totals_outputs[index].title())
figC.set_titles(col_template="", row_template="")
plt.figtext(0.025, 0.05, s='C:', fontdict={'fontsize':'xx-large',
                                           'fontweight':'bold'})
plt.savefig(fig_dir+'Relative Diff Boxplots testing regimes and props vaccinated (Totals) 2.png')
# plt.show()

plt.figure()
figA = sns.catplot(data=control_results,
                   height=1.5, aspect=1.9,
                   x='people',
                   margin_titles=False, color=palette_dict['No Testing'],
                   col='Output', col_order=just_totals_outputs, col_wrap=2,
                   sharex=False, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = figA.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = outputs[index].title())
figA.set_titles(col_template="", row_template="")
plt.figtext(0.01, 0.01, s='A:', fontdict={'fontsize':'small',
                                          'fontweight':'bold'})
legend_info = figC.axes[0].get_legend_handles_labels()
plt.legend(*figC.axes[0].get_legend_handles_labels(), loc= (0.8,0.85))
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig(fig_dir+'Control of Relative Diff Boxplots testing regimes and props vaccinated (Totals).png')

