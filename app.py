
import streamlit as st
import requests

from datetime import datetime, timezone

WX_CODES = {
    "-RA": "🌦️ Light Rain",
    "RA": "🌧️ Rain",
    "+RA": "⛈️ Heavy Rain",
    "-SN": "❄️ Light Snow",
    "SN": "❄️ Snow",
    "TS": "⛈️ Thunderstorm",
    "BR": "🌫️ Mist",
    "FG": "🌁 Fog",
    "HZ": "🌫️ Haze",
    "DZ": "🌦️ Drizzle",
    "SQ": "🌬️ Squall",
    "GR": "🧊 Hail",
    "GS": "🧊 Small Hail"
    }

CLOUD_CODES = {
    "FEW": "Few",
    "SCT": "Scattered",
    "BKN": "Broken",
    "OVC": "Overcast",
    "CLR": "Clear",
    "SKC": "Sky Clear",
    "VV": "Vertical Visibility"
    }

CHANGE_CODES = {
    "FM": "🟢 From",
    "TEMPO": "🟡 Temporary",
    "BECMG": "🔵 Becoming",
    "PROB30": "🟠 30% Probability",
    "PROB40": "🟠 40% Probability"
    }


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
                st.subheader("📋 METAR Summary")

                wind = f"{data.get('wdir', 'VRB')}° @ {data.get('wspd', 'N/A')} kt"
                
                if data.get("wgst"):
                    wind += f" (Gust {data.get('wgst')} kt)"
                
                weather = data.get("wxString", "No significant weather")
                
                flight_cat = data.get("fltCat", "N/A")
                
                visibility = f"{data.get('visib', 'N/A')} SM"
                
                temperature = f"{data.get('temp', 'N/A')}°C"
                
                dewpoint = f"{data.get('dewp', 'N/A')}°C"
                
                pressure = f"{data.get('altim', 'N/A')} inHg"
                
                st.info(f"""
                **Station:** {data.get('icaoId', icao)}
                
                **Observation Time:** {format_time(data.get('obsTime'))}
                
                **Flight Category:** {flight_cat}
                
                **Wind:** {wind}
                
                **Visibility:** {visibility}
                
                **Weather:** {decode_weather(weather)}
                
                **Temperature / Dew Point:** {temperature} / {dewpoint}
                
                **Altimeter:** {pressure}
                """)
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
    
    def format_time(t):
        if not t:
            return "N/A"

        try:
            # If API returns Unix timestamp
            if isinstance(t, (int, float)):
                dt = datetime.fromtimestamp(t, tz=timezone.utc)

            # If API returns timestamp as a string
            elif str(t).isdigit():
                dt = datetime.fromtimestamp(int(t), tz=timezone.utc)

            # If API returns ISO format
            else:
                dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

            return dt.strftime("%d %b %Y %H:%M UTC")

        except Exception:
            return str(t)

    def decode_weather(wx):
        if not wx:
            return "No significant weather"

        parts = wx.split()

        decoded = []

        for p in parts:
            decoded.append(WX_CODES.get(p, p))

        return ", ".join(decoded)
    
    def wind_direction(deg):
        if deg is None:
            return "Variable"

        dirs = [
            "North","North-Northeast","Northeast","East-Northeast",
            "East","East-Southeast","Southeast","South-Southeast",
            "South","South-Southwest","Southwest","West-Southwest",
            "West","West-Northwest","Northwest","North-Northwest"
            ]

        return dirs[round(deg / 22.5) % 16]

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

                st.subheader("📋 General Information")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "🛫 Station",
                        taf.get("icaoId", "N/A")
                    )

                    st.metric(
                        "🕒 Issued",
                        format_time(taf.get("issueTime"))
                    )

                with col2:
                    st.metric(
                        "📅 Valid From",
                        format_time(taf.get("validTimeFrom"))
                    )

                    st.metric(
                        "📅 Valid Until",
                        format_time(taf.get("validTimeTo"))
                    )
                st.subheader("Forecast Periods")

                forecasts = taf.get("fcsts", [])

                if forecasts:

                    for i, fcst in enumerate(forecasts, start=1):

                        title = CHANGE_CODES.get(
                            fcst.get("changeIndicator", ""),
                            f"Forecast {i}"
                        )

                        with st.expander(title, expanded=(i == 1)):

                            st.write(
                                f"🕒 **Valid:** {format_time(fcst.get('timeFrom'))} → {format_time(fcst.get('timeTo'))}"
                            )

                            st.write("### 🌬️ Wind")

                            direction = wind_direction(fcst.get("wdir"))

                            st.write(
                                f"{direction} ({fcst.get('wdir','VRB')}°) @ {fcst.get('wspd','N/A')} kt"
                            )

                            gust = fcst.get("wgst")

                            if gust:
                                st.write(f"💨 Gusts: {gust} kt")

                            st.write("### 👀 Visibility")
                            st.write(f"{fcst.get('visib','N/A')} SM")

                            st.write("### 🌦️ Weather")
                            st.write(decode_weather(fcst.get("wxString")))
                            
                            st.write("### ☁️ Cloud Layers")

                            clouds = fcst.get("clouds", [])

                            if clouds:

                                for cloud in clouds:

                                    cover = CLOUD_CODES.get(
                                        cloud.get("cover"),
                                        cloud.get("cover")
                                    )

                                    st.write(
                                        f"• {cover} at {cloud.get('base')} ft"
                                    )

                            else:
                                st.write("Sky clear")

                # else:
                #     st.info("Forecast details not available.")
    except Exception as e:
        st.error(f"Error fetching TAF: {e}")
