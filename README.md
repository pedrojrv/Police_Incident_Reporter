# Police Incident Reporter


This repository hosts an unofficial SFPD incident reporter website:

- https://pedrojrv.github.io/sfpd_incident_reporter/

This website was created for educational purposes. The database is updated daily at 10:00 AM PST. The repository, and consequently the website, are also updated daily by simply running the `src/updater.py` script. More information on the official dataset can be found in the following websites:

- https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783
- https://data.sfgov.org/profile/edit/developer_settings
- https://dev.socrata.com/foundry/data.sfgov.org/wg3w-h783

The `notebook` directory contains the `main.ipynb` notebook. It contains all the code necessary for creating and updating the website. It is the same code as in the `src/updater.py`. 

# Machine Learning

In this project we trained a series of algorithms including decision trees, support vector machines, and k-nearest neighbors to predict future crime rates in the city of San Francisco. This challenge deals with a time series dataset from the SFPD database which records incidents and crime event along with other features including the incident category, police district, time, and more. Due to recent modernizations, this particular database was commissioned in 2018. To present, there are only approximately 450,000 datapoints. The objective is to predict the daily incidents therefore reducing the dataset to only 12000 points (grouped by day). 

Simpler algorithms like decision trees and support vector machines work well with datasets of this size. SVMs in particular are very powerful but are limited due to the computational complexity that rapidly increases with the number of training samples. These are appropriate to predict day-level predictions (due to reduction in data size). KNN models are also widely used in various tasks related to pattern recognition and were therefore also tested.

Grid search with cross validation was used to search for the best set of parameters in all three models. While all models are closely competing, KNN were the clear winner with a Mean Absolute Error of 7.6. 

<center>

| Algorithm      | Validation MAE |
| ----------- | ----------- |
| Decision Trees      | 7.86295       |
| K-Nearest Neighbors   | 7.45178        |
| Support Vector Machines   | 7.66604        |

</center>

Advance algorithms like LSTMs and RNNs are appropriate for these types of time-series dataset. However, the type of algorithm is somewhat constrained by the dataset size. For DNNs, larger amounts of data are preferred and were therefore not tested here. 

# Contact

Pedro Vicente-Valdez

e-mail: vicentepedrojr@gmail.com

