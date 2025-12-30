import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURATION IPHONE
st.set_page_config(page_title="So.Bio Tinqueux - Expert", layout="centered")

# STYLE CORRIGÉ (TEXTE NOIR LISIBLE)
st.markdown("""
    <style>
    .main { background-color: #fdfaf6; }
    /* Force le texte des métriques en noir pour la lisibilité */
    [data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #333333 !important; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #ddd; }
    .card { background-color: #e8f5e9; padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #c8e6c9; color: #2e7d32; }
    .conseil-box { background-color: #fff3e0; padding: 15px; border-radius: 15px; border-left: 5px solid #ff9800; color: #e65100; font-size: 0.9em; }
    h1, h2, h3 { color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# 2. FONCTION VACANCES ZONE B (Reims)
def est_vacances_zone_b(d):
    if date(2025, 12, 20) <= d <= date(2026, 1, 5): return True
    if date(2026, 2, 7) <= d <= date(2026, 2, 23): return True
    if date(2026, 4, 4) <= d <= date(2026, 4, 20): return True
    return False

# 3. CHARGEMENT DATA
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

# --- PARAMÈTRES ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        d_cible = st.date_input("Date choisie", datetime.now())
    with col2:
        meteo = st.selectbox("Météo", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie / Froid"])

# --- CALCULS ---
jour_sem = d_cible.weekday()
mois_cible = d_cible.month
est_vac = est_vacances_zone_b(d_cible)

hist_filtre = data[(data['date'].dt.month == mois_cible) & (data['date'].dt.weekday == jour_sem)]
base_ca = hist_filtre['ca'].mean() if not hist_filtre.empty else 850.0

coef = 1.0
if meteo == "☀️ Grand Soleil": coef += 0.15
if meteo == "🌧️ Pluie / Froid": coef -= 0.15
if est_vac: coef += 0.10

ca_prevu = base_ca * coef
if jour_sem == 5: ca_prevu = min(ca_prevu, 1122.0)

# --- AFFICHAGE ULTRA LISIBLE ---
st.subheader("📈 Estimation de vente")
st.metric("CA PRÉVU HT", f"{ca_prevu:.0f} €", delta=f"{'Vacances' if est_vac else 'Scolaire'}")

# --- STRATÉGIE COMMANDE ---
st.markdown("---")
st.subheader("📦 Conseil d'achat")
nb_jours = st.slider("Jours à couvrir", 1, 5, 2)
ca_total = ca_prevu * nb_jours
achat_ht = ca_total * 0.70

st.markdown(f"""
    <div class="card">
        <p style="margin:0; font-size:1em;">MONTANT À COMMANDER :</p>
        <h1 style="margin:0; color:#1b5e20; font-size:2.5em;">{achat_ht:.0f} € HT</h1>
        <p style="margin:0; font-size:0.8em;">(Basé sur {ca_total:.0f}€ de CA sur {nb_jours} jours)</p>
    </div>
    """, unsafe_allow_html=True)

# CONSEIL SAISON
if mois_cible in [12, 1]:
    st.info("💡 **Focus :** Plein boom des agrumes & Pot-au-feu !")

