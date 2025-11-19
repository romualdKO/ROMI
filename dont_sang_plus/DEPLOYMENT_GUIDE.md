# 🚀 Guide de Déploiement sur Render.com

## ✅ Préparation Complétée

Tous les changements suivants ont été appliqués :

### 1. Configuration de Production (settings.py)
- ✅ `DEBUG = False` par défaut
- ✅ `STATIC_ROOT` configuré pour collectstatic
- ✅ WhiteNoise middleware ajouté pour servir les fichiers statiques
- ✅ Configurations de sécurité (SSL, HSTS, cookies sécurisés)
- ✅ Support PostgreSQL avec DATABASE_URL

### 2. Nettoyage du Code
- ✅ Suppression de tous les `print("DEBUG:...")` sensibles
- ✅ Gestion d'erreurs propre sans exposition de données

### 3. Dépendances Mises à Jour (requirements.txt)
- ✅ `whitenoise==6.6.0` - Service de fichiers statiques
- ✅ `gunicorn==21.2.0` - Serveur WSGI pour production
- ✅ Toutes les dépendances existantes préservées

### 4. Fichiers Render Créés
- ✅ `runtime.txt` - Version Python 3.13.1
- ✅ `build.sh` - Script de construction automatique
- ✅ `render.yaml` - Configuration infrastructure as code
- ✅ `.env.example` - Template des variables d'environnement

---

## 📋 Étapes de Déploiement

### Étape 1 : Tester Localement
```powershell
# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Tester avec DEBUG=False (dans .env local)
DEBUG=False
python manage.py runserver

# Si tout fonctionne, passer à l'étape 2
```

### Étape 2 : Commit et Push vers GitHub
```powershell
# Ajouter tous les changements
git add .

# Créer un commit
git commit -m "Production ready: Render deployment configuration"

# Pousser vers GitHub
git push origin main
```

### Étape 3 : Créer le Service sur Render

1. **Se connecter à Render** : https://dashboard.render.com/

2. **Option A : Utiliser render.yaml (Recommandé)**
   - Cliquer sur "New" → "Blueprint"
   - Connecter votre dépôt GitHub : `https://github.com/romualdKO/ROMI`
   - Render détectera automatiquement `render.yaml`
   - Configurer les variables d'environnement manquantes

3. **Option B : Configuration Manuelle**
   - Créer une nouvelle "Web Service"
   - Repository : `https://github.com/romualdKO/ROMI`
   - Branch : `main`
   - Root Directory : `dont_sang_plus`
   - Build Command : `./build.sh`
   - Start Command : `gunicorn dont_sang_plus.wsgi:application`

### Étape 4 : Configurer les Variables d'Environnement

Dans le Dashboard Render, ajouter ces variables :

#### **Essentielles (à définir immédiatement)**
```
SECRET_KEY = [Générer une nouvelle clé secrète Django]
DEBUG = False
ALLOWED_HOSTS = your-app-name.onrender.com
```

#### **Base de Données (Render configure automatiquement)**
```
DATABASE_URL = [Fourni automatiquement par Render]
```

#### **Email (pour les notifications)**
```
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = [App Password de Gmail]
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = smtp.gmail.com
```

#### **Sécurité (Activer après le premier déploiement réussi)**
```
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Étape 5 : Créer la Base de Données PostgreSQL

1. Dans Render Dashboard : "New" → "PostgreSQL"
2. Nom : `dont-sang-plus-db`
3. Plan : Free (ou payant selon besoins)
4. Créer la base de données
5. Lier la base à votre Web Service :
   - Dans les settings du Web Service
   - Section "Environment"
   - Ajouter la variable `DATABASE_URL` qui pointe vers votre base

### Étape 6 : Déploiement

1. **Déclencher le build** : Render va automatiquement :
   - Installer les dépendances (`pip install -r requirements.txt`)
   - Collecter les fichiers statiques (`collectstatic`)
   - Migrer la base de données (`migrate`)
   - Démarrer Gunicorn

2. **Surveiller les logs** : Vérifier que tout se passe bien

3. **Premier accès** :
   - URL : `https://your-app-name.onrender.com`
   - Créer un superuser si nécessaire :
     ```bash
     # Via le shell Render
     python manage.py createsuperuser
     ```

---

## 🔧 Configuration Post-Déploiement

### 1. Créer un Superutilisateur
Dans le shell Render (Dashboard → Shell) :
```bash
python manage.py createsuperuser
```

### 2. Vérifier l'Admin
Accéder à : `https://your-app-name.onrender.com/admin/`

### 3. Configurer les Emails
- Utiliser un **App Password Gmail** (pas votre mot de passe normal)
- Générer sur : https://myaccount.google.com/apppasswords

### 4. Tester les Fonctionnalités
- ✅ Inscription donneur
- ✅ Inscription hôpital
- ✅ Connexion
- ✅ Envoi d'emails
- ✅ Fichiers statiques (CSS, JS, images)
- ✅ Fichiers média (photos de profil)

---

## 🎯 Checklist de Vérification

### Avant le Push
- [x] DEBUG=False dans settings.py
- [x] Tous les print("DEBUG:...") supprimés
- [x] STATIC_ROOT configuré
- [x] WhiteNoise ajouté
- [x] requirements.txt à jour
- [x] runtime.txt créé
- [x] build.sh créé
- [x] render.yaml créé
- [x] .env.example créé

### Après le Déploiement
- [ ] Application accessible via HTTPS
- [ ] Page d'accueil se charge correctement
- [ ] CSS et JS fonctionnent
- [ ] Login fonctionne
- [ ] Inscription donneur fonctionne
- [ ] Inscription hôpital fonctionne
- [ ] Emails sont envoyés
- [ ] Admin accessible
- [ ] Upload d'images fonctionne

---

## 🆘 Dépannage

### Erreur : "Disallowed Host"
**Solution** : Ajouter votre domaine Render à `ALLOWED_HOSTS` dans les variables d'environnement
```
ALLOWED_HOSTS=your-app.onrender.com
```

### Erreur : "Static files not found"
**Solution** :
1. Vérifier que `collectstatic` s'exécute dans `build.sh`
2. Vérifier que WhiteNoise est dans `MIDDLEWARE`
3. Redéployer

### Erreur : "Database connection"
**Solution** :
1. Vérifier que `DATABASE_URL` est définie
2. Vérifier que la base PostgreSQL est créée et liée
3. Vérifier les migrations dans les logs

### Emails ne s'envoient pas
**Solution** :
1. Utiliser un **App Password Gmail** (pas le mot de passe normal)
2. Vérifier `EMAIL_HOST_USER` et `EMAIL_HOST_PASSWORD`
3. Activer "Accès moins sécurisé" si nécessaire

---

## 📊 Monitoring

### Logs en Temps Réel
- Dashboard Render → Votre service → "Logs"
- Surveiller les erreurs 500

### Performance
- Render Free Tier : 512 MB RAM, 0.1 CPU
- Se met en veille après 15 min d'inactivité
- Premier accès peut prendre 30-60 secondes

### Mise à l'Échelle
Si besoin de plus de ressources :
- Passer au plan Starter ($7/mois)
- 512 MB RAM, pas de mise en veille

---

## 🎉 Félicitations !

Votre application **Don Sang Plus** est maintenant déployée en production sur Render ! 🚀

**URL de production** : `https://your-app-name.onrender.com`

**Prochaines étapes** :
1. Configurer un nom de domaine personnalisé (optionnel)
2. Activer les sauvegardes de base de données
3. Configurer des alertes de monitoring
4. Ajouter Google Analytics ou similaire

---

## 📚 Ressources

- [Documentation Render](https://render.com/docs)
- [Déploiement Django sur Render](https://render.com/docs/deploy-django)
- [Configuration WhiteNoise](http://whitenoise.evans.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

**Support** : romualdndri9@gmail.com
