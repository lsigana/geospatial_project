import sqlite3
import pandas as pd
import random

# Generate fake data
towns = ["Kitale", "Garissa", "Eldoret", "Wajir", "Marsabit", "Isiolo", "Lodwar"]
latitudes = [random.uniform(-1.5, 3) for _ in towns]  # Approximate latitudes in Kenya
longitudes = [random.uniform(36, 40) for _ in towns]  # Approximate longitudes
populations = [random.randint(5000, 50000) for _ in towns]
distances_to_water = [random.uniform(2, 30) for _ in towns]  # Simulated distance (km)

df = pd.DataFrame({
    "Town": towns,
    "Latitude": latitudes,
    "Longitude": longitudes,
    "Population": populations,
    "Distance_to_Water": distances_to_water
})

# Create SQLite database
conn = sqlite3.connect("resource_allocation.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS WaterAccess (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Town TEXT,
        Latitude REAL,
        Longitude REAL,
        Population INTEGER,
        Distance_to_Water REAL
    )
''')

df.to_sql("WaterAccess", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Database created successfully!")
