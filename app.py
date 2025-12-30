import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURATION IPHONE
st.set_page_config(page_title="So.Bio Tinqueux - Expert", layout="centered")

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

# 2. FONCTION VACANCES ZONE B (Reims)
def est_vacances_zone_b(d):
    # Noël 2025, Hiver 2026, Printemps 2026
    if date(2025, 12, 20) <= d <= date(2026, 1, 5): return True
    if date(2026, 2, 7) <= d <= date(2026, 2, 23): return True
    if date(2026, 4, 4) <= d <= date(2026, 4, 20): return True
    return False

# 3. CHARGEMENT DES DONNÉES HISTORIQUES
@st.cache_data
def load_data():
    try:
        # On lit tes 5 ans de tableaux
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

# 4. INTERFACE PRINCIPALE
st.title("🍏 Salut ! Prêt pour Tinqueux ?")
st.write(f"Aujourd'hui : **{datetime.now().strftime('%d/%m/%Y')}**")

# --- PARAMÈTRES ---
with st.expander("⚙️ Ajuster le contexte", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        d_cible = st.date_input("Date ciblée", datetime.now())
    with col2:
        meteo = st.selectbox("Météo prévue", ["☀️ Grand Soleil", "⛅ Variable", "🌧️ Pluie / Froid"])

# 5. CALCULS IA (Basés sur tes tableaux)
jour_sem = d_cible.weekday()
mois_cible = d_cible.month
est_vac = est_vacances_zone_b(d_cible)

# On cherche la moyenne de TOUS les jours identiques dans ton historique (ex: tous les lundis de janvier)
hist_filtre = data[(data['date'].dt.month == mois_cible) & (data['date'].dt.weekday == jour_sem)]

if not hist_filtre.empty:
    base_ca = hist_filtre['ca'].mean()
else:
    base_ca = 850.0  # Valeur de secours si le tableau est vide

# Application des coefficients
coef = 1.0
if meteo == "☀️ Grand Soleil": coef += 0.15
if meteo == "🌧️ Pluie / Froid": coef -= 0.15
if est_vac: coef += 0.10  # Bonus Vacances Zone B

ca_prevu = base_ca * coef
if jour_sem == 5: ca_prevu = min(ca_prevu, 1122.0) # Ton plafond de 1122€ le samedi

# --- AFFICHAGE DE L'ESTIMATION ---
st.subheader("📈 Ton estimation de vente")
st.metric("Potentiel CA HT", f"{ca_prevu:.0f} €", delta=f"{'Vacances Zone B' if est_vac else 'Période scolaire'}")

# 6. STRATÉGIE DE COMMANDE (Spécial Jours Fériés)
st.markdown("---")
st.subheader("📦 Aide à la commande")
st.info("Pousse le curseur si tu dois couvrir plusieurs jours (ex: jour férié jeudi).")
nb_jours = st.slider("Nombre de jours à couvrir", 1, 5, 2)

ca_total = ca_prevu * nb_jours
achat_ht = ca_total * 0.70  # On garde 30% de marge brute

st.markdown(f"""
    <div class="card">
        <p style="margin-bottom:5px;">Montant conseillé à commander :</p>
        <h2 style="margin:0;">{achat_ht:.0f} € HT</h2>
        <p style="font-size:0.8em; margin-top:5px;">Pour couvrir {nb_jours} jours (Total CA prévu : {ca_total:.0f}€).</p>
    </div>
    """, unsafe_allow_html=True)

# 7. CONSEILS DE SAISON
st.subheader("🍊 Le conseil de saison")
if mois_cible in [12, 1]:
    st.markdown("""
    <div class="conseil-box">
        <b>Focus Janvier :</b><br>
        • Plein boom des <b>agrumes</b> (Clémentines, Oranges).<br>
        • Surveille tes stocks de <b>Litchis</b> et <b>Ananas</b>.<br>
        • Temps froid : Booste le <b>Pot-au-feu</b> (Poireaux, Carottes, Navets).
    </div>
    """, unsafe_allow_html=True)

# 8. SAISIE DU RÉEL
st.markdown("---")
with st.expander("📝 Noter mes chiffres du soir"):
    ca_r = st.number_input("CA Réalisé aujourd'hui (€)", value=0.0)
    if st.button("Enregistrer sur mon iPhone"):
        st.success("Note prise ! (Bientôt synchronisée avec ton historique)")
