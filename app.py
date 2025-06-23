import streamlit as st
import pandas as pd
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import re

# Page configuration with Gujarati support
st.set_page_config(
    page_title="ClearDeals Gujarati Marketing Generator",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded"
)

# Custom CSS for Gujarati font support and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;500;600;700&display=swap');
    
    .gujarati-text {
        font-family: 'Noto Sans Gujarati', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        direction: ltr;
    }
    
    .message-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #00b894;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .day-badge {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .toggle-container {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e6ed;
        margin: 20px 0;
    }
    
    .upload-area {
        border: 2px dashed #00b894;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        background: #f7fffe;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration from Streamlit secrets
try:
    GEOAPIFY_API_KEY = st.secrets.get("geoapify", {}).get("api_key", "d1632c8149f94409b7f78f29c458716d")
    HF_API_TOKEN = st.secrets.get("huggingface", {}).get("api_token", "")
    EMI_LINK = st.secrets.get("links", {}).get("emi_calculator", "https://lnk.ink/FUwEc")
    VALUATION_LINK = st.secrets.get("links", {}).get("valuation_calculator", "https://lnk.ink/fkYwF")
except Exception:
    # Fallback values for development
    GEOAPIFY_API_KEY = "d1632c8149f94409b7f78f29c458716d"
    HF_API_TOKEN = ""
    EMI_LINK = "https://lnk.ink/FUwEc"
    VALUATION_LINK = "https://lnk.ink/fkYwF"

# Static Gujarati Message Templates
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

# Column mapping for property data
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
    """Handle property data processing and validation"""
    
    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to A-L mapping"""
        original_columns = df.columns.tolist()
        
        # Create mapping based on position or common names
        column_map = {}
        expected_columns = list(COLUMN_MAPPING.keys())
        
        for i, col in enumerate(original_columns[:len(expected_columns)]):
            column_map[col] = expected_columns[i]
        
        df_normalized = df.rename(columns=column_map)
        
        # Ensure all required columns exist with NA defaults
        for col in expected_columns:
            if col not in df_normalized.columns:
                df_normalized[col] = "NA"
        
        return df_normalized[expected_columns]
    
    @staticmethod
    def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean property data"""
        for col in df.columns:
            df[col] = df[col].fillna("NA").astype(str)
            df[col] = df[col].replace(['nan', 'None', ''], 'NA')
        
        return df
    
    @staticmethod
    def format_property_identifier(row: pd.Series) -> str:
        """Create a unique identifier for each property"""
        project_name = row.get('A', 'Unknown')
        city = row.get('B', 'Unknown')
        return f"{project_name} - {city}"

class GeoapifyService:
    """Handle Geoapify API interactions for nearby places"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_nearby_places(self, location: str) -> Dict[str, List[str]]:
        """Get nearby places for a location"""
        if not self.api_key or self.api_key == "":
            return {"schools": [], "hospitals": [], "malls": [], "colleges": []}
        
        try:
            # Geocode location
            lat, lon = self._geocode_location(location)
            if not lat or not lon:
                return {"schools": [], "hospitals": [], "malls": [], "colleges": []}
            
            return {
                "schools": self._fetch_places(lat, lon, "education.school"),
                "hospitals": self._fetch_places(lat, lon, "healthcare.hospital"),
                "malls": self._fetch_places(lat, lon, "commercial.shopping_mall"),
                "colleges": self._fetch_places(lat, lon, "education.college")
            }
        except Exception as e:
            st.warning(f"Could not fetch nearby places: {str(e)}")
            return {"schools": [], "hospitals": [], "malls": [], "colleges": []}
    
    def _geocode_location(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode a location to get coordinates"""
        url = f"https://api.geoapify.com/v1/geocode/search?text={location}&apiKey={self.api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                return coords[1], coords[0]  # lat, lon
        
        return None, None
    
    def _fetch_places(self, lat: float, lon: float, category: str, limit: int = 2) -> List[str]:
        """Fetch nearby places by category"""
        url = f"https://api.geoapify.com/v2/places?categories={category}&filter=circle:{lon},{lat},3000&limit={limit}&apiKey={self.api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return [place["properties"]["name"] for place in data.get("features", []) if "name" in place["properties"]]
        
        return []

class HuggingFaceLLM:
    """Handle Hugging Face LLM interactions"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def generate_gujarati_message(self, property_data: Dict, day: int, message_type: str, nearby_places: Dict) -> str:
        """Generate Gujarati marketing message using LLM"""
        if not self.api_token:
            return self._generate_fallback_message(property_data, day, message_type)
        
        prompt = self._create_gujarati_prompt(property_data, day, message_type, nearby_places)
        
        try:
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    generated = result[0].get("generated_text", "")
                    return self._clean_generated_text(generated, prompt)
            
        except Exception as e:
            st.warning(f"LLM generation failed for Day {day}: {str(e)}")
        
        return self._generate_fallback_message(property_data, day, message_type)
    
    def _create_gujarati_prompt(self, property_data: Dict, day: int, message_type: str, nearby_places: Dict) -> str:
        """Create prompt for Gujarati message generation"""
        nearby_text = ""
        if nearby_places.get("schools"):
            nearby_text += f"Schools: {', '.join(nearby_places['schools'][:2])}\n"
        if nearby_places.get("hospitals"):
            nearby_text += f"Hospitals: {', '.join(nearby_places['hospitals'][:2])}\n"
        
        return f"""Generate a Gujarati WhatsApp marketing message for property follow-up:

Property: {property_data.get('A', 'NA')}
City: {property_data.get('B', 'NA')}
Price: ₹{property_data.get('D', 'NA')}
Configuration: {property_data.get('E', 'NA')}
Area: {property_data.get('F', 'NA')} sq.yds

Day {day} Focus: {message_type}
{nearby_text}

Requirements:
- Write in authentic Gujarati (not transliteration)
- 3-4 lines maximum
- Include appropriate emoji
- End with call-to-action
- Professional but friendly tone

Generate message:"""
    
    def _clean_generated_text(self, generated: str, prompt: str) -> str:
        """Clean and format generated text"""
        if prompt in generated:
            generated = generated.replace(prompt, "").strip()
        
        lines = [line.strip() for line in generated.split('\n') if line.strip()]
        return '\n'.join(lines[:4])  # Limit to 4 lines
    
    def _generate_fallback_message(self, property_data: Dict, day: int, message_type: str) -> str:
        """Generate fallback message if LLM fails"""
        if day <= len(GUJARATI_TEMPLATES):
            return self._substitute_template_variables(GUJARATI_TEMPLATES[day-1]["template"], property_data)
        
        return f"🏠 {property_data.get('A', 'NA')} માટે સંપર્ક કરો\n👉 રિપ્લાય કરો YES"
    
    def _substitute_template_variables(self, template: str, property_data: Dict) -> str:
        """Substitute template variables with actual data"""
        for key, value in property_data.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

class MessageGenerator:
    """Main message generation controller"""
    
    def __init__(self):
        self.geoapify = GeoapifyService(GEOAPIFY_API_KEY)
        self.llm = HuggingFaceLLM(HF_API_TOKEN)
        self.processor = PropertyDataProcessor()
    
    def generate_static_messages(self, property_data: Dict) -> List[Dict]:
        """Generate static template messages"""
        messages = []
        
        for template_info in GUJARATI_TEMPLATES:
            message_text = template_info["template"]
            
            # Substitute variables
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
    
    def generate_llm_messages(self, property_data: Dict) -> List[Dict]:
        """Generate LLM-powered dynamic messages"""
        messages = []
        
        # Get nearby places for context
        location = f"{property_data.get('A', '')}, {property_data.get('C', '')}, {property_data.get('B', '')}"
        nearby_places = self.geoapify.get_nearby_places(location)
        
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
        
        progress_bar = st.progress(0)
        
        for i, message_type in enumerate(message_types):
            generated_message = self.llm.generate_gujarati_message(
                property_data, i+1, message_type, nearby_places
            )
            
            messages.append({
                "day": i+1,
                "title": message_type,
                "message": generated_message,
                "type": "llm"
            })
            
            progress_bar.progress((i+1) / len(message_types))
            time.sleep(0.5)  # Rate limiting
        
        progress_bar.empty()
        return messages

def create_download_content(messages: List[Dict], property_data: Dict) -> str:
    """Create downloadable content for messages"""
    content = f"ClearDeals Gujarati Marketing Messages\n"
    content += f"Property: {property_data.get('A', 'NA')}\n"
    content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "="*50 + "\n\n"
    
    for msg in messages:
        content += f"Day {msg['day']}: {msg['title']}\n"
        content += "-" * 30 + "\n"
        content += msg['message'] + "\n\n"
    
    return content

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #00b894; margin-bottom: 10px;">🏠 ClearDeals Gujarati Marketing Generator</h1>
        <p style="color: #666; font-size: 18px;">8 દિવસીય અનુક્રમિક ગુજરાતી માર્કેટિંગ સંદેશા જનરેટર</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Generation mode toggle
        st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
        generation_mode = st.radio(
            "Select Generation Mode:",
            ["📝 Static Templates", "🤖 LLM-Powered Dynamic"],
            help="Choose between predefined templates or AI-generated messages"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # API Status
        st.markdown("### 🔗 API Status")
        st.success("✅ Geoapify: Connected") if GEOAPIFY_API_KEY else st.error("❌ Geoapify: Not configured")
        st.success("✅ HuggingFace: Connected") if HF_API_TOKEN else st.warning("⚠️ HuggingFace: Not configured")
        
        # Column mapping reference
        with st.expander("📋 Column Mapping Reference"):
            for key, desc in COLUMN_MAPPING.items():
                st.write(f"**{key}**: {desc}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload section
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📁 Upload Property Data File",
            type=["csv", "xlsx", "json"],
            help="Upload CSV, Excel, or JSON file with property data"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            try:
                # Load and process data
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_json(uploaded_file)
                
                # Initialize processors
                processor = PropertyDataProcessor()
                message_generator = MessageGenerator()
                
                # Normalize and validate data
                df_normalized = processor.normalize_columns(df)
                df_clean = processor.validate_and_clean_data(df_normalized)
                
                # Display data preview
                with st.expander("👀 Data Preview", expanded=True):
                    st.dataframe(df_clean, use_container_width=True)
                
                # Property selection
                if not df_clean.empty:
                    property_options = [processor.format_property_identifier(row) for _, row in df_clean.iterrows()]
                    
                    selected_property_idx = st.selectbox(
                        "🏠 Select Property:",
                        range(len(property_options)),
                        format_func=lambda x: property_options[x]
                    )
                    
                    selected_property_data = df_clean.iloc[selected_property_idx].to_dict()
                    
                    # Generate messages button
                    if st.button("🚀 Generate Gujarati Messages", type="primary", use_container_width=True):
                        with st.spinner("Generating messages..."):
                            if generation_mode == "📝 Static Templates":
                                messages = message_generator.generate_static_messages(selected_property_data)
                                st.success("✅ Static messages generated successfully!")
                            else:
                                messages = message_generator.generate_llm_messages(selected_property_data)
                                st.success("✅ LLM-powered messages generated successfully!")
                        
                        # Display generated messages
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
                            
                            # Copy button for each message
                            if st.button(f"📋 Copy Day {msg['day']} Message", key=f"copy_{msg['day']}"):
                                st.write("📋 Message copied to display:")
                                st.code(msg['message'], language=None)
                            
                            all_messages_text += f"Day {msg['day']}: {msg['title']}\n{msg['message']}\n\n"
                        
                        # Download all messages
                        download_content = create_download_content(messages, selected_property_data)
                        
                        st.download_button(
                            label="📥 Download All Messages",
                            data=download_content.encode('utf-8'),
                            file_name=f"ClearDeals_Gujarati_Messages_{selected_property_data.get('A', 'Property').replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        
                        # Batch processing option
                        st.markdown("---")
                        if st.button("🔄 Generate for All Properties", type="secondary"):
                            batch_messages = {}
                            
                            progress_container = st.container()
                            with progress_container:
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for idx, (_, row) in enumerate(df_clean.iterrows()):
                                    property_data = row.to_dict()
                                    property_id = processor.format_property_identifier(row)
                                    
                                    status_text.text(f"Processing: {property_id}")
                                    
                                    if generation_mode == "📝 Static Templates":
                                        batch_messages[property_id] = message_generator.generate_static_messages(property_data)
                                    else:
                                        batch_messages[property_id] = message_generator.generate_llm_messages(property_data)
                                    
                                    progress_bar.progress((idx + 1) / len(df_clean))
                                    time.sleep(0.1)
                                
                                progress_bar.empty()
                                status_text.empty()
                            
                            # Create batch download
                            batch_content = "ClearDeals Gujarati Marketing Messages - Batch Export\n"
                            batch_content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            batch_content += "="*60 + "\n\n"
                            
                            for property_id, messages in batch_messages.items():
                                batch_content += f"PROPERTY: {property_id}\n"
                                batch_content += "-" * 40 + "\n"
                                for msg in messages:
                                    batch_content += f"Day {msg['day']}: {msg['title']}\n{msg['message']}\n\n"
                                batch_content += "="*60 + "\n\n"
                            
                            st.download_button(
                                label="📦 Download Batch Messages",
                                data=batch_content.encode('utf-8'),
                                file_name=f"ClearDeals_Batch_Messages_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                            st.success(f"✅ Batch processing completed for {len(df_clean)} properties!")
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with col2:
        # Information panel
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. **Upload** your property data file (CSV/Excel)
        2. **Select** generation mode (Static/LLM)
        3. **Choose** a property from the dropdown
        4. **Generate** 8-day Gujarati message sequence
        5. **Copy** individual messages or download all
        6. **Use** batch processing for multiple properties
        """)
        
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🎯 **8-Day Sequential Messages**
        - 🌐 **Authentic Gujarati Language**
        - 📝 **Static Templates**
        - 🤖 **AI-Powered Generation**
        - 📍 **Location-Based Context**
        - 📱 **WhatsApp Optimized**
        - 💾 **Batch Processing**
        - 📋 **Easy Copy & Download**
        """)
        
        # Sample data format
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
                "L": "https://video.link"
            }
            st.json(sample_data)

if __name__ == "__main__":
    main()
