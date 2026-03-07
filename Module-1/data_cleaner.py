import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def clean_nasa_data(json_data):
    # get the actual weather data from inside the json
    weather_params = json_data['properties']['parameter']

    # turn it into a DataFrame
    df = pd.DataFrame(weather_params)

    # the row labels are timestamps – convert to proper datetime
    df.index = pd.to_datetime(df.index, format='%Y%m%d%H')

    # make sure rows are in chronological order
    df.sort_index(inplace=True)

    # NASA uses -999 to mean missing data – replace with NaN
    df.replace(-999, np.nan, inplace=True)

    # quick summary – useful to check data ranges
    print(df.describe())

    # plot temperature
    df['T2M'].plot(figsize=(12,5), color='green', linewidth=2)
    plt.title('Temperature at 2 Meters - January 2023')
    plt.ylabel('Temperature °C')
    plt.xlabel('Date')
    plt.grid(True, alpha=0.6)
    plt.tight_layout()
    plt.show()

    # plot actual solar irradiance
    df['ALLSKY_SFC_SW_DWN'].plot(figsize=(12,5), color='red', linewidth=2)
    plt.title('AWE Solar Irradiance - Jan 2023')
    plt.ylabel('Solar Irradiance (Wh/m²)')
    plt.xlabel('Date')
    plt.grid(True, alpha=0.6)
    plt.show()

    # compare actual vs clear‑sky solar
    df[['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN']].plot(figsize=(12,5))
    plt.title('All Sky vs Clear Sky Solar Irradiance - Jan 2023')
    plt.xlabel('Date')
    plt.ylabel('Solar Irradiance (Wh/m²)')
    plt.grid(True, alpha=0.3)
    plt.legend(['Actual', 'Clear Sky'])
    plt.show()

    # compute cloud attenuation (sunlight blocked by clouds)
    df['cloud_attenuation'] = df['CLRSKY_SFC_SW_DWN'] - df['ALLSKY_SFC_SW_DWN']

    # plot cloud attenuation
    df['cloud_attenuation'].plot(figsize=(12,5), linewidth=2, color='orange')
    plt.title('Amount of solar blocked during cloudy days (solar attenuation)')
    plt.ylabel('Solar Attenuation (Wh/m²)')
    plt.xlabel('Date')
    plt.grid(True, alpha=0.6)
    plt.show()

    # optional – check last few rows if needed
    # print(df['cloud_attenuation'].tail(20))

    # save cleaned data to CSV (includes the datetime index as a column)
    df.to_csv('cleaned_nasa_data.csv', index=True)
    print("Cleaned data saved as 'cleaned_nasa_data.csv'")

    return df
  
