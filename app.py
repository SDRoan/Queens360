from flask import Flask, render_template, jsonify
from geopy.geocoders import Nominatim
import requests
import plotly.graph_objs as go
import pandas as pd 
import json


app = Flask(__name__)

# OpenWeatherMap API key
API_KEY = "ade2bcb7762da5cbe29ca58708ef2ff3"

# Geolocator setup
geolocator = Nominatim(user_agent="queens-geo-locator")

# Helper function to get coordinates
def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return [location.latitude, location.longitude]
    return None


# Route for the homepage
@app.route("/")
def home():
    return render_template("index.html")

# Route for the neighborhoods list
@app.route("/neighborhoods")
def neighborhoods():
    url = "https://data.cityofnewyork.us/resource/swpk-hqdp.json?$limit=5000"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Use a dictionary to remove duplicates
        unique_neighborhoods = {}
        for record in data:
            if record.get("borough") == "Queens":
                nta_name = record.get("nta_name")
                if nta_name not in unique_neighborhoods:
                    unique_neighborhoods[nta_name] = {
                        "nta_name": nta_name,
                        "population": record.get("population"),
                    }

        return render_template("neighborhoods.html", data=unique_neighborhoods.values())
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

# Dynamic route for each neighborhood
@app.route("/neighborhood/<name>")
def neighborhood_detail(name):
    url = "https://data.cityofnewyork.us/resource/swpk-hqdp.json?$limit=5000"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        neighborhood_info = next(
            (
                {
                    "nta_name": record.get("nta_name"),
                    "population": record.get("population"),
                    "borough": record.get("borough"),
                }
                for record in data
                if record.get("nta_name") == name
            ),
            None,
        )
        if neighborhood_info:
            return render_template("neighborhood_detail.html", neighborhood=neighborhood_info)
        else:
            return jsonify({"error": "Neighborhood not found"}), 404
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

# Route for crime visualization
@app.route("/crime-visualization")
def crime_visualization():
    # Static year-wise crime data for Queens
    year_crime_data = {
        2015: 12000,
        2016: 11800,
        2017: 11500,
        2018: 11000,
        2019: 10800,
        2020: 12000,
        2021: 12500,
        2022: 12200,
        2023: 11700,
    }

    # Create animated line chart using Plotly
    years = list(year_crime_data.keys())
    crime_counts = list(year_crime_data.values())

    frames = []
    for i in range(1, len(years) + 1):
        frame = go.Frame(
            data=[
                go.Scatter(
                    x=years[:i],
                    y=crime_counts[:i],
                    mode="lines+markers",
                    line=dict(color="blue"),
                )
            ],
            name=str(years[i - 1]),
        )
        frames.append(frame)

    # Initial data for the plot
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[years[0]],
                y=[crime_counts[0]],
                mode="lines+markers",
                line=dict(color="blue"),
                name="Crime Trend",
            )
        ],
        layout=dict(
            title="Year-wise Crime Trends in Queens",
            xaxis=dict(title="Year"),
            yaxis=dict(title="Number of Crimes"),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                dict(frame=dict(duration=500, redraw=True), fromcurrent=True),
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(frame=dict(duration=0, redraw=False)),
                            ],
                        ),
                    ],
                )
            ],
        ),
        frames=frames,  # Add the frames to the figure
    )

    graph_json = fig.to_json()

    return render_template("crime_visualization.html", graph_json=graph_json)

# Route for live weather data
@app.route("/weather")
def weather():
    # Query for Queens, NYC
    city = "Queens,US"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=imperial"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["name"],
            "temperature": f"{data['main']['temp']}°F",
            "description": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"],
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} mph",
        }
        return render_template("weather.html", weather=weather_data)
    else:
        return jsonify({"error": "Failed to fetch weather data"}), 500

# Route for rental price heatmap
@app.route("/rental-heatmap")
def rental_heatmap():
    neighborhoods = [
        "South Jamaica",
        "Flushing",
        "Astoria",
        "Jamaica Estates",
        "Ridgewood",
        "Forest Hills",
        "Corona",
        "Queens Village",
        "Jackson Heights",
        "Sunnyside"
    ]
    rental_prices = []

    for neighborhood in neighborhoods:
        coords = get_coordinates(f"{neighborhood}, Queens, NYC")
        if coords:
            price = 2000 + len(neighborhood) * 100  # Example pricing formula
            rental_prices.append({"name": neighborhood, "coords": coords, "price": price})

    return render_template("rental_heatmap.html", rental_data=rental_prices)

@app.route("/mta-map")
def mta_map():
    return render_template("mta_map.html")

@app.route("/school-map")
def school_map():
    # NYC Open Data API for public schools in NYC
    url = "https://data.cityofnewyork.us/resource/s3k6-pzi2.json?$limit=5000"
    response = requests.get(url)

    if response.status_code == 200:
        schools = response.json()

        # Filter only Queens schools
        queens_schools = [
            {
                "name": school.get("school_name"),
                "address": school.get("primary_address_line_1", "N/A"),
                "city": school.get("city", "N/A"),
                "state": school.get("state_code", "N/A"),
                "zip": school.get("zip", "N/A"),
                "lat": float(school["latitude"]) if "latitude" in school else None,
                "lon": float(school["longitude"]) if "longitude" in school else None,
                "rating": school.get("overall_rating", "N/A"),
            }
            for school in schools
            if school.get("borough", "").lower() == "queens"
        ]

        # Convert to JSON and send to the template
        return render_template("school_map.html", schools=queens_schools)
    else:
        return jsonify({"error": "Failed to fetch school data"}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
