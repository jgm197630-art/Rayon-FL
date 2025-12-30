import streamlit as st
import pandas as pd
from datetime import datetime, date
import numpy as np

# CONFIGURATION PRO
st.set_page_config(page_title="So.Bio Expert F&L", layout="wide")

# STYLE DESIGN (TEXTE NOIR LISIBLE)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { color: #1b5e20 !important; font-size: 2.5em !important; font-weight: 800; }
    [data-testid="stMetricLabel"] { color: #333333 !important; font-size: 1.1em !important; }
    .stMetric { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #eee; }
    .commande-card { background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%); color: white; padding: 30px; border-radius: 25px; }
    .saison-card { background-color: #fff3e0; border-left: 8px solid #ff9800; padding: 20px; border-radius: 15px; color: #5d4037; }
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

# HEADER
st.image("https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
st.title("🍏 Expert F&L Tinqueux")

# PARAMÈTRES
col_date, col_meteo, col_jours = st.columns([2,2,2])
with col_date:
    d_cible = st.date_input("Date de prévision", datetime.now())
with col_meteo:
    meteo = st.selectbox("Météo Reims", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie / Froid"])
with col_jours:
    nb_jours = st.slider("Jours à couvrir", 1, 5, 2)

# CALCULS PRÉCIS (Moyenne 5 ans)
jour_sem = d_cible.weekday()
mois_cible = d_cible.month
hist_filtre = data[(data['date'].dt.month == mois_cible) & (data['date'].dt.weekday == jour_sem)]

if not hist_filtre.empty:
    base_ca = hist_filtre['ca'].mean()
    std_dev = hist_filtre['ca'].std() if len(hist_filtre) > 1 else base_ca * 0.1
    erreur_p = (std_dev / base_ca) * 100
else:
    base_ca, erreur_p = 850.0, 15.0

coef = 1.15 if meteo == "☀️ Grand Soleil" else 0.85 if meteo == "🌧️ Pluie / Froid" else 1.0
ca_final = base_ca * coef
if jour_sem == 5: ca_final = min(ca_final, 1122.0)

# AFFICHAGE
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 📈 Vente Estimée")
    st.metric("POTENTIEL CA HT", f"{ca_final:.0f} €", f"± {erreur_p:.1f}% précision")
    st.progress(max(0, min(100, int(100-erreur_p)))/100, text="Indice de confiance")

with c2:
    st.markdown("#### 📦 Ta Commande")
    achat_ht = (ca_final * nb_jours) * 0.70
    st.markdown(f"""
        <div class="commande-card">
            <p style="margin:0; opacity:0.8; color:white;">MONTANT CONSEILLÉ (HT)</p>
            <h1 style="color:white; margin:10px 0; font-size:3.5em;">{achat_ht:.0f} €</h1>
            <p style="margin:0; font-size:0.9em;">🎯 Couverture de {nb_jours} jours</p>
        </div>
    """, unsafe_allow_html=True)

# SAISONNALITÉ
st.markdown("---")
st.markdown(f"""
    <div class="saison-card">
        <b>💡 Le conseil de l'Expert :</b><br>
        Pour le mois de {d_cible.strftime('%B')}, surveille tes stocks de saison. 
        Avec une météo {meteo}, les clients de Tinqueux privilégient les produits de {'fraîcheur' if 'Soleil' in meteo else 'confort (soupes/plats chauds)'}.
    </div>
""", unsafe_allow_html=True)


