# Créez un nouveau fichier nommé gmail_api.py dans le dossier minecraft_app

import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Si vous modifiez ces scopes, supprimez le fichier token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """
    Obtient un service authentifié pour l'API Gmail.
    
    Returns:
        Un service Gmail API authentifié
    """
    creds = None
    
    # Le fichier token.pickle stocke les tokens d'accès et de rafraîchissement de l'utilisateur
    token_path = settings.GMAIL_API_TOKEN
    credentials_path = settings.GMAIL_API_CREDENTIALS
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Si aucun identifiant valide disponible, demander à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Erreur lors du rafraîchissement du token: {str(e)}")
                # Si le rafraîchissement échoue, créer de nouveaux identifiants
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder les identifiants pour la prochaine exécution
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    # Retourner le service construit
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Erreur lors de la construction du service Gmail: {str(e)}")
        return None

def send_email(to, subject, body, from_email=None):
    """
    Envoie un email via l'API Gmail.
    
    Args:
        to (str): Adresse email du destinataire
        subject (str): Objet de l'email
        body (str): Corps de l'email
        from_email (str, optional): Adresse email de l'expéditeur. Si non fournie, utilisera l'email du compte autorisé.
    
    Returns:
        bool: True si l'envoi est réussi, False sinon
    """
    try:
        service = get_gmail_service()
        if not service:
            logger.error("Impossible d'obtenir le service Gmail")
            return False
        
        # Créer un message
        if from_email is None:
            from_email = settings.CONTACT_EMAIL
            
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        message['from'] = from_email
        
        # Encoder en base64 pour l'API Gmail
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Créer le message pour l'API
        create_message = {
            'raw': encoded_message
        }
        
        # Envoyer le message
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        logger.info(f"Message envoyé avec l'ID: {send_message['id']}")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False