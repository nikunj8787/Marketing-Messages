import streamlit as st
import pandas as pd

st.set_page_config(page_title="ClearDeals WhatsApp Marketing Generator", layout="wide")

# --- Short links (replace with your own) ---
EMI_LINK = "https://rb.gy/abcd12"  # Shortened EMI calculator link
VALUATION_LINK = "https://rb.gy/wxyz34"  # Shortened property valuation link

st.title("ClearDeals WhatsApp Marketing Message Generator")

uploaded_file = st.file_uploader(
    "Upload your property file (.csv, .xls, .xlsx)", 
    type=["csv", "xls", "xlsx"]
)

def get_value(prop, possible_names, default=""):
    """Try multiple column names, return value or default if all missing."""
    for name in possible_names:
        if name in prop:
            return prop[name]
    return default

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    # Normalize columns: strip spaces, lower-case, replace dashes/underscores with nothing
    df.columns = [col.strip().replace("-", "").replace("_", "").lower() for col in df.columns]

    st.write("**Columns detected in your file:**", list(df.columns))

    # Use normalized column names for access
    tag_col = [col for col in df.columns if col.startswith("tag")][0]
    tag = st.selectbox("Select Property Tag", df[tag_col].astype(str))
    prop = df[df[tag_col].astype(str) == tag].iloc[0]

    # Helper to get each field robustly
    def g(colnames, default=""):
        return get_value(prop, [c.strip().replace("-", "").replace("_", "").lower() for c in colnames], default)

    # Compose all 10 messages (each as 4+ lines, with WhatsApp formatting)
    messages = [
        # 1. Property Benefits
        f"""🏡 *{g(['Property-Address','propertyaddress'])}* offers a spacious {g(['BHK','bhk'])} with {g(['Super-Built-up-Construction-Area','superbuiltuppconstructionarea'])} of luxury living space.
A perfect blend of comfort and style for your family, with modern interiors and ample natural light.
Enjoy privacy and convenience in a well-planned layout.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 2. Location Advantage
        f"""📍 *{g(['Property-Address','propertyaddress'])}* is at an unbeatable location in {g(['Location','location'])}!
Everything you need is just minutes away—schools, hospitals, shopping centers, and public transport.
Live in a thriving neighborhood with excellent connectivity.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 3. FOMO/Urgency Creation
        f"""⏳ Opportunities like *{g(['Property-Address','propertyaddress'])}* in {g(['Location','location'])} don't last long!
Demand is high and units are moving fast—secure your dream home before it's gone.
Contact now to book your site visit and avoid missing out.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 4. Trust Building
        f"""✅ Join hundreds of happy families who chose *{g(['Property-Address','propertyaddress'])}*.
ClearDeals is trusted for transparent, no-brokerage deals and customer-first service.
Your investment is safe with us—see our track record and testimonials.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 5. Lifestyle Appeal
        f"""🌟 Experience premium living at *{g(['Property-Address','propertyaddress'])}*.
Enjoy amenities like {g(['Amenities','amenities'],'modern amenities')} and a vibrant community atmosphere.
Perfect for families seeking comfort, security, and a modern lifestyle.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 6. Value Proposition
        f"""💰 Exceptional value: *{g(['Property-Address','propertyaddress'])}* offers {g(['BHK','bhk'])} at just {g(['Property-Price','propertyprice'])}.
Compare with similar properties in {g(['Location','location'])} and see the difference.
A smart investment for your future—contact us for exclusive deals.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 7. Financial Assistance (EMI)
        f"""🏦 Need help with home finance? Calculate your EMI instantly for *{g(['Property-Address','propertyaddress'])}*.
Use our quick EMI calculator: {EMI_LINK}
Get expert assistance for loan approval and documentation.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 8. Market Analysis (Valuation)
        f"""📊 Curious about property value? Get a free valuation report for *{g(['Property-Address','propertyaddress'])}*.
Check your property's worth here: {VALUATION_LINK}
Make informed decisions with ClearDeals' expert insights.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 9. Social Validation
        f"""👥 Hear from our satisfied buyers at *{g(['Property-Address','propertyaddress'])}*.
Join a community of like-minded residents who love their new home.
Your positive experience is our top priority.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor.""",

        # 10. Action Oriented
        f"""🚀 Last few units left at *{g(['Property-Address','propertyaddress'])}* in {g(['Location','location'])}!
Book your second site visit or finalize your deal today—don't miss out.
We are ready to assist you every step of the way.
Reply with a "Hi" to take this deal forward.
www.cleardeals.co.in, No Brokerage Realtor."""
    ]

    # UI: Card-style message display
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
            height=160,
            key=f"msg_{i}",
            help="Click the copy icon to copy this message"
        )
        all_messages += msg + "\n\n"

    # Download all messages as .txt
    st.download_button(
        "📥 Download All Messages (.txt)",
        all_messages,
        file_name=f"{g(['Property-Address','propertyaddress']).replace(' ','_').replace('/','_')}_WhatsApp_Followup.txt"
    )

    st.info("💡 Tip: Copy individual messages using the copy icon, or download all messages for WhatsApp campaigns.")
