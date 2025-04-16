# Enqette Javaanse Gerechten

Een digitale enquête applicatie voor het verzamelen van feedback over Javaanse workshops en recepten, gebouwd met Streamlit.

## Features

- Digitale enquête toegankelijk via QR code
- Automatische opslag van responses in CSV formaat
- Winnaar selectie tool met animatie effect
- Downloadbare QR code voor marketing materiaal

## Setup

1. Installeer de benodigde packages:
```bash
pip install -r requirements.txt
```

2. Start de applicatie:
```bash
streamlit run app.py
```

3. De applicatie is nu beschikbaar op:
- Lokaal: http://localhost:8501
- Scan de QR code in de app om de enquête op een mobiel apparaat in te vullen

## Gebruik

### Voor Deelnemers
- Scan de QR code om toegang te krijgen tot de enquête
- Vul de enquête in om kans te maken op een wellnesspakket
- Ontvang een bevestiging na het succesvol invullen

### Voor Organisatoren
- Bekijk alle inzendingen in het "Winnaar Selectie" tabblad
- Gebruik de "Trek een Winnaar" knop om willekeurig een winnaar te selecteren
- Download de QR code om te gebruiken in marketing materiaal

## Data Opslag

Alle responses worden opgeslagen in `responses.csv` met de volgende velden:
- Deelgenomen workshops
- Product beoordelingen
- Interesse in toekomstige workshops
- Contactgegevens
- Feedback en opmerkingen
