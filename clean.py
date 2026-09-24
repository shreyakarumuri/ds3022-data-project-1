import duckdb
import logging

logging.basicConfig(
   level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
   filename='clean.log'
)
logger = logging.getLogger(__name__)

con = duckdb.connect(database='emissions.duckdb', read_only=False)
logger.info("Connected to DuckDB instance")

def dedupe(color):
    c = color 
    before = con.execute(f"SELECT COUNT(*) FROM {c}_trips").fetchone()[0]
    print(f"Raw row count: {before}")
    try:
        con.execute(f"""
        CREATE TABLE {c}_trips_clean AS
        SELECT DISTINCT * FROM {c}_trips;
        DROP TABLE {c}_trips;
        ALTER TABLE {c}_trips_clean RENAME TO {c}_trips;
    """)
        logger.info(f"Deduplicated {c}_trips")
        after = con.execute(f"SELECT COUNT(*) FROM {c}_trips").fetchone()[0]
        print(f"Row count after dedupe: {after}")
    except Exception as e:
        print(f"An error occurred while deduplicating {c}_trips: {e}")
        logger.error(f"An error occurred while deduplicating {c}_trips: {e}")

def remove_zero_pass_trips(color):
    c = color
    before = con.execute(f"""
        SELECT COUNT(*) FROM {c}_trips
        WHERE passenger_count = 0
        """).fetchone()[0]
    print(f'{c} trips before zero-passenger delete: {before}')
    try:
        con.execute(f"DELETE FROM {c}_trips WHERE passenger_count = 0")
    except Exception as e:
            print(f"An error occurred while removing zero-passenger {c}_trips: {e}")
            logger.error(f"An error occurred while zero-passenger {c}_trips: {e}")

    after = con.execute(f"""
        SELECT COUNT(*) FROM {c}_trips
        WHERE passenger_count = 0
        """).fetchone()[0]
    print(f'{c} trips after zero-passenger delete (verify): {after}')

def remove_zero_dist_trips(color):
    c = color
    before = con.execute(f"""
        SELECT COUNT(*) FROM {c}_trips
        WHERE trip_distance = 0
        """).fetchone()[0]
    print(f'{c}_trips before zero-distance delete: {before}')
    try:
        con.execute(f"DELETE FROM {c}_trips WHERE trip_distance = 0")
    except Exception as e:
            print(f"An error occurred while removing zero-distance {c}_trips: {e}")
            logger.error(f"An error occurred while zero-distance {c}_trips: {e}")

    after = con.execute(f"""
        SELECT COUNT(*) FROM {c}_trips
        WHERE trip_distance = 0
        """).fetchone()[0]
    print(f'{c}_trips after zero-distance delete (verify): {after}')

def remove_far_trips(color):
    c = color
    try:
        before = con.execute(f"""
                SELECT COUNT(*)
                FROM {c}_trips
                WHERE trip_distance > 100
            """).fetchone()[0]
        print(f"{c}_trips before over-100-mi delete: {before}")

        con.execute(f"""
                DELETE FROM {c}_trips
                WHERE trip_distance > 100
            """)
        after = con.execute(f"""
                            SELECT COUNT(*)
                            FROM {c}_trips
                            WHERE trip_distance > 100
                            """).fetchone()[0]
        print(f"{c}_trips after over-100-mi delete: {after}")
        logger.info(f"Removed long trips from {c}_trips")
    except Exception as e:
            print(f"An error occurred while removing over-100-mi {c}_trips: {e}")
            logger.error(f"An error occurred while over-100-mi {c}_trips: {e}")

def remove_over_one_day(color):
    c = color
    before = con.execute(f"""
    SELECT COUNT(*) FROM {c}_trips
    WHERE date_diff('second', pickup_time, dropoff_time) > 86400
    """).fetchone()[0]
    print(f'{c}_trips before over-one-day delete: {before}')
    con.execute(f"DELETE FROM {c}_trips WHERE date_diff('second', pickup_time, dropoff_time) > 86400")

    after = con.execute(f"""
    SELECT COUNT(*) FROM {c}_trips
    WHERE date_diff('second', pickup_time, dropoff_time) > 86400
    """).fetchone()[0]
    print(f'{c}_trips after over-one-day delete (verify): {after}')


if __name__ == "__main__":
    dedupe("yellow")
    dedupe("green")
    remove_zero_dist_trips("yellow")
    remove_zero_dist_trips("green")
    remove_zero_pass_trips("yellow")
    remove_zero_pass_trips("green")
    remove_far_trips("yellow")
    remove_far_trips("green")
    remove_over_one_day("yellow")
    remove_over_one_day("green")






