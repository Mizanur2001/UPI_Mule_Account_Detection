import pandas as pd

def load_transactions(path="data/transactions.csv"):
    return pd.read_csv(path)

def load_accounts(path="data/accounts.csv"):
    return pd.read_csv(path)

def load_devices(path="data/devices.csv"):
    return pd.read_csv(path)
