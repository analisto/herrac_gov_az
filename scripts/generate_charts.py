from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()
DATA_PATH = ROOT / 'data' / 'synthetic_fraud_data.csv'
CHARTS_DIR = ROOT / 'charts'
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    'figure.dpi': 150,
    'axes.titlesize': 14,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'font.size': 10
})


def save_fig(name):
    path = CHARTS_DIR / name
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


df = pd.read_csv(DATA_PATH)

# Chart 1: Fraud share by channel
channel = df.groupby('channel').agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
channel['share'] = channel['fraud'] / channel['txn']
channel = channel.sort_values('share', ascending=False)

plt.figure(figsize=(7, 4.2))
plt.bar(channel.index, channel['share'] * 100, color=['#d9534f', '#f0ad4e', '#5bc0de'][:len(channel)])
plt.title('Share of Transactions Flagged as Fraud by Channel')
plt.ylabel('Fraud Share (%)')
plt.xlabel('Channel')
plt.ylim(0, 105)
for i, (idx, row) in enumerate(channel.iterrows()):
    plt.text(i, row['share'] * 100 + 2, f"{int(row['txn']):,} txns", ha='center', va='bottom', fontsize=9)
save_fig('fraud_share_by_channel.png')

# Chart 2: Top 10 countries by volume (stacked fraud vs non-fraud)
country = df.groupby('country').agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
country['non_fraud'] = country['txn'] - country['fraud']
country_top = country.sort_values('txn', ascending=False).head(10)

plt.figure(figsize=(9, 5))
plt.bar(country_top.index, country_top['non_fraud'], label='Not Fraud', color='#5bc0de')
plt.bar(country_top.index, country_top['fraud'], bottom=country_top['non_fraud'], label='Fraud', color='#d9534f')
plt.title('Transaction Volume and Fraud Counts by Country (Top 10 by Volume)')
plt.ylabel('Number of Transactions')
plt.xlabel('Country')
plt.xticks(rotation=30, ha='right')
plt.legend(frameon=False)
save_fig('volume_and_fraud_by_country_top10.png')

# Chart 3: Fraud share by amount band
bins = [0, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000, 50000, 100000]
labels = [f"${bins[i]}-${bins[i+1]}" for i in range(len(bins)-1)]
amount_band = pd.cut(df['amount'], bins=bins, labels=labels, include_lowest=True)
amount = df.groupby(amount_band).agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
amount['share'] = amount['fraud'] / amount['txn']

plt.figure(figsize=(10, 4.6))
plt.bar(amount.index.astype(str), amount['share'] * 100, color='#f0ad4e')
plt.title('Fraud Share by Transaction Amount Band')
plt.ylabel('Fraud Share (%)')
plt.xlabel('Amount Band')
plt.xticks(rotation=30, ha='right')
plt.ylim(0, max(70, (amount['share'].max() * 100) + 10))
save_fig('fraud_share_by_amount_band.png')

# Chart 4: Fraud share by hour of day
hour = df.groupby('transaction_hour').agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
hour['share'] = hour['fraud'] / hour['txn']

plt.figure(figsize=(9, 4.2))
plt.plot(hour.index, hour['share'] * 100, marker='o', color='#5cb85c')
plt.title('Fraud Share by Hour of Day')
plt.ylabel('Fraud Share (%)')
plt.xlabel('Hour (0-23)')
plt.xticks(range(0, 24, 2))
plt.ylim(0, max(45, (hour['share'].max() * 100) + 5))
save_fig('fraud_share_by_hour.png')

# Chart 5: Fraud share by city size
city = df.groupby('city_size').agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
city['share'] = city['fraud'] / city['txn']

plt.figure(figsize=(6.5, 4.2))
plt.bar(city.index, city['share'] * 100, color='#5bc0de')
plt.title('Fraud Share by City Size')
plt.ylabel('Fraud Share (%)')
plt.xlabel('City Size')
plt.ylim(0, max(15, (city['share'].max() * 100) + 5))
for i, (idx, row) in enumerate(city.iterrows()):
    plt.text(i, row['share'] * 100 + 0.7, f"{int(row['txn']):,} txns", ha='center', va='bottom', fontsize=9)
save_fig('fraud_share_by_city_size.png')

# Chart 6: Fraud share by high-risk merchant flag
risk = df.groupby('high_risk_merchant').agg(txn=('transaction_id','count'), fraud=('is_fraud','sum'))
risk['share'] = risk['fraud'] / risk['txn']

plt.figure(figsize=(6.5, 4.2))
plt.bar(risk.index.astype(str), risk['share'] * 100, color='#d9534f')
plt.title('Fraud Share by High-Risk Merchant Flag')
plt.ylabel('Fraud Share (%)')
plt.xlabel('High-Risk Merchant Flag')
plt.ylim(0, max(15, (risk['share'].max() * 100) + 5))
for i, (idx, row) in enumerate(risk.iterrows()):
    plt.text(i, row['share'] * 100 + 0.7, f"{int(row['txn']):,} txns", ha='center', va='bottom', fontsize=9)
save_fig('fraud_share_by_high_risk_flag.png')

print(f"Charts saved to: {CHARTS_DIR}")
