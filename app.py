import streamlit as st
import requests

st.set_page_config(
    page_title="Aviation Weather Dashboard",
    page_icon="✈️",
    layout="centered"
)


st.markdown("""
<style>
.fixed-title {
    position: fixed;
    top: 12px;
    left: 20px;
    z-index: 99999;

    font-size: 24px;
    font-weight: 700;
    color: white;
    background: transparent;
}
</style>

<div class="fixed-title">
    ✈️ Aviation Weather Dashboard
</div>
""", unsafe_allow_html=True)

st.title("✈️ Aviation Weather Dashboard")
st.write("Enter an ICAO airport code to get the latest METAR.")

icao = st.text_input("ICAO Code", "VIDP").upper()

if st.button("Get METAR"):

    url = f"https://aviationweather.gov/api/data/metar?ids={icao}&format=json"

    try:
        response = requests.get(url)

        if response.status_code != 200:
            st.error("Unable to fetch data.")
        else:
            metar = response.json()

            if not metar:
                st.warning("No METAR found for this airport.")
            else:
                data = metar[0]

                st.success("METAR Retrieved Successfully!")

                st.subheader("Raw METAR")
                st.code(data.get("rawOb", "N/A"))

                st.subheader("Weather Details")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Temperature", f"{data.get('temp', 'N/A')} °C")
                    st.metric("Wind Speed", f"{data.get('wspd', 'N/A')} kt")
                    st.metric("Wind Direction", f"{data.get('wdir', 'N/A')}°")

                with col2:
                    st.metric("Visibility", f"{data.get('visib', 'N/A')} SM")
                    st.metric("Dew Point", f"{data.get('dewp', 'N/A')} °C")
                    st.metric("Flight Category", data.get("fltCat", "N/A"))

                st.subheader("Cloud Layers")

                if "clouds" in data:
                    for cloud in data["clouds"]:
                        st.write(
                            f"• {cloud.get('cover', 'N/A')} at {cloud.get('base', 'N/A')} ft"
                        )
                else:
                    st.write("No cloud information available.")

    except Exception as e:
        st.error(f"Error: {e}")


#TAFFF
# -------------------- TAF --------------------

if st.button("Get TAF"):
    st.divider()
    st.header("🛫 Terminal Aerodrome Forecast (TAF)")

    taf_url = f"https://aviationweather.gov/api/data/taf?ids={icao}&format=json"

    try:
        response = requests.get(taf_url)

        if response.status_code != 200:
            st.error("Unable to fetch TAF.")
        else:
            taf_list = response.json()

            if not taf_list:
                st.warning("No TAF available.")
            else:
                taf = taf_list[0]

                st.success("TAF Retrieved Successfully!")

                st.subheader("Raw TAF")
                st.code(taf.get("rawTAF", "N/A"))

                st.subheader("General Information")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Issue Time", taf.get("issueTime", "N/A"))
                    st.metric("Valid From", taf.get("validTimeFrom", "N/A"))

                with col2:
                    st.metric("Valid To", taf.get("validTimeTo", "N/A"))
                    st.metric("Station", taf.get("icaoId", "N/A"))

                st.subheader("Forecast Periods")

                forecasts = taf.get("fcsts", [])

                if forecasts:
                    for i, fcst in enumerate(forecasts, start=1):

                        st.markdown(f"### Forecast {i}")

                        c1, c2 = st.columns(2)

                        with c1:
                            st.write(f"**From:** {fcst.get('timeFrom', 'N/A')}")
                            st.write(f"**Wind:** {fcst.get('wdir', 'VRB')}° @ {fcst.get('wspd', 'N/A')} kt")
                            st.write(f"**Visibility:** {fcst.get('visib', 'N/A')} SM")

                        with c2:
                            st.write(f"**To:** {fcst.get('timeTo', 'N/A')}")
                            st.write(f"**Wind Gust:** {fcst.get('wgst', 'None')} kt")
                            st.write(f"**Weather:** {fcst.get('wxString', 'None')}")

                        clouds = fcst.get("clouds", [])

                        if clouds:
                            st.write("**Cloud Layers:**")
                            for cloud in clouds:
                                st.write(
                                    f"• {cloud.get('cover', 'N/A')} at {cloud.get('base', 'N/A')} ft"
                                )

                        st.divider()

                else:
                    st.info("Forecast details not available.")

    except Exception as e:
        st.error(f"Error fetching TAF: {e}")