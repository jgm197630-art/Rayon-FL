import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# 1. CONFIGURATION PRO IPHONE
st.set_page_config(page_title="Pilotage F&L Tinqueux", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Contraste maximum pour les indicateurs en Noir */
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 800 !important; font-size: 2.2em !important; }
    [data-testid="stMetricLabel"] { color: #444444 !important; font-size: 1em !important; font-weight: bold !important; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #ddd; }
    
    .commande-box { background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%); color: white; padding: 25px; border-radius: 20px; border: 2px solid #000; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    .section-title { color: #1b5e20; font-weight: bold; font-size: 1.2em; border-bottom: 2px solid #1b5e20; margin-bottom: 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 2. CHARGEMENT DATA (2021 - 29/12/2025)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except: return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

st.title("🍏 Pilotage Expert So.Bio")

# --- 1. CONFIGURATION COMMANDE ---
st.markdown("<p class='section-title'>⚙️ Configuration Commande</p>", unsafe_allow_html=True)
c_cde1, c_cde2 = st.columns(2)
with c_cde1:
    jours_cde_selection = st.multiselect("Mes jours de commande :", 
                                     ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"],
                                     default=["Lundi", "Mercredi", "Vendredi"])
with c_cde2:
    d_cible = st.date_input("Consulter la date du :", datetime.now())
    meteo = st.selectbox("Météo prévue", ["☀️ Soleil", "⛅ Variable", "🌧️ Pluie"])

# --- 2. SAISIE RÉELLE (BARRE LATÉRALE) ---
with st.sidebar:
    st.header("📝 Saisie Flash")
    ca_j = st.number_input("CA HT du jour (€)", value=0.0, format="%.2f")
    casse_j = st.number_input("Casse HT du jour (€)", value=0.0, format="%.2f")
    st.info("La saisie met à jour les indicateurs de la semaine en temps réel.")

# --- 3. RÉSULTATS DE LA SEMAINE (RATIOS TABLEAUX) ---
st.markdown("<p class='section-title'>📊 Ma Performance (Semaine en cours)</p>", unsafe_allow_html=True)

# Calcul du cumul du Lundi au jour choisi
lundi_semaine = d_cible - timedelta(days=d_cible.weekday())
mask_sem = (data['date'].dt.date >= lundi_semaine) & (data['date'].dt.date <= d_cible)
df_sem = data[mask_sem]

vente_sem = df_sem['ca'].sum()
# Ajout de la saisie si on consulte la date du jour
if d_cible == date.today() and ca_j > 0:
    vente_sem += ca_j

# Ratios extraits de tes tableaux (71% achat, 4.3% inconnue)
total_achat = vente_sem * 0.71
total_inconnue = vente_sem * 0.043
# Casse connue : saisie ou 7% estimé
total_connue = casse_j if (d_cible == date.today() and casse_j > 0) else (vente_sem * 0.07)
marge_nette = vente_sem - total_achat - total_connue - total_inconnue

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventes HT", f"{vente_sem:.0f} €")
col2.metric("Achats HT (est.)", f"{total_achat:.0f} €")
col3.metric("Casse Totale", f"{(total_connue + total_inconnue):.0f} €")
col4.metric("Marge Nette", f"{marge_nette:.0f} €", f"{(marge_nette/vente_sem*100 if vente_sem>0 else 0):.1f}%")

# --- 4. AIDE À LA COMMANDE DYNAMIQUE ---
nom_jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][d_cible.weekday()]

if nom_jour in jours_cde_selection:
    st.markdown("---")
    st.markdown("<p class='section-title'>📦 Ta Commande</p>", unsafe_allow_html=True)
    
    # Moyenne historique du jour/mois précis sur 4 ans
    hist_j = data[(data['date'].dt.month == d_cible.month) & (data['date'].dt.weekday == d_cible.weekday())]
    base_ca = hist_j['ca'].mean() if not hist_j.empty else 850.0
    
    coef = 1.15 if meteo == "☀️ Soleil" else 0.85 if meteo == "🌧️ Pluie" else 1.0
    ca_prevu = base_ca * coef
    
    # Slider juste au dessus du bloc de commande
    nb_j = st.select_slider("Couverture de la commande (nombre de jours) :", options=[1, 2, 3, 4, 5], value=2)
    montant_cde = (ca_prevu * nb_j) * 0.70
    
    st.markdown(f"""
        <div class="commande-box">
            <div style="display:flex; justify-content: space-between; align-items: center;">
                <div>
                    <small style="opacity:0.8;">ESTIMATION VENTE DU JOUR</small>
                    <h2 style="color:white; margin:0;">{ca_prevu:.0f} € HT</h2>
                </div>
                <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.3); padding-left: 20px;">
                    <small style="opacity:0.8;">MONTANT À COMMANDER (HT)</small>
                    <h1 style="color:white; margin:0; font-size:3.5em;">{montant_cde:.0f} €</h1>
                    <small>Pour tenir {nb_j} jours de vente</small>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"Pas de commande prévue aujourd'hui ({nom_jour}) selon tes réglages.")
