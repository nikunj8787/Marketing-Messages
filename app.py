import streamlit as st
import pandas as pd
import requests
import json
import time
from typing import Dict, List, Optional

st.set_page_config(
    page_title="ClearDeals AI Marketing Generator", 
    layout="wide",
    page_icon="🏠"
)

# Configuration from Streamlit secrets
try:
    HF_API_TOKEN = st.secrets["huggingface"]["api_token"]
    GEOAPIFY_API_KEY = st.secrets["geoapify"]["api_key"]
    EMI_LINK = st.secrets["links"]["emi_calculator"]
    VALUATION_LINK = st.secrets["links"]["valuation_calculator"]
except KeyError:
    st.error("Please configure your API tokens in Streamlit secrets.")
    st.stop()

# LLM Configuration
DEFAULT_MODEL = "microsoft/DialoGPT-medium"  # Free, reliable model for chat
BACKUP_MODEL = "gpt2"  # Fallback model

class PropertyDataProcessor:
    @staticmethod
    def process_location(location: str) -> str:
        """Remove prefix codes from location (e.g., 'A-Gota' -> 'Gota')"""
        if location and len(location) > 2 and location[1] == '-':
            return location[2:].strip()
        return location.strip() if location else ""

    @staticmethod
    def get_value(prop: pd.Series, possible_names: List[str], default: str = "") -> str:
        """Safely extract values from property data with multiple possible column names"""
        for name in possible_names:
            if name in prop:
                value = prop[name]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
        return default

class GeoapifyService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def geocode_address(self, address: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode address to get coordinates"""
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={self.api_key}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and response.json()["features"]:
                coords = response.json()["features"][0]["geometry"]["coordinates"]
                return coords[1], coords[0]  # lat, lon
        except Exception as e:
            st.warning(f"Geocoding failed: {str(e)}")
        return None, None

    def fetch_nearby_places(self, lat: float, lon: float, category: str, limit: int = 2, radius: int = 5000) -> List[str]:
        """Fetch nearby places by category"""
        url = (
            f"https://api.geoapify.com/v2/places?categories={category}"
            f"&filter=circle:{lon},{lat},{radius}&limit={limit}&apiKey={self.api_key}"
        )
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                features = response.json().get("features", [])
                return [f["properties"]["name"] for f in features if "name" in f["properties"]]
        except Exception as e:
            st.warning(f"Places search failed for {category}: {str(e)}")
        return []

    def get_nearby_info(self, address: str, city: str = "Ahmedabad", state: str = "Gujarat") -> Dict[str, List[str]]:
        """Get comprehensive nearby places information"""
        full_address = f"{address}, {city}, {state}"
        lat, lon = self.geocode_address(full_address)
        
        if lat is None or lon is None:
            lat, lon = self.geocode_address(f"{city}, {state}")
        
        if lat is None or lon is None:
            return {"schools": [], "colleges": [], "malls": [], "hospitals": []}

        return {
            "schools": self.fetch_nearby_places(lat, lon, "education.school", limit=2),
            "colleges": self.fetch_nearby_places(lat, lon, "education.college", limit=2),
            "malls": self.fetch_nearby_places(lat, lon, "commercial.shopping_mall", limit=2),
            "hospitals": self.fetch_nearby_places(lat, lon, "healthcare.hospital", limit=2),
        }

class HuggingFaceLLM:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def generate_message(self, prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 200) -> str:
        """Generate text using Hugging Face Inference API"""
        url = f"https://api-inference.huggingface.co/models/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        generated = result[0]["generated_text"]
                        # Clean up the response
                        return self._clean_generated_text(generated, prompt)
                elif isinstance(result, dict) and "generated_text" in result:
                    return self._clean_generated_text(result["generated_text"], prompt)
            else:
                st.warning(f"HuggingFace API returned status {response.status_code}")
                
        except Exception as e:
            st.warning(f"LLM generation failed: {str(e)}")
        
        return None

    def _clean_generated_text(self, generated_text: str, original_prompt: str) -> str:
        """Clean and format the generated text"""
        # Remove the original prompt if it's included
        if original_prompt in generated_text:
            generated_text = generated_text.replace(original_prompt, "").strip()
        
        # Clean up common artifacts
        generated_text = generated_text.strip()
        
        # Ensure proper formatting
        lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
        return '\n\n'.join(lines)

class MarketingMessageGenerator:
    def __init__(self, llm: HuggingFaceLLM):
        self.llm = llm
        self.message_types = [
            "Property Benefits",
            "Location Advantage", 
            "FOMO/Urgency",
            "Trust Building",
            "Lifestyle Appeal",
            "Value Proposition",
            "Financial Assistance",
            "Market Analysis",
            "Social Validation",
            "Action Oriented"
        ]

    def create_prompt(self, property_data: Dict, message_type: str, nearby_info: Dict, day_number: int) -> str:
        """Create a detailed prompt for message generation"""
        
        context_instructions = {
            "Property Benefits": "Focus on space, comfort, and lifestyle advantages of this specific property",
            "Location Advantage": "Emphasize connectivity, nearby amenities, and neighborhood quality",
            "FOMO/Urgency": "Create urgency without being pushy, mention market demand and opportunity",
            "Trust Building": "Highlight ClearDeals reputation, transparency, and no-brokerage model",
            "Lifestyle Appeal": "Paint a picture of modern living and community features",
            "Value Proposition": "Compare value with market rates and investment potential",
            "Financial Assistance": f"Include EMI calculator link: {EMI_LINK} for loan planning",
            "Market Analysis": f"Include valuation link: {VALUATION_LINK} for market insights",
            "Social Validation": "Mention community reviews and resident satisfaction",
            "Action Oriented": "Encourage next steps with confidence and support"
        }

        nearby_text = ""
        if nearby_info.get('schools'):
            nearby_text += f"Schools: {', '.join(nearby_info['schools'][:2])}\n"
        if nearby_info.get('hospitals'):
            nearby_text += f"Hospitals: {', '.join(nearby_info['hospitals'][:2])}\n"
        if nearby_info.get('malls'):
            nearby_text += f"Shopping: {', '.join(nearby_info['malls'][:2])}\n"

        return f"""Write a professional WhatsApp marketing message for this property:

Property: {property_data['address']}
Location: {property_data['location']}
Type: {property_data['bhk']}
Price: {property_data['price']}
Area: {property_data['area']}

{nearby_text}

Message Focus: {message_type}
Instructions: {context_instructions.get(message_type, '')}

Requirements:
- Personal, warm tone for Indian homebuyers
- Include relevant emojis (2-3 maximum)
- Exactly 4 lines of content
- Mention buyer has visited once before
- End with: "Reply with a 'Hi' to take this deal forward."
- End with: "www.cleardeals.co.in, No Brokerage Realtor."

Write only the message content:"""

    def generate_fallback_message(self, property_data: Dict, message_type: str, nearby_info: Dict) -> str:
        """Generate fallback template message if LLM fails"""
        templates = {
            "Property Benefits": f"🏡 *{property_data['address']}* offers spacious {property_data['bhk']} living with {property_data['area']} in {property_data['location']}.\n\nYou've shortlisted the perfect match after your visit—this home combines comfort and style beautifully.\n\nReply with a 'Hi' to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.",
            
            "Location Advantage": f"📍 *{property_data['address']}* in {property_data['location']} offers unbeatable connectivity and convenience.\n\nEverything you need is nearby—schools, hospitals, shopping, and transport links are all accessible.\n\nReply with a 'Hi' to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.",
        }
        
        return templates.get(message_type, f"🏠 *{property_data['address']}* is ready for you in {property_data['location']}.\n\nYour dream home awaits—let's move forward with confidence.\n\nReply with a 'Hi' to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor.")

    def generate_all_messages(self, property_data: Dict, nearby_info: Dict) -> List[str]:
        """Generate all 10 marketing messages"""
        messages = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, message_type in enumerate(self.message_types):
            status_text.text(f"Generating {message_type} message...")
            
            prompt = self.create_prompt(property_data, message_type, nearby_info, i+1)
            
            # Try LLM generation first
            generated_message = self.llm.generate_message(prompt)
            
            if generated_message and len(generated_message) > 50:
                # Ensure proper ending
                if not generated_message.endswith("www.cleardeals.co.in, No Brokerage Realtor."):
                    if "Reply with a 'Hi'" not in generated_message:
                        generated_message += "\n\nReply with a 'Hi' to take this deal forward.\nwww.cleardeals.co.in, No Brokerage Realtor."
                    elif not generated_message.endswith("www.cleardeals.co.in, No Brokerage Realtor."):
                        generated_message += "\nwww.cleardeals.co.in, No Brokerage Realtor."
                messages.append(generated_message)
            else:
                # Use fallback template
                fallback_message = self.generate_fallback_message(property_data, message_type, nearby_info)
                messages.append(fallback_message)
                st.warning(f"Used template for {message_type} (LLM generation failed)")
            
            progress_bar.progress((i + 1) / len(self.message_types))
            time.sleep(0.5)  # Rate limiting
        
        progress_bar.empty()
        status_text.empty()
        
        return messages

# Main Streamlit App
def main():
    st.title("🏠 ClearDeals AI Marketing Message Generator")
    st.markdown("*Generate personalized WhatsApp marketing messages using AI*")

    # Initialize services
    geoapify = GeoapifyService(GEOAPIFY_API_KEY)
    llm = HuggingFaceLLM(HF_API_TOKEN)
    message_generator = MarketingMessageGenerator(llm)
    processor = PropertyDataProcessor()

    uploaded_file = st.file_uploader(
        "Upload your property file (.csv, .xls, .xlsx)", 
        type=["csv", "xls", "xlsx"]
    )

    if uploaded_file:
        # Load and process data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Normalize column names
        df.columns = [col.strip().replace("-", "").replace("_", "").lower() for col in df.columns]

        with st.expander("Show detected columns"):
            st.write("**Columns detected in your file:**", list(df.columns))

        # Find tag column
        tag_columns = [col for col in df.columns if col.startswith("tag")]
        if not tag_columns:
            st.error("No 'Tag' column found in your file. Please ensure your file has a 'Tag' column.")
            return

        tag_col = tag_columns[0]
        tag = st.selectbox("Select Property Tag", df[tag_col].astype(str))
        
        if st.button("🚀 Generate AI Marketing Messages", type="primary"):
            # Get property data
            prop = df[df[tag_col].astype(str) == tag].iloc[0]

            # Extract property information
            property_data = {
                "address": processor.get_value(prop, ['propertyaddress', 'address', 'name']),
                "location": processor.process_location(processor.get_value(prop, ['location', 'area', 'locality'])),
                "bhk": processor.get_value(prop, ['bhk', 'configuration', 'type']),
                "price": processor.get_value(prop, ['propertyprice', 'price', 'amount']),
                "area": processor.get_value(prop, ['superbuiltuppconstructionarea', 'area', 'size'])
            }

            # Validate required data
            if not all([property_data['address'], property_data['location']]):
                st.error("Missing required property information. Please check your data.")
                return

            # Fetch nearby places
            with st.spinner("Fetching nearby places..."):
                nearby_info = geoapify.get_nearby_info(property_data['address'])

            # Show fetched places
            with st.expander("📍 Nearby Places Found"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("🏫 **Schools:**", ", ".join(nearby_info['schools']) if nearby_info['schools'] else "None found")
                    st.write("🏥 **Hospitals:**", ", ".join(nearby_info['hospitals']) if nearby_info['hospitals'] else "None found")
                with col2:
                    st.write("🛍️ **Malls:**", ", ".join(nearby_info['malls']) if nearby_info['malls'] else "None found")
                    st.write("🎓 **Colleges:**", ", ".join(nearby_info['colleges']) if nearby_info['colleges'] else "None found")

            # Generate messages
            st.markdown("---")
            st.subheader("🤖 AI-Generated Marketing Messages")
            
            messages = message_generator.generate_all_messages(property_data, nearby_info)

            # Display messages
            categories = [
                "PROPERTY BENEFITS", "LOCATION ADVANTAGE", "FOMO/URGENCY", 
                "TRUST BUILDING", "LIFESTYLE APPEAL", "VALUE PROPOSITION",
                "FINANCIAL ASSISTANCE", "MARKET ANALYSIS", "SOCIAL VALIDATION", 
                "ACTION ORIENTED"
            ]

            all_messages = ""
            for i, (msg, category) in enumerate(zip(messages, categories)):
                st.markdown(
                    f"""
                    <div style="background:#f8f9fa; border-radius:10px; padding:16px; margin-bottom:16px; border:1px solid #e0e0e0; line-height:1.5;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <div style="font-weight:bold; color:#2e8b57;">🤖 {category}</div>
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
                    key=f"ai_msg_{i}",
                    help="Click the copy icon to copy this AI-generated message"
                )
                all_messages += msg + "\n\n"

            # Download option
            st.download_button(
                "📥 Download All AI Messages (.txt)",
                all_messages,
                file_name=f"{property_data['address'].replace(' ','_').replace('/','_')}_AI_WhatsApp_Messages.txt",
                mime="text/plain"
            )

            st.success("🎉 Successfully generated AI-powered marketing messages!")
            st.info("💡 Each message is uniquely generated by AI and customized for your property.")

if __name__ == "__main__":
    main()
