# Déploiement Render - Guide de Configuration

## 📋 Fichiers de Configuration Créés

1. **runtime.txt** - Spécifie Python 3.13.5
2. **build.sh** - Script de construction pour Render
3. **render.yaml** - Configuration complète du service
4. **.env.example** - Template des variables d'environnement

## 🚀 Étapes de Déploiement sur Render

### 1. Préparer le Repository GitHub

```bash
# Ajouter tous les fichiers
git add .

# Commit avec message descriptif
git commit -m "Production ready: Add Render config, WhiteNoise, security hardening"

# Push vers GitHub
git push origin main
```

### 2. Créer un Compte Render

- Aller sur https://render.com
- S'inscrire avec votre compte GitHub
- Autoriser Render à accéder à vos repositories

### 3. Créer un Nouveau Web Service

1. Cliquer sur **"New +"** → **"Web Service"**
2. Connecter votre repository: `romualdKO/ROMI`
3. Sélectionner la branche: `main`
4. Configuration automatique (render.yaml sera détecté)

### 4. Variables d'Environnement à Configurer

Dans le dashboard Render, ajouter ces variables:

```
SECRET_KEY = [Render génèrera automatiquement]
DEBUG = False
ALLOWED_HOSTS = votre-app.onrender.com
EMAIL_HOST_USER = votre-email@gmail.com (optionnel)
EMAIL_HOST_PASSWORD = votre-mot-de-passe-app (optionnel)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**Note:** DATABASE_URL sera automatiquement fourni par Render.

### 5. Configuration de la Base de Données

Render créera automatiquement une base PostgreSQL gratuite avec:
- Nom: `dont-sang-plus-db`
- Database: `dont_sang_plus_db`
- User: `dont_sang_plus_user`

**Important:** Les données de votre DB locale ne seront PAS transférées.

### 6. Déploiement

1. Cliquer sur **"Create Web Service"**
2. Render exécutera automatiquement:
   - Installation des dépendances (pip install)
   - Collection des fichiers statiques (collectstatic)
   - Migrations de la base de données
   - Démarrage du serveur Gunicorn

### 7. Post-Déploiement

#### Créer un Super Utilisateur

```bash
# Dans le shell Render (Dashboard → Shell)
python manage.py createsuperuser
```

#### Tester l'Application

1. Accéder à: `https://votre-app.onrender.com`
2. Vérifier la page d'accueil
3. Tester l'inscription/connexion
4. Accéder à l'admin: `https://votre-app.onrender.com/admin`

## 🔧 Modifications Apportées pour la Production

### 1. Settings.py
- ✅ `DEBUG = False` par défaut
- ✅ `STATIC_ROOT` configuré
- ✅ WhiteNoise middleware ajouté
- ✅ Paramètres de sécurité (SSL, HSTS, cookies)

### 2. Requirements.txt
- ✅ `gunicorn==21.2.0` ajouté
- ✅ `whitenoise==6.6.0` ajouté

### 3. Code Cleanup
- ✅ Tous les `print("DEBUG:...")` supprimés
- ✅ Logging sensible nettoyé

## ⚠️ Points d'Attention

### Base de Données

**La base PostgreSQL de Render est VIDE au départ.**

Vous devrez:
1. Réinsérer les données de test si nécessaire
2. Recréer les super utilisateurs
3. Vérifier les hôpitaux et donneurs

### Plan Gratuit Render

Limitations:
- 750 heures/mois (suffisant pour un projet)
- Application en veille après 15 min d'inactivité
- Premier chargement peut être lent (réveil)
- 100 GB de bande passante/mois

### Email

Si vous configurez Gmail:
1. Activez la vérification en 2 étapes
2. Générez un "mot de passe d'application"
3. Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

## 🔍 Dépannage

### Erreur de Build

```bash
# Vérifier les logs dans Render Dashboard → Logs
# Problèmes fréquents:
# - Dépendances manquantes dans requirements.txt
# - Erreur de syntaxe Python
# - Migration échouée
```

### Fichiers Statiques Non Chargés

```bash
# Vérifier dans les logs:
python manage.py collectstatic --no-input
```

### Base de Données Non Connectée

```bash
# Vérifier que DATABASE_URL est bien défini
# Render le fournit automatiquement si vous avez créé la DB
```

## 📞 Support

- Documentation Render: https://render.com/docs/deploy-django
- Repository GitHub: https://github.com/romualdKO/ROMI
- Django Deployment Checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

## ✅ Checklist Finale

Avant le déploiement:
- [x] DEBUG=False
- [x] STATIC_ROOT configuré
- [x] WhiteNoise installé
- [x] Sécurité SSL configurée
- [x] Debug prints supprimés
- [x] requirements.txt à jour
- [x] runtime.txt créé
- [x] build.sh créé
- [x] render.yaml créé
- [x] .env.example mis à jour

Après le déploiement:
- [ ] Super utilisateur créé
- [ ] Admin accessible
- [ ] Inscription/connexion testée
- [ ] Upload d'images testé
- [ ] Emails testés (si configuré)
- [ ] Voice assistant testé
