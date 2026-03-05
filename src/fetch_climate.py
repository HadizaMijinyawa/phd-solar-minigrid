# NASA POWER Hourly API Parameters
# Endpoint: https://power.larc.nasa.gov/api/temporal/hourly/point
#
# Required parameters:
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
# Temporal resolution: Hourly (LST) – matches my GAN output (8760 steps) and captures diurnal cycles essential for my physics rules
# Why hourly: Efficiency losses, cloud effects, dust accumulation tracking all need sub‑day precision
# Max 15 parameters per hourly request – this list fits exactly

# 1. ALLSKY_SFC_SW_DWN – All Sky Insolation on Horizontal Surface
#    What it is: Total sunlight (direct + diffuse) reaching the ground under actual sky conditions.
#    Why I need it: Primary input for PV generation. My GAN learns realistic solar power profiles from this.

# 2. CLRSKY_SFC_SW_DWN – Clear Sky Insolation on Horizontal Surface
#    What it is: Sunlight that would reach the ground if there were no clouds.
#    Why I need it: Compare with ALLSKY to quantify cloud attenuation – used in my cloud‑cover physics rule.

# 3. T2M – Temperature at 2 Meters
#    What it is: Ambient air temperature (the weather you feel).
#    Why I need it: Core input for my 0.45% efficiency loss per °C above 25°C (my temperature rule).

# 4. RH2M – Relative Humidity at 2 Meters
#    What it is: Percentage of water vapour in the air.
#    Why I need it: High humidity → corrosion risk for inverters and metal parts. Used in my failure‑mode profiling.

# 5. PRECTOTCORR – Precipitation (corrected)
#    What it is: Daily rainfall amount.
#    Why I need it: For my dust accumulation rule – I need “days since last rainfall” because rain cleans panels.

# 6. CLOUD_AMT – Cloud Amount
#    What it is: Percentage of sky covered by clouds.
#    Why I need it: Directly affects solar generation; used in my cloud‑cover physics penalty (15‑30% loss).

# 7. WS10M – Wind Speed at 10 Meters
#    What it is: How fast the wind blows at 10m height.
#    Why I need it: Wind transports dust (affects soiling) and can slightly cool panels – helps me model dust accumulation.

# 8. PS – Surface Pressure
#     What it is: Air pressure at ground level.
#     Why I need it: Optional but fills my 15‑parameter limit; relates to air density and cooling.

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

#Fetch Data of awe LGA (using its latitude and longitude) in json format from NASA POWER

endpoint_url = 'https://power.larc.nasa.gov/api/temporal/hourly/point'
community = 'RE'
lat=8.11
lon=9.15
start=20230101
end=20230131
t_std= 'LST'
parameters = ['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN', 'T2M', 'RH2M', 'PRECTOTCORR', 'CLOUD_AMT', 'WS10M', 'PS', 'T2MDEW', 'KT', 'WD10M']
parameters_str = ','.join(parameters)

request_url = f'{endpoint_url}?parameters={parameters_str}&community={community}&latitude={lat}&longitude={lon}&start={start}&end={end}&time-standard={t_std}'

# Catch and handle network errors
try:
   response = requests.get(request_url, timeout=30)
except requests.exceptions.ConnectionError:
   print('No or Bad INTERNET Connection')
except requests.exceptions.Timeout:
   print('Time Out')
except requests.exceptions.TooManyRedirects:
   print ('Too many Redirects ')
except requests.exceptions.RequestException as e:
    print(f'An unexpected request error occurred: {e}')
#except requests.exceptions.RequestException:
   #print(f'An unexpected request error occured', {e})
except requests.exceptions.JSONDecodeError:
   print('Invalid response: {response.text}')


#Handle Server errors
if response.status_code == 200:
   print(response.status_code)
   json_data = response.json()
   print(f'response in json format is {json_data}')
elif response.status_code == 422:
   error_data = response.json()
   if 'messages' in error_data:
      msg = error_data['messages']
      print(f'Error {msg}')
      if'time-standard' in str(msg).lower():
         print('Hint: LST time required ')
      if 'parameter' in str(msg).lower():
         print('Hint: parameters incorrect or not supported ')
      if 'limit' in str(msg).lower():
         print('Hint: you may have exceeded the parameters limit')
      if 'detail' in error_data:
         missing = [item['loc'][-1] for item in error_data['detail'] if item['type'] == 'missing']
         print(f'Hint: missing required API parameter(s): {", ".join(missing)}')

   else :
      print(f'Server Error! Make sure the link is correct and all API parameters are correct')
elif response.status_code == 429:
   print ('Rate limit exceeded, wait some mins before retry ')
elif response.status_code == 500:
   print('Server Error (500), try again later')
elif response.status_code == 503:
   print ('Service temporarily unavailable ')



#Converting the fetched json data to DataFrame
