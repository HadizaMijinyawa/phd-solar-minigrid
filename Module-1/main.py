from nasa_fetcher import fetch_nasa_data, get_float_input, get_date_input
from data_cleaner import clean_nasa_data

# Get user inputs using your validation functions
lat = get_float_input("Enter latitude (-90 to 90): ", -90, 90)
lon = get_float_input("Enter longitude (-180 to 180): ", -180, 180)
start = get_date_input("Enter start date (YYYYMMDD): ")
end = get_date_input("Enter end date (YYYYMMDD): ")

# Optional: check date order (copied from your script)
while start > end:
    print("Error: start date must be on or before end date. Please re-enter both.")
    start = get_date_input("Re-enter start date (YYYYMMDD): ")
    end = get_date_input("Re-enter end date (YYYYMMDD): ")

print(f"\nFetching data for: lat={lat}, lon={lon}, start={start}, end={end}\n")

# Fetch the data
json_data = fetch_nasa_data(lat, lon, start, end)

if json_data:
    # Clean and plot
    df = clean_nasa_data(json_data)
    print("Done. Cleaned DataFrame is ready.")
else:
    print("Data fetch failed. Check your inputs or connection.")
