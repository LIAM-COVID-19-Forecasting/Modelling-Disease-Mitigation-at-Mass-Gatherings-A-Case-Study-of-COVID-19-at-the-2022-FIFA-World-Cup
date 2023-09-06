"""
Creation:
    Author: Martin Grunnill
    Date: 2022-11-02
Description: Wrapper functions for loading parameters and variables from csvs for international sports match
             simulations.
    
"""
import pandas as pd
import os

def load_parameters(file='Parameters values in LHS Sports Match Sims.xlsx',
                    directory='parameters'):
    parameters_df = pd.read_excel(directory+'/'+file, sheet_name='Sheet1',index_col='Parameter')
    fixed_params = parameters_df['Fixed Value'].dropna()
    fixed_params = fixed_params.to_dict()
    parameters_df = parameters_df[parameters_df['Fixed Value'].isnull()]
    # no waning immunity or flows of people between clusters and vaccination groups.
    parameters_held_at_0 = {param: 0
                            for param in
                            ['alpha', 'iota_{RA}', 'iota_{RTPCR}', 'nu_e', 'nu_b', 'nu_w']}
    fixed_params.update(parameters_held_at_0)
    return parameters_df, fixed_params



