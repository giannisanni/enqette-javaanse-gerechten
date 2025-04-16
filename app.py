import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import random
import time
from pathlib import Path
import base64
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# Initialize Google Sheets connection
@st.cache_resource
def init_google_sheets():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

def get_sheet_data():
    """Get all responses from Google Sheets."""
    try:
        service = init_google_sheets()
        sheet = service.spreadsheets()
        
        # Get all data from the sheet
        result = sheet.values().get(
            spreadsheetId=st.secrets["sheets"]["spreadsheet_id"],
            range='A:H'  # Adjust range based on your columns
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return pd.DataFrame(columns=[
                'workshops', 'massage_oil_rating', 'muscle_spray_rating',
                'future_interests', 'name', 'email', 'whatsapp', 'feedback'
            ])
            
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Error reading from Google Sheets: {str(e)}")
        return pd.DataFrame()

def append_to_sheet(data):
    """Append a new response to Google Sheets."""
    try:
        service = init_google_sheets()
        sheet = service.spreadsheets()
        
        values = [[
            data['workshops'],
            data['massage_oil_rating'],
            data['muscle_spray_rating'],
            data['future_interests'],
            data['name'],
            data['email'],
            data['whatsapp'],
            data['feedback']
        ]]
        
        body = {
            'values': values
        }
        
        # Append the data
        sheet.values().append(
            spreadsheetId=st.secrets["sheets"]["spreadsheet_id"],
            range='A:H',  # Adjust range based on your columns
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Error writing to Google Sheets: {str(e)}")
        return False

# Initialize session state variables
if 'show_thank_you' not in st.session_state:
    st.session_state.show_thank_you = False

def create_qr_code():
    """Generate QR code for the survey URL."""
    # Use production URL or fallback to localhost for development
    url = 'https://javaanse-rituelen-en-recepten.streamlit.app'
    img = qrcode.make(url)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def check_existing_contact(email, whatsapp):
    """Check if email or WhatsApp number already exists in responses."""
    df = get_sheet_data()
    if not df.empty:
        if email in df['email'].values:
            return False, "Dit e-mailadres is al gebruikt voor een eerdere inzending."
        if whatsapp in df['whatsapp'].values:
            return False, "Dit WhatsApp-nummer is al gebruikt voor een eerdere inzending."
    return True, ""

def save_response(data):
    """Save survey response to Google Sheets."""
    is_valid, error_message = check_existing_contact(data['email'], data['whatsapp'])
    
    if not is_valid:
        st.error(error_message)
        return False
        
    if append_to_sheet(data):
        st.session_state.show_thank_you = True
        return True
    return False

def spin_wheel():
    """Animate spinning wheel effect and select winner."""
    df = get_sheet_data()
    if df.empty:
        st.error("Geen deelnemers beschikbaar voor de trekking.")
        return
    
    participants = [f"{row['name']} ({row['email']})" for _, row in df.iterrows()]
    placeholder = st.empty()
    
    # Spinning animation
    for _ in range(20):
        placeholder.markdown(f"## 🎯 {random.choice(participants)}")
        time.sleep(0.1)
    
    # Show winner
    winner = random.choice(participants)
    placeholder.markdown(f"## 🎉 Winnaar: {winner}")
    return winner

def main():
    st.title("Javaanse Rituelen en Recepten - Enquête")
    
    # Create tabs for Survey and Winner Selection
    tab1, tab2, tab3 = st.tabs(["Enquête", "Winnaar Selectie", "QR Code"])
    
    with tab1:
        if not st.session_state.show_thank_you:
            st.write("Bedankt voor je deelname aan onze workshop(s)! Vul deze korte enquête in en maak kans op een wellnesspakket.")
            
            # Workshop participation
            workshops = st.multiselect(
                "1. Aan welke workshop(s) heb je deelgenomen?",
                ["Klepon maken", "Pitjit massage", "Geen van beide, ik was toeschouwer"]
            )
            
            # Product ratings
            st.write("2. Wat vond je van de producten?")
            massage_oil = st.slider("Massageolie:", 1, 5, 3)
            muscle_spray = st.slider("Muscle spray:", 1, 5, 3)
            
            # Future interests
            future_interests = st.multiselect(
                "3. Waar heb je interesse in voor toekomstige workshops?",
                ["Workshop Jamu maken", "Cursus Pitjit massage", "Indonesische kookcursus", "Geen interesse op dit moment"]
            )
            
            # Contact information
            st.write("4. Contactgegevens")
            name = st.text_input("Naam:")
            email = st.text_input("E-mailadres:")
            whatsapp = st.text_input("WhatsApp-nummer:")
            
            # Feedback
            feedback = st.text_area("5. Feedback of opmerkingen")
            
            if st.button("Verstuur"):
                if not name:  # Name validation
                    st.error("Vul alstublieft uw naam in.")
                    return

                if not email or not whatsapp:  # Basic validation
                    st.error("Vul alstublieft uw e-mailadres en WhatsApp-nummer in.")
                    return

                if not '@' in email:  # Basic email format validation
                    st.error("Vul alstublieft een geldig e-mailadres in.")
                    return

                if not whatsapp.isdigit():  # Basic phone number validation
                    st.error("Vul alstublieft een geldig telefoonnummer in (alleen cijfers).")
                    return

                response_data = {
                    'workshops': ', '.join(workshops),
                    'massage_oil_rating': massage_oil,
                    'muscle_spray_rating': muscle_spray,
                    'future_interests': ', '.join(future_interests),
                    'name': name,
                    'email': email,
                    'whatsapp': whatsapp,
                    'feedback': feedback
                }
                if save_response(response_data):
                    st.success("Bedankt voor je deelname! Je maakt nu kans op het wellnesspakket.")
        else:
            st.success("Bedankt voor je deelname! Je maakt nu kans op het wellnesspakket.")
            if st.button("Nieuwe enquête invullen"):
                st.session_state.show_thank_you = False
                st.rerun()
    
    with tab2:
        st.write("## Winnaar Selectie")
        if st.button("Trek een Winnaar"):
            spin_wheel()
        
        # Display all participants
        df = get_sheet_data()
        if not df.empty:
            st.write("### Deelnemers:")
            st.dataframe(df[['name', 'email', 'whatsapp']])
    
    with tab3:
        st.write("## QR Code")
        st.write("Scan deze QR code om de enquête in te vullen:")
        qr_code = create_qr_code()
        st.image(qr_code)
        
        # Download button for QR code
        st.download_button(
            label="Download QR Code",
            data=qr_code,
            file_name="enquete_qr.png",
            mime="image/png"
        )

if __name__ == "__main__":
    main()
