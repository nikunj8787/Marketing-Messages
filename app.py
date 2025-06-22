import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ClearDeals WhatsApp Marketing Generator", layout="wide")

# --- Short links ---
EMI_LINK = "https://lnk.ink/FUwEc"
VALUATION_LINK = "https://lnk.ink/fkYwF"

# --- Your Geoapify API Key ---
GEOAPIFY_API_KEY = "d1632c8149f94409b7f78f29c458716d"

def process_location(location):
    # Remove first letter and dash if present, e.g. "A-Gota" -> "Gota"
    if location and len(location) > 2 and location[1] == '-':
        return location[2:].strip()
    return location.strip() if location else ""

def geocode_address(address):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200 and resp.json()["features"]:
        coords = resp.json()["features"][0]["geometry"]["coordinates"]
        return coords[1], coords[0]  # lat, lon
    return None, None

def fetch_nearby(lat, lon, category, limit=2):
    url = (
        f"https://api.geoapify.com/v2/places?categories={category}"
        f"&filter=circle:{lon},{lat},2000&limit={limit}&apiKey={GEOAPIFY_API_KEY}"
    )
    resp = requests.get(url)
    if resp.status_code == 200:
        features = resp.json().get("features", [])
        return [f["properties"]["name"] for f in features if "name" in f["properties"]]
    return []

def get_nearby_info(address):
    lat, lon = geocode_address(address)
    if lat is None or lon is None:
        return {
            "schools": [],
            "colleges": [],
            "malls": [],
            "hospitals": [],
        }
    return {
        "schools": fetch_nearby(lat, lon, "education.school", limit=2),
        "colleges": fetch_nearby(lat, lon, "education.college", limit=2),
        "malls": fetch_nearby(lat, lon, "commercial.shopping_mall", limit=2),
        "hospitals": fetch_nearby(lat, lon, "healthcare.hospital", limit=2),
    }

def get_amenities(address, amenities_from_file):
    # If amenities are missing or empty, use a generic list
    if pd.isna(amenities_from_file) or str(amenities_from_file).strip().lower() in ["", "nan", "not available"]:
        return "Clubhouse, Gym, Swimming Pool, Security"
    return amenities_from_file

st.title("ClearDeals WhatsApp Marketing Message Generator")

uploaded_file = st.file_uploader(
    "Upload your property file (.csv, .xls, .xlsx)", 
    type=["csv", "xls", "xlsx"]
)

def get_value(prop, possible_names, default=""):
    for name in possible_names:
        if name in prop:
            return prop[name]
    return default

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = [col.strip().replace("-", "").replace("_", "").lower() for col in df.columns]

    st.write("**Columns detected in your file:**", list(df.columns))

    tag_col = [col for col in df.columns if col.startswith("tag")][0]
    tag = st.selectbox("Select Property Tag", df[tag_col].astype(str))
    prop = df[df[tag_col].astype(str) == tag].iloc[0]

    def g(colnames, default=""):
        return get_value(prop, [c.strip().replace("-", "").replace("_", "").lower() for c in colnames], default)

    property_address = g(['Property-Address','propertyaddress'])
    location_raw = g(['Location','location'])
    location = process_location(location_raw)
    bhk = g(['BHK','bhk'])
    area = g(['Super-Built-up-Construction-Area','superbuiltuppconstructionarea'])
    price = g(['Property-Price','propertyprice'])
    amenities = get_amenities(property_address, g(['Amenities','amenities']))

    # Fetch real nearby info
    with st.spinner("Fetching real nearby places..."):
        nearby = get_nearby_info(f"{property_address}, {location}")
    schools = ', '.join(nearby["schools"]) if nearby["schools"] else "top schools nearby"
    colleges = ', '.join(nearby["colleges"]) if nearby["colleges"] else "reputed colleges in the area"
    malls = ', '.join(nearby["malls"]) if nearby["malls"] else "popular shopping malls"
    hospitals = ', '.join(nearby["hospitals"]) if nearby["hospitals"] else "multi-speciality hospitals"

    # Compose all 10 messages (highly formatted, vertical spacing, emojis, personal, WhatsApp-ready)
    spacing = "\n\n"
    messages = [
        f"""🏡 *{property_address}* is a spacious {bhk} home with {area} of luxury living in {location}.{spacing}You've already shortlisted the best match for your needs after your first visit—congratulations!{spacing}Enjoy comfort, style, and privacy in a thoughtfully designed layout.{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""📍 Location is everything! *{property_address}* is in the heart of {location}.{spacing}Top schools: {schools}{spacing}Colleges: {colleges}{spacing}Shopping malls: {malls}{spacing}Hospitals: {hospitals}{spacing}You’ve chosen a vibrant, well-connected neighborhood—move forward with confidence!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""⏳ Properties like *{property_address}* in {location} are in high demand!{spacing}You've already picked the best option—don't let this opportunity slip away.{spacing}Secure your dream home before someone else does. Book your next visit or reserve today!{spacing}Reply with
