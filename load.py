import duckdb
import os
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

baseurl = "https://d37ci6vzurychx.cloudfront.net/trip-data/"

def load_parquet_files():

    con = None
# Connecting to DuckDB
    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to connect to DuckDB: {e}")
            return
    
# Creating yellow_trips table based on January data, dropping the table if it already exists
    try:
        con.execute(f"""
            DROP TABLE IF EXISTS yellow_trips;
            CREATE TABLE yellow_trips AS
            SELECT
            VendorID,
            tpep_pickup_datetime AS pickup_time,
            tpep_dropoff_datetime AS dropoff_time,
            passenger_count,
            trip_distance
            FROM read_parquet(
            '{baseurl}yellow_tripdata_2024-01.parquet');
        """)
        logger.info("Created yellow_trips table, drop if table exists")
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to make yellow_trips: {e}")

# Creating green_trips table based on January data, dropping the table if it already exists           
    try:
        con.execute(f"""
                    DROP TABLE IF EXISTS green_trips;
                    CREATE TABLE green_trips AS
                    SELECT 
                    VendorID,
                    lpep_pickup_datetime AS pickup_time,
                    lpep_dropoff_datetime AS dropoff_time,
                    passenger_count,
                    trip_distance
                    FROM read_parquet(
                    '{baseurl}green_tripdata_2024-01.parquet');
                """)
        logger.info("Created green_trips table, drop if table exists")
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to make green_trips: {e}")

# Creating vehicle emissions table from the csv, dropping the table if it already exists
    try:
        con.execute("""
            DROP TABLE IF EXISTS vehicle_emissions;
            CREATE TABLE vehicle_emissions AS
            SELECT * FROM read_csv_auto(
            'data/vehicle_emissions.csv');
        """)
        logger.info("Created vehicle_emissions table, drop if table exists")
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to make vehicle_emissions: {e}")

# Logging and printing the number of rows in the vehicle_emissions table
    try:
        n = con.execute(
            "SELECT COUNT(*) FROM vehicle_emissions"
        ).fetchone()[0]
        logger.info(f"vehicle_emissions: {n} rows loaded")
        print(f'vehicle_emissions: {n} rows loaded')
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to print vehicle_emissions row count: {e}")

# Inserting the data for February-December into the yellow_trips table
    for month in range(2,13):
        url = (f'{baseurl}yellow_tripdata_2024-{month:02d}.parquet'
        )
        # Select necessary columns and rename pickup and dropoff for consistency with green_trips
        try:
                con.execute(
                f"""INSERT INTO yellow_trips 
                SELECT
                VendorID,
                tpep_pickup_datetime AS pickup_time, -- lpep_pickup_datetime on GREEN
                tpep_dropoff_datetime AS dropoff_time, 
                passenger_count,
                trip_distance
                FROM read_parquet('{url}')"""
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to insert into yellow_trips: {e}")


# Logging and printing the number of rows in the yellow_trips table
    try:
            n = con.execute(
                "SELECT COUNT(*) FROM yellow_trips"
            ).fetchone()[0]
            logger.info(f"yellow_trips: {n} rows loaded")
            print(f'yellow_trips: {n} rows loaded')
    except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to print yellow_trips row count: {e}")


    for month in range(2,13):
            url = (f'{baseurl}green_tripdata_2024-{month:02d}.parquet'
            )
            # Select necessary columns and rename pickup and dropoff for consistency with yellow_trips
            try:
                con.execute(
                    f"""INSERT INTO green_trips 
                    SELECT 
                    VendorID,
                    lpep_pickup_datetime AS pickup_time,
                    lpep_dropoff_datetime AS dropoff_time,
                    passenger_count,
                    trip_distance
                    FROM read_parquet('{url}')"""
            )
            except Exception as e:
                print(f"An error occurred: {e}")
                logger.error(f"An error occurred while inserting green trips: {e}")

# Logging and printing the number of rows in the green_trips table
    try:
                n = con.execute(
                    "SELECT COUNT(*) FROM green_trips"
                ).fetchone()[0]
                logger.info(f"green_trips: {n} rows loaded")
                print(f'green_trips: {n} rows loaded')
    except Exception as e:
                print(f"An error occurred: {e}")
                logger.error(f"An error occurred while trying to print green_trips row count: {e}")




if __name__ == "__main__":
    load_parquet_files()

