import streamlit as st
import pandas as pd

st.set_page_config(page_title="ClearDeals WhatsApp Marketing Generator", layout="wide")

# --- Short links (replace with your own if needed) ---
EMI_LINK = "https://lnk.ink/FUwEc"  # EMI calculator
VALUATION_LINK = "https://lnk.ink/fkYwF"  # Property valuation

# Simulated public info for demo purposes (expand as needed)
public_info = {
    "Samruddh Green Residency": {
        "nearby_schools": ["Green Valley High School", "Sunrise Public School"],
        "nearby_colleges": ["Ahmedabad Engineering College", "City Arts College"],
        "nearby_malls": ["Alpha Mall", "City Center Mall"],
        "nearby_hospitals": ["City Hospital", "Green Care Clinic"],
        "amenities": "Clubhouse, Garden, Gym, Swimming Pool"
    },
    "Kismat Society": {
        "nearby_schools": ["Kismat Public School", "Bright Future Academy"],
        "nearby_colleges": ["Kismat College of Commerce"],
        "nearby_malls": ["Kismat Shopping Complex"],
        "nearby_hospitals": ["Kismat Health Center"],
        "amenities": "Playground, Community Hall, Security"
    }
    # Add more properties as needed
}

def get_public_info(property_address):
    return public_info.get(property_address, {
        "nearby_schools": [],
        "nearby_colleges": [],
        "nearby_malls": [],
        "nearby_hospitals": [],
        "amenities": "Modern amenities"
    })

def process_location(location):
    # Remove first letter and dash if present, e.g. "A-Gota" -> "Gota"
    if location and len(location) > 2 and location[1] == '-':
        return location[2:].strip()
    return location.strip() if location else ""

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
    amenities = g(['Amenities','amenities'])
    if amenities.lower() in ["", "nan", "not available"]:
        amenities = get_public_info(property_address)["amenities"]

    pubinfo = get_public_info(property_address)
    schools = ', '.join(pubinfo["nearby_schools"]) if pubinfo["nearby_schools"] else "top schools nearby"
    colleges = ', '.join(pubinfo["nearby_colleges"]) if pubinfo["nearby_colleges"] else "reputed colleges in the area"
    malls = ', '.join(pubinfo["nearby_malls"]) if pubinfo["nearby_malls"] else "popular shopping malls"
    hospitals = ', '.join(pubinfo["nearby_hospitals"]) if pubinfo["nearby_hospitals"] else "multi-speciality hospitals"
    amenities_text = pubinfo["amenities"] if pubinfo["amenities"] else amenities

    # Compose all 10 messages (each as 4+ lines, WhatsApp formatting, personal tone)
    messages = [
        f"""🏡 *{property_address}* is a spacious {bhk} home with {area} of luxury living in {location}.
You've already shortlisted the best match for your needs after your first visit—congratulations!
Enjoy comfort, style, and privacy in a thoughtfully designed layout.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""📍 Location is everything! *{property_address}* is in the heart of {location}.
Top schools ({schools}), colleges ({colleges}), shopping malls ({malls}), and hospitals ({hospitals}) are all close by.
You’ve chosen a vibrant, well-connected neighborhood—move forward with confidence!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""⏳ Properties like *{property_address}* in {location} are in high demand!
You've already picked the best option—don't let this opportunity slip away.
Secure your dream home before someone else does. Book your next visit or reserve today!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""✅ Trust matters! Hundreds of families have chosen *{property_address}* for its transparency and value.
You’ve made a smart choice with ClearDeals—no brokerage, no hidden fees, just honest service.
Your investment is protected with us. Let's move ahead!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🌟 Imagine your family enjoying {amenities_text} at *{property_address}*.
The community is lively, secure, and perfect for a modern lifestyle.
You’ve already found the right fit—let’s make it yours!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""💰 Value for money! *{property_address}* offers a {bhk} at just {price} in {location}.
Compared to similar properties, this is a standout deal.
You’ve done your homework—now let’s close the best deal for you!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🏦 Need help with home finance? Calculate your EMI for *{property_address}* here: {EMI_LINK}
Our experts will guide you through loan approval and paperwork, so you can move in stress-free.
You’ve selected the right home—let’s make it yours!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""📊 Want to know the market value? Get a free valuation report for *{property_address}*: {VALUATION_LINK}
Make an informed decision—ClearDeals provides verified insights for your peace of mind.
You’ve already shortlisted the best—let’s take the next step!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""👥 Join happy residents at *{property_address}*—read their stories and see why they love it here.
You’ve chosen a community with great reviews and a welcoming vibe.
Let’s make you the newest member!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        f"""🚀 Only a few units left at *{property_address}* in {location}!
You’ve already found your perfect fit—now’s the time to act.
Let’s finalize your dream home and start your new journey!
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor."""
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
            height=180,
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
