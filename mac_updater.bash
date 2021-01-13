#! /bin/bash

conda activate data_mining
cd /Users/pedrovicentevaldez/Desktop/GithubPages/sfpd_incident_reporter/src
python updater.py
git add -A
git commit -m "daily update"
git push origin HEAD