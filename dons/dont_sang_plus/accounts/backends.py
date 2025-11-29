"""
Backend d'authentification personnalisé pour utiliser l'email au lieu du username
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authentifie les utilisateurs en utilisant leur adresse email au lieu du username.
    Compatible avec le modèle CustomUser qui utilise email comme identifiant unique.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Tente d'authentifier un utilisateur avec son email et mot de passe.
        
        Args:
            request: La requête HTTP
            username: L'email de l'utilisateur (nommé 'username' pour compatibilité Django)
            password: Le mot de passe de l'utilisateur
            
        Returns:
            L'objet User si l'authentification réussit, None sinon
        """
        try:
            # Chercher l'utilisateur par email (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # L'utilisateur n'existe pas
            return None
        except User.MultipleObjectsReturned:
            # Plusieurs utilisateurs avec le même email (ne devrait pas arriver)
            # On prend le premier actif
            user = User.objects.filter(email__iexact=username, is_active=True).first()
            if not user:
                return None
        
        # Vérifier le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: L'ID de l'utilisateur
            
        Returns:
            L'objet User si trouvé, None sinon
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None
