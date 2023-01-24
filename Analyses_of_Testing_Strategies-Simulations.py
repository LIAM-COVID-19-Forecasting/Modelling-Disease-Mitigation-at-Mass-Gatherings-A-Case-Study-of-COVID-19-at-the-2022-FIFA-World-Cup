"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-09
Description: Running testing scenarios along with Latin Hypercube Sampling.

Code adapted from function LH_sampling.LHS_and_PRCC.LHS_and_PRCC_parallel to run method outlined in
'Analyses of Testing Strategies' section of manuscript.
"""
import pandas as pd
from utils.load_variables_and_parameters import load_parameters
from LH_sampling.LHS_and_PRCC_parallel import run_samples_in_parrallell
from LH_sampling.LHS_and_PRCC_serial import format_sample
from scipy.stats import qmc
import os
from simulations.sports_match_sim import SportMatchMGESimulation

if __name__ == '__main__':
    parameters_df, fixed_parameters = load_parameters()
    other_samples_to_repeat = None
    sample_size = 10
    save_dir = 'C:/Data/World Cup Modelling Test Changes' #  directory for saving resuls into.
    save_dir = save_dir + '/Assesing testing regimes with LH sample Size ' + str(sample_size)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    LH_sample_file = save_dir+'/LH sample.csv'
    if os.path.isfile(LH_sample_file):
        sample_df = pd.read_csv(LH_sample_file)
        parameters_sampled = sample_df.columns.to_list()
        parameters_sampled.remove('Sample Number')
    else:
        LHS_obj = qmc.LatinHypercube(len(parameters_df))
        LH_sample = LHS_obj.random(sample_size)
        sample_df, parameters_sampled = format_sample(parameters_df, LH_sample, other_samples_to_repeat)
        sample_df.index.name = 'Sample Number'
        sample_df.reset_index(level=0,inplace=True)
        sample_df.to_csv(LH_sample_file, index=False)


    testing_regimes = {'No Testing': {'Pre-travel RTPCR': False,
                                      'Pre-match RTPCR': False,
                                      'Pre-travel RA': False,
                                      'Pre-match RA': False},
                       'Pre-travel RTPCR':{'Pre-travel RTPCR': True,
                                           'Pre-match RTPCR': False,
                                           'Pre-travel RA': False,
                                           'Pre-match RA': False},
                       'Pre-match RTPCR': {'Pre-travel RTPCR': False,
                                           'Pre-match RTPCR': True,
                                           'Pre-travel RA': False,
                                           'Pre-match RA': False},
                       'Pre-travel RA': {'Pre-travel RTPCR': False,
                                         'Pre-match RTPCR': False,
                                         'Pre-travel RA': True,
                                         'Pre-match RA': False},
                       'Pre-match RA': {'Pre-travel RTPCR': False,
                                        'Pre-match RTPCR': False,
                                        'Pre-travel RA': False,
                                        'Pre-match RA': True},
                       'Double RTPCR': {'Pre-travel RTPCR': True,
                                        'Pre-match RTPCR': True,
                                        'Pre-travel RA': False,
                                        'Pre-match RA': False},
                       'Double RA': {'Pre-travel RTPCR': False,
                                     'Pre-match RTPCR': False,
                                     'Pre-travel RA': True,
                                     'Pre-match RA': True},
                       'RTPCR then RA': {'Pre-travel RTPCR': True,
                                         'Pre-match RTPCR': False,
                                         'Pre-travel RA': False,
                                         'Pre-match RA': True},
                       'RA then RTPCR': {'Pre-travel RTPCR': False,
                                         'Pre-match RTPCR': True,
                                         'Pre-travel RA': True,
                                         'Pre-match RA': False}
                       }  # Information on testing regimes.
    for testing_regime, test_parmeters in testing_regimes.items():
        regime_save_dir = save_dir + '/' + testing_regime
        if not os.path.exists(regime_save_dir):
            os.makedirs(regime_save_dir)
        fixed_parameters.update(test_parmeters)
        model_or_simulation_obj = SportMatchMGESimulation(fixed_parameters=fixed_parameters)
        model_run_method = model_or_simulation_obj.run_simulation
        samples_already_run = []
        for sample_num in range(len(sample_df)):
            focused_output_file = regime_save_dir +'/Focused Outputs and Sample ' + str(sample_num)+ '.csv'
            if os.path.isfile(focused_output_file):
                samples_already_run.append(sample_num)

        samples_not_run_df = sample_df[~sample_df['Sample Number'].isin(samples_already_run)]

        if len(samples_not_run_df)>0:
            run_samples_in_parrallell(samples_not_run_df, model_run_method,
                                      save_dir=regime_save_dir, return_full_results=True)






