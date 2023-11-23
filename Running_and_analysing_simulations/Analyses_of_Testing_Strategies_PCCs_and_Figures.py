"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-14
Description: Performing PRCC and producing figures on simulation outlined in 'Analyses of Testing Strategies' section
of manuscript. Figures presented and discussed in sections 'Effects of Testing Regimes', 'Effects of Parameters and
Starting Conditions Relating to COVID-19 control measures' and supplementary materials in manuscript.
    
"""
#%%

import pandas as pd
import copy
import os
from LH_sampling.LHS_and_PRCC_serial import calucate_PCC
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import string
import scipy

sample_size = 10000
data_dir = 'E:/World Cup Modelling'  #  directory for saving results into.
data_dir = data_dir + '/Assesing testing regimes with LH sample Size ' + str(sample_size)+'/'
fig_dir = data_dir +'Figures'
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
                   'Pre-travel RA low',
                   'Pre-travel RA mid',
                   'Pre-match RTPCR',
                   'Pre-match RA low',
                   'Pre-match RA mid',
                   'Double RTPCR',
                   'Double RA low',
                   'Double RA mid',
                   'RTPCR then RA low',
                   'RTPCR then RA mid',
                   'RA low then RTPCR',
                   'RA mid then RTPCR',
                   'No Testing'
                   ]
testing_regimes_labels = [testing_regime.replace(' ', '\n') for testing_regime in testing_regimes]
actual_testing_regimes = copy.deepcopy(testing_regimes)
actual_testing_regimes.remove('No Testing')
actual_testing_regimes_labels = [testing_regime.replace(' ', '\n') for testing_regime in actual_testing_regimes]
sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
palette_tab20b = sns.color_palette(palette='tab20b', n_colors=20)
palette_tab20 = sns.color_palette(palette='tab20', n_colors=20)
palette_set1 = sns.color_palette(palette='Set1', n_colors=9)
palette_dict = {'Pre-travel RTPCR': palette_tab20b[12],
                'Pre-travel RA low': palette_tab20b[15],
                'Pre-travel RA mid': palette_tab20b[14],
                'Pre-match RTPCR': palette_tab20b[0],
                'Pre-match RA low': palette_tab20b[3],
                'Pre-match RA mid': palette_tab20b[2],
                'Double RTPCR': palette_tab20b[4],
                'Double RA low': palette_tab20b[7],
                'Double RA mid': palette_tab20b[6],
                'RTPCR then RA low': palette_tab20[3],
                'RTPCR then RA mid': palette_tab20[2],
                'RA low then RTPCR': palette_tab20b[19],
                'RA mid then RTPCR': palette_tab20b[18],
                'No Testing': palette_set1[0]}
alphabet = list(string.ascii_lowercase) # for assigning leters to sub figures.
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
        csvs = [regime_data_dir+'Focused Outputs and Sample ' + str(index)+ '.csv' for index in range(sample_size)]
        df = pd.concat(map(pd.read_csv, csvs), ignore_index=True)
        df['Testing Regime'] = testing_regime
        results_df.append(df)

    results_df = pd.concat(results_df)
    results_df.to_csv(results_file, index=False)


#%%
# Test regime as parameter

test_PCC = []
for testing_regime in actual_testing_regimes:
    no_testing_results_df = copy.deepcopy(results_df[results_df['Testing Regime'] == 'No Testing'])
    no_testing_results_df[testing_regime] = 0
    testing_regime_results = copy.deepcopy(results_df[results_df['Testing Regime'] == testing_regime])
    testing_regime_results[testing_regime] = 1
    comparison_df = pd.concat([no_testing_results_df,testing_regime_results])
    for output in outputs:
        PCC = calucate_PCC(comparison_df,
                           parameter=testing_regime,
                           output=output,
                           covariables=parameters_sampled,
                           method='spearman')
        test_PCC.append(PCC)

test_PCC = pd.concat(test_PCC)
test_PCC.reset_index(inplace=True)
PCC_measure = test_PCC['index'].str.split(' on ', n = 1, expand = True)
test_PCC['Test Regime'] = PCC_measure[0]
test_PCC['Output'] = PCC_measure[1]
test_PCC.drop(columns=['index'],inplace=True)


#%%
plt.figure()
fig = sns.catplot(data=test_PCC, height=7, aspect=0.9,
                  hue='Test Regime', hue_order=actual_testing_regimes, palette=palette_dict,
                  x="r", y="Output", width=0.75, order=outputs, kind='bar'
                  )
fig.ax.set_xlim(-0.25,0.05)
fig.ax.set(xlabel='Partial Rank Correlation Coefficient')
fig.set_yticklabels(output_labels)

plt.tight_layout(rect=(0,0,0.8,1))
plt.savefig(fig_dir + 'Test Regime PCCs against no testing.png')

#%% Figure 2 of manuscript.
plt.figure()
fig = sns.catplot(data=test_PCC, height=7, aspect=0.9,
                  hue='Test Regime', hue_order=actual_testing_regimes, palette=palette_dict,
                  x="r", y="Output", width=0.75, order=just_totals_outputs, kind='bar'
                  )
fig.ax.set_xlim(-0.25,0.05)
fig.ax.set(xlabel='Partial Rank Correlation Coefficient')
fig.set_yticklabels(just_totals_output_labels)

plt.tight_layout(rect=(0,0,0.8,1))
plt.savefig(fig_dir + 'Fig2.eps')


#%%
# Calculating PCCs
pcc_args = []
for parameter in parameters_sampled:
    covariables = [item
                   for item in parameters_sampled
                   if item != parameter]
    for output in outputs:
        pcc_args.append((parameter, output, covariables))

PCCs = []

for testing_regime in tqdm(testing_regimes, desc='PCCs for testing regime'):
    select_results = results_df[results_df['Testing Regime'] == testing_regime]
    pccs_in_regime = []
    for parameter, output, covariables in tqdm(pcc_args, desc='PCC for parameter'):
        PCC = calucate_PCC(select_results, parameter, output, covariables, method='spearman')
        pccs_in_regime.append(PCC)


    pccs_in_regime = pd.concat(pccs_in_regime)
    pccs_in_regime.sort_index(inplace=True)
    pccs_in_regime['Test Regime'] = testing_regime
    PCCs.append(pccs_in_regime)

PCCs_df = pd.concat(PCCs)
PCCs_df.reset_index(inplace=True)
PCC_measure = PCCs_df['index'].str.split(' on ', n = 1, expand = True)
PCCs_df['Parameter'] = PCC_measure[0]
PCCs_df['Output'] = PCC_measure[1]
PCCs_df.drop(columns=['index'],inplace=True)

#%%

# Figures
orders = {'starting variable': ['N_{A}', 'eta_{spectators}', 'N_{staff}',
                                 'v_A', 'v_B',
                                 'sigma_A', 'sigma_B', 'sigma_{host}'],
          'parameter': ['R_0', 'b',
                        'l_effective', 'VE_{hos}',
                        'epsilon_H', 'gamma_H',
                        'p_s',  'p_h',
                        'kappa', 'theta']}
paramater_legends = {'starting variable': {'$N_A$': 'Number of Attendees',
                                            '$N^*_{Q}$': 'Proportion of host tickets',
                                            '$N_{S}$': 'Staff Population',
                                            '$v_A$':'Proportion Recently Vaccinated  Team A',
                                            '$v_B$':'Proportion Recently Vaccinated  Team B',
                                            '$\sigma_A$': 'Prevalence in Supporters A',
                                            '$\sigma_B$': 'Prevalence in Supporters B',
                                            '$\sigma_H$': 'Prevalence in Hosts'},
                     'parameter': {'$R_0$': 'Basic Reproduction Number',
                                     '$b$': 'Increase in Transmission Match Day',
                                     '$l_E$':'Recent Vaccine Efficacy against infection',
                                     '$VE_{h}$':'Recent Vaccine Efficacy against hospitalising infection',
                                     '$\epsilon_h$':'Rate of Hospitalisation',
                                     '$\gamma_h$':'Rate of Hospital Recovery',
                                     '$p_s$':'Proportion Symptomatic',
                                     '$p_{h|s}$':'Proportion Hospitalised given Symptomatic',
                                     '$\kappa$':'Isolation Transmission Modifier',
                                     '$\\theta$': 'Asymptomatic Transmission Modifier'}}

for name, params_or_vars in orders.items():
    plt.figure()
    fig = sns.catplot(data=PCCs_df, height=7, aspect=0.9,
                      hue='Test Regime', hue_order=testing_regimes, palette=palette_dict,
                      x="r", y="Parameter", width=0.75, order=params_or_vars, kind='bar',
                      col='Output', col_order=outputs, col_wrap=2
                      )
    fig.set(xlim=(-0.95,0.95))
    fig.axes[0].set_ylabel(name.title())
    fig.axes[2].set_ylabel(name.title())
    fig.axes[2].set_xlabel('Partial Rank Correlation Coefficient')
    fig.axes[3].set_xlabel('Partial Rank Correlation Coefficient')
    for index, ax in enumerate(fig.axes):
        ax.set_title(alphabet[index] + ': ' + outputs[index].title())
    handles, labels = ax.get_legend_handles_labels() # needed for legend of a later figure.
    fig.set_yticklabels(paramater_legends[name].keys())
    plt.tight_layout(rect=(0,0,0.875,1))
    plt.savefig(fig_dir+'PRCCs '+ name +' on outputs.png')

#%% Figure 4

params_related_to_npis = ['kappa', 'theta', 'v_A', 'v_B']
params_related_to_npis_legend = ['$\kappa$', '$\\theta$', '$v_A$', '$v_B$']
plt.figure()
fig = sns.catplot(data=PCCs_df, height=7, aspect=0.9,
                  hue='Test Regime', hue_order=testing_regimes, palette=palette_dict,
                  x="r", y="Parameter", width=0.75, order=params_related_to_npis, kind='bar',
                  col='Output', col_order=just_totals_outputs, col_wrap=2
                  )
fig.axes[0].set_ylabel(name.title())
fig.axes[1].set_ylabel(name.title())
fig.axes[0].set_xlabel('Partial Rank Correlation Coefficient')
fig.axes[1].set_xlabel('Partial Rank Correlation Coefficient')
for index, ax in enumerate(fig.axes):
    ax.set_title(alphabet[index] + ': ' + just_totals_outputs[index].title())
handles, labels = ax.get_legend_handles_labels() # needed for legend of a later figure.
fig.set_yticklabels(params_related_to_npis_legend)
plt.tight_layout(rect=(0, 0, 0.875, 1))
#plt.figtext(0.03, 0.03, s='A', fontdict={'fontsize':'x-large'})
#plt.figtext(0.46, 0.03, s='B', fontdict={'fontsize':'x-large'})
plt.savefig(fig_dir+'Fig4.eps')


#%%
# boxplots of outcomes against test regime
results_reshaped = results_df.set_index(['Testing Regime', 'Sample Number'])
results_reshaped = results_reshaped[outputs]
results_reshaped = results_reshaped.stack()
results_reshaped = results_reshaped.reset_index()
results_reshaped.rename(columns={'level_2':'Output',
                                 0:'people'},
                        inplace=True)
against_no_testing = results_reshaped[results_reshaped['Testing Regime'] != 'No Testing']
against_no_testing['Comparison'] = 'Test Regime'
no_testing = results_reshaped[results_reshaped['Testing Regime'] == 'No Testing']
no_testing['Comparison'] = 'No Testing'
for testing_regime in actual_testing_regimes:
    no_testing['Testing Regime'] = testing_regime
    against_no_testing = pd.concat([against_no_testing,no_testing])

#%%
# Need to reshape results for plotting boxplots of outcomes against test regime
results_reshaped = results_df.set_index(['Testing Regime', 'Sample Number'])
results_reshaped = results_reshaped[outputs]
results_reshaped = results_reshaped.stack()
results_reshaped = results_reshaped.reset_index()
results_reshaped.rename(columns={'level_2':'Output',
                                 0:'people'},
                        inplace=True)


results_pivoted = results_reshaped.pivot(index=['Sample Number','Output'],
                                         columns=['Testing Regime'],
                                         values='people')
#%%
relative_diffs = []
for testing_regime in actual_testing_regimes:
    relative_diff = (results_pivoted[testing_regime]-results_pivoted['No Testing'])/results_pivoted['No Testing']
    relative_diff.name = testing_regime
    relative_diffs.append(relative_diff*100)

relative_diffs = pd.concat(relative_diffs, axis=1)
relative_diffs = relative_diffs.stack()
relative_diffs.name = 'people'
relative_diffs = relative_diffs.reset_index()
relative_diffs.rename(columns={'level_2':'Testing Regime'}, inplace=True)

plt.figure()
pre_travel_regimes = ['Pre-travel RTPCR', 'Pre-travel RA low', 'Pre-travel RA mid']
other_regimes = [regime for regime in testing_regimes
                 if regime not in pre_travel_regimes + ['No Testing']]
fig = sns.catplot(data=relative_diffs[relative_diffs['Testing Regime'].isin(pre_travel_regimes)],
                  height=3.5, aspect=2,
                  x='people', y='Testing Regime', margin_titles=False,
                  col='Output', col_order=outputs, col_wrap=2,
                  sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Relative Difference Boxplots Testing regimes vs No Testing v1.png')

plt.figure()
fig = sns.catplot(data=relative_diffs[~relative_diffs['Testing Regime'].isin(pre_travel_regimes)],
                  height=7, aspect=0.9,
                  x='people', y='Testing Regime', margin_titles=False,
                  col='Output', col_order=outputs, col_wrap=2,
                  sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Relative Difference Boxplots Testing regimes vs No Testing v2.png')

plt.figure()
control_df = results_reshaped[results_reshaped['Testing Regime'] == 'No Testing']
fig = sns.catplot(data=control_df ,
                  height=7, aspect=0.9,
                  x='people', margin_titles=False,
                  col='Output', col_order=outputs, col_wrap=2,
                  sharex=False, color=palette_dict['No Testing'], kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Control Relative Difference Boxplots Testing regimes vs No Testing.png')

#%% Figure 3 of manuscript
# These sub-figures have been merged and labeled A-B-C in powerpoint for the manuscript.

# Fig3A
plt.figure()
fig = sns.catplot(data=control_df ,
                  height=1.5, aspect=1.9,
                  x='people', margin_titles=False,
                  col='Output', col_order=just_totals_outputs, col_wrap=2,
                  sharex=False, color=palette_dict['No Testing'], kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Fig3A.png')

# Fig3B
plt.figure()
fig = sns.catplot(data=relative_diffs[relative_diffs['Testing Regime'].isin(pre_travel_regimes)],
                  height=2, aspect=3,
                  x='people', y='Testing Regime', margin_titles=False,
                  col='Output', col_order=just_totals_outputs, col_wrap=2,
                  sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + just_totals_outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Fig3B.png')

plt.figure()
fig = sns.catplot(data=relative_diffs[~relative_diffs['Testing Regime'].isin(pre_travel_regimes)],
                  height=7, aspect=0.9,
                  x='people', y='Testing Regime', margin_titles=False,
                  col='Output', col_order=just_totals_outputs, col_wrap=2,
                  sharex=False, palette=palette_dict, kind="box", showmeans=True, meanprops=box_plot_mean_marker)
axes = fig.axes
for index, ax in enumerate(axes):
    ax.set(xlabel = '% Difference in ' + just_totals_outputs[index].title())
fig.set_titles(col_template="", row_template="")
plt.tight_layout()
plt.savefig(fig_dir+'Fig3C.png')




#%%
# Checking that increasing proportion effectivly vaccinated is a
# singificant improvements on the best testing regime.

def PCC_significant_diffs(df_1,df_2, output_field):
    """
    Funcation for checking if differences between two sets of PCCs are significant.
    """
    df_1 = df_1.set_index(output_field)
    df_2 = df_2.set_index(output_field)
    correlation_diffs = df_1.r.subtract(df_2.r)
    correlation_diffs.name = 'Differences in PCC'
    denominator_part_1 = 1/(df_1.n-3-df_1.Number_of_Covariables)
    denominator_part_2 = 1/(df_2.n-3-df_2.Number_of_Covariables)
    denominator = (denominator_part_1+denominator_part_2)**(1/2)
    z_scores = correlation_diffs/denominator
    correlation_diffs = correlation_diffs.to_frame()
    correlation_diffs['z-score'] = z_scores
    correlation_diffs['p_value (one tailed)'] = scipy.stats.norm.sf(abs(z_scores))
    correlation_diffs['p_value (two tailed)'] = correlation_diffs['p_value (one tailed)']*2
    return correlation_diffs

best_test_regime = []
for output in outputs:
    pcc_for_output = test_PCC[test_PCC.Output==output]
    lowest_pcc_for_output = pcc_for_output[pcc_for_output.r==min(pcc_for_output.r)]
    best_test_regime.append(lowest_pcc_for_output)

best_test_regime = pd.concat(best_test_regime)
# For all of them it is 'RTPCR then RA'.
# But we can do for all easily enough.

sig_diffs_lst =[]
for testing_regime in actual_testing_regimes:
    selected_test_regime_PCC = test_PCC[test_PCC['Test Regime']==testing_regime]
    for parameter in ['v_A','v_B']:
        selected_PCCs = PCCs_df[(PCCs_df.Parameter==parameter)&(PCCs_df['Test Regime']=='No Testing')]
        correlation_diffs = PCC_significant_diffs(selected_test_regime_PCC,
                                                  selected_PCCs, output_field='Output')
        correlation_diffs['Test Regime'] = testing_regime
        correlation_diffs['Proportion Effectively Vaccinated'] = parameter
        sig_diffs_lst.append(correlation_diffs)

sig_diffs_df = pd.concat(sig_diffs_lst)
sig_diffs_df.reset_index(inplace=True)
desired_columns = ['Test Regime',
                   'Proportion Effectively Vaccinated',
                   'Output', 'Differences in PCC',
                   'z-score', 'p_value (one tailed)', 'p_value (two tailed)']
sig_diffs_df = sig_diffs_df[desired_columns]
sig_diffs_df_va = sig_diffs_df[sig_diffs_df['Proportion Effectively Vaccinated'] == 'v_A'].drop(columns='Proportion Effectively Vaccinated')
sig_diffs_df_va.to_csv(fig_dir+'S1 Table Differences in PCCs between proportions of Team A visitor effectively vaccinated and different testing regimes.csv',
                       index=False)
sig_diffs_df_vb = sig_diffs_df[sig_diffs_df['Proportion Effectively Vaccinated'] == 'v_B'].drop(columns='Proportion Effectively Vaccinated')
sig_diffs_df_vb.to_csv(fig_dir+'S2 Table Differences in PCCs between proportions of Team B visitor effectively vaccinated and different testing regimes.csv',
                       index=False)


