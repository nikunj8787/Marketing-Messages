import streamlit as st
import pandas as pd
import io

st.title("Property Marketing Message Generator")

uploaded_file = st.file_uploader("Upload your .xls file", type=["xls", "xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    tag = st.selectbox("Select Property Tag", df['Tag'].astype(str))
    prop = df[df['Tag'].astype(str) == tag].iloc[0]
    
    # Generate messages
    messages = [
        f"🏠 {prop['Property Name']} located in {prop['Location']} offers a comfortable {prop['Configuration']} with {prop['Area']} area.",
        f"📍 Prime location at {prop['Location']} with excellent connectivity and amenities.",
        f"⚡ Limited availability! Grab your chance to own {prop['Property Name']} at just {prop['Price']}.",
        f"🔒 Trusted by many, {prop['Property Name']} comes with top-notch amenities like {prop['Amenities']}.",
        f"🌟 Experience a premium lifestyle with {prop['Configuration']} at {prop['Property Name']}.",
        f"💰 Great value for money at {prop['Price']} for a property in {prop['Location']}.",
        f"🏦 Check your loan eligibility easily and make {prop['Property Name']} yours.",
        f"📊 Get a free property valuation report for {prop['Property Name']} to understand its market value.",
        f"👥 Join a thriving community at {prop['Property Name']} with excellent social amenities.",
        f"⏳ Don't miss out! Schedule a visit to {prop['Property Name']} today and take the first step towards your dream home."
    ]
    st.write("### Marketing Messages")
    for m in messages:
        st.write(m)
    
    # Download as .txt
    txt = "\n".join(messages)
    st.download_button("Download All Messages (.txt)", txt, file_name=f"{prop['Property Name'].replace(' ','_')}_WhatsApp_Followup.txt")
