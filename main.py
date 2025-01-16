import time

import pandas as pd
import numpy as np

# Options
# TODO: Add handler for "Tarif tempo"
# HC and HP range
upper_range = 22
lower_range = 6

# https://particulier.edf.fr/content/dam/2-Actifs/Documents/Offres/Grille_prix_Tarif_Bleu.pdf
BASE_PRICE = 0.2516
HC_PRICE = 0.2068
HP_PRICE = 0.27

csv_data = pd.read_csv(
    "data/detailed_daily_consumption/mes-puissances-atteintes-30min-004048667824-69003.csv",
    sep=";",
    encoding="utf-8",
    header=None,
    names=["Time", "Power", "Type"]
)

# Get the date of the analyzed day, which mean where kwh is NaN in the csv
# TODO: check if error can happen where Kwh is NaN and the date is actually the time
csv_data["Base_Date"] = csv_data["Time"].where(csv_data["Power"].isna())

# Propagate the value of Base_date where it's not NaN to other Base_date rows, meaning that we are getting the Date where kwh is NaN by creating a new column propagated by that value
csv_data["Base_Date"] = csv_data["Base_Date"].fillna(method="ffill")
csv_data = csv_data.dropna(subset=["Power", "Time"])

# Convert "Time" to datetime and extract the hour
csv_data["Time"] = pd.to_datetime(csv_data["Base_Date"] + " " + csv_data["Time"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
csv_data["Hour"] = csv_data["Time"].dt.hour

csv_data["Kwh"] = (csv_data["Power"] * 0.5) / 1000

csv_data["base_price"] = csv_data["Kwh"] * BASE_PRICE

csv_data["HC_HP_price"] = np.where(
    (csv_data["Hour"] >= upper_range) | (csv_data["Hour"] < lower_range),  # HC condition
    csv_data["Kwh"] * HC_PRICE,  # HC price
    csv_data["Kwh"] * HP_PRICE   # HP price
)

csv_data.to_csv("data/detailed_daily_consumption/kwh_with_prices.csv", index=False)
