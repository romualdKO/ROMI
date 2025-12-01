# 🩸 DON SANG PLUS - Guide de Collaboration

## 📋 Informations du Projet

**Nom du Projet :** Don Sang Plus  
**Description :** Plateforme de mise en relation entre donneurs de sang et hôpitaux  
**Technologies :** Django 5.2.7, PostgreSQL, Bootstrap 5, JavaScript  
**Repository GitHub :** https://github.com/romualdKO/ROMI  
**Branche principale :** main  

---

## 🔐 Accès Administrateur

### Compte Super Admin
- **Email :** romualdndri9@gmail.com
- **Mot de passe :** romuald2005
- **URL Admin :** http://127.0.0.1:8000/admin/

### Permissions
- Accès complet à la base de données
- Validation des comptes hôpitaux
- Gestion des utilisateurs
- Supervision des dons et demandes

---

## 🚀 Installation et Configuration

### 1. Cloner le Projet

```bash
git clone https://github.com/romualdKO/ROMI.git
cd ROMI/dont_sang_plus/dont_sang_plus
```

### 2. Créer un Environnement Virtuel (Recommandé)

**Windows (PowerShell) :**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

**Dépendances principales :**
- Django==5.2.7
- psycopg2-binary==2.9.10
- python-decouple==3.8
- Pillow==11.3.0
- django-widget-tweaks==1.5.0
- whitenoise==6.6.0
- gunicorn==21.2.0

### 4. Configuration de la Base de Données

Le projet utilise **PostgreSQL**. Les informations de connexion sont dans le fichier `.env` :

```env
# Base de données PostgreSQL
DATABASE_NAME=dont_sang_plus_db
DATABASE_USER=dont_sang_plus_user
DATABASE_PASSWORD=romuald2005
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Si vous n'avez pas PostgreSQL :**
1. Télécharger : https://www.postgresql.org/download/
2. Installer PostgreSQL
3. Créer la base de données :
```sql
CREATE DATABASE dont_sang_plus_db;
CREATE USER dont_sang_plus_user WITH PASSWORD 'romuald2005';
GRANT ALL PRIVILEGES ON DATABASE dont_sang_plus_db TO dont_sang_plus_user;
```

### 5. Appliquer les Migrations

```bash
python manage.py migrate
```

### 6. Créer un Superutilisateur (Si nécessaire)

```bash
python manage.py createsuperuser
```

### 7. Collecter les Fichiers Statiques

```bash
python manage.py collectstatic --no-input
```

### 8. Lancer le Serveur de Développement

```bash
python manage.py runserver
```

Le site sera accessible sur : **http://127.0.0.1:8000/**

---

## 👥 Comptes de Test Disponibles

### Compte Donneur 1
- **Email :** donneur1@test.com
- **Mot de passe :** test123
- **Type :** Donneur
- **Groupe sanguin :** A+

### Compte Donneur 2
- **Email :** donneur2@test.com
- **Mot de passe :** test123
- **Type :** Donneur
- **Groupe sanguin :** O-

### Compte Hôpital 1
- **Email :** hopital@test.com
- **Mot de passe :** test123
- **Type :** Hôpital
- **Nom :** CHU de Cocody

**Note :** Ces comptes peuvent ne pas exister dans votre base. Vous pouvez les créer via l'inscription ou l'admin.

---

## 📂 Structure du Projet

```
dont_sang_plus/
├── dont_sang_plus/          # Configuration principale Django
│   ├── settings.py          # Paramètres du projet
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuration WSGI
├── accounts/                # Application Authentification
│   ├── models.py            # Modèle utilisateur personnalisé
│   ├── views.py             # Vues (login, signup, etc.)
│   ├── forms.py             # Formulaires
│   └── templates/           # Templates HTML
├── donations/               # Application Don de Sang
│   ├── models.py            # Modèles (BloodRequest, etc.)
│   ├── views.py             # Vues dashboard, demandes
│   └── templates/           # Templates dashboard
├── hospitals/               # Application Hôpitaux
├── static/                  # Fichiers statiques
│   ├── css/                 # Styles CSS
│   │   ├── modern-design.css
│   │   ├── responsive-fixes.css
│   │   └── voice-assistant.css
│   ├── js/                  # Scripts JavaScript
│   │   ├── main.js
│   │   ├── responsive-menu.js
│   │   └── voice-assistant.js
│   └── images/              # Images
├── media/                   # Fichiers uploadés
│   └── profile_pics/        # Photos de profil
├── staticfiles/             # Fichiers statiques collectés
├── db.sqlite3               # Base de données SQLite (dev)
├── manage.py                # Script de gestion Django
└── requirements.txt         # Dépendances Python
```

---

## 🎯 Fonctionnalités à Tester

### 1. Authentification
- [ ] Inscription donneur
- [ ] Inscription hôpital
- [ ] Connexion
- [ ] Déconnexion
- [ ] Mot de passe oublié
- [ ] Modification de profil
- [ ] Upload photo de profil

### 2. Dashboard Donneur
- [ ] Affichage des statistiques
- [ ] Mise à jour de disponibilité
- [ ] Consultation des demandes de sang
- [ ] Réponse aux demandes
- [ ] Historique des dons
- [ ] Système de badges (Bronze, Argent, Or, Platine)
- [ ] Classement des donneurs
- [ ] Mes récompenses

### 3. Dashboard Hôpital
- [ ] Création de demande de sang
- [ ] Gestion des demandes
- [ ] Consultation des réponses
- [ ] Changement de statut (En cours, Validée, Terminée)
- [ ] Chat avec les donneurs
- [ ] Historique des demandes

### 4. Assistant Vocal IA
- [ ] Activation du bouton vocal (coin inférieur droit)
- [ ] Reconnaissance vocale en français
- [ ] Synthèse vocale (lecture des instructions)
- [ ] Navigation par commandes vocales
- [ ] Accessibilité pour analphabètes

### 5. Responsivité
- [ ] Page de connexion sur mobile
- [ ] Dashboard donneur sur mobile
- [ ] Dashboard hôpital sur mobile
- [ ] Navbar responsive (menu hamburger)
- [ ] Sidebar mobile avec overlay
- [ ] Tables responsive
- [ ] Formulaires responsive

### 6. Notifications
- [ ] Email de bienvenue (nouveau donneur)
- [ ] Email de validation hôpital
- [ ] Notifications de nouvelles demandes
- [ ] Alertes urgentes

---

## 🐛 Tests et Débogage

### Activer le Mode Debug (Développement uniquement)

Dans le fichier `.env`, modifier :
```env
DEBUG=True
```

**⚠️ IMPORTANT :** Ne JAMAIS mettre `DEBUG=True` en production !

### Consulter les Logs

Les logs s'affichent dans le terminal où le serveur est lancé.

### Accéder à la Base de Données

**Via Django Admin :**
- URL : http://127.0.0.1:8000/admin/
- Email : romualdndri9@gmail.com
- Mot de passe : romuald2005

**Via pgAdmin (PostgreSQL) :**
1. Ouvrir pgAdmin
2. Se connecter au serveur localhost
3. Naviguer vers : Servers > PostgreSQL > Databases > dont_sang_plus_db

### Commandes Utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un super utilisateur
python manage.py createsuperuser

# Lancer les tests
python manage.py test

# Shell Django (interactif)
python manage.py shell

# Collecter les fichiers statiques
python manage.py collectstatic

# Nettoyer les sessions expirées
python manage.py clearsessions
```

---

## 🔧 Améliorations à Apporter

### Priorité Haute 🔴
- [ ] Tests unitaires (models, views, forms)
- [ ] Validation des données (sécurité)
- [ ] Gestion des erreurs (pages 404, 500)
- [ ] Performance des requêtes (N+1 queries)
- [ ] Sécurité CSRF complète
- [ ] Rate limiting (anti-spam)

### Priorité Moyenne 🟡
- [ ] Système de notifications en temps réel (WebSockets)
- [ ] Export des données (CSV, PDF)
- [ ] Statistiques avancées (graphiques)
- [ ] Géolocalisation des donneurs
- [ ] Calcul de distance hôpital-donneur
- [ ] Système de rappel automatique (3 mois)

### Priorité Basse 🟢
- [ ] Mode sombre (dark mode)
- [ ] Multi-langues (FR, EN)
- [ ] PWA (Progressive Web App)
- [ ] Application mobile (React Native)
- [ ] Intégration SMS
- [ ] API REST (pour mobile app)

---

## 📝 Bonnes Pratiques

### Code Style
- Suivre PEP 8 pour Python
- Commenter le code complexe
- Nommer les variables de manière explicite
- Utiliser des docstrings pour les fonctions

### Git Workflow
1. Créer une branche pour chaque feature :
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```

2. Commit réguliers avec messages clairs :
   ```bash
   git add .
   git commit -m "feat: Ajout système de notifications"
   ```

3. Push et créer une Pull Request :
   ```bash
   git push origin feature/nom-de-la-feature
   ```

4. Code review avant merge

### Conventions de Nommage
- **Branches :** `feature/`, `bugfix/`, `hotfix/`
- **Commits :** `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`
- **Fonctions :** snake_case (ex: `get_user_profile`)
- **Classes :** PascalCase (ex: `BloodRequest`)
- **Constantes :** UPPER_CASE (ex: `MAX_DONATIONS`)

---

## 🚨 Problèmes Connus

### 1. WhiteNoise Not Installed
**Erreur :** `ModuleNotFoundError: No module named 'whitenoise'`  
**Solution :**
```bash
pip install whitenoise==6.6.0
```

### 2. Base de Données Non Connectée
**Erreur :** `connection to server at "localhost" ... failed`  
**Solution :** Vérifier que PostgreSQL est démarré

### 3. Fichiers Statiques Non Chargés
**Solution :**
```bash
python manage.py collectstatic --no-input
```

### 4. Migrations en Conflit
**Solution :**
```bash
python manage.py migrate --fake accounts zero
python manage.py migrate accounts
```

---

## 📧 Contact et Support

### Chef de Projet
**KONAN Romuald**
- 📧 Email : romualdndri9@gmail.com
- 💻 GitHub : https://github.com/romualdKO
- 📱 Téléphone : [Votre numéro]

### Repository GitHub
- 🔗 URL : https://github.com/romualdKO/ROMI
- 🐛 Issues : https://github.com/romualdKO/ROMI/issues
- 📖 Wiki : https://github.com/romualdKO/ROMI/wiki

### Communication
- **Urgent :** Email + Appel téléphonique
- **Bugs :** Créer une issue sur GitHub
- **Features :** Discussion via Pull Request
- **Questions :** Email ou GitHub Discussions

---

## 📊 Objectifs du Projet

### Court Terme (1 mois)
- ✅ MVP fonctionnel (Fait)
- ✅ Assistant vocal IA (Fait)
- ✅ Système de récompenses (Fait)
- [ ] Tests complets
- [ ] Documentation API
- [ ] Déploiement sur Render

### Moyen Terme (3 mois)
- [ ] Application mobile
- [ ] Intégration SMS
- [ ] Géolocalisation
- [ ] Notifications push
- [ ] Statistiques avancées

### Long Terme (6 mois)
- [ ] Déploiement national (Côte d'Ivoire)
- [ ] Partenariat avec CNTS
- [ ] Expansion régionale (Afrique de l'Ouest)
- [ ] 10,000+ utilisateurs actifs
- [ ] 1,000+ vies sauvées

---

## 🎓 Ressources d'Apprentissage

### Documentation Officielle
- Django : https://docs.djangoproject.com/
- PostgreSQL : https://www.postgresql.org/docs/
- Bootstrap : https://getbootstrap.com/docs/

### Tutoriels Recommandés
- Django Girls : https://tutorial.djangogirls.org/
- Real Python : https://realpython.com/
- MDN Web Docs : https://developer.mozilla.org/

### Outils Utiles
- Postman : Test des APIs
- pgAdmin : Gestion PostgreSQL
- VS Code : Éditeur recommandé
- Git : Contrôle de version

---

## ✅ Checklist Avant de Commencer

- [ ] Python 3.11+ installé
- [ ] PostgreSQL installé et configuré
- [ ] Git installé
- [ ] Repository cloné
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] Base de données migrée
- [ ] Compte super admin créé
- [ ] Serveur lancé avec succès
- [ ] Page http://127.0.0.1:8000/ accessible

---

## 🙏 Merci !

Merci de contribuer à **Don Sang Plus** ! Chaque ligne de code, chaque test, chaque suggestion nous rapproche de notre objectif : **sauver des vies grâce à la technologie**.

Ensemble, nous pouvons faire une différence ! 🩸❤️

---

**Version du Document :** 1.0  
**Dernière Mise à Jour :** 26 Novembre 2025  
**Auteur :** KONAN Romuald - ESATIC
