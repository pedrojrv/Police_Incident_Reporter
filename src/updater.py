import pandas as pd
from sodapy import Socrata
import folium
import config
import json
import plotly.express as px

# Example authenticated client (needed for non-public datasets):
client = Socrata("data.sfgov.org",
                 config.api_key,
                 username=config.username,
                 password=config.password)

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("wg3w-h783", limit=15000, order="incident_date DESC")
# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
results_df['incident_datetime'] = pd.to_datetime(results_df['incident_datetime'])


district_df = results_df[["incident_datetime", "police_district"]]
district_df["Count"] = 1
district_df["incident_datetime"] = district_df.incident_datetime.dt.date
district_df = district_df.groupby(['incident_datetime','police_district'], as_index=False)['Count'].sum()

total_df = results_df[["incident_datetime"]]
total_df["Count"] = 1
total_df = total_df.groupby(total_df.incident_datetime.dt.date)[['Count']].sum()
total_df = total_df.iloc[1:]

district_df.incident_datetime = district_df.incident_datetime.astype(str)
total_df = total_df.reset_index()
total_df.incident_datetime = total_df.incident_datetime.astype(str)

mean = total_df.rolling(5).mean().fillna(method="backfill")


# Read in the file
with open('../template.html', 'r') as file :
    filedata = file.read()

filedata = filedata.replace('          labels: [], // INCLUDE X AXIS DATES', 
                            '          labels: {}, // INCLUDE X AXIS DATES'.format(
                                list(district_df.incident_datetime.unique())))

filedata = filedata.replace('            data: [], // Total', 
                            '            data: {}, // Total'.format(
                                list(total_df.Count.values)))

filedata = filedata.replace('            data: [], // Average', 
                            '            data: {}, // Average'.format(
                                list(mean.Count.values)))

for i in district_df.police_district.unique():
    if i != "Out of SF":
        district_info = district_df[district_df.police_district == i]
        filedata = filedata.replace('            data: [], // {}'.format(i), 
                                    '            data: {}, // {}'.format(list(district_info.Count.values), i))

# Write the file out again
with open('../index.html', 'w') as file:
    file.write(filedata)

to_show = results_df.copy()
to_show = to_show[["incident_datetime", "police_district", "incident_category", "incident_subcategory", 
                   "incident_description", "resolution", "intersection"]]
to_show.columns = ["Incident Date", "District", "Incident Category", "Subcategory", "Description", "Resolution", "Intersection"]
to_show.head(5).to_html(open('../table.html', 'w'), classes=["table", "table-hover"], border=0, index=False, justify="center")

with open("../index.html", "r") as f1:
    t1 = f1.readlines()
with open("../table.html", "r") as f2:
    t2 = f2.readlines()

initial = 78
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


avg_district_df = results_df[["incident_datetime", "police_district"]]
avg_district_df["Count"] = 1
avg_district_df = avg_district_df.set_index(avg_district_df["incident_datetime"]).drop(columns=["incident_datetime"])
avg_district_df = avg_district_df.groupby('police_district').resample('1w').sum()
avg_district_df = avg_district_df.reset_index()

latest = pd.DataFrame(columns=avg_district_df.columns)

for i in avg_district_df.police_district.unique():
    latest = latest.append(avg_district_df[avg_district_df.police_district == i].iloc[[-2]])

latest = latest[["police_district", "Count"]]
latest.columns = ["Neighborhood", "Count"]
latest.Neighborhood = latest.Neighborhood.apply(lambda x: x.upper())
latest.Count = latest.Count.astype(int)



# San Francisco latitude and longitude values
latitude = 37.77
longitude = -122.42


with open("sf.geojson") as f:
    data = json.load(f)

for i in range(0, len(data["features"])):
    copy_dict = data["features"][i]
    copy_dict["id"] = copy_dict["properties"]["DISTRICT"]
    data["features"][i] = copy_dict

fig = px.choropleth_mapbox(latest, geojson=data, locations='Neighborhood', color='Count',
                           color_continuous_scale="Turbo",
                           range_color=(0, latest.Count.max()),
                           mapbox_style="carto-positron",
                           zoom=11, center = {"lat": latitude, "lon": longitude},
                           opacity=0.5,
                           labels={"Count":"Weekly Crime Rate"}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_html("../plotly_map.html")

results_df["Count"] = 1
incident_category = results_df.groupby("incident_category")[["Count"]].sum().reset_index().sort_values(by="Count", ascending=False).head(10)

fig = px.bar(incident_category, x='incident_category', y='Count', 
             labels={"incident_category":"Incident Category"}, color="Count", opacity=1.0)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig.write_html("../incident_category.html")