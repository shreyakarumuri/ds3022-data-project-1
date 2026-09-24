import duckdb
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB_PATH = "emissions.duckdb"
TABLES  = {"YELLOW": "yellow_trips", "GREEN": "green_trips"}
DAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]
MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

logging.basicConfig(
   level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
   filename='analysis.log'
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
            

# Prints and logs a message so you no longer need to type out both print() and logger.info()
def report(message):
    print(message)        # screen
    logger.info(message)  # + log

# Returns the single trip with the largest co2 emission in 2024
def largest_trip(con, label, table):
    row = con.execute(f"""
        SELECT trip_co2_kgs, trip_distance, pickup_time
        FROM {table}
        ORDER BY trip_co2_kgs DESC LIMIT 1
    """).fetchone()
    report(f"[{label}] Largest single-trip CO2 of 2024: "
           f"{row[0]:.2f} kg ({row[1]:.2f} mi, picked up {row[2]})")
    
# Returns the heaviest and lowest average co2 emission
def heaviest_lightest(con, label, table, column, description, names = None):
    rows = con.execute(f"""
        SELECT {column}, AVG(trip_co2_kgs) AS avg_co2
        FROM {table} GROUP BY {column} ORDER BY avg_co2 DESC
    """).fetchall()
    pretty = lambda v: names[int(v)] if names else v
    high, low = rows[0], rows[-1]
    report(f"[{label}] Most carbon-heavy {description}: "
           f"{pretty(high[0])} ({high[1]:.3f} kg avg/trip)")
    report(f"[{label}] Most carbon-light {description}: "
           f"{pretty(low[0])} ({low[1]:.3f} kg avg/trip)")
    
# Plots the co2 emission data by month for both yellow and green trips
def monthly_plot(con, filename="co2_by_month_2024.png"):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    # Two axes needed due to varying scale
    ax2 = ax1.twinx()

    axes = {"YELLOW": ax1, "GREEN": ax2}
    colors = {"YELLOW": "y", "GREEN": "tab:green"}
    
    for label, table in TABLES.items():
        rows = con.execute(f"""
            SELECT month_of_year, SUM(trip_co2_kgs) AS total_co2
            FROM {table} GROUP BY month_of_year ORDER BY 1
        """).fetchall()
        months = [r[0] for r in rows]
        totals = [r[1] / 1000.0 for r in rows]   # kg -> tonnes
        ax = axes[label]
        color = colors[label]
        ax.plot(months, totals, marker="o", color=color, label=label)        
        ax.set_ylabel(f"{label} CO2 (tonnes)", color=color)
        ax.tick_params(axis="y", labelcolor=color)
    ax1.set_xlabel("Month")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2)
    fig.savefig(filename, dpi=150)
    report(f"Plot written to {filename}")      

# Iterates through yellow and green trip tables to calculate co2 emission stats
def main():
    # Prints the highest and lowest co2 emission day of the week/hour/week of the year/month
    for label, table in TABLES.items():
        largest_trip(con, label, table)
        heaviest_lightest(con, label, table, "hour_of_day",   "hour of day") 
        heaviest_lightest(con, label, table, "day_of_week",   "day of week", DAY_NAMES)
        heaviest_lightest(con, label, table, "week_of_year",  "week of year")
        heaviest_lightest(con, label, table, "month_of_year", "month of year", MONTH_NAMES)
    monthly_plot(con)
    con.close()
 
if __name__ == "__main__":   # not on the slide: add this
    main()