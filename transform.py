import duckdb
import logging

logging.basicConfig(
   level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
   filename='transform.log'
)
logger = logging.getLogger(__name__)

# Connecting to DuckDB
try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")
except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred while trying to connect to DuckDB: {e}")
# Adds new columns and defines their type
def add_columns(color):
    c = color
    try:
        con.execute(f"""
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS trip_co2_kgs DOUBLE;
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS avg_mph DOUBLE;
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS hour_of_day INTEGER;
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS day_of_week INTEGER;
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS week_of_year INTEGER;
            ALTER TABLE {c}_trips ADD COLUMN IF NOT EXISTS month_of_year INTEGER;
        """)
        logger.info(f"Added new columns to {c}_trips")
    except Exception as e:
        print(f"An error occurred while adding columns to {c}_trips: {e}")
        logger.error(f"An error occurred while adding columns to {c}_trips: {e}")

# Calculates the co2 emissions for taxi trips and adds that as a column to the dataset      
def trip_co2_kgs(color):
    c = color
    try:
        con.execute(f"""
            UPDATE {c}_trips SET trip_co2_kgs = (
                SELECT ({c}_trips.trip_distance * ve.co2_grams_per_mile) / 1000.0
                FROM vehicle_emissions ve
                WHERE ve.vehicle_type = '{c}_taxi'
                )
        """)
        logger.info(f"added trip_co2_kgs to {c}_trips")
    except Exception as e:
            print(f"An error occurred while adding trip_co2_kgs to {c}_trips: {e}")
            logger.error(f"An error occurred while adding trip_co2_kgs to {c}_trips: {e}")
# Calculates the averag emiles per hour of taxi trips and adds that as a column to the dataset      
def avg_mph(color):
    c = color
    try:
        con.execute(f"""
            UPDATE {c}_trips SET avg_mph = 
                trip_distance / (date_diff('second', pickup_time, dropoff_time) / 3600.0)
        """)
        logger.info(f"added avg_mph to {c}_trips")
    except Exception as e:
        print(f"An error occurred while adding avg_mph to {c}_trips: {e}")
        logger.error(f"An error occurred while adding avg_mph to {c}_trips: {e}")
    
# Adds columns for the hour of the day, day of the week, week of the year and month of the year
def time_breakdown(color):
    c = color
    try:
        con.execute(f"""
            UPDATE {c}_trips SET
                hour_of_day = date_part('hour', pickup_time),
                day_of_week = date_part('dow', pickup_time),
                week_of_year = date_part('week', pickup_time),
                month_of_year = date_part('month', pickup_time)
        """)
        logger.info(f"Added time breakdown columns to {c}_trips")
    except Exception as e:
        print(f"An error occurred while adding time breakdown columns to {c}_trips: {e}")
        logger.error(f"An error occurred while adding time breakdown columns to {c}_trips: {e}")

# Adds the empty columsn and specific caluclations for both yellow and green trips
if __name__ == "__main__":
    add_columns("yellow")
    add_columns("green")
    trip_co2_kgs("yellow")
    trip_co2_kgs("green")
    avg_mph("yellow")
    avg_mph("green")
    time_breakdown("yellow")
    time_breakdown("green")

