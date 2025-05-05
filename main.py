from datetime import datetime
from sqlalchemy import create_engine, types
from modules import extract, transform, load

data_frame = extract("./raw/data.csv")
transformed = transform(data_frame)
print(transformed["job_title"].unique())