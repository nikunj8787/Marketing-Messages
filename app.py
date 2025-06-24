import streamlit as st
import pandas as pd
import requests
import time
import io
import zipfile
import re

# --- Config ---
DEEPSEEK_API_KEY = "sk-54bd3323c4d14bf08b941f0bff7a47d5"
EMI_LINK = "https://lnk.ink/FUwEc"
VALUATION_LINK = "https://lnk.ink/fkYwF"

def safe_filename(s):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', s)

def clean_location(location):
    if pd.isna(location) or location == "NA":
        return "NA"
    loc = str(location).strip()
    if '-' in loc:
        return loc.split('-', 1)[1].strip()
    if '–' in loc:
        return loc.split('–', 1)[1].strip()
    if ' ' in loc and len(loc.split(' ', 1)[0]) == 1:
        return loc.split(' ', 1)[1].strip()
    return loc

def get_360_or_video(row):
    k = row.get('K', '')
    l = row.get('L', '')
    if pd.isna(k) or k.strip() == "" or k.strip().upper() == "NA":
        return l if not pd.isna(l) and l.strip() != "" and l.strip().upper() != "NA" else "NA"
    return k

# --- LLM (DeepSeek) ---
class DeepSeekLLM:
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    def generate(self, prompt: str, language: str = "English") -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are a helpful assistant that writes {language} WhatsApp marketing messages for real estate buyers."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.8,
            "top_p": 0.95
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            st.warning(f"DeepSeek API call failed: {str(e)}")
        return "[DeepSeek LLM generation failed.]"

# --- Static Templates ---
def scheduled_to_done_templates(row):
    location = clean_location(row.get('C', 'NA'))
    tour_link = get_360_or_video(row)
    return [
        f"""🌟 {row['B']} | {location}
👉🏻 {row['E']}
✨ {row['I']}
👀 360 tour થી ઘર detail જોઈ શકો
📍 {tour_link}
📞 Visit માટે timing જણાવો જેથી arrange થઈ શકે.""",
        f"""🌟 તમારું dream home હવે reality બનવા તૈયાર છે.
🏠 {row['E']}
🏢 {row['G']}
🧭 {row['H']}
🅿️ {row['J']}
📞 Visit suitable time share કરો જેથી personally જોઈ શકાય.""",
        f"""🌟 એક એવું ઘર જ્યાં family સાથે નવી memory બને.
✨ આ ઘર તમારું lifestyle easy બનાવી શકે.
📞 Visit plan today share કરો જેથી personally feel મળી શકે.""",
        f"""{row['B']} | {location}
👉🏻 {row['E']}
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

def done_to_closing_templates(row):
    return [
        f"🏡 {row['B']} માં તમારું ઘર પસંદ કરવા બદલ આભાર! Visit પછી closing માટે આગળ વધો.",
        f"📍 Location: {clean_location(row['C'])}, BHK: {row['E']}, Floor: {row['G']}",
        f"💰 Price: {row['D']}, Facing: {row['H']}, Furnishing: {row['I']}",
        f"🔗 360 Tour: {get_360_or_video(row)} | Video: {row['L']}",
        f"🤝 Cleardeals: 0% brokerage, loan/legal help, visit assist, negotiation support.",
        f"📞 Reply YES to proceed with closing steps.",
        f"📈 For valuation, check: {VALUATION_LINK}",
        f"💸 Check EMI: {EMI_LINK}"
    ]

# --- LLM Prompts ---
def scheduled_to_done_llm_prompts(row, language="Gujarati"):
    location = clean_location(row.get('C', 'NA'))
    tour_link = get_360_or_video(row)
    prompts = []
    if language == "Gujarati":
        prompts.append(
            f"Create a Gujarati WhatsApp message for a buyer who has scheduled a visit. "
            f"Property: {row['B']} | {location}, BHK: {row['E']}, Furniture: {row['I']}, 360 tour: {tour_link}. "
            f"Invite them to share a suitable time for the visit."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message listing property highlights: BHK: {row['E']}, Floor: {row['G']}, Facing: {row['H']}, Parking: {row['J']}. "
            f"Encourage sharing a time for a personal visit."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message that builds emotional connection and invites the buyer to plan a visit and experience the home."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message that gently builds urgency (FOMO) for {row['B']} | {location}, BHK: {row['E']}. "
            f"Encourage them to confirm the visit soon."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message highlighting Cleardeals' services (0% brokerage, loan/legal help, visit assist, negotiation support). "
            f"Invite to confirm visit or inquire about other properties."
        )
    else:  # English
        prompts.append(
            f"Write an English WhatsApp message for a buyer who has scheduled a visit. "
            f"Property: {row['B']} | {location}, BHK: {row['E']}, Furniture: {row['I']}, 360 tour: {tour_link}. "
            f"Invite them to share a suitable time for the visit."
        )
        prompts.append(
            f"Write an English WhatsApp message listing property highlights: BHK: {row['E']}, Floor: {row['G']}, Facing: {row['H']}, Parking: {row['J']}. "
            f"Encourage sharing a time for a personal visit."
        )
        prompts.append(
            f"Write an English WhatsApp message that builds emotional connection and invites the buyer to plan a visit and experience the home."
        )
        prompts.append(
            f"Write an English WhatsApp message that gently builds urgency (FOMO) for {row['B']} | {location}, BHK: {row['E']}. "
            f"Encourage them to confirm the visit soon."
        )
        prompts.append(
            f"Write an English WhatsApp message highlighting Cleardeals' services (0% brokerage, loan/legal help, visit assist, negotiation support). "
            f"Invite to confirm visit or inquire about other properties."
        )
    return prompts

def done_to_closing_llm_prompts(row, language="Gujarati"):
    location = clean_location(row.get('C', 'NA'))
    tour_link = get_360_or_video(row)
    prompts = []
    if language == "Gujarati":
        prompts.append(
            f"Create a Gujarati WhatsApp message thanking the buyer for visiting {row['B']} and encouraging them to move towards closing."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message summarizing property details: Location: {location}, BHK: {row['E']}, Floor: {row['G']}."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message mentioning Price: {row['D']}, Facing: {row['H']}, Furnishing: {row['I']}."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message sharing 360 Tour: {tour_link} and Video: {row['L']}."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message highlighting Cleardeals' support: 0% brokerage, loan/legal help, visit assist, negotiation support."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message with a call to action to reply YES to proceed with closing."
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message mentioning property valuation: {VALUATION_LINK}"
        )
        prompts.append(
            f"Create a Gujarati WhatsApp message mentioning EMI calculator: {EMI_LINK}"
        )
    else:  # English
        prompts.append(
            f"Write an English WhatsApp message thanking the buyer for visiting {row['B']} and encouraging them to move towards closing."
        )
        prompts.append(
            f"Write an English WhatsApp message summarizing property details: Location: {location}, BHK: {row['E']}, Floor: {row['G']}."
        )
        prompts.append(
            f"Write an English WhatsApp message mentioning Price: {row['D']}, Facing: {row['H']}, Furnishing: {row['I']}."
        )
        prompts.append(
            f"Write an English WhatsApp message sharing 360 Tour: {tour_link} and Video: {row['L']}."
        )
        prompts.append(
            f"Write an English WhatsApp message highlighting Cleardeals' support: 0% brokerage, loan/legal help, visit assist, negotiation support."
        )
        prompts.append(
            f"Write an English WhatsApp message with a call to action to reply YES to proceed with closing."
        )
        prompts.append(
            f"Write an English WhatsApp message mentioning property valuation: {VALUATION_LINK}"
        )
        prompts.append(
            f"Write an English WhatsApp message mentioning EMI calculator: {EMI_LINK}"
        )
    return prompts

def generate_llm_messages(row, llm, prompts, language="Gujarati"):
    messages = []
    for prompt in prompts:
        msg = llm.generate(prompt, language=language)
        messages.append(msg if msg.strip() else prompt)
        time.sleep(0.5)
    return messages

def create_download_content(messages: list, property_data: dict, header: str) -> str:
    content = f"ClearDeals Marketing Messages\n"
    content += f"Property: {property_data.get('B', 'NA')}\n"
    content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "="*50 + "\n\n"
    for idx, msg in enumerate(messages):
        content += f"{header} Day {idx+1}\n"
        content += "-" * 30 + "\n"
        content += msg + "\n\n"
    return content

# --- Main App ---
st.title("ClearDeals Marketing Generator")

mode = st.radio(
    "Choose Message Generation Mode:",
    [
        "📝 Static (Gujarati Templates)",
        "🤖 LLM Gujarati (DeepSeek)",
        "🌐 LLM English (DeepSeek)"
    ]
)

message_type = st.radio(
    "Which messages do you want to generate/download?",
    [
        "Visit Done to Closing (8 messages)",
        "Visit Scheduled to Visit Done (5 messages)",
        "Both (separate folders)"
    ]
)

uploaded_file = st.file_uploader(
    "Upload Property Data File (.csv, .xlsx, .json)",
    type=["csv", "xlsx", "json"],
    help="Upload your master property file"
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        expected = ['B','C','E','G','H','I','J','K','L','D']
        for col in expected:
            if col not in df.columns:
                df[col] = "NA"
        if 'Tag' not in df.columns:
            df['Tag'] = df['B']
        st.dataframe(df, use_container_width=True)
        llm = DeepSeekLLM(DEEPSEEK_API_KEY)
        # --- Single Property Selection ---
        property_options = [f"{row['Tag']} | {row['B']} | {clean_location(row['C'])}" for _, row in df.iterrows()]
        selected_property_idx = st.selectbox(
            "Select Property for Preview/Download:",
            range(len(property_options)),
            format_func=lambda x: property_options[x]
        )
        row = df.iloc[selected_property_idx].fillna("NA")
        tag = safe_filename(str(row['Tag']))
        # Generate messages for selected property
        if mode == "📝 Static (Gujarati Templates)":
            closing_msgs = done_to_closing_templates(row)
            scheduled_msgs = scheduled_to_done_templates(row)
        elif mode == "🤖 LLM Gujarati (DeepSeek)":
            closing_msgs = generate_llm_messages(row, llm, done_to_closing_llm_prompts(row, language="Gujarati"), language="Gujarati")
            scheduled_msgs = generate_llm_messages(row, llm, scheduled_to_done_llm_prompts(row, language="Gujarati"), language="Gujarati")
        else:
            closing_msgs = generate_llm_messages(row, llm, done_to_closing_llm_prompts(row, language="English"), language="English")
            scheduled_msgs = generate_llm_messages(row, llm, scheduled_to_done_llm_prompts(row, language="English"), language="English")
        # Preview & Download
        if message_type == "Visit Done to Closing (8 messages)":
            st.markdown("### Visit Done to Closing Messages")
            for idx, msg in enumerate(closing_msgs):
                st.markdown(f"**Day {idx+1}:**\n{msg}")
            closing_txt = create_download_content(closing_msgs, row, "Visit Done to Closing")
            st.download_button(
                label="⬇️ Download Visit Done to Closing (.txt)",
                data=closing_txt.encode('utf-8'),
                file_name=f"{tag}_VisitDoneToClosing.txt",
                mime="text/plain"
            )
        elif message_type == "Visit Scheduled to Visit Done (5 messages)":
            st.markdown("### Visit Scheduled to Visit Done Messages")
            for idx, msg in enumerate(scheduled_msgs):
                st.markdown(f"**Day {idx+1}:**\n{msg}")
            scheduled_txt = create_download_content(scheduled_msgs, row, "Visit Scheduled to Visit Done")
            st.download_button(
                label="⬇️ Download Visit Scheduled to Visit Done (.txt)",
                data=scheduled_txt.encode('utf-8'),
                file_name=f"{tag}_VisitScheduledToVisitDone.txt",
                mime="text/plain"
            )
        else:
            st.markdown("### Visit Done to Closing Messages")
            for idx, msg in enumerate(closing_msgs):
                st.markdown(f"**Day {idx+1}:**\n{msg}")
            st.markdown("### Visit Scheduled to Visit Done Messages")
            for idx, msg in enumerate(scheduled_msgs):
                st.markdown(f"**Day {idx+1}:**\n{msg}")
            closing_txt = create_download_content(closing_msgs, row, "Visit Done to Closing")
            scheduled_txt = create_download_content(scheduled_msgs, row, "Visit Scheduled to Visit Done")
            # ZIP for single property
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr(f"Visit Done to Closing/{tag}_VisitDoneToClosing.txt", closing_txt)
                zip_file.writestr(f"Visit Scheduled to Visit Done/{tag}_VisitScheduledToVisitDone.txt", scheduled_txt)
            zip_buffer.seek(0)
            st.download_button(
                label="⬇️ Download Both Message Sets (ZIP)",
                data=zip_buffer,
                file_name=f"{tag}_AllMessages.zip",
                mime="application/zip"
            )
        # --- Batch Download for All Properties ---
        if st.button("🔄 Generate for All Properties (ZIP)", type="secondary"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for idx, row in df.iterrows():
                    row = row.fillna("NA")
                    tag = safe_filename(str(row['Tag']))
                    if mode == "📝 Static (Gujarati Templates)":
                        closing_msgs = done_to_closing_templates(row)
                        scheduled_msgs = scheduled_to_done_templates(row)
                    elif mode == "🤖 LLM Gujarati (DeepSeek)":
                        closing_msgs = generate_llm_messages(row, llm, done_to_closing_llm_prompts(row, language="Gujarati"), language="Gujarati")
                        scheduled_msgs = generate_llm_messages(row, llm, scheduled_to_done_llm_prompts(row, language="Gujarati"), language="Gujarati")
                    else:
                        closing_msgs = generate_llm_messages(row, llm, done_to_closing_llm_prompts(row, language="English"), language="English")
                        scheduled_msgs = generate_llm_messages(row, llm, scheduled_to_done_llm_prompts(row, language="English"), language="English")
                    if message_type == "Visit Done to Closing (8 messages)":
                        closing_txt = create_download_content(closing_msgs, row, "Visit Done to Closing")
                        closing_path = f"Visit Done to Closing/{tag}_VisitDoneToClosing.txt"
                        zip_file.writestr(closing_path, closing_txt)
                    elif message_type == "Visit Scheduled to Visit Done (5 messages)":
                        scheduled_txt = create_download_content(scheduled_msgs, row, "Visit Scheduled to Visit Done")
                        scheduled_path = f"Visit Scheduled to Visit Done/{tag}_VisitScheduledToVisitDone.txt"
                        zip_file.writestr(scheduled_path, scheduled_txt)
                    else:
                        closing_txt = create_download_content(closing_msgs, row, "Visit Done to Closing")
                        closing_path = f"Visit Done to Closing/{tag}_VisitDoneToClosing.txt"
                        zip_file.writestr(closing_path, closing_txt)
                        scheduled_txt = create_download_content(scheduled_msgs, row, "Visit Scheduled to Visit Done")
                        scheduled_path = f"Visit Scheduled to Visit Done/{tag}_VisitScheduledToVisitDone.txt"
                        zip_file.writestr(scheduled_path, scheduled_txt)
            zip_buffer.seek(0)
            st.success("✅ Messages generated for all properties!")
            st.download_button(
                label="⬇️ Download All Messages (ZIP)",
                data=zip_buffer,
                file_name=f"All_Properties_Messages_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
            st.info("Each property has .txt files in separate folders inside the ZIP.")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
