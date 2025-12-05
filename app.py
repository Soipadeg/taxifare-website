import streamlit as st
import requests
from datetime import datetime

# Fonction pour obtenir l'adresse à partir des coordonnées
@st.cache_data(ttl=3600)
def get_address_from_coords(lat, lon):
    """Géocodage inversé pour obtenir l'adresse depuis les coordonnées"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "TaxiFareApp/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})

            # Construire une adresse lisible
            parts = []
            if "house_number" in address and "road" in address:
                parts.append(f"{address['house_number']} {address['road']}")
            elif "road" in address:
                parts.append(address["road"])

            if "neighbourhood" in address:
                parts.append(address["neighbourhood"])
            elif "suburb" in address:
                parts.append(address["suburb"])

            if "city" in address:
                parts.append(address["city"])
            elif "town" in address:
                parts.append(address["town"])

            return ", ".join(parts) if parts else data.get("display_name", f"{lat:.4f}, {lon:.4f}")
        else:
            return f"{lat:.4f}, {lon:.4f}"
    except Exception as e:
        return f"{lat:.4f}, {lon:.4f}"

# Fonction pour obtenir les coordonnées à partir d'une adresse (géocodage)
@st.cache_data(ttl=3600)
def get_coords_from_address(address):
    """Géocodage pour obtenir les coordonnées depuis une adresse"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "TaxiFareApp/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None
    except Exception as e:
        return None, None

# Configuration de la page - Layout centré comme une app mobile
st.set_page_config(
    page_title="🚕 TaxiFare",
    page_icon="🚕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialiser les coordonnées dans session_state
if 'pickup_lat' not in st.session_state:
    st.session_state.pickup_lat = 40.748817
if 'pickup_lon' not in st.session_state:
    st.session_state.pickup_lon = -73.985428
if 'dropoff_lat' not in st.session_state:
    st.session_state.dropoff_lat = 40.758817
if 'dropoff_lon' not in st.session_state:
    st.session_state.dropoff_lon = -73.975428

# CSS personnalisé - Design moderne minimaliste
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* Global */
    .main {
        max-width: 480px;
        padding: 0;
        font-family: 'Poppins', sans-serif;
        background: #1a1a1a;
    }

    .block-container {
        padding: 1.5rem 1rem;
    }

    /* Hero Header */
    .hero-header {
        background: linear-gradient(160deg, #FFC837 0%, #FF8008 100%);
        padding: 3rem 1.5rem 3.5rem;
        margin: -1.5rem -1rem 2rem;
        position: relative;
        overflow: hidden;
    }

    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }

    .hero-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }

    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 0 4px 12px rgba(0,0,0,0.15);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .hero-emoji {
        display: inline-block;
        animation: bounce 2s ease-in-out infinite;
        font-size: 3.5rem;
        margin-right: 0.3rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        margin-top: 0.8rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Tabs style */
    .tab-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
    }

    .tab {
        flex: 1;
        padding: 0.75rem;
        text-align: center;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }

    .tab.active {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Input groups */
    .input-group {
        background: linear-gradient(135deg, rgba(255, 200, 55, 0.15) 0%, rgba(255, 128, 8, 0.15) 100%);
        padding: 0;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(255, 128, 8, 0.2);
        border: 1px solid rgba(255, 200, 55, 0.3);
        overflow: hidden;
    }

    .input-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #ffffff;
        background: linear-gradient(160deg, rgba(255, 200, 55, 0.7) 0%, rgba(255, 128, 8, 0.7) 100%);
        font-weight: 600;
        font-size: 0.95rem;
        margin: 0;
        padding: 1rem 1.25rem;
        border-radius: 16px;
    }

    .input-content {
        padding: 1.25rem;
    }

    .icon {
        font-size: 1.3rem;
    }

    /* Compact inputs */
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1.5px solid rgba(255, 200, 55, 0.3);
        padding: 0.6rem 0.8rem;
        font-size: 0.95rem;
        background: rgba(0, 0, 0, 0.4);
        color: #ffffff;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }

    /* Boutons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(160deg, #FFC837 0%, #FF8008 100%);
        color: white;
        border: none;
        padding: 1.1rem;
        border-radius: 14px;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 0.5rem;
        box-shadow: 0 6px 20px rgba(255, 128, 8, 0.35);
        transition: transform 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 128, 8, 0.45);
    }

    /* Map button style */
    button[key="pickup_map_btn"],
    button[key="dropoff_map_btn"],
    button[key="close_map"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-size: 0.9rem !important;
        padding: 0.7rem !important;
        margin-top: 0 !important;
        box-shadow: 0 3px 12px rgba(102, 126, 234, 0.3) !important;
    }

    /* Prix display */
    .price-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }

    .price-display::before {
        content: '💰';
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 8rem;
        opacity: 0.1;
    }

    .price-label {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        font-weight: 400;
        margin-bottom: 0.5rem;
    }

    .price-amount {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    /* Route info */
    .route-info {
        background: #f8f9fa;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-top: 1rem;
    }

    .route-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px dotted #d0d0d0;
    }

    .route-row:last-child {
        border-bottom: none;
    }

    .route-label {
        color: #666;
        font-size: 0.85rem;
    }

    .route-value {
        color: #333;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Slider personnalisé */
    .stSlider {
        padding: 0.5rem 0;
    }

    /* Captions */
    .stCaptionContainer p {
        color: rgba(255, 200, 55, 0.8) !important;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        color: rgba(255, 200, 55, 0.6);
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1.5rem 0;
        border-top: 1px solid rgba(255, 200, 55, 0.2);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
    <div class="hero-header">
        <div class="hero-title">
            <span class="hero-emoji">🚕</span>TaxiFare
        </div>
        <div class="hero-subtitle">🚋 Un taxi grâce au Wagon 🚋</div>
    </div>
""", unsafe_allow_html=True)

# Section Date & Heure
st.markdown('<div class="input-group">', unsafe_allow_html=True)
st.markdown('<div class="input-label"><span class="icon">🕐</span> Quand partez-vous ?</div>', unsafe_allow_html=True)
st.markdown('<div class="input-content">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Date", datetime.now(), label_visibility="collapsed")
with col2:
    time = st.time_input("Heure", datetime.now().time(), label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Section Départ
st.markdown('<div class="input-group">', unsafe_allow_html=True)
st.markdown('<div class="input-label"><span class="icon">📍</span> Point de départ</div>', unsafe_allow_html=True)
st.markdown('<div class="input-content">', unsafe_allow_html=True)

# Champ de saisie d'adresse
pickup_address_input = st.text_input(
    "Adresse de départ",
    value="",
    placeholder="Ex: 350 5th Ave, New York, NY",
    label_visibility="collapsed",
    key="pickup_address_input"
)

# Bouton pour rechercher l'adresse
if st.button("🔍 Rechercher", key="search_pickup"):
    if pickup_address_input:
        lat, lon = get_coords_from_address(pickup_address_input)
        if lat and lon:
            st.session_state.pickup_lat = lat
            st.session_state.pickup_lon = lon
            st.success(f"✅ Adresse trouvée: {pickup_address_input}")
            st.rerun()
        else:
            st.error("❌ Adresse introuvable. Essayez d'être plus précis.")
    else:
        st.warning("⚠️ Veuillez entrer une adresse")

# Afficher l'adresse actuelle
current_pickup_address = get_address_from_coords(st.session_state.pickup_lat, st.session_state.pickup_lon)
st.caption(f"📍 Actuel: {current_pickup_address}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Section Destination
st.markdown('<div class="input-group">', unsafe_allow_html=True)
st.markdown('<div class="input-label"><span class="icon">🎯</span> Destination</div>', unsafe_allow_html=True)
st.markdown('<div class="input-content">', unsafe_allow_html=True)

# Champ de saisie d'adresse
dropoff_address_input = st.text_input(
    "Adresse de destination",
    value="",
    placeholder="Ex: Times Square, New York, NY",
    label_visibility="collapsed",
    key="dropoff_address_input"
)

# Bouton pour rechercher l'adresse
if st.button("🔍 Rechercher", key="search_dropoff"):
    if dropoff_address_input:
        lat, lon = get_coords_from_address(dropoff_address_input)
        if lat and lon:
            st.session_state.dropoff_lat = lat
            st.session_state.dropoff_lon = lon
            st.success(f"✅ Adresse trouvée: {dropoff_address_input}")
            st.rerun()
        else:
            st.error("❌ Adresse introuvable. Essayez d'être plus précis.")
    else:
        st.warning("⚠️ Veuillez entrer une adresse")

# Afficher l'adresse actuelle
current_dropoff_address = get_address_from_coords(st.session_state.dropoff_lat, st.session_state.dropoff_lon)
st.caption(f"🎯 Actuel: {current_dropoff_address}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Section Passagers
st.markdown('<div class="input-group">', unsafe_allow_html=True)
st.markdown('<div class="input-label"><span class="icon">👥</span> Nombre de passagers</div>', unsafe_allow_html=True)
st.markdown('<div class="input-content">', unsafe_allow_html=True)
passenger_count = st.select_slider(
    "Passagers",
    options=[1, 2, 3, 4, 5, 6, 7, 8],
    value=1,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Bouton de prédiction
predict_button = st.button("🚀 Calculer le prix", type="primary")

# Appel à l'API et affichage du résultat
if predict_button:
    # Utiliser les valeurs du session_state
    pickup_latitude = st.session_state.pickup_lat
    pickup_longitude = st.session_state.pickup_lon
    dropoff_latitude = st.session_state.dropoff_lat
    dropoff_longitude = st.session_state.dropoff_lon

    # Combiner date et heure
    pickup_datetime = f"{date} {time}"

    # Construction du dictionnaire de paramètres
    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count
    }

    # Appel à l'API
    url = 'https://taxifare.lewagon.ai/predict'

    with st.spinner("🔄 Calcul en cours..."):
        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                prediction = response.json()
                fare = prediction.get('fare', 0)

                # Affichage du prix moderne
                st.markdown(f"""
                    <div class="price-display">
                        <div class="price-label">Tarif estimé de votre course</div>
                        <div class="price-amount">${fare:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)

                # Obtenir les adresses pour l'affichage
                pickup_addr = get_address_from_coords(pickup_latitude, pickup_longitude)
                dropoff_addr = get_address_from_coords(dropoff_latitude, dropoff_longitude)

                # Détails de la course avec adresses
                st.markdown("""
                    <div class="route-info">
                        <div class="route-row">
                            <span class="route-label">📅 Date</span>
                            <span class="route-value">""" + date.strftime('%d/%m/%Y') + """</span>
                        </div>
                        <div class="route-row">
                            <span class="route-label">🕐 Heure</span>
                            <span class="route-value">""" + time.strftime('%H:%M') + """</span>
                        </div>
                        <div class="route-row">
                            <span class="route-label">📍 Départ</span>
                            <span class="route-value">""" + pickup_addr + """</span>
                        </div>
                        <div class="route-row">
                            <span class="route-label">🎯 Arrivée</span>
                            <span class="route-value">""" + dropoff_addr + """</span>
                        </div>
                        <div class="route-row">
                            <span class="route-label">👥 Passagers</span>
                            <span class="route-value">""" + str(passenger_count) + """</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ Erreur API (Code: {response.status_code})")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

# Footer
st.markdown("""
    <div class="app-footer">
        Made with ❤️ using Streamlit<br>
        <small>Powered by TaxiFare API</small>
    </div>
""", unsafe_allow_html=True)
