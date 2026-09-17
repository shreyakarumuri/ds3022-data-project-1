import duckdb
import os
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

def load_parquet_files():

    con = None

    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        con.execute("""
            DROP TABLE IF EXISTS vehicle_emissions;
            CREATE TABLE vehicle_emissions AS
            SELECT * FROM read_csv_auto(
            'data/vehicle_emissions.csv');
        """)
        logger.info("Dropped table if exists")

        n = con.execute(
            "SELECT COUNT(*) FROM vehicle_emissions"
        ).fetchone()[0]
        logger.info(f"vehicle_emissions: {n} rows loaded")

        for month in range(1, 13):
            url = (f'.../yellow_tripdata_2024-{month:02d}.parquet'
            )
            con.execute(
                f"INSERT INTO yellow_trips "
                f"SELECT * FROM read_parquet('{url}')"
            )

        


    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    load_parquet_files()