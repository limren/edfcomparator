import requests

import numpy as np
import pandas as pd

# Options
# HC and HP range
upper_range = 22
lower_range = 6

# https://particulier.edf.fr/content/dam/2-Actifs/Documents/Offres/Grille_prix_Tarif_Bleu.pdf
base_price = 0.2516

HC_PRICE = 0.2068
HP_PRICE = 0.27

# 0: tarif inconnu (pas encore communiqué par RTE) 1: tarif bleu 2: tarif blanc 3: tarif rouge
TEMPO_BLEU_HC = 0.1296
TEMPO_BLEU_HP = 0.1609
TEMPO_BLANC_HC = 0.1486
TEMPO_BLANC_HP = 0.1894
TEMPO_ROUGE_HC = 0.1568
TEMPO_ROUGE_HP = 0.7562

TEEMPO_PRICES_MAP = {
    1: (TEMPO_BLEU_HC, TEMPO_BLEU_HP),
    2: (TEMPO_BLANC_HC, TEMPO_BLANC_HP),
    3: (TEMPO_ROUGE_HC, TEMPO_ROUGE_HP),
}


API_URL = "https://www.api-couleur-tempo.fr/api/joursTempo"

csv_data = pd.read_csv(
    "data/detailed_daily_consumption/mes-puissances-atteintes-30min-004048667824-69003.csv",
    sep=";",
    encoding="utf-8",
    header=None,
    names=["time", "power", "type"]
)

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except ValueError:
        print("Error occured while parsing JSON.")
    return None

data = fetch_data(API_URL)

# Loading api JSON in a dictionnary
api_dict = {entry["dateJour"]: entry["codeJour"] for entry in data}

# Get the date of the analyzed day, which mean where kwh is NaN in the csv
csv_data["base_date"] = csv_data["time"].where(csv_data["power"].isna())

# Propagate the value of base_date where it's not NaN to other base_date rows, meaning that we are getting the Date where kwh is NaN by creating a new column propagated by that value
csv_data["base_date"] = csv_data["base_date"].fillna(method="ffill")
csv_data["base_date"] = pd.to_datetime(csv_data["base_date"]).dt.strftime('%Y-%m-%d')
csv_data = csv_data.dropna(subset=["power", "time"])

# Convert "time" to datetime and extract the hour
csv_data["time"] = pd.to_datetime(csv_data["base_date"] + " " + csv_data["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
csv_data["hour"] = csv_data["time"].dt.hour
csv_data["tempo_code"] = csv_data["base_date"].apply(lambda date: api_dict.get(date, None))
csv_data["kwh"] = (csv_data["power"] * 0.5) / 1000

csv_data["base_price"] = csv_data["kwh"] * base_price

csv_data["hc_hp_price"] = np.where(
    (csv_data["hour"] >= upper_range) | (csv_data["hour"] < lower_range) | ((csv_data["hour"] == lower_range) & (csv_data["time"].dt.minute == 0)),  # HC condition
    csv_data["kwh"] * HC_PRICE,  # HC price
    csv_data["kwh"] * HP_PRICE   # HP price
)

def calculate_tempo_price(row):
    if pd.isna(row["tempo_code"]):
        return 0

    is_hc = (
        (row["hour"] >= upper_range) |
        (row["hour"] < lower_range) |
        ((row["hour"] == lower_range) & (row["time"].minute == 0))
    )

    tempo_prices = TEEMPO_PRICES_MAP.get(row["tempo_code"], (0, 0))
    return row["kwh"] * (tempo_prices[0] if is_hc else tempo_prices[1])

csv_data["tempo_price"] = csv_data.apply(calculate_tempo_price, axis=1)

csv_data.to_csv("data/detailed_daily_consumption/kwh_with_prices.csv", index=False)
