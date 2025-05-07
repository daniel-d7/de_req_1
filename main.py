from datetime import datetime
from sqlalchemy import create_engine, types
from modules import extract, transform, load
    
data = extract("./raw/data_test.csv")
data = transform(data)
print(data)