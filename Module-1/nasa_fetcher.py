# NASA POWER Hourly API Parameters
# Endpoint: https://power.larc.nasa.gov/api/temporal/hourly/point
#
# Required API Parameters:
#   parameters   : Comma-separated list of parameter IDs (max 15)   e.g., "T2M,WS10M,PRECTOTCORR"
#   start        : Start date in YYYYMMDD format                    e.g., "20230101"
#   end          : End date in YYYYMMDD format                      e.g., "20230102"
#   latitude     : Decimal latitude (-90 to 90)                     e.g., "40.5"
#   longitude    : Decimal longitude (-180 to 180)                  e.g., "-100.3"
#   community    : Data community: "RE", "AG", or "SB"              e.g., "RE"
#
# Optional parameters:
#   time-standard: "UTC" or "LST" (Local Solar Time, default)       e.g., "UTC"
#   format       : Output format: "JSON", "CSV", "NETCDF", "ICASA"  e.g., "JSON"
#   user         : For API usage tracking (optional)                 e.g., "my_name"
#   user-api     : For API usage tracking (optional)                 e.g., "my_project"
#
# Notes:
#   - Parameter list must not contain spaces after commas.
#   - Date range can be up to one year (but hourly data volume may be large).
#   - See full parameter list at: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/parameters/
#
# Example URL (for reference):
# https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=T2M,WS10M,PRECTOTCORR&community=RE&latitude=40.5&longitude=-100.3&start=20230101&end=20230102&time-standard=UTC




# NASA POWER parameters I selected for my physics-informed GAN
# Community: RE (Renewable Energy) – tailored for solar/wind system design
# Temporal resolution: Hourly (LST) – matches my GAN output and captures diurnal cycles essential for my physics rules
# Why hourly: Efficiency losses, cloud effects, dust accumulation tracking all need sub‑day precision
# Max 15 parameters per hourly request – this list fits exactly

# 1. ALLSKY_SFC_SW_DWN – All Sky Insolation on Horizontal Surface
#    What it is: Total sunlight (direct + diffuse) reaching the ground under actual sky conditions.
#    Why I need it: Primary input for PV generation. My GAN learns realistic solar power profiles from this.

# 2. CLRSKY_SFC_SW_DWN – Clear Sky Insolation on Horizontal Surface
#    What it is: Sunlight that would reach the ground if there were no clouds.
#    Why I need it: Compare with ALLSKY to quantify cloud attenuation – used in my cloud‑cover physics rule.

# 3. T2M – Temperature at 2 Meters
#    What it is: Ambient air temperature (the hot/cold weathernyou feel).
#    Why I need it: Core input for my temperature rule (efficiency loss).

# 4. RH2M – Relative Humidity at 2 Meters
#    What it is: Percentage of water vapour in the air.
#    Why I need it: High humidity → corrosion risk for inverters and metal parts. Used in my failure‑mode profiling.

# 5. PRECTOTCORR – Precipitation (corrected)
#    What it is: Daily rainfall amount.
#    Why I need it: For my dust accumulation rule – I need “days since last rainfall” because rain cleans panels.

# 6. CLOUD_AMT – Cloud Amount
#    What it is: Percentage of sky covered by clouds.
#    Why I need it: Directly affects solar generation; used in my cloud‑cover physics penalty.

# 7. WS10M – Wind Speed at 10 Meters
#    What it is: How fast the wind blows at 10m height.
#    Why I need it: Wind transports dust (affects soiling) and can slightly cool panels – helps me model dust accumulation.

# 8. PS – Surface Pressure
#     What it is: Air pressure at ground level.
#     Why I need it: Optionàl; relates to air density and cooling.

# 9. T2MDEW – Dew Point Temperature at 2 Meters
#     What it is: Temperature at which air becomes saturated and dew forms.
#     Why I need it: Indicator of moisture and corrosion risk; complements RH2M.

# 10. KT – Insolation Clearness Index
#     What it is: Ratio of actual sunlight (ALLSKY) to sunlight at top of atmosphere (0–1 scale).
#     Why I need it: Compact representation of cloudiness – helps my GAN learn clear vs. cloudy day patterns.

# 11. WD10M – Wind Direction at 10 Meters
#     What it is: Direction wind comes from (e.g., NE for harmattan dust).
#     Why I need it: Helps me identify dust source regions; refines my dust‑risk profiling.



import requests
import sys
from datetime import datetime



##------Validate User Inputs ---------#
def get_float_input(prompt, min_val, max_val, max_attempts=3):
    """Ask user for a float within range, with limited attempts."""
    for attempt in range(1, max_attempts + 1):
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Number must be between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    print("Too many invalid attempts. Exiting.")
    sys.exit(1)


def get_date_input(prompt, max_attempts=3):
    """Ask for a date in YYYYMMDD format (8 digits)."""
    for attempt in range(1, max_attempts + 1):
        date_str = input(prompt).strip()
        if date_str.isdigit() and len(date_str) == 8:
            try:
                # Validate using datetime (handles leap years, month lengths)
                datetime.strptime(date_str, "%Y%m%d")
                return date_str
            except ValueError:
                print("Invalid date – please enter a real calendar date.")
        else:
            print("Date must be 8 digits in format YYYYMMDD.")
    print("Too many invalid attempts. Exiting.")
    sys.exit(1)


# ----- The fetching function (now reusable) -----
def fetch_nasa_data(lat, lon, start, end):
    #----- Other NASA API Parameters ----------#
    endpoint_url = 'https://power.larc.nasa.gov/api/temporal/hourly/point'
    community = 'RE'
    t_std= 'LST'
    parameters = ['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN', 'T2M', 'RH2M', 'PRECTOTCORR', 'CLOUD_AMT', 'WS10M', 'PS', 'T2MDEW', 'KT', 'WD10M']
    parameters_str = ','.join(parameters)

    # Fetching the request data
    request_url = f'{endpoint_url}?parameters={parameters_str}&community={community}&latitude={lat}&longitude={lon}&start={start}&end={end}&time-standard={t_std}'

    # Catch and handle network errors
    try:
        response = requests.get(request_url, timeout=30)
    except requests.exceptions.ConnectionError:
        print('No or Bad INTERNET Connection')
        return None
    except requests.exceptions.Timeout:
        print('Time Out')
        return None
    except requests.exceptions.TooManyRedirects:
        print ('Too many Redirects ')
        return None
    except requests.exceptions.RequestException as e:
        print(f'An unexpected request error occurred: {e}')
        return None
    except requests.exceptions.JSONDecodeError:
        print('Invalid response: {response.text}')
        return None

    #Handle Server errors
    if response.status_code == 200:
        print(f'{response.status_code}: SUCCESS!')
        json_data = response.json()
        # print(f'response in json format is {json_data}')   # optional, can be commented out
        return json_data
    elif response.status_code == 422:
        error_data = response.json()
        if 'messages' in error_data:
            msg = error_data['messages']
            print(f'Error {msg}')
            if 'time-standard' in str(msg).lower():
                print('Hint: LST time required ')
            if 'parameter' in str(msg).lower():
                print('Hint: parameters incorrect or not supported ')
            if 'limit' in str(msg).lower():
                print('Hint: you may have exceeded the parameters limit')
            if 'detail' in error_data:
                missing = [item['loc'][-1] for item in error_data['detail'] if item['type'] == 'missing']
                print(f'Hint: missing required API parameter(s): {", ".join(missing)}')
        else:
            print(f'Server Error! Make sure the link is correct and all API parameters are correct')
        return None
    elif response.status_code == 429:
        print ('Rate limit exceeded, wait some mins before retry ')
        return None
    elif response.status_code == 500:
        print('Server Error (500), try again later')
        return None
    elif response.status_code == 503:
        print ('Service temporarily unavailable ')
        return None
    else:
        print(f'Unhandled status code: {response.status_code}')
        return None


# --- Get user inputs with validation ---
lat = get_float_input("Enter latitude (-90 to 90): ", -90, 90)
lon = get_float_input("Enter longitude (-180 to 180): ", -180, 180)
start = get_date_input("Enter start date (YYYYMMDD): ")
end = get_date_input("Enter end date (YYYYMMDD): ")

# Ensure start date is not after end date (re‑prompt until corrected)
while start > end:
    print("Error: start date must be on or before end date. Please re-enter both.")
    start = get_date_input("Re-enter start date (YYYYMMDD): ")
    end = get_date_input("Re-enter end date (YYYYMMDD): ")

print(f"\nYou entered:\nLatitude: {lat}\nLongitude: {lon}\nStart date : {start}\nEnd date: {end}\n")



# Call the function with the validated inputs
json_data = fetch_nasa_data(lat, lon, start, end)

# inspect if data is fetched successfully after calling function
if json_data:
    print("Data fetched successfully. Ready for cleaning.")
else:
    print("Failed to fetch data.")
