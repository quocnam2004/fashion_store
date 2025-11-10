import pandas as pd, os
BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_products():
    p = os.path.join(BASE, 'products.csv')
    try:
        df = pd.read_csv(p, dtype=str)
        df = df.fillna('')
        return df.to_dict(orient='records')
    except Exception:
        return []

def load_users():
    p = os.path.join(BASE, 'users.csv')
    try:
        df = pd.read_csv(p, dtype=str)
        df = df.fillna('')
        return df.to_dict(orient='records')
    except Exception:
        return []

def load_history():
    p = os.path.join(BASE, 'history.csv')
    try:
        df = pd.read_csv(p, dtype=str)
        df = df.fillna('')
        return df.to_dict(orient='records')
    except Exception:
        return []
