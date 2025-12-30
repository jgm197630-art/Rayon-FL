import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# CONFIGURATION INTERFACE NOIR & VERT (LISIBLE)
st.set_page_config(page_title="So.Bio - Données Réelles", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #1b5e20 !important; font-weight: bold; }
    .commande-box { background-color: #1b5e20; color: white; padding: 20px; border-radius: 15px; border: 2px solid black; }
    </style>
    """, unsafe_allow_html=True)

# CHARGEMENT RIGOUREUX DES DONNÉES
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_historique.csv")
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['ca'] = pd.to_numeric(df['ca'], errors='coerce')
        return df.dropna()
    except:
        return pd.DataFrame(columns=['date', 'ca'])

data = load_data()

st.title("📊 Expert F&L : Tes Chiffres Réels")

# --- RÉGLAGES ---
col_a, col_b = st.columns(2)
with col_a:
    jours_cde = st.multiselect("Jours de livraison :", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"], default=["Lundi", "Mercredi", "Vendredi"])
    d_cible = st.date_input("Date sélectionnée", datetime.now())
with col_b:
    meteo = st.selectbox("Météo", ["☀️ Soleil", "⛅ Variable", "🌧️ Pluie"])
    nb_jours_cde = st.number_input("Jours à couvrir pour la commande", min_value=1, max_value=5, value=2)

# --- CALCULS PERFORMANCE SEMAINE ---
st.subheader("📈 Performance Semaine (Réel vs N-1)")

# On récupère le CA du jour choisi dans ton historique
chiffre_du_jour = data[data['date'] == d_cible]
ca_ht_reel = chiffre_du_jour['ca'].values[0] if not chiffre_du_jour.empty else 0.0

# Calcul de la semaine (Lundi au Dimanche)
lundi = d_cible - timedelta(days=d_cible.weekday())
dimanche = lundi + timedelta(days=6)
mask_semaine = (data['date'] >= lundi) & (data['date'] <= d_cible)
ca_semaine = data[mask_semaine]['ca'].sum()

# RATIOS RÉELS (Basés sur tes tableaux)
ratio_achat = 0.71  # 71% d'achat HT
taux_inconnue = 0.043 # 4.3% de démarque inconnue

achats_est = ca_semaine * ratio_achat
casse_inconnue = ca_semaine * taux_inconnue
# On estime la casse connue à 6% si non saisie
casse_connue = ca_semaine * 0.06 
marge_nette = ca_semaine - achats_est - casse_inconnue - casse_connue

# AFFICHAGE DES MÉTRIQUES
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventes Semaine", f"{ca_semaine:.2f} €")
c2.metric("Achats HT (71%)", f"{achats_est:.2f} €")
c3.metric("Casse (Total)", f"{(casse_inconnue + casse_connue):.2f} €")
c4.metric("Marge Nette", f"{marge_nette:.2f} €", f"{(marge_nette/ca_semaine*100 if ca_semaine > 0 else 0):.1f}%")

# --- BLOC COMMANDE ---
nom_jour = d_cible.strftime('%A') # Anglais par défaut, on peut traduire si besoin
jours_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
jour_actuel_fr = jours_fr[nom_jour]

if jour_actuel_fr in jours_cde:
    st.markdown("---")
    # Estimation basée sur la moyenne du même jour les années précédentes
    hist_filtre = data[(pd.to_datetime(data['date']).dt.month == d_cible.month) & (pd.to_datetime(data['date']).dt.weekday == d_cible.weekday())]
    prev_base = hist_filtre['ca'].mean() if not hist_filtre.empty else 850.0
    
    # Ajustement météo
    coef = 1.15 if meteo == "☀️ Soleil" else 0.85 if meteo == "🌧️ Pluie" else 1.0
    ca_prevu = prev_base * coef
    montant_cde = (ca_prevu * nb_jours_cde) * 0.70

    st.markdown(f"""
        <div class="commande-box">
            <h3>📦 Commande conseillée ({jour_actuel_fr})</h3>
            <p>Vente estimée pour aujourd'hui : <b>{ca_prevu:.2f} € HT</b></p>
            <h1 style="color: #00ffcc; font-size: 4em;">{montant_cde:.0f} € HT</h1>
            <p>Pour couvrir les <b>{nb_jours_cde} prochains jours</b> de vente.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(f"Aujourd'hui ({jour_actuel_fr}), ce n'est pas un jour de commande.")
