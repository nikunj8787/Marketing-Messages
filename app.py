import streamlit as st
import pandas as pd
import requests
import time
import json

# Set page config
st.set_page_config(page_title="ClearDeals Gujarati Marketing Generator", layout="wide")

# Load secrets
try:
    HF_TOKEN = st.secrets["huggingface"]["api_token"]
    GEO_API_KEY = st.secrets["geoapify"]["api_key"]
    EMI_LINK = st.secrets["links"]["emi_calculator"]
    VALUATION_LINK = st.secrets["links"]["valuation_calculator"]
except KeyError:
    st.error("Please set your API tokens in Secrets.")
    st.stop()

# Classes for services
class Geoapify:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and resp.json()["features"]:
                coords = resp.json()["features"][0]["geometry"]["coordinates"]
                return coords[1], coords[0]
        except:
            pass
        return None, None

    def nearby_places(self, lat, lon, category, limit=2, radius=5000):
        url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{lon},{lat},{radius}&limit={limit}&apiKey={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return [f["properties"]["name"] for f in resp.json().get("features", []) if "name" in f["properties"]]
        except:
            pass
        return []

    def get_nearby(self, address, city="Ahmedabad", state="Gujarat"):
        full_addr = f"{address}, {city}, {state}"
        lat, lon = self.geocode(full_addr)
        if lat is None or lon is None:
            lat, lon = self.geocode(f"{city}, {state}")
        if lat is None or lon is None:
            return {"schools": [], "colleges": [], "malls": [], "hospitals": []}
        return {
            "schools": self.nearby_places(lat, lon, "education.school"),
            "colleges": self.nearby_places(lat, lon, "education.college"),
            "malls": self.nearby_places(lat, lon, "commercial.shopping_mall"),
            "hospitals": self.nearby_places(lat, lon, "healthcare.hospital")
        }

class HuggingFaceLLM:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def generate(self, prompt):
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and "generated_text" in result[0]:
                    text = result[0]["generated_text"]
                    return text.replace(prompt, "").strip()
                elif isinstance(result, dict) and "generated_text" in result:
                    return result["generated_text"].replace(prompt, "").strip()
        except:
            pass
        return ""

# Helper functions
def process_location(loc):
    if loc and len(loc) > 2 and loc[1] == '-':
        return loc[2:].strip()
    return loc.strip() if loc else ""

def get_value(prop, keys, default="NA"):
    for k in keys:
        if k in prop and pd.notna(prop[k]) and str(prop[k]).strip():
            return str(prop[k]).strip()
    return default

# Main app
st.title("🏠 ClearDeals Gujarati Marketing Generator")
uploaded_file = st.file_uploader("Upload your data file (.csv, .xls, .xlsx)", type=["csv","xls","xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = [c.strip().replace("-", "").replace("_", "").lower() for c in df.columns]
    st.write("**Detected columns:**", list(df.columns))
    tag_col = [c for c in df.columns if c.startswith("tag")]
    if not tag_col:
        st.error("No 'Tag' column found.")
        st.stop()
    tag_col = tag_col[0]
    tags = df[tag_col].astype(str)
    selected_tag = st.selectbox("Select Property Tag", tags)
    prop = df[df[tag_col].astype(str) == selected_tag].iloc[0]

    # Extract data
    def get_field(cols):
        return get_value(prop, cols, "NA")
    address = get_field(['propertyaddress','name'])
    loc_raw = get_field(['location','area'])
    location = process_location(loc_raw)
    bhk = get_field(['bhk','configuration'])
    price = get_field(['propertyprice','price'])
    area = get_field(['superbuiltuppconstructionarea','area'])
    furnishing = get_field(['furnishing','furnishing'])
    age = get_field(['age','propertyage'])
    tour_link = get_field(['360tourlink','k'])
    video_link = get_field(['videolink','l'])

    # Fetch nearby info
    geo = Geoapify(GEO_API_KEY)
    with st.spinner("Fetching nearby places..."):
        nearby = geo.get_nearby(address)
    schools = ', '.join(nearby['schools']) if nearby['schools'] else "શાળા નજીક"
    colleges = ', '.join(nearby['colleges']) if nearby['colleges'] else "કોલેજ નજીક"
    malls = ', '.join(nearby['malls']) if nearby['malls'] else "મોલ નજીક"
    hospitals = ', '.join(nearby['hospitals']) if nearby['hospitals'] else "હૉસ્પિટલ નજીક"

    # Initialize LLM
    llm = HuggingFaceLLM(HF_TOKEN)

    # Generate messages
    message_types = [
        "Property Benefits",
        "Location Advantage",
        "FOMO/Urgency",
        "Trust Building",
        "Lifestyle Appeal",
        "Value Proposition",
        "Financial Assistance",
        "Market Analysis",
        "Social Validation",
        "Action Oriented"
    ]

    messages = []
    for idx, mtype in enumerate(message_types):
        prompt = f"""
        Create a friendly, professional Gujarati WhatsApp message for a property with these details:

        Project Name / Location: {address}
        City: {get_value(prop, ['city'],'NA')}
        Locality: {location}
        Price: {price}
        BHK: {bhk}
        Area: {area} sq.yds
        Facing: {get_value(prop,['facing'],'NA')}
        Furnishing: {furnishing}
        Age: {age}
        360 Tour Link: {tour_link}
        Video Link: {video_link}

        Focus: {mtype}
        Context: This is a follow-up message after the first site visit.
        End with: "Reply with a 'Hi' to take this deal forward."
        End with: "www.cleardeals.co.in, No Brokerage Realtor."
        """

        msg = llm.generate(prompt)
        if not msg or len(msg) < 50:
            # fallback template
            msg = f"🏡 {address} in {location} is a beautiful {bhk} with {area} sq.yds. Price: {price}. Visit again to explore more! Reply 'Hi' to proceed.\nwww.cleardeals.co.in, No Brokerage Realtor."
        messages.append(msg)
        time.sleep(0.5)

    # Display messages
    st.markdown("---")
    st.subheader("Gujarati Marketing Messages")
    all_text = ""
    for i, msg in enumerate(messages):
        st.markdown(
            f"""<div style="background:#f0f0f0; border-radius:8px; padding:12px; margin-bottom:12px; line-height:1.5;">
            <b>દિવસ {i+1}</b> - {message_types[i]}<br><br>
            {msg}
            </div>""", unsafe_allow_html=True
        )
        all_text += msg + "\n\n"

    # Download all
    st.download_button(
        "📥 Download All Messages (.txt)",
        all_text,
        file_name=f"{address}_Gujarati_Messages.txt"
    )
    st.success("Messages generated successfully!")

