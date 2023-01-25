"""
Creation:
    Author: Martin Grunnill
    Date: 28/09/2022
Description: Functions for calculating Reproductive numbers and Beta for model described in manuscript.
             See MGE_single_population_derivation.py for dervation.
    
"""


def MGE_R_0_no_vaccine_1_cluster(beta, theta,
                                epsilon_3, epsilon_H,
                                gamma_A_1, gamma_A_2, gamma_I_1, gamma_I_2,
                                p_h_s, p_s):
    """
    Calculates R_0 for Mass gathering event assuming 1 homogenous population.
    Here 1 homogenous population means:
      - 1 cluster
      - No vaccination therefore 1 vaccine group.

    See MGE_single_population_derivation.py for derivation.

    Parameters
    ----------
    beta : float
        Model parameter see manuscript section Disease Stages.
    theta : float
        Model parameter see manuscript section Disease Stages.
    epsilon_3 : float
        Model parameter see manuscript section Disease Stages.
    epsilon_H : float
        Model parameter see manuscript section Disease Stages.
    gamma_A_1 : float
        Model parameter see manuscript section Disease Stages.
    gamma_A_2 : float
        Model parameter see manuscript section Disease Stages.
    gamma_I_1 : float
        Model parameter see manuscript section Disease Stages.
    gamma_I_2 : float
        Model parameter see manuscript section Disease Stages.
    p_h_s : float
        Model parameter see manuscript section Disease Stages.
    p_s : float
        Model parameter see manuscript section Disease Stages.

    Returns
    -------
    R0 : float
        Calculated R0.
    """
    R_0 = (-beta*p_h_s*p_s/gamma_I_2 + beta*p_s/gamma_I_2 -
           beta*p_h_s*p_s/gamma_I_1 + beta*p_s/gamma_I_1 -
           beta*p_s*theta/gamma_A_2 + beta*theta/gamma_A_2 -
           beta*p_s*theta/gamma_A_1 + beta*theta/gamma_A_1 +
           beta*p_h_s*p_s/epsilon_H +
           beta*theta/epsilon_3)
    return R_0

def MGE_beta_no_vaccine_1_cluster(R_0, theta,
                                  epsilon_3, epsilon_H,
                                  gamma_A_1, gamma_A_2, gamma_I_1, gamma_I_2,
                                  p_h_s, p_s):
    """
    Calculates beta for Mass gathering event assuming 1 homogenous population.
    Here 1 homogenous population means:
      - 1 cluster
      - No vaccination therefore 1 vaccine group.

    See MGE_single_population_derivation.py for derivation.


    Parameters
    ----------
    R_0 : float
        Model parameter see manuscript section Disease Stages.
    theta : float
        Model parameter see manuscript section Disease Stages.
    epsilon_3 : float
        Model parameter see manuscript section Disease Stages.
    epsilon_H : float
        Model parameter see manuscript section Disease Stages.
    gamma_A_1 : float
        Model parameter see manuscript section Disease Stages.
    gamma_A_2 : float
        Model parameter see manuscript section Disease Stages.
    gamma_I_1 : float
        Model parameter see manuscript section Disease Stages.
    gamma_I_2 : float
        Model parameter see manuscript section Disease Stages.
    p_h_s : float
        Model parameter see manuscript section Disease Stages.
    p_s : float
        Model parameter see manuscript section Disease Stages.

    Returns
    -------
    beta : float
        Calculated beta.
    """
    numrator = R_0*epsilon_3*epsilon_H*gamma_A_1*gamma_A_2*gamma_I_1*gamma_I_2
    denominator = (-epsilon_3*epsilon_H*gamma_A_1*gamma_A_2*gamma_I_1*p_h_s*p_s +
                   epsilon_3*epsilon_H*gamma_A_1*gamma_A_2*gamma_I_1*p_s -
                   epsilon_3*epsilon_H*gamma_A_1*gamma_A_2*gamma_I_2*p_h_s*p_s +
                   epsilon_3*epsilon_H*gamma_A_1*gamma_A_2*gamma_I_2*p_s -
                   epsilon_3*epsilon_H*gamma_A_1*gamma_I_1*gamma_I_2*p_s*theta +
                   epsilon_3*epsilon_H*gamma_A_1*gamma_I_1*gamma_I_2*theta -
                   epsilon_3*epsilon_H*gamma_A_2*gamma_I_1*gamma_I_2*p_s*theta +
                   epsilon_3*epsilon_H*gamma_A_2*gamma_I_1*gamma_I_2*theta +
                   epsilon_3*gamma_A_1*gamma_A_2*gamma_I_1*gamma_I_2*p_h_s*p_s +
                   epsilon_H*gamma_A_1*gamma_A_2*gamma_I_1*gamma_I_2*theta)

    return numrator/denominator