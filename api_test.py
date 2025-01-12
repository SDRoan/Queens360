from flask import Flask, render_template
import requests
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

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

# Route for crime data visualization
@app.route("/crime-visualization")
def crime_visualization():
    # Static year-wise crime data for Queens
    year_crime_data = {
        2015: 12000,
        2016: 11800,
        2017: 11500,
        2018: 11000,
        2019: 10800,
        2020: 12000,  # Spike due to COVID-19
        2021: 12500,
        2022: 12200,
        2023: 11700,
    }

    # Create a line graph
    years = list(year_crime_data.keys())
    crime_counts = list(year_crime_data.values())

    fig, ax = plt.subplots()
    ax.plot(years, crime_counts, marker="o", linestyle="-", color="blue", label="Queens Crime Rate")
    ax.set_title("Year-wise Crime Trends in Queens")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Crimes")
    ax.legend()

    # Convert the graph to an image for rendering in the template
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template("crime_visualization.html", graph_url=graph_url)

if __name__ == "__main__":
    app.run(debug=True)
