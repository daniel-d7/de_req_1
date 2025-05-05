import pandas as pd

def extract(file_path):
    data = pd.read_csv(file_path)
    return data