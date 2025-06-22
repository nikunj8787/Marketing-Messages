import streamlit as st
import pandas as pd
import io

st.title("Property Marketing Message Generator")

uploaded_file = st.file_uploader(
    "Upload your property file (.csv, .xls, .xlsx)", 
    type=["csv", "xls", "xlsx"]
)

if uploaded_file:
    # Determine file type and load accordingly
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove extra spaces from headers

    # Use the 'Tag' column for selection
    tag = st.selectbox("Select Property Tag", df['Tag'].astype(str))
    prop = df[df['Tag'].astype(str) == tag].iloc[0]

    # Generate messages
    messages = [
        f"🏠 {prop['Property-Address']} ({prop['BHK']}) in {prop['Location']} offers {prop['Super-Built-up-Construction-Area']} of space.",
        f"📍 Prime spot: {prop['Location']} - perfect for your needs.",
        f"💰 Attractive price: {prop['Property-Price']} for this property.",
        f"✨ Spacious {prop['BHK']} at {prop['Property-Address']}.",
        f"🔑 Secure your dream property at {prop['Property-Address']} today.",
        f"🌟 Modern amenities and great connectivity in {prop['Location']}.",
        f"🏦 Need a loan? Check your eligibility for {prop['Property-Price']}.",
        f"📊 Get a free valuation for {prop['Property-Address']} now.",
        f"👥 Join a thriving community at {prop['Property-Address']}.",
        f"⏳ Don’t wait! Schedule your visit to {prop['Property-Address']} today."
    ]
    st.write("### Marketing Messages")
    for m in messages:
        st.write(m)

    # Download as .txt
    txt = "\n".join(messages)
    safe_name = prop['Property-Address'].replace(' ', '_').replace('/', '_')
    st.download_button(
        "Download All Messages (.txt)", 
        txt, 
        file_name=f"{safe_name}_WhatsApp_Followup.txt"
    )
