"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-29
Description: Running increasing proportions effectivly vaccination through LHS.

Code adapted from function LH_sampling.LHS_and_PRCC.LHS_and_PRCC_parallel to run method outlined in
'Analyses of Travel Vaccination Restrictions' section of manuscript.
"""
import pandas as pd
from simulation_classes.inernational_sports_match.load_variables_and_parameters import load_parameters
from LH_sampling.LHS_and_PRCC_parallel import run_samples_in_parrallell
from LH_sampling.LHS_and_PRCC_serial import format_sample
from scipy.stats import qmc
import os
from simulation_classes.inernational_sports_match.sports_match_sim import SportMatchMGESimulation
import multiprocessing

if __name__ == '__main__':
    max_workers = multiprocessing.cpu_count()
    parameters_df, fixed_parameters = load_parameters()
    parameters_df = parameters_df[~parameters_df.index.isin(['v_A','v_B'])]
    other_samples_to_repeat = None
    sample_size = 10000
    props_effectivly_vaccinated = [0.0, 0.25, 0.5, 0.75, 1.0]
    save_dir = 'C:/Data/World Cup Modelling'  #  directory for saving resuls into.
    save_dir = save_dir + '/Assesing vaccination with LH sample Size ' + str(sample_size)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    LH_sample_file = save_dir+'/LH sample.csv'
    if os.path.isfile(LH_sample_file):
        sample_df = pd.read_csv(LH_sample_file)
        parameters_sampled = sample_df.columns.to_list()
        parameters_sampled.remove('Sample Number')
    else:
        LHS_obj = qmc.LatinHypercube(len(parameters_df)+1) # the +1 is for generation of seed for multinomial seeding
        # of infections. This ensures same seeding of infections in an LH sample.
        # seeding of infections.
        LH_sample = LHS_obj.random(sample_size)
        sample_df, parameters_sampled = format_sample(parameters_df, LH_sample, other_samples_to_repeat)
        sample_df.index.name = 'Sample Number'
        sample_df.reset_index(level=0,inplace=True)
        sample_df.to_csv(LH_sample_file, index=False)


    testing_regimes = {'No Testing': {'Pre-travel RTPCR': False,
                                      'Pre-match RTPCR': False,
                                      'Pre-travel RA': False,
                                      'Pre-match RA': False},
                       'RTPCR then RA high': {'Pre-travel RTPCR': True,
                                              'Pre-match RTPCR': False,
                                              'Pre-travel RA': False,
                                              'Pre-match RA': True},
                       'Pre-travel RTPCR':{'Pre-travel RTPCR': True,
                                           'Pre-match RTPCR': False,
                                           'Pre-travel RA': False,
                                           'Pre-match RA': False},
                       'Pre-match RA high': {'Pre-travel RTPCR': False,
                                             'Pre-match RTPCR': False,
                                             'Pre-travel RA': False,
                                             'Pre-match RA': True}
                       }  # Information on testing regimes.

    for testing_regime, test_parmeters in testing_regimes.items():
        regime_save_dir = save_dir + '/' + testing_regime
        if not os.path.exists(regime_save_dir):
            os.makedirs(regime_save_dir)
        for prop_effectivly_vaccinated in props_effectivly_vaccinated:
            prop_vaccinated_save_dir = regime_save_dir + '/Prop Effectively vaccinated ' + str(prop_effectivly_vaccinated)
            if not os.path.exists(prop_vaccinated_save_dir):
                os.makedirs(prop_vaccinated_save_dir)
            fixed_parameters.update(test_parmeters)
            fixed_parameters.update({'v_A': prop_effectivly_vaccinated,
                                     'v_B': prop_effectivly_vaccinated})
            model_or_simulation_obj = SportMatchMGESimulation(fixed_parameters=fixed_parameters)
            model_run_method = model_or_simulation_obj.run_simulation
            samples_already_run = []
            for sample_num in range(len(sample_df)):
                focused_output_file = prop_vaccinated_save_dir +'/Focused Outputs and Sample ' + str(sample_num)+ '.csv'
                if os.path.isfile(focused_output_file):
                    samples_already_run.append(sample_num)

            samples_not_run_df = sample_df[~sample_df['Sample Number'].isin(samples_already_run)]

            if len(samples_not_run_df) > 0:
                run_samples_in_parrallell(samples_not_run_df, model_run_method, max_workers=max_workers,
                                          save_dir=prop_vaccinated_save_dir, return_full_results=True)
