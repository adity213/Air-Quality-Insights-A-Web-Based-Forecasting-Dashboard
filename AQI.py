import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load city data
@st.cache_data
def load_city_data():
    city_data = pd.read_csv("CityVals.csv")
    return city_data

# Streamlit App Layout
def main():
    st.title("City Air Quality Index (AQI) Dashboard")
    st.write("### Check Hourly AQI for Specific Cities")

    # Load and process city data
    city_data = load_city_data()

    # Clean data: Remove cities with entirely missing values
    city_columns = [col for col in city_data.columns if col != "Timestamp"]
    city_data_cleaned = city_data.dropna(subset=city_columns, how='all')

    # Melt the DataFrame to long format
    city_data_melted = city_data_cleaned.melt(
        id_vars=["Timestamp"],
        value_vars=city_columns,
        var_name="City",
        value_name="Max_AQI"
    )

    # Extract 'Hour' from the 'Timestamp' column
    city_data_melted['Timestamp'] = pd.to_datetime(city_data_melted['Timestamp'], dayfirst=True)
    city_data_melted['Hour'] = city_data_melted['Timestamp'].dt.hour
    city_data_melted['City'] = city_data_melted['City'].str.replace('_Max_AQI', '', regex=True).str.strip()

    # Drop rows where 'Max_AQI' is NaN
    city_data_melted = city_data_melted.dropna(subset=["Max_AQI"])

    # Retrieve unique city names
    cities = city_data_melted['City'].unique()

    # Dropdown to select a city
    selected_city = st.selectbox("Select a City", cities)

    # Filter data for the selected city
    city_aqi_data = city_data_melted[city_data_melted['City'] == selected_city]

    # User input for date
    unique_dates = city_aqi_data['Timestamp'].dt.date.unique()
    selected_date = st.date_input("Select a Date", min_value=min(unique_dates), max_value=max(unique_dates))

    # Filter data for the selected date
    date_data = city_aqi_data[city_aqi_data['Timestamp'].dt.date == selected_date]

    # Check button
    if st.button("Show Hourly AQI Data"):
        if date_data.empty:
            st.warning(f"No AQI data available for {selected_city} on {selected_date}.")
        else:
            # Create a line plot for hourly AQI data
            plt.figure(figsize=(10, 6))
            plt.plot(date_data['Hour'], date_data['Max_AQI'], marker='o', linestyle='-', color='blue')
            plt.title(f"Hourly AQI for {selected_city} on {selected_date}")
            plt.xlabel("Hour of the Day")
            plt.ylabel("AQI")
            plt.xticks(range(0, 24))
            plt.grid(True)
            st.pyplot(plt)

    # Ranklist of cities based on AQI for the day
    st.sidebar.title("City Rankings")
    st.sidebar.write("### Least Polluted Cities (Ranked)")

    # Exclude cities without valid AQI data for the selected date
    daily_data = city_data_melted[city_data_melted['Timestamp'].dt.date == selected_date]
    city_daily_avg = daily_data.groupby('City')['Max_AQI'].mean().dropna().sort_values()

    # Display rankings
    for idx, (city, aqi) in enumerate(city_daily_avg.items(), 1):
        st.sidebar.markdown(f"**{idx}. {city}: {aqi:.2f}**")


if __name__ == "__main__":
    main()
