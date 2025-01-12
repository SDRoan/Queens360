import pandas as pd
import json
from geopy.geocoders import Nominatim

# Load the CSV file
csv_file = "static/data/2019_NYC_School_Survey_-_Student.csv"
data = pd.read_csv(csv_file)

# Initialize geolocator
geolocator = Nominatim(user_agent="school-geocoder")

# Prepare an empty list to store GeoJSON features
features = []

# Iterate over each row to process data
for index, row in data.iterrows():
    school_name = row['School Name']
    address = f"{school_name}, New York, NY"  # Generic address format
    try:
        location = geolocator.geocode(address)
        if location:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [location.longitude, location.latitude]
                },
                "properties": {
                    "name": school_name,
                    "address": address,
                    "response_rate": row['Total Parent Response Rate'] if 'Total Parent Response Rate' in row else 'N/A',
                    "teachers_score": row['Collaborative Teachers Score'] if 'Collaborative Teachers Score' in row else 'N/A',
                    "leadership_score": row['Effective School Leadership Score'] if 'Effective School Leadership Score' in row else 'N/A'
                }
            }
            features.append(feature)
    except Exception as e:
        print(f"Error geocoding {school_name}: {e}")

# Create a GeoJSON structure
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Save to a GeoJSON file
with open("static/data/schools.json", "w") as geojson_file:
    json.dump(geojson_data, geojson_file, indent=4)

print("GeoJSON file created successfully.")
