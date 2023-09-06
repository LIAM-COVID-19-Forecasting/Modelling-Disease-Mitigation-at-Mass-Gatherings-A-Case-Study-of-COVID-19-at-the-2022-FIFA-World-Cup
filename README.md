# Modelling-Disease-Mitigation-at-Mass-Gatherings-A-Case-Study-of-COVID-19-at-the-2022-FIFA-World-Cup

Supplementary Material for article Modelling Disease Mitigation at Mass Gatherings: A Case Study of COVID-19 at the 2022 FIFA World Cup.


## Required Packages
- scipy
- numpy
- pandas
- tqdm
- pingouin
- sympy (Only required to run meta_population_models\reproductive_numbers\MGE_single_population_derivation.py)

## Contents

### event_handling 
- event_que.py : Event queue described in Event Queue section of manuscript. 
- events.py : Events described in 'Event Queue' and 'Simulation of a FIFA 2022 World Cup Match' section of manuscript.

### LH_sampling
Code for Latin Hypercube sampling, simulating parameter samples via parallel processing and performing Partial
Correlation Coefficient analyses.

### meta_population_models
- base_meta_structure.py : Generalisable Framework for Models with stratified populations.
- mass_gathering_model.py : Core ODE model outlined in manuscript.
- meta_population_structures : Contains code for generating and json file outlining metapopulation structure described
sections Vaccine Groups and Clusters of manuscript.
- reproductive_numbers : Derivation of models R0 and beta, under no stratification of population or vaccination, as well
as functions for calculating them.

### Qatars_COVID_Cases_During_World_Cup
Contains code producing figures of detected, hospitalised and ICU cases of COVID-19 in Qatar around the time of the
World Cup. 

### seeding_infections
Code for probabilistic seeding of infections into multi-infection branch/pathway model.

### simulation_classes
Classes and function that bring together code in meta_population_models and event_handling to simulate Mass Gathering
events. The sub-directory international_sport_match simulate the model and events outlined in the 'Simulation of a FIFA
2022 World Cup Match' section of the manuscript.

### Running_and_analysing_simulations
- Analyses_of_Testing_Strategies_Simulations.py : runs simulations outlined in
  this section of manuscript.
- Analyses_of_Testing_Strategies_Figures.py : Performs
  PCC analyses and produces figures from the results of simulations.
- Analyses_of_Travel_Vaccination_Restrictions_Simulations.py : runs simulations outlined in
  this section of manuscript.
- Analyses_of_Travel_Vaccination_Restrictions_Figures.py : Produces figures from the results of these simulations.
- parameters : Parameters used in simulations.
  - 'Parameters values in LHS Sports Match Sims.xlsx' contains parameters used in simulations.
  - Subdirectory data_extraction contains code and files for obtaining prevalence data for
    countries in FIFA 2022 world cup.




## Notes 
### Derivation of Basic Reproductive Number (R_0)
This can be found in 
meta_population_models\reproductive_numbers\MGE_single_population_derivation.py


