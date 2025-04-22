import logging
from mcrcon import MCRcon
from django.conf import settings

logger = logging.getLogger(__name__)

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
        
        # Se connecter au serveur Minecraft via RCON
        with MCRcon(
            settings.MINECRAFT_RCON_HOST, 
            settings.MINECRAFT_RCON_PASSWORD, 
            settings.MINECRAFT_RCON_PORT
        ) as mcr:
            # La commande dépend de votre plugin de permissions
            # Exemples pour différents plugins:
            
            # Pour LuckPerms:
            lp_command = f"lp user {username} parent add {clean_rank}"
            resp = mcr.command(lp_command)
            logger.info(f"RCON command executed: {lp_command}, Response: {resp}")
            
            # Pour PermissionsEx:
            # pex_command = f"pex user {username} group add {clean_rank}"
            # resp = mcr.command(pex_command)
            
            # Pour GroupManager:
            # gm_command = f"manuadd {username} {clean_rank}"
            # resp = mcr.command(gm_command)
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply rank in Minecraft: {str(e)}")
        return False