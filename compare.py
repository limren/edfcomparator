import pandas as pd
import matplotlib.pyplot as plt

# TODO: Make graph more readable with new metrics

# Need to be written with : time, power, type, base_date, hour, kwh, base_price, hc_hp_price
csv_data = pd.read_csv("data/detailed_daily_consumption/kwh_with_prices.csv")

grouped_data = csv_data.groupby('base_date').agg({
    'base_price': 'sum',
    'hc_hp_price': 'sum',
    'tempo_price': 'sum',
    'kwh': 'sum',
    'power': 'mean'
}).reset_index()

grouped_data[["base_price", "hc_hp_price", 'tempo_price']].head(50).plot.bar()
plt.show()

data_sum = csv_data.agg({
    'base_price': 'sum',
    'hc_hp_price': 'sum',
    'tempo_price': 'sum',
    'kwh': 'sum',
    'power': 'mean'
})

data_sum[["base_price", "hc_hp_price", 'tempo_price']].head(50).plot.bar()
plt.show()



grouped_data.to_csv("data/detailed_daily_consumption/prices_per_day.csv", index=False)
