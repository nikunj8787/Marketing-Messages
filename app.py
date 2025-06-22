import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ClearDeals WhatsApp Marketing Generator", layout="wide")

# --- Short links ---
EMI_LINK = "https://lnk.ink/FUwEc"
VALUATION_LINK = "https://lnk.ink/fkYwF"

# --- Geoapify API Key ---
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

        f"""⏳ Properties like *{property_address}* in {location} are in high demand!{spacing}You've already picked the best option—don't let this opportunity slip away.{spacing}Secure your dream home before someone else does. Book your next visit or reserve today!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""✅ Trust matters! Hundreds of families have chosen *{property_address}* for its transparency and value.{spacing}You’ve made a smart choice with ClearDeals—no brokerage, no hidden fees, just honest service.{spacing}Your investment is protected with us. Let's move ahead!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🌟 Imagine your family enjoying {amenities} at *{property_address}*.{spacing}The community is lively, secure, and perfect for a modern lifestyle.{spacing}You’ve already found the right fit—let’s make it yours!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""💰 Value for money! *{property_address}* offers a {bhk} at just {price} in {location}.{spacing}Compared to similar properties, this is a standout deal.{spacing}You’ve done your homework—now let’s close the best deal for you!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🏦 Need help with home finance? Calculate your EMI for *{property_address}* here: {EMI_LINK}{spacing}Our experts will guide you through loan approval and paperwork, so you can move in stress-free.{spacing}You’ve selected the right home—let’s make it yours!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""📊 Want to know the market value? Get a free valuation report for *{property_address}*: {VALUATION_LINK}{spacing}Make an informed decision—ClearDeals provides verified insights for your peace of mind.{spacing}You’ve already shortlisted the best—let’s take the next step!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""👥 Join happy residents at *{property_address}*—read their stories and see why they love it here.{spacing}You’ve chosen a community with great reviews and a welcoming vibe.{spacing}Let’s make you the newest member!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🎯 Ready to move ahead with *{property_address}* in {location}?{spacing}You’ve already found your perfect fit—now’s the time to act.{spacing}Let’s finalize your dream home and start your new journey!{spacing}Reply with a "Hi" to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor."""
    ]

    st.markdown("---")
    st.subheader("Generated WhatsApp Marketing Messages")
    all_messages = ""
    categories = [
        "PROPERTY BENEFITS", "LOCATION ADVANTAGE", "FOMO/URGENCY", 
        "TRUST BUILDING", "LIFESTYLE APPEAL", "VALUE PROPOSITION",
        "FINANCIAL ASSISTANCE", "MARKET ANALYSIS", "SOCIAL VALIDATION", 
        "ACTION ORIENTED"
    ]
    for i, msg in enumerate(messages):
        st.markdown(
            f"""
            <div style="background:#f8f9fa; border-radius:10px; padding:16px; margin-bottom:16px; border:1px solid #e0e0e0;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:bold; color:#2e8b57;">{categories[i]}</div>
                    <div style="background:#e0f7fa; color:#00838f; border-radius:12px; padding:2px 10px; font-size:13px;">Day {i+1}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.text_area(
            label="",
            value=msg,
            height=220,
            key=f"msg_{i}",
            help="Click the copy icon to copy this message"
        )
        all_messages += msg + "\n\n"

    st.download_button(
        "📥 Download All Messages (.txt)",
        all_messages,
        file_name=f"{property_address.replace(' ','_').replace('/','_')}_WhatsApp_Followup.txt"
    )

    st.info("💡 Tip: Copy individual messages using the copy icon, or download all messages for WhatsApp campaigns.")
