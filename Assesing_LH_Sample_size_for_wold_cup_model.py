"""
Creation:
    Author: Martin Grunnill
    Date: 2023-01-23
Description: 
    
"""

from LH_sampling.LHS_and_PRCC_parallel import LHS_and_PRCC_parallel
from utils.load_variables_and_parameters import load_parameters
import multiprocessing
import os
from simulations.sports_match_sim import SportMatchMGESimulation
from LH_sampling.asses_LH_sample_size import determine_LH_sample_size

if __name__ == '__main__':
    max_workers = multiprocessing.cpu_count()
    parameters_df, fixed_parameters = load_parameters()
    save_dir = ('C:/Data/World Cup Modelling')
    save_dir = save_dir +'/Determining Adaquate LH Size'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    repeats_per_n = 10
    sample_size = 10000
    std_aim = 0.025
    n_increase_addition = 2000
    testing_regimes = {'No Testing': {'Pre-travel RTPCR': False,
                                      'Pre-match RTPCR': False,
                                      'Pre-travel RA': False,
                                      'Pre-match RA': False},
                       'Pre-travel RTPCR': {'Pre-travel RTPCR': True,
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
                       }
    for testing_regime, test_parmeters in testing_regimes.items():
        regime_save_dir = save_dir + '/' + testing_regime
        if not os.path.exists(regime_save_dir):
            os.makedirs(regime_save_dir)
        fixed_parameters.update(test_parmeters)
        model_or_simulation_obj = SportMatchMGESimulation(fixed_parameters=fixed_parameters)
        model_run_method = model_or_simulation_obj.run_simulation
        sample_size = determine_LH_sample_size(parameters_df=parameters_df,
                                               model_run_method=model_run_method,
                                               start_n=sample_size,
                                               repeats_per_n=repeats_per_n,
                                               std_aim=std_aim,
                                               LHS_PRCC_method=LHS_and_PRCC_parallel,
                                               n_increase_addition=n_increase_addition,
                                               save_dir=regime_save_dir,
                                               max_workers=max_workers)