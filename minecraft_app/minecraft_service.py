import logging
from mcrcon import MCRcon
from django.conf import settings

logger = logging.getLogger('minecraft_app')

def apply_rank_to_player(username, rank_name):
    """
    Applique un rang à un joueur sur le serveur Minecraft via RCON.
    
    Args:
        username (str): Nom d'utilisateur Minecraft
        rank_name (str): Nom du rang à appliquer
    
    Returns:
        bool: True si le rang a été appliqué avec succès, False sinon
    """
    if not username:
        logger.error("Cannot apply rank: No Minecraft username provided")
        return False
    
    try:
        # Nettoyer le nom du rang (enlever les espaces, convertir en minuscules)
        clean_rank = rank_name.lower().replace(' ', '_')
        
        # Ajouter les logs de débogage
        logger.info(f"Connexion RCON à {settings.MINECRAFT_RCON_HOST}:{settings.MINECRAFT_RCON_PORT}")
        
        # Se connecter au serveur Minecraft via RCON
        with MCRcon(
            settings.MINECRAFT_RCON_HOST, 
            settings.MINECRAFT_RCON_PASSWORD, 
            settings.MINECRAFT_RCON_PORT,
            timeout=60  # Augmentez à une minute
        ) as mcr:
            # La commande dépend de votre plugin de permissions
            # Pour LuckPerms:
            lp_command = f"lp user {username} parent add {clean_rank}"
            logger.info(f"Envoi de la commande: {lp_command}")
            resp = mcr.command(lp_command)
            logger.info(f"Réponse reçue: {resp}")
            
        return True
        
    except Exception as e:
        logger.error(f"Erreur RCON détaillée: {str(e)}", exc_info=True)
        return False