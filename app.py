import streamlit as st
import pandas as pd
import requests
import json
import time

# Load secrets
try:
    HF_TOKEN = st.secrets["huggingface"]["api_token"]
    EMI_LINK = st.secrets["links"]["emi_calculator"]
    VALUATION_LINK = st.secrets["links"]["valuation_calculator"]
except:
    st.error("Please set your API tokens and links in secrets.toml.")
    st.stop()

st.set_page_config(page_title="Gujarati Property Marketing", layout="wide")

# Gujarati static messages templates (columns A-L mapped)
STATIC_MESSAGES = [
    "દિવસ 1\n🏡 ચાલો ફરીથી યાદ કરીએ કે કેમ તમને આ ઘર પસંદ આવ્યું હતું!\n📏 {{E}} | {{F}} ક્વાયાર્ડ | {{I}}\n📍 {{H}} | {{G}} માળ\n👉 શું આપણે તમારા માટે વેચનાર સાથે મીટિંગ ફિક્સ કરીએ?\nરિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.",
    "દિવસ 2\n📍 {{A}} ફક્ત લોકેશન નથી, એ લાઇફસ્ટાઇલ છે.\nસ્કૂલ, કોલેજ, હોસ્પિટલ, શોપિંગ મોલ બધું નજીકમાં છે.\n👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.",
    "દિવસ 3\n🎥 આ શોર્ટ વિડિયો માં ફરીથી ઘર જુઓ!\nઘરના લેઆઉટ અને લાઇટિંગ સમજવું હવે સરળ છે.\n👉 {{L}}\n👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.",
    "દિવસ 4\n🧭 {{A}} ની ડિજિટલ મુલાકાત લો, એ પણ મોબાઇલ પરથી!\nદરેક ખૂણાનું 360° ટૂર જુઓ.\n👉 {{K}}\n👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.",
    "દિવસ 5\n💰 {{A}} ₹{{D}} માં એક ઉત્તમ ઓપ્શન છે!\nઆ જ સોસાયટીમાં આવી કિંમતની ઘણી ડીલ્સ થઇ ચૂકી છે.\n👉 શું અમે વેચનાર સાથે ભાવ વાત માટે મીટિંગ ફિક્સ કરીએ? રિપ્લાય કરો YES.",
    "દિવસ 6\n🤝 Cleardeals સાથે તમારું ઘર ખરીદવું હવે વધુ સરળ છે!\n✅ 0% બ્રોકરેજ\n✅ નેગોશિએશન સપોર્ટ\n✅ લોન અને લીગલ સહાય — બધું એકજ જગ્યા એ\nCheck Loan EMI for {{A}}: https://lnk.ink/FUwEc\n👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES.",
    "દિવસ 7\nશું તમે {{A}} ની પ્રોપર્ટીનું વેલ્યૂએશન જાણવા માંગો છો?\nચેક કરો: https://lnk.ink/fkYwF\n👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES.",
    "દિવસ 8\n🕒 શું તમે હજુ ઈન્ટરેસ્ટેડ છો કે નહીં?\nજો હજી વિચારમાં છો તો અમે લોકઅપ બંધ કરીશું — હવે નિર્ણયનો સમય છે!\n👉 શું પ્રોપર્ટી માટે આગળ વધવું છે? રિપ્લાય કરો YES."
]

# Function to replace placeholders with actual data
def fill_template(template, data):
    for key, val in data.items():
        template = template.replace(f"{{{{{key}}}}}", val)
    return template

# Function to generate Gujarati messages via LLM
def generate_gujarati_message(property_data, message_type, nearby_info):
    prompt = f"""
    Create a professional Gujarati marketing message for a home buyer based on these details:
    Project: {property_data['A']}
    City: {property_data['B']}
    Locality: {property_data['C']}
    Price: {property_data['D']}
    BHK: {property_data['E']}
    Area: {property_data['F']}
    Floor: {property_data['G']}
    Facing: {property_data['H']}
    Furnishing: {property_data['I']}
    Age: {property_data['J']}
    360 Tour Link: {property_data['K']}
    Video Link: {property_data['L']}
    Nearby Schools: {nearby_info['schools']}
    Nearby Hospitals: {nearby_info['hospitals']}
    Nearby Malls: {nearby_info['malls']}
    Use a friendly, persuasive tone, 4-5 lines, emojis, and end with:
    "Reply with a 'Hi' to take this deal forward."
    "www.cleardeals.co.in, No Brokerage Realtor."
    Focus on {message_type}.
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 250, "temperature": 0.7}
    }
    try:
        response = requests.post(f"https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium", headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
    except:
        pass
    return "Error generating message."

# Main app
st.title("🏡 Gujarati Home Buyer Marketing Messages")
uploaded_file = st.file_uploader("Upload Data (CSV/XLS)", type=["csv","xls","xlsx"])

generate_mode = st.radio("Choose Mode", ["Static Templates", "LLM-Powered"], index=0)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = [col.strip() for col in df.columns]
    # Map columns A-L
    col_map = {
        "A": "Project Name/Location",
        "B": "City",
        "C": "Locality",
        "D": "Price",
        "E": "BHK",
        "F": "Area",
        "G": "Floor",
        "H": "Facing",
        "I": "Furnishing",
        "J": "Age",
        "K": "360 Tour Link",
        "L": "Video Link"
    }
    # Create a dict for each property
    for idx, row in df.iterrows():
        data = {}
        for col_key, col_name in col_map.items():
            data[col_key] = row.get(col_name, "NA") if col_name in df.columns else "NA"
        # Clean data
        for k in data:
            if pd.isna(data[k]):
                data[k] = "NA"
        # Process location
        data["A"] = data["A"]
        data["C"] = data["C"]
        # Fetch nearby info
        with st.spinner(f"Fetching nearby places for {data['A']}..."):
            nearby = {
                "schools": [],
                "hospitals": [],
                "malls": []
            }
            # Geocode address
            full_addr = f"{data['A']}, {data['C']}, {data['B']}"
            lat, lon = None, None
            try:
                resp = requests.get(f"https://api.geoapify.com/v1/geocode/search?text={full_addr}&apiKey={GEOAPIFY_API_KEY}")
                if resp.status_code == 200 and resp.json()["features"]:
                    coords = resp.json()["features"][0]["geometry"]["coordinates"]
                    lat, lon = coords[1], coords[0]
            except:
                pass
            if lat and lon:
                for category in ["education.school", "education.college", "commercial.shopping_mall", "healthcare.hospital"]:
                    url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{lon},{lat},5000&limit=2&apiKey={GEOAPIFY_API_KEY}"
                    try:
                        r = requests.get(url)
                        if r.status_code == 200:
                            feats = r.json().get("features", [])
                            names = [f["properties"]["name"] for f in feats if "name" in f["properties"]]
                            if category == "education.school":
                                nearby["schools"] = names
                            elif category == "education.college":
                                nearby["colleges"] = names
                            elif category == "commercial.shopping_mall":
                                nearby["malls"] = names
                            elif category == "healthcare.hospital":
                                nearby["hospitals"] = names
                    except:
                        pass
            # Generate messages
            messages = []
            if generate_mode == "Static Templates":
                for i, template in enumerate(STATIC_MESSAGES):
                    msg = fill_template(template, data)
                    messages.append(msg)
            else:
                # LLM mode
                messages = []
                for i, mtype in enumerate([
                    "Property Benefits", "Location Advantage", "FOMO/Urgency", "Trust Building",
                    "Lifestyle Appeal", "Value Proposition", "Financial Assistance",
                    "Market Analysis"
                ]):
                    prompt = f"""
                    Create a Gujarati marketing message for a property:
                    Project: {data['A']}
                    Locality: {data['C']}
                    City: {data['B']}
                    Price: {data['D']}
                    BHK: {data['E']}
                    Area: {data['F']}
                    Facing: {data['H']}
                    Furnishing: {data['I']}
                    Age: {data['J']}
                    360 Tour: {data['K']}
                    Video: {data['L']}
                    Nearby Schools: {', '.join(nearby['schools'])}
                    Nearby Hospitals: {', '.join(nearby['hospitals'])}
                    Nearby Malls: {', '.join(nearby['malls'])}
                    Focus on: {mtype}
                    Use a friendly, persuasive tone, 4 lines, emojis, and end with:
                    "Reply with a 'Hi' to take this deal forward."
                    "www.cleardeals.co.in, No Brokerage Realtor."
                    """
                    msg = generate_gujarati_message(data, mtype, nearby)
                    # fallback if error
                    if not msg or "Error" in msg:
                        msg = fill_template(STATIC_MESSAGES[i], data)
                    messages.append(msg)
            # Show messages
            for idx, msg in enumerate(messages):
                st.markdown(f"### {['દિવસ 1','દિવસ 2','દિવસ 3','દિવસ 4','દિવસ 5','દિવસ 6','દિવસ 7','દિવસ 8'][idx]}")
                st.text_area(f"Message {idx+1}", msg, height=150)
            # Download all
            all_text = "\n\n".join(messages)
            st.download_button("Download All Messages (.txt)", all_text, filename=f"{data['A']}_Gujarati_Messages.txt")
