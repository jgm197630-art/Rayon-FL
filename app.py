import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Configuration iPhone
st.set_page_config(page_title="So.Bio Tinqueux", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button { width: 100%; border-radius: 15px; height: 3em; background-color: #00ffcc; color: black; font-weight: bold; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 15px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    df = pd.read_csv("data_historique.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    data = load_data()
except:
    data = pd.DataFrame(columns=['date', 'ca'])

# --- LOGIQUE DE PRÉVISION ---
st.title("🍏 So.Bio Tinqueux")
st.write(f"Pilotage Rayon F&L - iPhone 17 Edition")

# Sélection de la date (Aujourd'hui par défaut)
date_target = st.date_input("Prévision pour le :", datetime.now())
jour_semaine = date_target.weekday() # 0=Lundi, 5=Samedi

# Calcul de la moyenne historique pour ce jour précis
month = date_target.month
weekday = date_target.weekday()
historique_jour = data[(data['date'].dt.month == month) & (data['date'].dt.weekday == weekday)]

if not historique_jour.empty:
    base_ca = historique_jour['ca'].mean()
else:
    base_ca = 800.0 # Valeur par défaut si pas de données

# --- INTERFACE ---
col1, col2 = st.columns(2)
with col1:
    meteo = st.selectbox("Météo prévue", ["☀️ Beau temps", "⛅ Variable", "🌧️ Pluie / Froid"])

# Ajustement
coef = 1.0
if meteo == "☀️ Beau temps": coef = 1.15
if meteo == "🌧️ Pluie / Froid": coef = 0.88

estimation = base_ca * coef

# Application du plafond de 1122€ pour le samedi (ta règle d'or)
if jour_semaine == 5:
    estimation = min(estimation, 1122.0)
    st.info("⚠️ Plafond historique du samedi (1122€) appliqué.")

# --- AFFICHAGE ---
st.metric("Estimation Chiffre d'Affaire", f"{estimation:.2f} € HT")

# --- CONSEIL COMMANDE ---
st.write("---")
st.subheader("📦 Aide à la Commande")

# Jours de commande : Lundi (0), Mercredi (2), Vendredi (4)
if jour_semaine in [0, 2, 4]:
    st.success("C'est un jour de commande !")
    # On prévoit pour les 2 ou 3 prochains jours
    jours_a_couvrir = 3 if jour_semaine == 4 else 2
    total_commande = estimation * jours_a_couvrir * 0.7 # 0.7 car on a déjà du stock
    st.write(f"Estimation besoin de stock : **{total_commande:.0f} € HT**")
    st.caption("Basé sur ton historique 2021-2025 et la météo.")
else:
    st.write("Pas de grosse commande prévue aujourd'hui.")

# --- GRAPHIQUE DE PERFORMANCE ---
if not data.empty:
    st.write("---")
    st.write("### Tendance des 30 derniers jours")
    recent_data = data.tail(30)
    fig = px.line(recent_data, x='date', y='ca', title="Evolution CA HT")
    fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
