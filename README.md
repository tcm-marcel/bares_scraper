# Data scraper to get a list of objects of the TV show "Bares für Rares"

This script scrapes the Website of the TV channel ZDF to generate a CSV file
of objects by parsing the show desription.

## Viz
[Tableau Public Viz](https://public.tableau.com/shared/PYZW58JK9?:display_count=n&:origin=viz_share_link) that uses the CSV generated by this script

## Usage
```
./create_venv.py 3.9
.venv/bin/python3 bares_scraper.py 2021-10-01 bares.csv
```
