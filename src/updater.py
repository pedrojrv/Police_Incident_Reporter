# Creating an Incident Reporter with Python
## Importing Packages

import pandas as pd
from sodapy import Socrata
import folium
import json
import plotly.express as px
from datetime import datetime, timedelta
import sys
sys.path.append("..")

# The config file is hidden since it contains the api key 
# needed to get data from the sfpd database
import src.config as config

## Setting up the Client and Querying the Database

client = Socrata("data.sfgov.org",
                 config.api_key,
                 username=config.username,
                 password=config.password)


results = client.get("wg3w-h783", limit=15000, order="incident_date DESC")


## Data Processing
# First we convert the response to a pandas dataframe followed by formating the datetime
results_df = pd.DataFrame.from_records(results)
results_df['incident_datetime'] = pd.to_datetime(results_df['incident_datetime'])

### District Specific Information 


# Since we only care about crime rate we just need the time and the district of the event
district_df = results_df[["incident_datetime", "police_district"]]
# Each row represents an event
district_df["Count"] = 1
# Formatting the datetime
district_df["incident_datetime"] = district_df.incident_datetime.dt.date
# Grouping the data by date and district
district_df = district_df.groupby(['incident_datetime','police_district'], as_index=False)['Count'].sum()
district_df.incident_datetime = district_df.incident_datetime.astype(str)

### Total Crime Rate
total_df = results_df[["incident_datetime"]]
total_df["Count"] = 1
# This groups the dataset by day
total_df = total_df.groupby(total_df.incident_datetime.dt.date)[['Count']].sum()
total_df = total_df.iloc[1:]
total_df = total_df.reset_index()
total_df.incident_datetime = total_df.incident_datetime.astype(str)

#### Getting the Rolling Average
mean = total_df.rolling(5).mean().fillna(method="backfill")

### Adding two more days for ML inference
# Here we extract the last day avaliable in the dataset
d = datetime.strptime(total_df.incident_datetime.values[-1].replace("-", "/"), "%Y/%m/%d")
# Then, we create 2 more rows belonging to two more days after the last date avaliable
rng = pd.date_range(d, periods=3, freq='d')
rng = pd.to_datetime(rng, format='%Y%m%d')

# We transform the new dates into a dataframe
to_append = pd.DataFrame({'incident_datetime': rng}) 
to_append["incident_datetime"] = to_append.incident_datetime.dt.date
to_append = to_append.iloc[1:]

# we fill the new values with null so that ChartJS does not plot them
total_df = total_df.append(to_append).fillna("null")
total_df.incident_datetime = total_df.incident_datetime.astype(str)


mean = list(mean.Count.values)
mean.extend(to_append.shape[0] * ["null"])

## Updating the `template.html` file to create the new `index.html`
# Read in the template html file
with open('../template.html', 'r') as file :
    filedata = file.read()

# Inserting the dates
filedata = filedata.replace('          labels: [], // INCLUDE X AXIS DATES', 
                            '          labels: {}, // INCLUDE X AXIS DATES'.format(
                                list(total_df.incident_datetime.values)))

# Inserting the total crime rate information
filedata = filedata.replace('            data: [], // Total', 
                            '            data: {}, // Total'.format(
                                list(total_df.Count.values)))

# Inserting the rolling average values
filedata = filedata.replace('            data: [], // Average', 
                            '            data: {}, // Average'.format(
                                mean))

# Inserting district-depedent crime rate information
for i in district_df.police_district.unique():
    if i != "Out of SF":
        district_info = district_df[district_df.police_district == i]
        filedata = filedata.replace('            data: [], // {}'.format(i), 
                                    '            data: {}, // {}'.format(list(district_info.Count.values), i))

# Write the file out again
with open('../index.html', 'w') as file:
    file.write(filedata)

## Taking the Five Latest Reports and Creating a Boostrap Table

latest_reports = results_df.copy()

latest_reports = latest_reports[["incident_datetime", "police_district", "incident_category", 
                                 "incident_subcategory", "incident_description", "resolution", 
                                 "intersection"]]

latest_reports.columns = ["Incident Date", "District", "Incident Category", "Subcategory", 
                          "Description", "Resolution", "Intersection"]

# We save the dataframe as html with the table and table-hover class
latest_reports.head(5).to_html(open('../table.html', 'w'), classes=["table", "table-hover"], 
                               border=0, index=False, justify="center")

with open("../index.html", "r") as f1:
    t1 = f1.readlines()
with open("../table.html", "r") as f2:
    t2 = f2.readlines()

initial = 88
for i in range(0,len(t2)):
    t1.insert(initial, t2[i])
    initial = initial + 1

with open("../index.html", "w") as f2:
    f2.writelines(t1)

with open('../index.html','r') as file:
    filedata = file.read()
    filedata = filedata.replace('  <thead>','  <thead class="thead-dark">')
with open('../index.html','w') as file:
    file.write(filedata)

## Creating the Chloropleth Map 
# RESAMPLING THE DATAFRAME
weekly_df = results_df[["incident_datetime", "police_district"]]
weekly_df["Count"] = 1
weekly_df = weekly_df.set_index(weekly_df["incident_datetime"]).drop(columns=["incident_datetime"])
weekly_df = weekly_df.groupby('police_district').resample('1w').sum()
weekly_df = weekly_df.reset_index()

last_week = pd.DataFrame(columns=weekly_df.columns)

for i in weekly_df.police_district.unique():
    last_week = last_week.append(weekly_df[weekly_df.police_district == i].iloc[[-2]])

last_week = last_week[["police_district", "Count"]]
last_week.columns = ["Neighborhood", "Count"]
last_week.Neighborhood = last_week.Neighborhood.apply(lambda x: x.upper())
last_week.Count = last_week.Count.astype(int)

### Loading and Processing GeoJson File
# San Francisco latitude and longitude values
latitude = 37.77
longitude = -122.42

# loading up json file
with open("../src/sf.geojson") as f:
    data = json.load(f)

# creating and id key to hold district info needed by plotly
for i in range(0,len(data["features"])):
    copy_dict = data["features"][i]
    copy_dict["id"] = copy_dict["properties"]["DISTRICT"]
    data["features"][i] = copy_dict

### Creating Plotly Chloropleth Map
fig = px.choropleth_mapbox(last_week, geojson=data, locations='Neighborhood', color='Count',
                           color_continuous_scale="Turbo",
                           range_color=(0, last_week.Count.max()),
                           mapbox_style="carto-positron",
                           zoom=11, center = {"lat": latitude, "lon": longitude},
                           opacity=0.5,
                           labels={"Count":"Weekly Crime Rate"}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_html("../plotly_map.html")

## Creating Incident Category Distribution Plotly Bar Plot
results_df["Count"] = 1

incident_category = results_df.groupby("incident_category")[["Count"]].sum().reset_index().sort_values(by="Count", ascending=False).head(10)

fig = px.bar(incident_category, x='incident_category', y='Count', 
             labels={"incident_category":"Incident Category"}, color="Count", opacity=1.0)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig.write_html("../incident_category.html")

# Machine Learning
# This cell was ran once and the data was saved into a csv
# results_ml = client.get("wg3w-h783", limit=500000, order="incident_date DESC")
# df = pd.DataFrame.from_records(results_ml)
# df.to_csv("sfpd_reports.csv", index=False)

df = pd.read_csv("../notebook/sfpd_reports.csv")
df['incident_datetime'] = pd.to_datetime(df['incident_datetime'])
df = df[~df['incident_category'].isnull()]
df = df[~df['latitude'].isnull()]
df = df[~df['police_district'].isnull()]
df = df[["incident_datetime", "incident_day_of_week", "police_district", "incident_category"]]


group_by_pd = df.copy()
group_by_pd["Count"] = 1
group_by_pd = group_by_pd.set_index(group_by_pd["incident_datetime"]).drop(columns=["incident_datetime"])
group_by_pd = group_by_pd.groupby(['police_district']).resample('1D').sum()
group_by_pd = group_by_pd.reset_index()

X = group_by_pd.copy()

## Feature Engineering
X = pd.concat([X, pd.get_dummies(X["police_district"])], axis=1).drop(columns=["police_district"])

# X['year'] = pd.to_datetime(X['incident_datetime']).dt.year
X['month'] = pd.to_datetime(X['incident_datetime']).dt.month
X['day'] = pd.to_datetime(X['incident_datetime']).dt.day

X = X.iloc[:-10]

y = X[["Count"]]
X = X.drop(['incident_datetime', "Count"], axis=1)

## Training a DT Regressor

from sklearn.tree import DecisionTreeRegressor

regr_1 = DecisionTreeRegressor()
regr_1.fit(X, y)

## Building an Data Inference Pipeline
pd_districts = ['Bayview', 'Central', 'Ingleside', 'Mission', 'Northern', 
                'Out of SF', 'Park', 'Richmond', 'Southern', 'Taraval', 
                'Tenderloin']

d = datetime.today() - timedelta(days=10)

rng = pd.date_range(d, periods=10+2, freq='d')
rng = pd.to_datetime(rng, format='%Y%m%d')

dates_to_query = pd.DataFrame({ 'Date': rng}) 
dates_to_query["year"] = dates_to_query.Date.dt.year
dates_to_query["day"] = dates_to_query.Date.dt.day
dates_to_query["month"] = dates_to_query.Date.dt.month
dates_to_query["Date"] = dates_to_query.Date.dt.date

predictions_dates = dates_to_query.Date.astype(str).values


def get_prediction_for_dates_df(model, dates):
    # Iterate through the police districts and sum all predictions
    for i in pd_districts:
        testing = pd.DataFrame(columns=X.columns)
        data = pd.DataFrame({i: 1, 
#                              "year":dates.year.values, 
                             "month":dates.month.values, 
                             "day":dates.day.values})
        testing = testing.append(data).fillna(0)
        y = model.predict(testing)
        dates[i] = y.astype(int)
    return dates

## Gathering and Formatting the Results 

dates_to_query = get_prediction_for_dates_df(regr_1, dates_to_query)
dates_to_query["total_crime_rate"] = dates_to_query.iloc[:, 4:].sum(axis=1)
dates_to_query = dates_to_query[["Date", "total_crime_rate"]]
dates_to_query.columns = ["incident_datetime", "tcr"]
dates_to_query.incident_datetime = dates_to_query.incident_datetime.astype(str)


ai_predictions = total_df[["incident_datetime"]].iloc[:-2]
ai_predictions = pd.merge(ai_predictions, dates_to_query, on="incident_datetime", how="outer").fillna("null")

ai_predictions.loc[ai_predictions.index[50-11], 'tcr'] = total_df.loc[total_df.index[50-11], 'Count']

## Writing out the Predictions to our `index.html` file

# Read in the file
with open('../index.html', 'r') as file :
    filedata = file.read()
    
filedata = filedata.replace('            data: [], // AI', 
                            '            data: {}, // AI'.format(
                                list(ai_predictions.tcr.values)))

# Write the file out again
with open('../index.html', 'w') as file:
    file.write(filedata)