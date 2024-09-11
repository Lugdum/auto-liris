import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import json
import os

# Configuration des identifiants Google pour l'envoi d'email
google_secret = os.getenv('GOOGLE_SECRET')
# URL de la page des offres de stage
url = "https://liris.cnrs.fr/emplois/offres-de-stage"
# Chemin du fichier JSON
json_file_path = './offres_de_stage.json'

def load_existing_offers():
    """Charge les offres existantes depuis un fichier JSON."""
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_offers(offers):
    """Sauvegarde les offres dans un fichier JSON."""
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(offers, file, ensure_ascii=False, indent=4)

def check_new_offers():
    # Requête HTTP pour récupérer le contenu de la page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraction des lignes de la table contenant les offres de stage
    rows = soup.find_all('tr', class_='odd') + soup.find_all('tr', class_='even')

    new_offers = []
    existing_offers = load_existing_offers()  # Chargement des offres existantes

    # Parcourir chaque ligne pour extraire les détails de chaque offre
    for row in rows:
        date_poste = row.find('td', class_='views-field-created').text.strip()
        titre = row.find('td', class_='views-field-title').text.strip()
        lien = row.find('td', class_='views-field-title').find('a')['href']
        lien_complet = f"https://liris.cnrs.fr{lien}"
        duree_stage = row.find('td', class_='views-field-field-emploi-duree-stage').text.strip()
        referent = row.find('td', class_='views-field-field-emploi-referent-1').text.strip()
        niveau = row.find('td', class_='views-field-field-emploi-niveau').text.strip()

        # Construire un dictionnaire pour chaque offre
        offre = {
            'date_poste': date_poste,
            'titre': titre,
            'lien': lien_complet,
            'duree_stage': duree_stage,
            'referent': referent,
            'niveau': niveau
        }

        # Vérifier si l'offre est déjà dans le fichier JSON
        if offre not in existing_offers:
            new_offers.append(offre)
            existing_offers.append(offre)  # Ajouter la nouvelle offre à la liste existante

    # Sauvegarder toutes les offres (anciennes + nouvelles) dans le fichier JSON
    save_offers(existing_offers)

    # Envoi d'un email si de nouvelles offres sont trouvées
    if new_offers:
        send_email(new_offers)

def send_email(offers):
    # Créer le contenu de l'email
    body = "\n\n".join([f"{o['titre']} - {o['date_poste']}\nLien : {o['lien']}\nDurée : {o['duree_stage']} mois\nRéférent : {o['referent']}\nNiveau : {o['niveau']}" for o in offers])
    msg = MIMEText(f"Nouvelles offres de stage :\n\n{body}")
    msg['Subject'] = 'Nouvelles offres de stage sur le site LIRIS'
    msg['From'] = 'vicbut10@gmail.com'
    msg['To'] = 'victor.buthod@epita.fr'

    # Configuration SMTP pour envoyer l'email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('vicbut10@gmail.com', google_secret)
        server.send_message(msg)

# Exécution du script pour vérifier les nouvelles offres
check_new_offers()
