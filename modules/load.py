from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, String, Date, Float
from urllib.parse import quote_plus

def load(data):
    username = "root"
    password = "Phieulang68@"
    password = quote_plus(password)
    database = "personal"
    host = "localhost"
    port = "3306"
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    metadata = MetaData()
    my_table = Table(
        "topcv", metadata,
        Column("pk", BigInteger, primary_key=True),
        Column("created_date", Date),
        Column("job_title", String(255)),
        Column("company", String(255)),
        Column("salary", String(255)),
        Column("province", String(255)),
        Column("district", String(255)),
        Column("time", String(255)),
        Column("link_description", String(255)),
        Column("min_salary", Float),
        Column("max_salary", Float),
        Column("salary_currency", String(5))
    )

    metadata.create_all(engine)

    try:
        data.to_sql(
            name = "topcv",
            con = engine,
            index = False,
            if_exists = 'append',
            chunksize = 1000
        )
        print("Data loaded successfully to MySQL")
    except Exception as e:
        print(f"Error loading data to MySQL: {e}")
    finally:
        engine.dispose()