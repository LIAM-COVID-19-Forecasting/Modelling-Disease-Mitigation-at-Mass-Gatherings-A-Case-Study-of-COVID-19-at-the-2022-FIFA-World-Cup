"""
Creation:
    Author: Martin Grunnill
    Date: 2023-01-25
Description: Derivation of Basic Reproductive Number (R0) and beta given R0 for model described in manuscript.
             For methods see:
             Diekmann, O., Heesterbeek, J. A. P., & Roberts, M. G. (2010). The construction of next-generation matrices
             for compartmental epidemic models. Journal of the Royal Society Interface, 7(47), 873–885.
             https://doi.org/10.1098/rsif.2009.0386
    
"""
import sympy

all_params = ['epsilon_1', 'gamma_A_1', 'p_s', 'gamma_I_1', 'epsilon_2', 'gamma_I_2', 'alpha',
                  'p_h_s', 'epsilon_H', 'epsilon_3', 'N', 'theta', 'gamma_A_2', 'gamma_H', 'beta']
all_states = ['S', 'E', 'G_I', 'G_A', 'P_I', 'P_A', 'M_H', 'M_I', 'M_A', 'F_H', 'F_I', 'F_A', 'R']

for list_of_symbols in [all_params, all_states]:
    for symbol in list_of_symbols:
        exec(symbol + ' = sympy.symbols("'+symbol +'")')

odes = sympy.Matrix([[R*alpha - S*beta*(F_A*theta + F_I + M_A*theta + M_H + M_I + P_A*theta + P_I*theta)/N],
                     [-E*epsilon_1*p_s - E*epsilon_1*(1 - p_s) + S*beta*(F_A*theta + F_I + M_A*theta + M_H + M_I + P_A*theta + P_I*theta)/N],
                     [E*epsilon_1*p_s - G_I*epsilon_2],
                     [E*epsilon_1*(1 - p_s) - G_A*epsilon_2],
                     [G_I*epsilon_2 - P_I*epsilon_3*p_h_s - P_I*epsilon_3*(1 - p_h_s)],
                     [G_A*epsilon_2 - P_A*epsilon_3],
                     [-M_H*epsilon_H + P_I*epsilon_3*p_h_s],
                     [-M_I*gamma_I_1 + P_I*epsilon_3*(1 - p_h_s)],
                     [-M_A*gamma_A_1 + P_A*epsilon_3],
                     [-F_H*gamma_H + M_H*epsilon_H],
                     [-F_I*gamma_I_2 + M_I*gamma_I_1],
                     [-F_A*gamma_A_2 + M_A*gamma_A_1],
                     [F_A*gamma_A_2 + F_H*gamma_H + F_I*gamma_I_2 - R*alpha]])

infecteds = odes[1:-1]
infecteds = sympy.Matrix(odes[1:-1])
infecteds = infecteds.subs(S, N)
infecteds_jacobian = infecteds.jacobian(X=[E,
                                           G_I, G_A,
                                           P_I, P_A,
                                           M_H, M_I, M_A,
                                           F_H, F_I, F_A
                                           ])

# e.g. removing people becoming infected from the jacobian above.
Sigma = infecteds_jacobian.subs(beta, 0)
Sigma

# Obtainning matrix  of transitions into of infectious stages (T)
# E.g. removing people transitioning from the jacobian above.
# Suggest not use T to name a variable could be confused with transpose of a matrix.
T_inf_births_subs = {eval(param):0
                     for param in all_params
                     if param not in ['beta', 'theta', 'kappa']}
T_inf_births = infecteds_jacobian.subs(T_inf_births_subs)
T_inf_births

# Obtainning Next Geneation Matrix
Sigma_inv = Sigma**-1 # note for powers in python it is ** not ^.
neg_Sigma_inv = -Sigma_inv

K_L = T_inf_births*neg_Sigma_inv
K_L

# Finally the Basic Reproductive Number
eigen_values = K_L.eigenvals()
eigen_values
none_zero_eigen_values = [item for item in eigen_values.keys() if item !=0]
eq_R0 = none_zero_eigen_values[0]
#%%
eq_R0 = sympy.simplify(eq_R0)

#%%
# Dervining Beta

R0 = sympy.symbols('R0')
eq_R0 = sympy.Eq(eq_R0, R0)
beta_eq = sympy.solve(eq_R0, beta)
beta_eq = beta_eq[0]
#%%
beta_eq = sympy.simplify(beta_eq)