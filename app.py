
import streamlit as st
import pandas as pd
from datetime import datetime, date

# Config iPhone
st.set_page_config(page_title="So.Bio Tinqueux - Assistant F&L", layout="centered")

# STYLE CHALEUREUX ET PRO
st.markdown("""
    <style>
    .main { background-color: #fdfaf6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #4CAF50; }
    .card { background-color: #e8f5e9; padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #c8e6c9; color: #2e7d32; }
    .conseil-box { background-color: #fff3e0; padding: 15px; border-radius: 15px; border-left: 5px solid #ff9800; color: #e65100; font-size: 0.9em; }
    h1, h2, h3 { color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# FONCTION VACANCES ZONE B (Simplifiée pour 2025/2026)
def est_vacances_zone_b(d):
    # Noël 2025 : jusqu'au 5 Janvier
    # Hiver 2026 : 7 Février au 23 Février
    # Printemps 2026 : 4 Avril au 20 Avril
    if date(2025, 12, 20) <= d <= date(2026, 1, 5): return True
    if date(2026, 2, 7) <= d <= date(2026, 2, 23): return True
    if date(2026, 4, 4) <= d <= date(2026, 4, 20): return True
    return False

# CHARGEMENT DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    except:
        return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

st.title("🍏 Salut ! Prêt pour Tinqueux ?")
st.write(f"Aujourd'hui, nous sommes le **{datetime.now().strftime('%d/%m/%Y')}**")

# --- PARAMÈTRES ---
with st.expander("⚙️ Ajuster le contexte du jour", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        d_cible = st.date_input("Date ciblée", datetime.now())
    with col2:
        meteo = st.selectbox("Météo prévue", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie / Froid"])

# --- CALCUL IA ---
est_vac = est_vacances_zone_b(d_cible)
jour_sem = d_cible.weekday()

# Moyenne historique
hist_filtre = data[(pd.to_datetime(data['date']).dt.month == d_cible.month) & (pd.to_datetime(data['date']).dt.weekday == jour_sem)]
base_ca = hist_filtre['ca'].mean() if not hist_filtre.empty else 850.0

# Coefficients
coef = 1.0
if meteo == "☀️ Grand Soleil": coef += 0.15
if meteo == "🌧️ Pluie / Froid": coef -= 0.15
if est_vac: coef += 0.10  # On vend souvent un peu plus en F&L quand les gens sont à la maison

ca_prevu = base_ca * coef
if jour_sem == 5: ca_prevu = min(ca_prevu, 1122.0) # Ton plafond du Samedi

# --- AFFICHAGE ---
st.subheader("📈 Ton estimation de vente")
st.metric("Potentiel CA HT", f"{ca_prevu:.0f} €", delta=f"{'Vacances Zone B' if est_vac else 'Période scolaire'}")

# --- STRATÉGIE DE COMMANDE ---
st.markdown("---")
st.subheader("📦 Aide à la commande")
st.info("Pousse le curseur selon le nombre de jours que ta livraison doit tenir (ex: jours fériés).")
nb_jours = st.slider("Nombre de jours à couvrir", 1, 5, 2)

ca_total = ca_prevu * nb_jours
achat_ht = ca_total * 0.70 # Objectif 30% de marge

st.markdown(f"""
    <div class="card">
        <p style="margin-bottom:5px;">Montant conseillé à commander :</p>
        <h2 style="margin:0;">{achat_ht:.0f} € HT</h2>
        <p style="font-size:0.8em; margin-top:5px;">Basé sur un CA total prévu de {ca_total:.0f}€ sur {nb_jours} jours.</p>
    </div>
    """, unsafe_allow_html=True)

# --- SAISONNALITÉ & CONSEILS ---
st.subheader("🍊 Le conseil de saison")
mois = d_cible.month
if mois == 12 or mois == 1:
    st.markdown("""
    <div class="conseil-box">
        <b>Focus Janvier :</b><br>
        • C'est le plein boom des <b>agrumes</b> (Clémentine de Corse, Oranges).<br>
        • Surveille tes stocks de <b>Litchis</b> et <b>Ananas</b> (fin de fêtes).<br>
        • Côté légumes : Pot-au-feu en avant ! (Poireaux, Carottes, Navets).
    </div>
    """, unsafe_allow_html=True)
elif 5 <= mois <= 8:
    st.markdown("<div class='conseil-box'><b>Focus Été :</b> Attention à la casse sur les pêches/nectarines si grand soleil !</div>", unsafe_allow_html=True)

# --- SAISIE DU SOIR ---
st.markdown("---")
with st.expander("📝 Noter mes chiffres du soir"):
    ca_r = st.number_input("CA Réalisé (€)", value=0.0)
    st.button("Enregistrer sur mon iPhone")
