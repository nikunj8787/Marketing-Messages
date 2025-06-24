import streamlit as st
import pandas as pd
import io
import zipfile
import re

# Constants
EMI_LINK = "https://lnk.ink/FUwEc"
VALUATION_LINK = "https://lnk.ink/fkYwF"

# Column mapping as per your CSV
COLUMN_MAP = {
    "A": "Tag",
    "B": "Property-Address",
    "C": "Location",
    "D": "Property-Price",
    "E": "BHK",
    "F": "Super-Built-up-Construction-Area",
    "G": "Property-On-Floor",
    "H": "Property-Facing",
    "I": "Furniture-Details",
    "J": "Parking-Details",
    "K": "360DGT-Link",
    "L": "Property-Link"
}

def safe_filename(s):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', s)

def clean_location(loc):
    if pd.isna(loc) or loc == "NA":
        return "NA"
    loc = str(loc).strip()
    if '-' in loc:
        return loc.split('-', 1)[1].strip()
    return loc

def get_value(row, code):
    col = COLUMN_MAP.get(code)
    if col and col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
        return str(row[col]).strip()
    return "NA"

def get_360_or_video(row):
    k = get_value(row, 'K')
    l = get_value(row, 'L')
    if k == "NA":
        return l
    return k

def visit_done_to_closing_msgs(row):
    return [
        f"""🏡 ચાલો ફરીથી યાદ કરીએ કે કેમ તમને આ ઘર પસંદ આવ્યું હતું!
📏 {get_value(row,'E')} | {get_value(row,'F')} | {get_value(row,'I')}
📍 {get_value(row,'H')} | {get_value(row,'G')} માળ
👉 શું આપણે તમારા માટે વેચનાર સાથે મીટિંગ ફિક્સ કરીએ?
રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.""",

        f"""📍 {get_value(row,'A')} ફક્ત લોકેશન નથી, એ લાઇફસ્ટાઇલ છે.
સ્કૂલ, કોલેજ, હોસ્પિટલ, શોપિંગ મોલ બધું નજીકમાં છે.
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.""",

        f"""🎥 આ શોર્ટ વિડિયો માં ફરીથી ઘર જુઓ!
ઘરના લેઆઉટ અને લાઇટિંગ સમજવું હવે સરળ છે.
👉 {get_value(row,'L')}
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.""",

        f"""🧭 {get_value(row,'A')} ની ડિજિટલ મુલાકાત લો, એ પણ મોબાઇલ પરથી!
દરેક ખૂણાનું 360° ટૂર જુઓ.
👉 {get_value(row,'K')}
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો.""",

        f"""💰 {get_value(row,'A')} ₹{get_value(row,'D')} માં એક ઉત્તમ ઓપ્શન છે!
આ જ સોસાયટીમાં આવી કિંમતની ઘણી ડીલ્સ થઇ ચૂકી છે.
👉 શું અમે વેચનાર સાથે ભાવ વાત માટે મીટિંગ ફિક્સ કરીએ? રિપ્લાય કરો YES.""",

        f"""🤝 Cleardeals સાથે તમારું ઘર ખરીદવું હવે વધુ સરળ છે!
✅ 0% બ્રોકરેજ
✅ નેગોશિએશન સપોર્ટ
✅ લોન અને લીગલ સહાય — બધું એકજ જગ્યા એ Click here: {EMI_LINK}
👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES.""",

        f"""📊 શું તમે {get_value(row,'A')} ની પ્રોપર્ટીનું વેલ્યૂએશન જાણવા માંગો છો?
👉 શરુ કરો તમારા પ્રોપર્ટીનું મૂલ્યાંકન આજે જ. Click here: {VALUATION_LINK}
👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES.""",

        f"""🕒 શું તમે હજુ ઈન્ટરેસ્ટેડ છો કે નહીં?
જો હજી વિચારમાં છો તો અમે લોકઅપ બંધ કરીશું — હવે નિર્ણયનો સમય છે!
👉 શું પ્રોપર્ટી માટે આગળ વધવું છે? રિપ્લાય કરો YES."""
    ]

def visit_scheduled_to_done_msgs(row):
    location = clean_location(get_value(row,'C'))
    return [
        f"""🌟 {get_value(row,'B')} | {location}
👉🏻 {get_value(row,'E')}
✨ {get_value(row,'I')}
👀 360 tour થી ઘર detail જોઈ શકો
📍 {get_360_or_video(row)}
📞 Visit માટે timing જણાવો જેથી arrange થઈ શકે.""",

        f"""🌟 તમારું dream home હવે reality બનવા તૈયાર છે.
🏠 {get_value(row,'E')}
🏢 {get_value(row,'G')} માળ
🧭 {get_value(row,'H')}
🅿️ {get_value(row,'J')}
📞 Visit suitable time share કરો જેથી personally જોઈ શકાય.""",

        f"""🌟 એક એવું ઘર જ્યાં family સાથે નવી memory બને.
✨ આ ઘર તમારું lifestyle easy બનાવી શકે.
📞 Visit plan today share કરો જેથી personally feel મળી શકે.""",

        f"""{get_value(row,'B')} | {location}
👉🏻 {get_value(row,'E')}
🌟 આ property માટે Buyers interest સતત વધી રહ્યો છે.
👉 આજે visit કરો અને deal Miss ન કરો.
📞 Visit confirm કરો.""",

        f"""🏠 Cleardeals = trust + full support
📌 0% brokerage
📌 Loan + legal help
📌 Visit assist
📌 Negotiation support
📞 Visit confirm કરવા કે બીજું property જાણવા reply કરો."""
    ]

def create_txt(messages, property_address, header):
    content = f"ClearDeals Marketing Messages\n"
    content += f"Property: {property_address}\n"
    content += f"Generated: {pd.Timestamp.now()}\n"
    content += "="*50 + "\n\n"
    for idx, msg in enumerate(messages):
        content += f"{header} Day {idx+1}\n"
        content += "-" * 30 + "\n"
        content += msg + "\n\n"
    return content

# --- Streamlit App ---
st.title("ClearDeals Marketing Messages Generator")

uploaded_file = st.file_uploader(
    "Upload Property Data File (.csv, .xlsx, .json)",
    type=["csv", "xlsx", "json"],
    help="Upload your master property file"
)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)
    df.columns = [col.strip() for col in df.columns]
    # Ensure all mapped columns exist
    for code, col in COLUMN_MAP.items():
        if col not in df.columns:
            df[col] = "NA"
    st.dataframe(df, use_container_width=True)
    # Single property selection
    property_options = [f"{row[COLUMN_MAP['B']]} | {clean_location(row[COLUMN_MAP['C']])}" for _, row in df.iterrows()]
    selected_idx = st.selectbox(
        "Select Property for Preview/Download:",
        range(len(property_options)),
        format_func=lambda x: property_options[x]
    )
    row = df.iloc[selected_idx]
    property_address = get_value(row, "B")
    tag = safe_filename(property_address)
    # Generate messages
    closing_msgs = visit_done_to_closing_msgs(row)
    scheduled_msgs = visit_scheduled_to_done_msgs(row)
    # Preview and download for single property
    st.markdown("### Visit Done to Closing Messages")
    for idx, msg in enumerate(closing_msgs):
        st.markdown(f"**Day {idx+1}:**\n{msg}")
    st.markdown("### Visit Scheduled to Visit Done Messages")
    for idx, msg in enumerate(scheduled_msgs):
        st.markdown(f"**Day {idx+1}:**\n{msg}")
    st.download_button(
        label="⬇️ Download Visit Done to Closing (.txt)",
        data=create_txt(closing_msgs, property_address, "Visit Done to Closing").encode('utf-8'),
        file_name=f"{tag}_VisitDoneToClosing.txt",
        mime="text/plain"
    )
    st.download_button(
        label="⬇️ Download Visit Scheduled to Visit Done (.txt)",
        data=create_txt(scheduled_msgs, property_address, "Visit Scheduled to Visit Done").encode('utf-8'),
        file_name=f"{tag}_VisitScheduledToVisitDone.txt",
        mime="text/plain"
    )
    # Batch download for all properties
    if st.button("🔄 Generate for All Properties (ZIP)", type="secondary"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, row in df.iterrows():
                property_address = get_value(row, "B")
                tag = safe_filename(property_address)
                closing_msgs = visit_done_to_closing_msgs(row)
                scheduled_msgs = visit_scheduled_to_done_msgs(row)
                closing_txt = create_txt(closing_msgs, property_address, "Visit Done to Closing")
                scheduled_txt = create_txt(scheduled_msgs, property_address, "Visit Scheduled to Visit Done")
                zip_file.writestr(f"Visit Done to Closing/{tag}_VisitDoneToClosing.txt", closing_txt)
                zip_file.writestr(f"Visit Scheduled to Visit Done/{tag}_VisitScheduledToVisitDone.txt", scheduled_txt)
        zip_buffer.seek(0)
        st.success("✅ Both sets of messages generated for all properties!")
        st.download_button(
            label="⬇️ Download All Messages (ZIP)",
            data=zip_buffer,
            file_name=f"All_Properties_Messages_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            use_container_width=True
        )
        st.info("Each property has two .txt files in separate folders inside the ZIP.")
