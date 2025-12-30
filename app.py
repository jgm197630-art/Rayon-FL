import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# CONFIG PRO IPHONE
st.set_page_config(page_title="So.Bio Expert", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 800 !important; }
    .stMetric { background-color: white; padding: 15px; border-radius: 15px; border: 1px solid #eee; }
    .commande-section { background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%); color: white; padding: 25px; border-radius: 20px; border: 2px solid #000; }
    .section-title { color: #1b5e20; font-weight: bold; font-size: 1.1em; border-bottom: 2px solid #1b5e20; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# CHARGEMENT DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except: return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

st.title("🍏 Pilotage Rayon Tinqueux")

# --- 1. CONFIGURATION DES JOURS DE COMMANDE ---
st.markdown("<p class='section-title'>⚙️ Configuration Commande</p>", unsafe_allow_html=True)
c_cde1, c_cde2 = st.columns(2)
with c_cde1:
    jours_cde_choisis = st.multiselect("Mes jours de commande :", 
                                     ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"],
                                     default=["Lundi", "Mercredi", "Vendredi"])
with c_cde2:
    d_cible = st.date_input("Date consultée", datetime.now())
    meteo = st.selectbox("Météo", ["☀️ Soleil", "⛅ Variable", "🌧️ Pluie"])

# --- 2. SAISIE RÉELLE ---
with st.sidebar:
    st.header("📝 Saisie du jour")
    ca_realise = st.number_input("Ton CA réalisé (€ HT)", value=0.0)
    casse_reelle = st.number_input("Ta Casse connue (€ HT)", value=0.0)
    st.info("Ces chiffres corrigent les indicateurs de la semaine ci-dessous.")

# --- 3. RÉSULTATS DE LA SEMAINE (COHÉRENT TABLEAUX) ---
st.markdown("<p class='section-title'>📊 Ma Semaine (Lundi au jour choisi)</p>", unsafe_allow_html=True)

# Calcul dynamique basé sur saisie ou historique
debut_sem = d_cible - timedelta(days=d_cible.weekday())
mask = (data['date'].dt.date >= debut_sem) & (data['date'].dt.date <= d_cible)
historique_semaine = data[mask]['ca'].sum()

# On utilise le CA saisi en priorité, sinon l'historique
ca_total_semaine = ca_realise if ca_realise > 0 else historique_semaine
achat_ht = ca_total_semaine * 0.71 # Ton ratio moyen d'achat
demarque_connue = casse_reelle if casse_reelle > 0 else (ca_total_semaine * 0.06)
demarque_inconnue = ca_total_semaine * 0.043 # Ton chiffre exact
marge_nette = ca_total_semaine - achat_ht - demarque_connue - demarque_inconnue

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vente Semaine", f"{ca_total_semaine:.0f} €")
col2.metric("Achats (est.)", f"{achat_ht:.0f} €")
col3.metric("Casse Totale", f"{(demarque_connue + demarque_inconnue):.0f} €")
col4.metric("Marge Nette", f"{marge_nette:.0f} €", f"{(marge_nette/ca_total_semaine*100 if ca_total_semaine>0 else 0):.1f}%")

# --- 4. COMMANDE (APPAREIT UNIQUEMENT LES JOURS DE CDE) ---
nom_jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][d_cible.weekday()]

if nom_jour in jours_cde_choisis:
    st.markdown("---")
    st.markdown("<p class='section-title'>📦 Ta Commande</p>", unsafe_allow_html=True)
    nb_j = st.slider("Nombre de jours à couvrir", 1, 4, 2)
    
    # Calcul prévision
    hist_jour = data[(data['date'].dt.month == d_cible.month) & (data['date'].dt.weekday == d_cible.weekday())]
    base_ca = hist_jour['ca'].mean() if not hist_jour.empty else 850.0
    coef_m = 1.15 if meteo == "☀️ Soleil" else 0.85 if meteo == "🌧️ Pluie" else 1.0
    ca_prevu = base_ca * coef_m
    
    montant_cde = (ca_prevu * nb_j) * 0.70
    
    st.markdown(f"""
        <div class="commande-section">
            <small style="opacity:0.8;">C'est un jour de commande ({nom_jour})</small>
            <div style="display:flex; justify-content: space-between; align-items: center;">
                <h2 style="color:white; margin:0;">Vente prévue : {ca_prevu:.0f}€</h2>
                <h1 style="color:white; margin:0; font-size:3.5em;">CDE HT : {montant_cde:.0f} €</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning(f"Aujourd'hui ({nom_jour}) n'est pas un jour de commande selon tes réglages.")
