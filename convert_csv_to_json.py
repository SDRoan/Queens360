import csv
import json

# Correct CSV file path
csv_file = "static/data/2019_NYC_School_Survey_-_Student.csv"  # Correct path to your CSV file
json_file = "static/data/schools.json"  # Output JSON file (will be created)

try:
    # Open the CSV file and read it
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        data = []

        for row in csvreader:
            # Process each row into JSON format
            data.append(row)

    # Write the JSON data to a file
    with open(json_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    print(f"Successfully created JSON file at {json_file}")

except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found. Check the file path and try again.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
