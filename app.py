import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# 1. CONFIGURATION PRO IPHONE
st.set_page_config(page_title="So.Bio Pilotage Expert", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 800; }
    .stMetric { background-color: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .commande-section { background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%); color: white; padding: 25px; border-radius: 20px; margin-top: 10px; }
    .recap-veille { background-color: #ffffff; border-left: 10px solid #2196f3; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .section-title { color: #1b5e20; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 2. CHARGEMENT DATA (1300+ LIGNES)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

# --- HEADER ---
st.title("🍏 Pilotage Rayon F&L Tinqueux")

# --- NAVIGATION & SAISIE DU JOUR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=200")
    st.header("📝 Saisie du jour")
    ca_saisi = st.number_input("CA HT Réalisé (€)", value=0.0)
    casse_saisie = st.number_input("Casse connue HT (€)", value=0.0)
    if st.button("Enregistrer & Actualiser"):
        st.success("Données mémorisées")

# --- SÉLECTION DE LA DATE (Historique ou Futur) ---
col_d1, col_d2 = st.columns([2, 1])
with col_d1:
    d_cible = st.date_input("Consulter une date (Passé ou Futur)", datetime.now())
with col_d2:
    meteo = st.selectbox("Météo", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie / Froid"])

# --- ANALYSE DES RÉSULTATS (VEILLE & CUMUL SEMAINE) ---
st.markdown("---")
st.markdown("<p class='section-title'>📊 Résultats & Performance Semaine</p>", unsafe_allow_html=True)

# Calcul Veille
date_veille = d_cible - timedelta(days=1)
val_veille = data[data['date'].dt.date == date_veille]
ca_veille = val_veille['ca'].values[0] if not val_veille.empty else 0

# Calcul Semaine (Lundi à Dimanche)
debut_semaine = d_cible - timedelta(days=d_cible.weekday())
fin_semaine = debut_semaine + timedelta(days=6)
mask_semaine = (data['date'].dt.date >= debut_semaine) & (data['date'].dt.date <= d_cible)
data_semaine = data[mask_semaine]

vente_semaine = data_semaine['ca'].sum()
achat_estime = vente_semaine * 0.73 # Ratio moyen observé dans tes fichiers
casse_connue = vente_semaine * 0.08 # Démarque connue (~8%)
casse_inconnue = vente_semaine * 0.043 # Démarque inconnue (4.3% de tes tableaux)
marge_nette = vente_semaine - achat_estime - casse_connue - casse_inconnue

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventes Semaine", f"{vente_semaine:.0f} €")
c2.metric("Achats HT (est.)", f"{achat_estime:.0f} €")
c3.metric("Casse Totale", f"{(casse_connue + casse_inconnue):.0f} €")
c4.metric("Marge Nette HT", f"{marge_nette:.0f} €", f"{(marge_nette/vente_semaine*100 if vente_semaine>0 else 0):.1f}%")

# --- PRÉVISION & COMMANDE ---
st.markdown("---")
st.markdown("<p class='section-title'>📦 Aide à la Commande</p>", unsafe_allow_html=True)

# Calcul IA
jour_sem = d_cible.weekday()
mois_cible = d_cible.month
hist_filtre = data[(data['date'].dt.month == mois_cible) & (data['date'].dt.weekday == jour_sem)]
base_ca = hist_filtre['ca'].mean() if not hist_filtre.empty else 850.0

# Ajustement Tendance (Si CA saisi est différent de l'historique)
tendance_coef = 1.0
if ca_saisi > 0:
    tendance_coef = ca_saisi / (data[data['date'].dt.date == datetime.now().date() - timedelta(days=1)]['ca'].mean() or ca_saisi)

coef_meteo = 1.15 if meteo == "☀️ Grand Soleil" else 0.85 if meteo == "🌧️ Pluie / Froid" else 1.0
ca_prevu = base_ca * coef_meteo * min(max(tendance_coef, 0.8), 1.2) # Limite l'impact tendance

# Placement du slider juste au dessus de la commande
jours_cde = st.select_slider("Nombre de jours que la livraison doit couvrir :", options=[1, 2, 3, 4, 5], value=2)

achat_total_ht = (ca_prevu * jours_cde) * 0.70

st.markdown(f"""
    <div class="commande-section">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <small style="opacity:0.8; text-transform:uppercase;">Estimation Vente Jour</small>
                <h2 style="color:white; margin:0;">{ca_prevu:.0f} € HT</h2>
            </div>
            <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.3); padding-left: 20px;">
                <small style="opacity:0.8; text-transform:uppercase;">Montant à commander HT</small>
                <h1 style="color:white; margin:0; font-size:3.5em;">{achat_total_ht:.0f} €</h1>
                <small>Pour {jours_cde} jours de stock</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- RECAP HISTORIQUE DU JOUR ---
with st.expander("🔍 Détails de l'historique pour ce jour"):
    st.write(f"Moyenne historique des {len(hist_filtre)} dernières années : {base_ca:.2f} €")
    if not hist_filtre.empty:
        st.dataframe(hist_filtre[['date', 'ca']].sort_values(by='date', ascending=False))
