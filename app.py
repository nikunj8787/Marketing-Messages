import streamlit as st
import pandas as pd
import requests
import time
import io
import zipfile
from typing import Dict, List, Optional, Tuple

st.set_page_config(
    page_title="ClearDeals Marketing Generator",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;500;600;700&display=swap');
    .gujarati-text { font-family: 'Noto Sans Gujarati', sans-serif; font-size: 16px; line-height: 1.6; }
    .message-card { background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #00b894; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .day-badge { background: linear-gradient(135deg, #00b894, #00a085); color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 10px;}
    .toggle-container { background: #ffffff; padding: 20px; border-radius: 10px; border: 2px solid #e0e6ed; margin: 20px 0;}
    .upload-area { border: 2px dashed #00b894; border-radius: 10px; padding: 40px; text-align: center; background: #f7fffe; margin: 20px 0;}
</style>
""", unsafe_allow_html=True)

# --- API Configuration ---
DEEPSEEK_API_KEY = "sk-54bd3323c4d14bf08b941f0bff7a47d5"
EMI_LINK = "https://lnk.ink/FUwEc"
VALUATION_LINK = "https://lnk.ink/fkYwF"

GUJARATI_TEMPLATES = [
    {
        "day": 1,
        "title": "Property Reminder",
        "template": """🏡 ચાલો ફરીથી યાદ કરીએ કે કેમ તમને આ ઘર પસંદ આવ્યું હતું!
📏 {{E}} | {{F}} ક્વાયાર્ડ | {{I}}
📍 {{H}} | {{G}} માળ
👉 શું આપણે તમારા માટે વેચનાર સાથે મીટિંગ ફિક્સ કરીએ?
રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો."""
    },
    {
        "day": 2,
        "title": "Lifestyle Benefits",
        "template": """📍 {{A}} ફક્ત લોકેશન નથી, એ લાઇફસ્ટાઇલ છે.
સ્કૂલ, કોલેજ, હોસ્પિટલ, શોપિંગ મોલ બધું નજીકમાં છે.
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો."""
    },
    {
        "day": 3,
        "title": "Video Tour",
        "template": """🎥 આ શોર્ટ વિડિયો માં ફરીથી ઘર જુઓ!
ઘરના લેઆઉટ અને લાઇટિંગ સમજવું હવે સરળ છે.
👉 {{L}}
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો."""
    },
    {
        "day": 4,
        "title": "360° Tour",
        "template": """🧭 {{A}} ની ડિજિટલ મુલાકાત લો, એ પણ મોબાઇલ પરથી!
દરેક ખૂણાનું 360° ટૂર જુઓ.
👉 {{K}}
👉 રિપ્લાય કરો YES જો રસ હોય તો, No જો ન હોય તો."""
    },
    {
        "day": 5,
        "title": "Pricing Discussion",
        "template": """💰 {{A}} ₹{{D}} માં એક ઉત્તમ ઓપ્શન છે!
આ જ સોસાયટીમાં આવી કિંમતની ઘણી ડીલ્સ થઇ ચૂકી છે.
👉 શું અમે વેચનાર સાથે ભાવ વાત માટે મીટિંગ ફિક્સ કરીએ? રિપ્લાય કરો YES."""
    },
    {
        "day": 6,
        "title": "ClearDeals Services",
        "template": f"""🤝 Cleardeals સાથે તમારું ઘર ખરીદવું હવે વધુ સરળ છે!
✅ 0% બ્રોકરેજ
✅ નેગોશિએશન સપોર્ટ
✅ લોન અને લીગલ સહાય — બધું એકજ જગ્યા એ
Check Loan EMI for {{{{A}}}}: {EMI_LINK}
👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES."""
    },
    {
        "day": 7,
        "title": "Property Valuation",
        "template": f"""શું તમે {{{{A}}}} ની પ્રોપર્ટીનું વેલ્યૂએશન જાણવા માંગો છો?
ચેક કરો: {VALUATION_LINK}
👉 શું હવે વેચનાર સાથે મુલાકાત રાખી ફાઈનલ સ્ટેપ લઈએ? રિપ્લાય કરો YES."""
    },
    {
        "day": 8,
        "title": "Final Decision",
        "template": """🕒 શું તમે હજુ ઈન્ટરેસ્ટેડ છો કે નહીં?
જો હજી વિચારમાં છો તો અમે લોકઅપ બંધ કરીશું — હવે નિર્ણયનો સમય છે!
👉 શું પ્રોપર્ટી માટે આગળ વધવું છે? રિપ્લાય કરો YES."""
    }
]

COLUMN_MAPPING = {
    "A": "Project Name/Location",
    "B": "City",
    "C": "Locality", 
    "D": "Price",
    "E": "BHK",
    "F": "Area (sq.yds)",
    "G": "Floor",
    "H": "Facing",
    "I": "Furnishing",
    "J": "Age",
    "K": "360 Tour Link",
    "L": "Video Link"
}

class PropertyDataProcessor:
    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        original_columns = df.columns.tolist()
        column_map = {}
        expected_columns = list(COLUMN_MAPPING.keys())
        for i, col in enumerate(original_columns[:len(expected_columns)]):
            column_map[col] = expected_columns[i]
        df_normalized = df.rename(columns=column_map)
        for col in expected_columns:
            if col not in df_normalized.columns:
                df_normalized[col] = "NA"
        return df_normalized[expected_columns]
    @staticmethod
    def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            df[col] = df[col].fillna("NA").astype(str)
            df[col] = df[col].replace(['nan', 'None', ''], 'NA')
        return df
    @staticmethod
    def format_property_identifier(row: pd.Series) -> str:
        project_name = row.get('A', 'Unknown')
        city = row.get('B', 'Unknown')
        tag = row.get('Tag', None)
        return f"{tag or project_name} - {city}"

class DeepSeekLLM:
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    def generate_message(self, prompt: str, language: str = "English") -> str:
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
            else:
                st.warning(f"DeepSeek API error: {response.status_code} {response.text}")
        except Exception as e:
            st.warning(f"DeepSeek API call failed: {str(e)}")
        return "[DeepSeek LLM generation failed.]"

class MessageGenerator:
    def __init__(self):
        self.processor = PropertyDataProcessor()
        self.llm = DeepSeekLLM(DEEPSEEK_API_KEY)
    def generate_static_messages(self, property_data: Dict) -> List[Dict]:
        messages = []
        for template_info in GUJARATI_TEMPLATES:
            message_text = template_info["template"]
            for key, value in property_data.items():
                placeholder = f"{{{{{key}}}}}"
                message_text = message_text.replace(placeholder, str(value))
            messages.append({
                "day": template_info["day"],
                "title": template_info["title"],
                "message": message_text,
                "type": "static"
            })
        return messages
    def generate_llm_gujarati_messages(self, property_data: Dict) -> List[Dict]:
        messages = []
        message_types = [
            "Property Features Reminder",
            "Location & Lifestyle Benefits", 
            "Video Tour Promotion",
            "360° Virtual Tour",
            "Pricing & Value Discussion",
            "ClearDeals Services",
            "Property Valuation",
            "Final Decision Urgency"
        ]
        for i, message_type in enumerate(message_types):
            prompt = self._create_gujarati_prompt(property_data, i+1, message_type)
            generated_message = self.llm.generate_message(prompt, language="Gujarati")
            messages.append({
                "day": i+1,
                "title": message_type,
                "message": generated_message,
                "type": "llm_gujarati"
            })
        return messages
    def generate_llm_english_messages(self, property_data: Dict) -> List[Dict]:
        messages = []
        message_types = [
            "Property Features Reminder",
            "Location & Lifestyle Benefits", 
            "Video Tour Promotion",
            "360° Virtual Tour",
            "Pricing & Value Discussion",
            "ClearDeals Services",
            "Property Valuation",
            "Final Decision Urgency"
        ]
        for i, message_type in enumerate(message_types):
            prompt = self._create_english_prompt(property_data, i+1, message_type)
            generated_message = self.llm.generate_message(prompt, language="English")
            messages.append({
                "day": i+1,
                "title": message_type,
                "message": generated_message,
                "type": "llm_english"
            })
        return messages
    def _create_gujarati_prompt(self, property_data, day, message_type):
        return (
            f"Create a Gujarati WhatsApp marketing message for a home buyer who has already visited this property. "
            f"Day {day}: {message_type}. "
            f"Property: {property_data.get('A','NA')}, City: {property_data.get('B','NA')}, Locality: {property_data.get('C','NA')}, "
            f"Price: {property_data.get('D','NA')}, BHK: {property_data.get('E','NA')}, Area: {property_data.get('F','NA')} sq.yds, "
            f"Floor: {property_data.get('G','NA')}, Facing: {property_data.get('H','NA')}, Furnishing: {property_data.get('I','NA')}, "
            f"Age: {property_data.get('J','NA')}, 360 Tour: {property_data.get('K','NA')}, Video: {property_data.get('L','NA')}. "
            f"Message should be 3-4 lines, include one emoji, and end with: 'રિપ્લાય કરો YES જો રસ હોય તો.' Write in Gujarati only."
        )
    def _create_english_prompt(self, property_data, day, message_type):
        return (
            f"Write a professional, friendly, and concise English WhatsApp marketing message for a home buyer who has already visited this property. "
            f"Focus for Day {day}: {message_type}. "
            f"Property details: Project: {property_data.get('A','NA')}, City: {property_data.get('B','NA')}, Locality: {property_data.get('C','NA')}, "
            f"Price: {property_data.get('D','NA')}, BHK: {property_data.get('E','NA')}, Area: {property_data.get('F','NA')} sq.yds, "
            f"Floor: {property_data.get('G','NA')}, Facing: {property_data.get('H','NA')}, Furnishing: {property_data.get('I','NA')}, "
            f"Age: {property_data.get('J','NA')}, 360 Tour: {property_data.get('K','NA')}, Video: {property_data.get('L','NA')}. "
            f"Message should be 3-4 lines, include one emoji, and end with: 'Reply YES if interested.'"
        )

def create_download_content(messages: List[Dict], property_data: Dict) -> str:
    content = f"ClearDeals Marketing Messages\n"
    content += f"Property: {property_data.get('A', 'NA')}\n"
    content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "="*50 + "\n\n"
    for msg in messages:
        content += f"Day {msg['day']}: {msg['title']}\n"
        content += "-" * 30 + "\n"
        content += msg['message'] + "\n\n"
    return content

def main():
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #00b894; margin-bottom: 10px;">🏠 ClearDeals Marketing Generator</h1>
        <p style="color: #666; font-size: 18px;">8-Day Sequential Marketing Messages (Gujarati & English)</p>
    </div>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.header("⚙️ Configuration")
        generation_mode = st.radio(
            "Select Generation Mode:",
            [
                "📝 Static Templates (Gujarati)",
                "🤖 LLM-Powered Dynamic (Gujarati)",
                "🌐 LLM-Powered Dynamic (English)"
            ],
            help="Choose between predefined Gujarati templates, Gujarati AI, or English AI messages"
        )
        st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
        with st.expander("📋 Column Mapping Reference"):
            for key, desc in COLUMN_MAPPING.items():
                st.write(f"**{key}**: {desc}")
        st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📁 Upload Property Data File",
            type=["csv", "xlsx", "json"],
            help="Upload CSV, Excel, or JSON file with property data"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_json(uploaded_file)
                processor = PropertyDataProcessor()
                message_generator = MessageGenerator()
                df_normalized = processor.normalize_columns(df)
                df_clean = processor.validate_and_clean_data(df_normalized)
                with st.expander("👀 Data Preview", expanded=True):
                    st.dataframe(df_clean, use_container_width=True)
                if not df_clean.empty:
                    property_options = [processor.format_property_identifier(row) for _, row in df_clean.iterrows()]
                    selected_property_idx = st.selectbox(
                        "🏠 Select Property:",
                        range(len(property_options)),
                        format_func=lambda x: property_options[x]
                    )
                    selected_property_data = df_clean.iloc[selected_property_idx].to_dict()
                    if st.button("🚀 Generate Marketing Messages", type="primary", use_container_width=True):
                        with st.spinner("Generating messages..."):
                            if generation_mode == "📝 Static Templates (Gujarati)":
                                messages = message_generator.generate_static_messages(selected_property_data)
                                st.success("✅ Static Gujarati messages generated successfully!")
                            elif generation_mode == "🤖 LLM-Powered Dynamic (Gujarati)":
                                messages = message_generator.generate_llm_gujarati_messages(selected_property_data)
                                st.success("✅ LLM-powered Gujarati messages generated successfully!")
                            else:
                                messages = message_generator.generate_llm_english_messages(selected_property_data)
                                st.success("✅ LLM-powered English messages generated successfully!")
                        st.markdown("## 📱 Generated Messages")
                        all_messages_text = ""
                        for msg in messages:
                            st.markdown(f"""
                            <div class="message-card gujarati-text">
                                <div class="day-badge">Day {msg['day']}</div>
                                <h4 style="margin: 10px 0; color: #2d3748;">{msg['title']}</h4>
                                <div style="white-space: pre-line; font-size: 16px; line-height: 1.6;">
                                    {msg['message']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"📋 Copy Day {msg['day']} Message", key=f"copy_{msg['day']}"):
                                st.write("📋 Message copied to display:")
                                st.code(msg['message'], language=None)
                            all_messages_text += f"Day {msg['day']}: {msg['title']}\n{msg['message']}\n\n"
                        download_content = create_download_content(messages, selected_property_data)
                        st.download_button(
                            label="📥 Download All Messages",
                            data=download_content.encode('utf-8'),
                            file_name=f"ClearDeals_Messages_{selected_property_data.get('A', 'Property').replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        st.markdown("---")
                    # BATCH GENERATION SECTION
                    if st.button("🔄 Generate for All Properties", type="secondary"):
                        batch_messages = {}
                        progress_container = st.container()
                        with progress_container:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            for idx, (_, row) in enumerate(df_clean.iterrows()):
                                property_data = row.to_dict()
                                property_id = processor.format_property_identifier(row)
                                if generation_mode == "📝 Static Templates (Gujarati)":
                                    batch_messages[property_id] = message_generator.generate_static_messages(property_data)
                                elif generation_mode == "🤖 LLM-Powered Dynamic (Gujarati)":
                                    batch_messages[property_id] = message_generator.generate_llm_gujarati_messages(property_data)
                                else:
                                    batch_messages[property_id] = message_generator.generate_llm_english_messages(property_data)
                                progress_bar.progress((idx + 1) / len(df_clean))
                                time.sleep(0.1)
                            progress_bar.empty()
                            status_text.empty()
                        # Prepare ZIP file for download
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                            for idx, (property_id, messages) in enumerate(batch_messages.items()):
                                tag = df_clean.iloc[idx].get('Tag', None) or property_id.split(' - ')[0]
                                filename = f"{tag}_Marketing_Messages.txt".replace(" ", "_")
                                file_content = create_download_content(messages, messages[0] if messages else {})
                                zip_file.writestr(filename, file_content)
                        zip_buffer.seek(0)
                        st.download_button(
                            label="⬇️ Download All Messages (ZIP)",
                            data=zip_buffer,
                            file_name=f"All_Properties_Messages_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        # DISPLAY ALL BATCH MESSAGES ON SCREEN
                        st.markdown("## 📋 All Properties: Generated Messages")
                        for property_id, messages in batch_messages.items():
                            st.markdown(f"### 🏠 {property_id}")
                            for idx, msg in enumerate(messages):
                                st.markdown(f"**Day {idx+1}:**")
                                st.markdown(f"<div class='gujarati-text' style='margin-bottom:12px;white-space:pre-line'>{msg['message'] if isinstance(msg, dict) else msg}</div>", unsafe_allow_html=True)
                            st.markdown("---")
                        st.success(f"✅ Batch processing completed for {len(df_clean)} properties!")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    with col2:
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. **Upload** your property data file (CSV/Excel)
        2. **Select** a property or run batch mode
        3. **Generate** 8-day message sequence
        4. **Copy** individual messages or download all
        5. **Use** batch processing for multiple properties (ZIP download)
        """)
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🎯 **8-Day Sequential Messages**
        - 🌐 **Gujarati & English Language**
        - 📝 **Static Templates**
        - 🤖 **AI-Powered Generation (DeepSeek)**
        - 📱 **WhatsApp Optimized**
        - 💾 **Batch Processing & ZIP Download**
        - 📋 **Easy Copy & Download**
        """)
        with st.expander("📊 Sample Data Format"):
            sample_data = {
                "A": "સાંઈ એપાર્ટમેન્ટ",
                "B": "અમદાવાદ", 
                "C": "અંબાવાડી",
                "D": "68 લાખ",
                "E": "2 BHK",
                "F": "102",
                "G": "1મો માળ",
                "H": "ઈસ્ટ ફેસિંગ",
                "I": "સેમી ફર્નિશ્ડ",
                "J": "5 વર્ષ",
                "K": "https://360tour.link",
                "L": "https://video.link",
                "Tag": "SAI-101"
            }
            st.json(sample_data)

if __name__ == "__main__":
    main()
