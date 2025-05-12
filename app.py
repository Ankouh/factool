import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Factool - Gestion de Factures",
    page_icon="📄",
    layout="wide"
)

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('factures.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            montant REAL NOT NULL,
            commentaire TEXT,
            date_creation TEXT NOT NULL,
            est_paye BOOLEAN NOT NULL,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Fonction pour ajouter une facture
def ajouter_facture(nom, prenom, montant, commentaire, email):
    conn = sqlite3.connect('factures.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO factures (nom, prenom, montant, commentaire, date_creation, est_paye, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nom, prenom, montant, commentaire, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), False, email))
    conn.commit()
    conn.close()

# Fonction pour envoyer un email de relance
def envoyer_relance(email, nom, prenom, montant):
    if not email:
        st.warning("Aucune adresse email n'est associée à cette facture.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = email
        msg['Subject'] = "Rappel de paiement - Factool"
        
        body = f"""
        Bonjour {prenom} {nom},
        
        Nous vous rappelons que vous avez une facture d'un montant de {montant}€ qui n'a pas encore été réglée.
        
        Merci de bien vouloir procéder au paiement dans les plus brefs délais.
        
        Cordialement,
        L'équipe Factool
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

# Initialisation de la base de données
init_db()

# Interface utilisateur
st.title("📄 Factool - Gestion de Factures")

# Formulaire d'ajout de facture
with st.form("nouvelle_facture"):
    st.subheader("Ajouter une nouvelle facture")
    col1, col2 = st.columns(2)
    
    with col1:
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        montant = st.number_input("Montant (€)", min_value=0.0, step=0.01)
    
    with col2:
        email = st.text_input("Email client")
        commentaire = st.text_area("Commentaire")
    
    submitted = st.form_submit_button("Ajouter la facture")
    
    if submitted:
        if nom and prenom and montant:
            ajouter_facture(nom, prenom, montant, commentaire, email)
            st.success("Facture ajoutée avec succès!")
        else:
            st.error("Veuillez remplir tous les champs obligatoires.")

# Affichage des factures
st.subheader("Liste des factures")
conn = sqlite3.connect('factures.db')
df = pd.read_sql_query("SELECT * FROM factures", conn)
conn.close()

if not df.empty:
    # Création d'une interface pour gérer les factures
    for _, row in df.iterrows():
        with st.expander(f"Facture #{row['id']} - {row['nom']} {row['prenom']} - {row['montant']}€"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Date de création:** {row['date_creation']}")
                st.write(f"**Commentaire:** {row['commentaire']}")
                st.write(f"**Email:** {row['email']}")
            
            with col2:
                statut = "✅ Payée" if row['est_paye'] else "❌ Non payée"
                st.write(f"**Statut:** {statut}")
            
            with col3:
                if not row['est_paye']:
                    if st.button("Marquer comme payée", key=f"pay_{row['id']}"):
                        conn = sqlite3.connect('factures.db')
                        c = conn.cursor()
                        c.execute("UPDATE factures SET est_paye = TRUE WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.experimental_rerun()
                    
                    if st.button("Envoyer relance", key=f"relance_{row['id']}"):
                        if envoyer_relance(row['email'], row['nom'], row['prenom'], row['montant']):
                            st.success("Email de relance envoyé avec succès!")
else:
    st.info("Aucune facture n'a été ajoutée pour le moment.") 