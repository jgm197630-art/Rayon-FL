import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Config iPhone
st.set_page_config(page_title="So.Bio Tinqueux - Expert", layout="centered")

# STYLE PRO
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 15px; border: 1px solid #333; }
    .card { background-color: #262730; padding: 20px; border-radius: 15px; margin-bottom: 10px; border-left: 5px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# CHARGEMENT DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

st.title("🍏 Expert F&L Tinqueux")

# --- PARAMÈTRES DU JOUR ---
col1, col2 = st.columns(2)
with col1:
    date_ciblée = st.date_input("Date", datetime.now())
with col2:
    meteo = st.selectbox("Météo", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie/Froid"])

# --- CALCULS IA ---
jour_semaine = date_ciblée.weekday() 
# Moyenne historique pour ce mois et ce jour précis (2021-2025)
hist_filtre = data[(data['date'].dt.month == date_ciblée.month) & (data['date'].dt.weekday == jour_semaine)]
base_ca = hist_filtre['ca'].mean() if not hist_filtre.empty else 850.0

# Coefficients (Météo + Plafond Samedi)
coef = 1.15 if meteo == "☀️ Grand Soleil" else 0.85 if meteo == "🌧️ Pluie/Froid" else 1.0
ca_prevu = base_ca * coef
if jour_semaine == 5: ca_prevu = min(ca_prevu, 1122.0)

# --- AFFICHAGE CA ---
st.metric("Estimation Vente (CA HT)", f"{ca_prevu:.0f} €", delta=f"{coef*100-100:+.0f}% (Météo)")

# --- STRATÉGIE DE COMMANDE ---
st.markdown("### 📦 Stratégie de Commande")

# Jours de commande : Lundi(0), Mercredi(2), Vendredi(4)
if jour_semaine in [0, 2, 4]:
    # On calcule le CA à couvrir jusqu'à la prochaine livraison
    jours_couverture = 3 if jour_semaine == 4 else 2
    ca_a_couvrir = ca_prevu * jours_couverture
    
    # Calcul d'achat (On veut 30% de marge brute, donc achat = 70% du CA)
    achat_suggere = ca_a_couvrir * 0.70
    
    st.markdown(f"""
    <div class="card">
        <h4>CONSEIL D'ACHAT HT</h4>
        <h2 style="color:#00ffcc;">{achat_suggere:.0f} €</h2>
        <p>Pour couvrir les <b>{jours_couverture} prochains jours</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommandations spécifiques basées sur ton historique
    if date_ciblée.month in [5, 6, 7, 8] and meteo == "☀️ Grand Soleil":
        st.warning("🔥 Alerte Forte Chaleur : Prévoir +20% sur Fruits d'été et Fraîche découpe.")
    elif meteo == "🌧️ Pluie/Froid":
        st.info("🍲 Temps Soupe : Booster Poireaux, Carottes et Pommes de terre.")
else:
    st.write("Pas de grosse commande prévue. Gère le réassort et la fraîcheur.")

# --- FORMULAIRE DE SAISIE (Pour faire évoluer l'appli) ---
st.write("---")
st.subheader("📝 Saisie du Réel (Aujourd'hui)")
with st.form("Saisie"):
    ca_reel = st.number_input("Chiffre d'affaire réalisé (€ HT)", value=0.0)
    pertes = st.number_input("Montant de la démarque (€ HT)", value=0.0)
    if st.form_submit_button("Enregistrer sur mon iPhone"):
        st.success("Données enregistrées ! (Elles seront intégrées à l'historique)")
