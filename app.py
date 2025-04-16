import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import random
import time
from pathlib import Path
import base64
import os

# Initialize session state variables
if 'submissions' not in st.session_state:
    st.session_state.submissions = []
    
if 'show_thank_you' not in st.session_state:
    st.session_state.show_thank_you = False

def create_qr_code():
    """Generate QR code for the survey URL."""
    # Use environment variable for URL, fallback to localhost for development
    url = os.getenv('STREAMLIT_URL', 'http://localhost:8501')
    img = qrcode.make(url)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def check_existing_contact(email, whatsapp):
    """Check if email or WhatsApp number already exists in responses."""
    if Path('responses.csv').exists():
        df = pd.read_csv('responses.csv')
        if email in df['email'].values:
            return False, "Dit e-mailadres is al gebruikt voor een eerdere inzending."
        if whatsapp in df['whatsapp'].values:
            return False, "Dit WhatsApp-nummer is al gebruikt voor een eerdere inzending."
    return True, ""

def save_response(data):
    """Save survey response to CSV file."""
    is_valid, error_message = check_existing_contact(data['email'], data['whatsapp'])
    
    if not is_valid:
        st.error(error_message)
        return False
        
    df = pd.DataFrame([data])
    if Path('responses.csv').exists():
        df.to_csv('responses.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('responses.csv', index=False)
    st.session_state.submissions.append(data)
    st.session_state.show_thank_you = True
    return True

def spin_wheel():
    """Animate spinning wheel effect and select winner."""
    if not st.session_state.submissions:
        st.error("Geen deelnemers beschikbaar voor de trekking.")
        return
    
    participants = [sub['email'] for sub in st.session_state.submissions]
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
            email = st.text_input("E-mailadres:")
            whatsapp = st.text_input("WhatsApp-nummer:")
            
            # Feedback
            feedback = st.text_area("5. Feedback of opmerkingen")
            
            if st.button("Verstuur"):
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
        if st.session_state.submissions:
            st.write("### Deelnemers:")
            df = pd.DataFrame(st.session_state.submissions)
            st.dataframe(df[['email', 'whatsapp']])
    
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
