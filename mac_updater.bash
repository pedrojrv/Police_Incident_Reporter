#! /bin/bash

conda activate data_mining
cd /Users/pedrovicentevaldez/Desktop/GithubPages/Police_Incident_Reporter/src
python updater.py
git add -A
git commit -m "daily update"
git push origin HEAD