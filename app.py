import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import streamlit.components.v1 as components

st. set_page_config(layout="wide")

# Ajouter du CSS personnalisé pour le bouton
st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #059669; /* Vert émeraude 600 */
        color: #ffffff; /* Texte blanc */
        border-radius: 8px; /* Coins arrondis */
        border: none; /* Pas de bordure */
        padding: 10px 24px; /* Espacement interne */
        font-size: 16px; /* Taille du texte */
        font-weight: bold; /* Texte en gras */
        transition: background-color 0.3s ease; /* Animation de transition */
    }
    div.stButton > button:hover {
        background-color: #047857; /* Vert émeraude 700 au survol */
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)
show_print_button = """
    <script>
        function print_page(obj) {
            const originalDisplay = obj.style.display;
            obj.style.display = "none"; // Hide the button temporarily
            setTimeout(() => {
                obj.style.display = originalDisplay; // Restore the button after print dialog
            }, 1000); // Wait 1 second to ensure the print dialog is triggered
            parent.window.print();
        }
    </script>
    <style>
        div.stButton > button:first-child {
            background-color: #059669; /* Vert émeraude 600 */
            color: #ffffff; /* Texte blanc */
            border-radius: 8px; /* Coins arrondis */
            border: none; /* Pas de bordure */
            padding: 10px 24px; /* Espacement interne */
            font-size: 16px; /* Taille du texte */
            font-weight: bold; /* Texte en gras */
            transition: background-color 0.3s ease; /* Animation de transition */
        }
        div.stButton > button:hover {
            background-color: #047857; /* Vert émeraude 700 au survol */
            color: #ffffff;
        }
        button.print-button {
            background-color: #059669; /* Vert émeraude 600 */
            color: #ffffff; /* Texte blanc */
            border-radius: 8px; /* Coins arrondis */
            border: none; /* Pas de bordure */
            padding: 10px 24px; /* Espacement interne */
            font-size: 16px; /* Taille du texte */
            font-weight: bold; /* Texte en gras */
            cursor: pointer;
            transition: background-color 0.3s ease; /* Animation de transition */
        }
        button.print-button:hover {
            background-color: #047857; /* Vert émeraude 700 au survol */
            color: #ffffff;
        }
    </style>
    <button class="print-button" onclick="print_page(this)">
        Exporter en PDF (A4, Mise à l'échelle : 60%)
    </button>
    """

# Configuration des credentials Google
credentials = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    "universe_domain": st.secrets["universe_domain"]
}

SHEET_URL = st.secrets["SHEET_URL"]
SHEET_NAME = st.secrets["SHEET_NAME"]

# Authentification et accès à Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(credentials, scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).worksheet(SHEET_NAME)

def load_chart_data():
    raw_data = sheet.get("K218:AI218")[0]  # Charger une seule ligne
    data = []
    
    for val in raw_data:
        # Nettoyer et vérifier la valeur
        cleaned_val = val.replace("€", "").replace("\u00a0", "").replace("\u202f", "").strip()
        
        if cleaned_val in ['-', '']:
            # Si la valeur est '-' ou vide, la remplacer par 0
            data.append(0.0)
        else:
            try:
                # Convertir en float si possible
                data.append(float(cleaned_val))
            except ValueError:
                # Gestion d'erreur si une valeur inattendue est rencontrée
                data.append(0.0)  # Vous pouvez aussi lever une alerte ou journaliser l'erreur
    
    # Créer un DataFrame avec les années et les valeurs
    df = pd.DataFrame({
        'Année': [f'Année {i+1}' for i in range(len(data))],
        'Valeur': data
    })
    return df


# Nouvelle fonction pour charger les données du deuxième graphique
def load_cash_flow_data():
    # Charger les flux conservés dans la société
    flux_societe = sheet.get("K227:AI227")[0]
    # Charger les flux nets d'IR
    flux_ir = sheet.get("L289:AJ289")[0]

    # Nettoyer et convertir les données
    flux_societe_clean = [
        float(val.replace("€", "").replace("\u00a0", "").replace("\u202f", "").strip())
        if val.replace("€", "").replace("\u00a0", "").replace("\u202f", "").strip() not in ['-', '']
        else 0.0
        for val in flux_societe
    ]
    flux_ir_clean = [
        float(val.replace("€", "").replace("\u00a0", "").replace("\u202f", "").strip())
        if val.replace("€", "").replace("\u00a0", "").replace("\u202f", "").strip() not in ['-', '']
        else 0.0
        for val in flux_ir
    ]

    # Créer un DataFrame avec les deux séries
    df = pd.DataFrame({
        'Année': [f'Année {i+1}' for i in range(len(flux_societe_clean))],
        'Flux conservés': flux_societe_clean,
        'Flux nets IR': flux_ir_clean
    })

    return df

def load_summary_data():
    # Charger les données des cellules spécifiques
    summary_data = {
        "Apport de": sheet.acell("M5").value,
        "Enrichissement net (VAN)": sheet.acell("M7").value,
        "Rentabilité annuelle nette (TRI)": sheet.acell("M10").value,
        "Retour sur investissement annuel net (ROI)": sheet.acell("M12").value,
        "Rendement brut (loyers / prix)": sheet.acell("M15").value,
        "Multiple réalisé": sheet.acell("M17").value
    }
    return summary_data

def load_decomposition_data():
    # Charger les données des cellules spécifiques
    decomposition_data = {
        "Décomposition de l'enrichissement sur": sheet.acell("B48").value,
        "Total des loyers perçus": sheet.acell("S8").value,
        "Total taxes foncières": sheet.acell("S9").value,
        "Total PNO": sheet.acell("S10").value,
        "Total gestion locative": sheet.acell("S11").value,
        "Total autres charges": sheet.acell("S12").value,
        "Intérêts payés à la banque": sheet.acell("S13").value,
        "Amortissements du crédit": sheet.acell("S14").value,
        "Total fiscalité société": sheet.acell("S15").value,
        "Total fiscalité personnelle": sheet.acell("S16").value,
        "Valeur du bien à terme": sheet.acell("S17").value,
        "Capital restant dû banque": sheet.acell("S18").value,
        "Reprise des apports initiaux": sheet.acell("S19").value,
        "Total": sheet.acell("S20").value,
        "Soit par an": sheet.acell("S21").value,
        "Pour un apport de": sheet.acell("S22").value,
        "Retour sur investissement annualisé": sheet.acell("S23").value
    }
    return decomposition_data

# Fonction pour mettre à jour une cellule
def update_cell(cell, value, is_percentage=False):
    try:
        if value is not None and value != "":
            # Convertir en nombre si possible
            if isinstance(value, (int, float)):
                if is_percentage:
                    value = float(value) / 100  # Convertit le pourcentage en décimal
                else:
                    value = float(value)
            sheet.update(cell, [[value]])
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour de la cellule : {e}")

# Interface utilisateur avec Streamlit
st.title("Simulateur Qallanq")
# Add the button to the Streamlit app
components.html(show_print_button, height=60)

# Diviser l'interface en colonnes pour les inputs
col1, col2, col3 = st.columns(3)

# Champs de saisie regroupés dans les colonnes
m2_input = col1.number_input("Nombre de m2", min_value=0, step=1, value=None)
prix_acquisition_fai = col2.number_input("Prix d'acquisition FAI", min_value=0, step=1000, value=None)
meubles = col3.text_input("Meubles", value=None)

travaux = col1.number_input("Travaux", min_value=0, step=500, value=None)
frais_notaire = col2.number_input("Frais de notaire (%)", min_value=0.0, step=0.1, value=None)
duree_simulation_total = col3.number_input("Durée de la simulation", min_value=0, step=1, value=None)

col4, col5, col6, col7 = st.columns(4)
duree_simulation = col4.number_input("Durée du crédit", min_value=0, step=1, value=None)
differe = col5.number_input("Différé (en année)", min_value=0, step=1, value=None)
taux = col6.number_input("Taux du crédit (%)", min_value=0.0, step=0.1, value=None)
choix_d19 = col7.selectbox("Différé", ["Partiel", "Total"], index=0)

col8, col9, col10 = st.columns(3)

apport_initial = col8.number_input("Apport Initial (%)", min_value=0.0, step=0.1, value=None)
loyer_mensuel_hc = col9.number_input("Loyer mensuel HC", min_value=0, step=100, value=None)
revalorisation_loyer = col10.number_input("Revalorisation annuelle du Loyer (%)", min_value=0.0, step=0.1, value=None)

taxe_fonciere = col8.number_input("Taxe foncière", min_value=0, step=100, value=None)
revalorisation_taxe = col9.number_input("Revalorisation annuelle de la taxe (%)", min_value=0.0, step=0.1, value=None)
autres_charges = col10.number_input("Autres charges", min_value=0, step=50, value=None)

revalorisation_autres = col8.number_input("Revalorisation annuelle des autres charges (%)", min_value=0.0, step=0.1, value=None)
assurance_pno = col9.number_input("Assurance PNO", min_value=0, step=50, value=None)
revalorisation_assurance = col10.number_input("Revalorisation annuelle de l'assurance (%)", min_value=0.0, step=0.1, value=None)


frais_gestion_locative = col8.number_input("Frais de gestion locative (%)", min_value=0.0, step=0.1, value=None)
valeur_reelle_bien = col9.number_input("Valeur réelle du bien acquis", min_value=0, step=1000, value=None)
revalorisation_bien = col10.number_input("Revalorisation annuelle du bien (%)", min_value=0.0, step=0.1, value=None)

# Ajout d'un champ de liste déroulante
col4, col5, col6 = st.columns(3)


# Bouton pour générer
if st.button("Générer", use_container_width = True):
    # Mise à jour de chaque champ dans le Google Sheet
    update_cell("B6", m2_input)
    update_cell("B7", prix_acquisition_fai)
    update_cell("B8", meubles)
    update_cell("B9", travaux)
    update_cell("B10", frais_notaire, is_percentage=True)  # Pourcentage
    update_cell("C18", duree_simulation)
    update_cell("C19", differe)
    update_cell("D18", taux, is_percentage=True)  # Pourcentage
    update_cell("C24", apport_initial, is_percentage=True)  # Pourcentage
    update_cell("B32", loyer_mensuel_hc)
    update_cell("C32", revalorisation_loyer, is_percentage=True)  # Pourcentage
    update_cell("B35", taxe_fonciere)
    update_cell("C35", revalorisation_taxe, is_percentage=True)  # Pourcentage
    update_cell("B36", autres_charges)
    update_cell("C36", revalorisation_autres, is_percentage=True)  # Pourcentage
    update_cell("B37", assurance_pno)
    update_cell("C37", revalorisation_assurance, is_percentage=True)  # Pourcentage
    update_cell("B39", frais_gestion_locative, is_percentage=True)  # Pourcentage
    update_cell("B46", valeur_reelle_bien)
    update_cell("C46", revalorisation_bien, is_percentage=True)  # Pourcentage
    update_cell("B48", duree_simulation_total)
    update_cell("D19", choix_d19)

    # Charger les nouvelles données du graphique après la mise à jour
    st.session_state["chart_data"] = load_chart_data()
    st.session_state["cash_flow_data"] = load_cash_flow_data()

    st.success("La simulation démarre !")


# Charger les données du tableau récapitulatif
summary_data = load_summary_data()

# Afficher le tableau récapitulatif
st.subheader("Résultats Financiers")
summary_df = pd.DataFrame(list(summary_data.items()), columns=["Indicateur", "Valeur"])
st.table(summary_df)

# Charger les données du tableau de décomposition
decomposition_data = load_decomposition_data()

# Afficher le tableau de décomposition
st.subheader("Décomposition de l'enrichissement")
decomposition_df = pd.DataFrame(list(decomposition_data.items()), columns=["Élément", "Valeur"])
st.table(decomposition_df)

# Ajouter un espace invisible entre les éléments
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# Charger les données du graphique au premier affichage ou utiliser les données mises à jour
if "chart_data" not in st.session_state:
    st.session_state["chart_data"] = load_chart_data()

# Premier graphique
fig = px.bar(
    st.session_state["chart_data"],
    x='Année',
    y='Valeur',
    title='Trésorerie Cumulée',
    labels={'Valeur': 'Montant (€)'},
    text='Valeur'
)

# Personnaliser l'apparence du graphique
fig.update_traces(
    texttemplate='%{text:,.0f}€',  # Format sans décimales avec séparateur de milliers
    textfont=dict(size=14),  # Taille de police plus grande
    marker_color='rgb(255, 0, 0)'
)

fig.update_layout(
    xaxis_tickangle=-45,  # Rotation des labels de l'axe x
    bargap=0.2,          # Espace entre les barres
    height=600,          # Hauteur du graphique
    legend_title_text='Type de flux',  # Titre de la légende
    legend=dict(
        orientation="h",     # Légende horizontale
        yanchor="bottom",   # Ancrage en bas
        y=1.02,            # Position Y
        xanchor="right",    # Ancrage à droite
        x=1                # Position X
    )
)

# Afficher le graphique
st.plotly_chart(fig, use_container_width=True)

# Charger et afficher le deuxième graphique
if "cash_flow_data" not in st.session_state:
    st.session_state["cash_flow_data"] = load_cash_flow_data()

# Deuxième graphique
fig2 = px.bar(
    st.session_state["cash_flow_data"],
    x='Année',
    y=['Flux conservés', 'Flux nets IR'],
    title='Flux conservés et Flux nets d\'IR par année',
    labels={'value': 'Montant (€)', 'variable': 'Type de flux'},
    barmode='stack',
    color_discrete_map={
        'Flux conservés': 'rgb(255, 165, 0)',
        'Flux nets IR': 'rgb(0, 255, 0)'
    }
)

# Personnaliser l'apparence du deuxième graphique
fig2.update_traces(
    texttemplate='%{y:,.0f}€',  # Format sans décimales avec séparateur de milliers
    textfont=dict(size=14),     # Taille de police plus grande
)

fig2.update_layout(
    xaxis_tickangle=-45,  # Rotation des labels de l'axe x
    bargap=0.2,          # Espace entre les barres
    height=600,          # Hauteur du graphique
    legend_title_text='Type de flux',  # Titre de la légende
    legend=dict(
        orientation="h",     # Légende horizontale
        yanchor="bottom",   # Ancrage en bas
        y=1.02,            # Position Y
        xanchor="right",    # Ancrage à droite
        x=1                # Position X
    )
)
    

# Afficher le deuxième graphique
st.plotly_chart(fig2, use_container_width=True)
