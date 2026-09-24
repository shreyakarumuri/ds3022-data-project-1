# DS3022 - Data Project 1 (Fall 2025)

# NYC Taxi CO2 Emissions Data Pipeline

## Overview

This project analyzes CO2 emissions from New York City yellow and green taxi trips from 2024. The pipeline loads monthly taxi trip data and vehicle emissions data into DuckDB, cleans and transforms the trip data, and then analyzes CO2 emissions by taxi type and time period.

The pipeline consists of four main scripts:

* `load.py` loads the 2024 yellow taxi, green taxi, and vehicle emissions data into DuckDB tables.
* `clean.py` removes invalid or unusable trips, including duplicate trips, trips with zero passengers, trips with zero miles, trips over 100 miles, and trips lasting longer than 24 hours.
* `transform.py` calculates CO2 emissions, average speed, and time-based variables for each trip.
* `analysis.py` identifies the largest individual CO2-producing trip and compares average CO2 emissions across hours, days, weeks, and months. It also creates a monthly CO2 emissions plot for yellow and green taxis.

## How to Run

Make sure Python and the required packages are installed. From the project directory, run the scripts in the following order:

```bash
python load.py
python clean.py
python transform.py
python analysis.py
```

The pipeline creates the DuckDB database `emissions.duckdb` and generates the CO2 emissions plot from the transformed data.

## Data

The taxi trip data consists of monthly 2024 yellow and green taxi Parquet files. The vehicle emissions data is stored in `data/vehicle_emissions.csv`.

The taxi data is loaded directly from the provided data source using DuckDB's `read_parquet()` function. Only the columns needed for the analysis are selected when the data is loaded.

## Design Decisions

### Programmatic Monthly Loading

Instead of writing a separate query for every monthly file, `load.py` uses a loop to load the February through December files after creating the tables from the January data. This reduces repeated code while allowing all 12 months of 2024 data to be loaded.

### Data Cleaning

The cleaning process removes trips that could produce unreliable results, including duplicate records, trips with zero passengers, trips with zero distance, trips longer than 100 miles, and trips lasting longer than 24 hours.

### CO2 Calculation

CO2 emissions are calculated using the `vehicle_emissions` table rather than hardcoding emission factors into the transformation script. The taxi type is matched to the corresponding vehicle type in the emissions table, and the trip distance is multiplied by the appropriate CO2 emissions per mile. The result is converted from grams to kilograms.

### Time-Based Analysis

The transformation step creates hour, day, week, and month variables from the pickup timestamp. These variables make it possible to compare average CO2 emissions across different time periods.

### Visualization

The final analysis includes a monthly CO2 emissions plot with separate series for yellow and green taxis. The plot uses total CO2 emissions by month to show how emissions vary throughout 2024.
