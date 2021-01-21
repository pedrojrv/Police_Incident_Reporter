# Police Incident Reporter

First created as part of the <b>visualization course</b> of the IBM Data Science Specialization, this website was further developed to 
provide information on incident and crime rate in various districts of the San Francisco area. Based on Python and JavaScript, 
the website offers various graphics and even ML-powered crime rate predictions. Several models including Decision Trees, 
K-Nearest-Neighbors, and Support Vector Machines were trained and optimized using grid search with cross validation due to the 
dataset size (~12,000 datapoints).
The webapp refreshes daily by querying and processing data from the official SFPD database.

This repository hosts an unofficial SFPD incident reporter website:

- https://pedrojrv.github.io/sfpd_incident_reporter/

This website was created for educational purposes. The database is updated daily at 10:00 AM PST. The repository, and consequently the website, are also updated daily by simply running the `src/updater.py` script. 

# Dataset Source

More information on the official dataset can be found in the following websites:

- https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783
- https://data.sfgov.org/profile/edit/developer_settings
- https://dev.socrata.com/foundry/data.sfgov.org/wg3w-h783

The `notebook` directory contains the `main.ipynb` notebook. It contains all the code necessary for creating and updating the website. It is the same code as in the `src/updater.py`. 

# Machine Learning

In this project we trained a series of algorithms including decision trees, support vector machines, and k-nearest neighbors to predict future crime rates in the city of San Francisco. This challenge deals with a time series dataset from the SFPD database which records incidents and crime event along with other features including the incident category, police district, time, and more. Due to recent modernizations, this particular database was commissioned in 2018. To present, there are only approximately 450,000 datapoints. The objective is to predict the daily incidents therefore reducing the dataset to only 12000 points (grouped by day). 

Simpler algorithms like decision trees and support vector machines work well with datasets of this size. SVMs in particular are very powerful but are limited due to the computational complexity that rapidly increases with the number of training samples. These are appropriate to predict day-level predictions (due to reduction in data size). KNN models are also widely used in various tasks related to pattern recognition and were therefore also tested.

Grid search with cross validation was used to search for the best set of parameters in all three models. Decision Trees frequently overfitted the dataset, even after applying heavier regularization. Support Vector Machines showed robustness towards overfitting and good generalization. However, in almost all instances, KNN models outperformed both DTs and SVMs. The best KNN model had a Mean Absolute Error of 7.6 crimes per day on the validation set as seen in the table below.

<center>

| Algorithm (Best Model)     | Validation MAE |
| ----------- | ----------- |
| Decision Trees      | 7.86295       |
| K-Nearest Neighbors   | 7.45178        |
| Support Vector Machines   | 7.66604        |

</center>

Advance algorithms like LSTMs and RNNs are also appropriate for these types of time-series dataset. However, these types of algorithm may not be trained effectively due to the dataset size. For DNNs, larger amounts of data are preferred and were therefore not tested here. 

# Contact

Pedro Vicente-Valdez

e-mail: vicentepedrojr@gmail.com

