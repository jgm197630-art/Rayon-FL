import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# 1. CONFIGURATION PRO IPHONE
st.set_page_config(page_title="Pilotage F&L Tinqueux", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Contraste maximum pour les indicateurs */
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

# --- BARRE LATÉRALE : SAISIE ET RÉGLAGES ---
with st.sidebar:
    st.header("📝 Saisie du jour")
    ca_j = st.number_input("CA HT du jour (€)", value=0.0, format="%.2f")
    casse_j = st.number_input("Casse HT du jour (€)", value=0.0, format="%.2f")
    
    st.write("---")
    st.header("⚙️ Paramètres")
    jours_cde = st.multiselect("Jours de commande :", 
                              ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"],
                              default=["Lundi", "Mercredi", "Vendredi"])

# --- FILTRES DU TABLEAU DE BORD ---
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    d_cible = st.date_input("Consulter le calendrier", datetime.now())
with col_f2:
    meteo = st.selectbox("Météo prévue", ["☀️ Soleil", "⛅ Variable", "🌧️ Pluie"])

# --- CALCULS DE PERFORMANCE (COHÉRENT TABLEAUX) ---
st.markdown("<p class='section-title'>📊 Résultats de la Semaine (Lundi au jour choisi)</p>", unsafe_allow_html=True)

# Définition de la période (Lundi au d_cible)
lundi_semaine = d_cible - timedelta(days=d_cible.weekday())
mask_sem = (data['date'].dt.date >= lundi_semaine) & (data['date'].dt.date <= d_cible)
df_sem = data[mask_sem]

# On ajoute la saisie du jour si on est sur la date d'aujourd'hui
vente_sem = df_sem['ca'].sum()
if d_cible == date.today() and ca_j > 0:
    vente_sem += ca_j

# FORMULES RATIOS (TABLEAUX DE BORD)
achat_pct = 0.71 # Ton ratio achat de 71%
inconnue_pct = 0.043 # Tes 4.3% fixes

total_achat = vente_sem * achat_pct
total_casse = casse_j if (d_cible == date.today() and casse_j > 0) else (vente_sem * 0.07) # 7% est. si pas saisi
total_inconnue = vente_sem * inconnue_pct
marge_nette = vente_sem - total_achat - total_casse - total_inconnue

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventes Semaine", f"{vente_sem:.0f} €")
c2.metric("Achats HT (est.)", f"{total_achat:.0f} €")
c3.metric("Casse (Total)", f"{(total_casse + total_inconnue):.0f} €")
m_color = "normal" if marge_nette > 0 else "inverse"
c4.metric("Marge Nette", f"{marge_nette:.0f} €", f"{(marge_nette/vente_sem*100 if vente_sem>0 else 0):.1f}%", delta_color=m_color)

# --- AIDE À LA COMMANDE (LOGIQUE DYNAMIQUE) ---
nom_jour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][d_cible.weekday()]

if nom_jour in jours_cde:
    st.markdown("---")
    st.markdown("<p class='section-title'>📦 Ta Commande</p>", unsafe_allow_html=True)
    
    # 1. Estimation CA
    hist_j = data[(data['date'].dt.month == d_cible.month) & (data['date'].dt.weekday == d_cible.weekday())]
    base_ca = hist_j['ca'].mean() if not hist_j.empty else 850.0
    
    # Ajustement météo + Tendance (si saisie hier)
    coef = 1.15 if meteo == "☀️ Soleil" else 0.85 if meteo == "🌧️ Pluie" else 1.0
    ca_prevu = base_ca * coef
    
    # 2. Slider juste au dessus
    nb_j = st.select_slider("Nombre de jours que la livraison doit couvrir :", options=[1, 2, 3, 4, 5], value=2)
    
    # 3. Calcul Commande
    montant_cde = (ca_prevu * nb_j) * 0.70 # On vise 30% de marge brute à l'achat
    
    st.markdown(f"""
        <div class="commande-box">
            <div style="display:flex; justify-content: space-between; align-items: center;">
                <div>
                    <small style="opacity:0.8;">PRÉVISION VENTE JOUR</small>
                    <h2 style="color:white; margin:0;">{ca_prevu:.0f} € HT</h2>
                </div>
                <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.3); padding-left: 20px;">
                    <small style="opacity:0.8;">MONTANT À COMMANDER HT</small>
                    <h1 style="color:white; margin:0; font-size:3.5em;">{montant_cde:.0f} €</h1>
                    <small>Couverture : {nb_j} jours</small>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"Pas de commande prévue aujourd'hui ({nom_jour}). Utilise le calendrier pour préparer une autre date.")

# --- HISTORIQUE DÉTAILLÉ ---
with st.expander("🔍 Voir les archives de ce jour"):
    if not hist_j.empty:
        st.write(f"Basé sur {len(hist_j)} années d'historique (2021-2025)")
        st.dataframe(hist_j[['date', 'ca']].sort_values('date', ascending=False), hide_index=True)
