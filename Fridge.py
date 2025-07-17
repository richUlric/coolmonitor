import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- Configuration de la page ---
st.set_page_config(
    page_title="Monitoring Refroidissement",
    page_icon="💨",
    layout="wide"
)

# --- Chargement des données ---
@st.cache_data

def load_data():
    df = pd.read_csv("arduino_data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    for col in ['Temperature', 'Humidity', 'Luminosity', 'Charge']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# --- Interface personnalisée ---
st.markdown("""
    <style>
        .main {
            background-color: #f0f4f8;
        }
        h1, h2, h3 {
            color: #004080;
        }
        .stButton>button {
            background-color: #007acc;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.image("LOGO_2iE_AFRIQUE.jpg", width=100)
st.title("💨 Projet Intégrateur")

# --- Paramètres personnalisables ---
st.sidebar.header("⚙️ Paramètres")
seuil_temp = st.sidebar.slider("Seuil de température (alertes)", 10, 50, 30)
seuil_lumiere = st.sidebar.slider("Seuil de luminosité", 0, 1023, 400)
seuil_charge = st.sidebar.slider("Seuil de charge", 0, 1023, 900)

# --- Logique de décision ---
def choisir_refroidissement(row):
    if row['Temperature'] < seuil_temp:
        return "Pas de refroidissement"
    elif row['Luminosity'] > seuil_lumiere and row['Charge'] > seuil_charge:
        return "Refroidissement Solaire"
    else:
        return "Refroidissement Auxiliaire"

df['Mode_Refroidissement'] = df.apply(choisir_refroidissement, axis=1)

# --- Alertes ---
df['Alerte'] = (df['Temperature'] >= seuil_temp) & (df['Mode_Refroidissement'] == "Pas de refroidissement")
alertes = df[df['Alerte']]

if not alertes.empty:
    st.error(f"🚨 {len(alertes)} alerte(s) : Température > {seuil_temp}°C sans refroidissement actif")

# --- Affichage temporel synchronisé ---
st.subheader("🔄 Évolution Temporelle des Capteurs")
fig = px.line(
    df, x='Timestamp', y=['Temperature', 'Luminosity', 'Charge'],
    labels={"value": "Valeur", "variable": "Capteur"},
    title="Température / Luminosité / Charge dans le temps",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# --- Température et mode de refroidissement (Plotly) ---
st.subheader("🌡️ Température selon le Mode de Refroidissement")
fig_temp_mode = px.scatter(
    df, x='Timestamp', y='Temperature', color='Mode_Refroidissement',
    title="Température en fonction du mode de refroidissement",
    labels={'Temperature': 'Température (°C)', 'Timestamp': 'Temps'},
    template="plotly_white"
)
st.write("Analyse de la température en fonction du mode de refroidissement choisi.")
st.plotly_chart(fig_temp_mode, use_container_width=True)

# --- Répartition des modes ---
st.subheader("📊 Répartition des Modes de Refroidissement")
mode_counts = df['Mode_Refroidissement'].value_counts().reset_index()
mode_counts.columns = ['Mode', 'Occurrences']
fig_mode = px.pie(mode_counts, values='Occurrences', names='Mode', title='Répartition des modes de refroidissement')
st.plotly_chart(fig_mode, use_container_width=True)

# --- Tableau de bord sur les dernières heures ---
st.subheader("📖 Tableau de Bord - Dernières Heures")
last_minutes = st.slider("Afficher les X dernières minutes", 10, 180, 60)
df_recent = df[df['Timestamp'] >= datetime.now() - timedelta(minutes=last_minutes)]
st.dataframe(df_recent[['Timestamp', 'Temperature', 'Luminosity', 'Charge', 'Mode_Refroidissement']])

# --- Exportation ---
st.download_button(
    "📂 Télécharger les données enrichies",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="donnees_monitoring.csv",
    mime='text/csv'
)
