import streamlit as st
import pandas as pd

st.set_page_config(page_title="ClearDeals WhatsApp Marketing Generator", layout="wide")

# --- Short links (replace with your own if needed) ---
EMI_LINK = "https://rb.gy/abcd12"  # Shortened EMI calculator link
VALUATION_LINK = "https://rb.gy/wxyz34"  # Shortened property valuation link

st.title("ClearDeals WhatsApp Marketing Message Generator")

uploaded_file = st.file_uploader(
    "Upload your property file (.csv, .xls, .xlsx)", 
    type=["csv", "xls", "xlsx"]
)

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    tag = st.selectbox("Select Property Tag", df['Tag'].astype(str))
    prop = df[df['Tag'].astype(str) == tag].iloc[0]

    # Compose all 10 messages (each as 4+ lines, with WhatsApp formatting)
    messages = [
        # 1. Property Benefits
        f"""🏡 *{prop['Property-Address']}* offers a spacious {prop['BHK']} with {prop['Super-Built-up-Construction-Area']} of luxury living space.
A perfect blend of comfort and style for your family, with modern interiors and ample natural light.
Enjoy privacy and convenience in a well-planned layout.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 2. Location Advantage
        f"""📍 *{prop['Property-Address']}* is at an unbeatable location in {prop['Location']}!
Everything you need is just minutes away—schools, hospitals, shopping centers, and public transport.
Live in a thriving neighborhood with excellent connectivity.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 3. FOMO/Urgency Creation
        f"""⏳ Opportunities like *{prop['Property-Address']}* in {prop['Location']} don't last long!
Demand is high and units are moving fast—secure your dream home before it's gone.
Contact now to book your site visit and avoid missing out.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",
