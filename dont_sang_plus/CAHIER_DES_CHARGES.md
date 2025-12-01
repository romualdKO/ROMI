# 📋 CAHIER DES CHARGES - DON SANG PLUS

**Version :** 2.0 (Réaliste)  
**Date :** 29 Novembre 2025  
**Auteur :** KONAN Romuald - ESATIC  
**Projet :** Plateforme de Mise en Relation Donneurs-Hôpitaux  

---

## 📌 1. VUE D'ENSEMBLE

### 1.1 Nom du Projet
**DON SANG PLUS** - Plateforme Web de Mise en Relation Donneurs-Hôpitaux

### 1.2 Problématique

**Situation :** En Côte d'Ivoire, 15,000 poches de sang sont nécessaires/mois, mais seulement 8,000 sont collectées (déficit de 47%). Les hôpitaux mettent 24-72h pour trouver un donneur compatible, ce qui coûte des vies.

**Problèmes :**
- Hôpitaux : Recherche manuelle, pas de base de données centralisée
- Donneurs : Manque d'information, pas de reconnaissance
- Délai trop long en cas d'urgence

---

## 🎯 2. OBJECTIFS DU PROJET

### 2.1 Objectif Général
Créer une **plateforme digitale complète** permettant de connecter instantanément les hôpitaux en besoin de sang avec des donneurs volontaires, tout en offrant au CNTS-CI des outils de gestion moderne.

### 2.2 Objectifs Spécifiques

#### Pour les Donneurs :
1. ✅ Faciliter l'inscription et la gestion du profil donneur
2. ✅ Recevoir des notifications ciblées selon le groupe sanguin
3. ✅ Suivre l'impact de leurs dons (vies sauvées)
4. ✅ Obtenir des récompenses et badges de fidélisation
5. ✅ Accéder à un assistant vocal IA (pour analphabètes)

#### Pour les Hôpitaux :
1. ✅ Publier des demandes de sang en temps réel
2. ✅ Filtrer les donneurs par groupe sanguin et localisation
3. ✅ Recevoir des réponses rapides (< 2 heures)
4. ✅ Gérer les rendez-vous de don
5. ✅ Commander des poches au CNTS

#### Pour le CNTS-CI :
1. ✅ Dashboard de gestion des stocks en temps réel
2. ✅ Traçabilité complète des poches (du donneur au patient)
## 🎯 2. OBJECTIF

Connecter instantanément les hôpitaux avec des donneurs volontaires compatibles, réduire le délai de recherche de 24-72h à < 2h.
3. **Dashboard Donneur**
   - Statistiques personnelles :
     - Nombre total de dons
     - Dernière date de don
     - Prochaine date de don possible
     - Vies sauvées (1 don = 3 vies)
## 📦 3. FONCTIONNALITÉS ACTUELLES

### 🩸 ESPACE DONNEUR ✅
1. Inscription/Connexion (email + mot de passe)
2. Profil (groupe sanguin, localisation, photo, disponibilité)
3. Dashboard avec statistiques (total dons, vies sauvées)
4. Système de badges (Bronze, Argent, Or, Platine)
5. Voir demandes de sang compatibles
6. Répondre aux demandes (accepter/refuser)
7. Chat avec hôpitaux
8. Notifications email
9. **Assistant vocal IA** (reconnaissance vocale français)

### 🏥 ESPACE HÔPITAL ✅
1. Inscription (validation admin requise)
2. Créer demandes de sang (groupe, quantité, urgence)
3. Dashboard avec statistiques
4. Voir réponses des donneurs
5. Accepter/Refuser les réponses
6. Chat avec donneurs
7. Historique des demandes
8. Notifications email

### 🔐 SÉCURITÉ ✅
- HTTPS, hashage mots de passe, protection CSRF
- Responsive design (mobile-first)
### 4.2 Technologies Utilisées

#### Backend :
- **Framework** : Django 5.2.7 (Python)
- **Base de données** : PostgreSQL 16
- **ORM** : Django ORM
- **Authentication** : Django Auth + Custom Email Backend
- **API** : Django REST Framework (future)

#### Frontend :
- **HTML5** + **CSS3**
- **JavaScript ES6+** (Vanilla)
- **Bootstrap 5.3.0**
- **Font Awesome 6.4.0**
- **Responsive Design** (mobile-first)

#### Serveur Web :
- **Gunicorn** (WSGI)
- **WhiteNoise** (fichiers statiques)
- **Nginx** (reverse proxy - future)

#### IA et Fonctionnalités Avancées :
- **Web Speech API** (assistant vocal)
- **Geolocation API** (localisation)
- **Notifications API** (push notifications)
- **QR Code** : python-qrcode (traçabilité)
- **PDF Generation** : ReportLab (factures, certificats)
- **Email** : SMTP Gmail (notifications)

#### DevOps :
- **Hébergement** : Render.com
- **CI/CD** : GitHub Actions (future)
- **Monitoring** : Sentry (future)
- **Logs** : Django Logging

### 4.3 Base de Données

#### Modèles Principaux :

**1. CustomUser (accounts)**
```python
- email (unique)
- user_type (donor/hospital/cnts)
- first_name, last_name
- phone
- birth_date
- blood_type
- location
- hospital_name (si hôpital)
- is_available (si donneur)
- total_donations
- last_donation_date
- profile_picture
```

**2. BloodRequest (donations)**
```python
- hospital (FK CustomUser)
- blood_type
- quantity
- urgency_level
- description
- required_date
- status (active/completed/cancelled)
- created_at
```

**3. DonationResponse (donations)**
```python
- request (FK BloodRequest)
- donor (FK CustomUser)
- status (pending/accepted/rejected/completed)
- message
- appointment_date
- created_at
```

**4. BloodStock (donations - NOUVEAU)**
```python
- blood_group
- component (globules_rouges/plasma/plaquettes)
- quantity
- critical_threshold
- center_name
- center_location
- expiry_date
- last_updated
```

**5. BloodBagTraceability (donations - NOUVEAU)**
```python
- bag_id (unique)
- qr_code
- donor (FK)
- blood_group
- collection_date
- is_tested, test_date, test_results
- is_separated, separation_date
- storage_location, storage_temperature
- hospital (FK), dispatch_date, received_date
- transfusion_date, patient_anonymized_id
- status (collected/tested/separated/stored/dispatched/received/transfused)
```

**6. MobileCollection (donations - NOUVEAU)**
```python
- location_name
- location_address
- latitude, longitude
- collection_date
- start_time, end_time
- expected_donors, confirmed_donors, actual_donors
- bags_collected
- status (planned/confirmed/in_progress/completed/cancelled)
```

**7. RareDonor (donations - NOUVEAU)**
```python
- donor (FK)
- rare_blood_group (AB-/B-/A-/O-/Bombay/Rh_null)
- is_active
- priority_contact
- last_contacted
- total_rare_donations
```

**8. HospitalOrder (donations - NOUVEAU)**
```python
- order_number (unique)
- hospital (FK)
- blood_group
- component
- quantity
- urgency
- order_date, required_date, delivery_date
- unit_price, total_price
- status (pending/confirmed/prepared/dispatched/delivered/cancelled)
- tracking_number
```

**9. CNTSStatistics (donations - NOUVEAU)**
```python
- date (unique)
- total_collections, mobile_collections, fixed_center_collections
- total_donations, first_time_donors, repeat_donors
- bags_tested, bags_rejected, rejection_rate
- bags_distributed, hospitals_served
- total_stock, critical_groups
```

### 4.4 Sécurité et Conformité

#### Protection des Données (RGPD) :
- ✅ Consentement explicite lors de l'inscription
- ✅ Droit d'accès aux données personnelles
- ✅ Droit de rectification
- ✅ Droit à l'effacement
- ✅ Chiffrement des données sensibles
- ✅ Anonymisation des données patients

#### Sécurité Applicative :
- ✅ HTTPS obligatoire (SSL/TLS)
- ✅ Protection CSRF (tokens)
- ✅ Hashage des mots de passe (PBKDF2)
- ✅ Validation côté serveur
- ✅ Rate limiting (anti-spam)
- ✅ Sessions sécurisées (cookies HttpOnly)
- ✅ Headers de sécurité (HSTS, X-Frame-Options)

#### Conformité Médicale :
- ✅ Respect du secret médical
- ✅ Traçabilité obligatoire des poches (OMS)
- ✅ Conservation des logs (6 mois minimum)
- ✅ Certification ISO 27001 (future)

---

## 🚀 5. CONTRAINTES TECHNIQUES

### 5.1 Contraintes de Performance
- Temps de chargement < 3 secondes
- Disponibilité 99.9% (SLA)
- Support de 1000+ utilisateurs simultanés
- Base de données optimisée (indexation)
## 🛠️ 4. TECHNOLOGIES

**Backend :** Django 5.2.7 (Python), PostgreSQL  
**Frontend :** HTML5, CSS3, JavaScript (Bootstrap 5, Font Awesome)  
**IA :** Web Speech API (assistant vocal)  
**Hébergement :** Render.com (HTTPS/SSL)  
**Email :** SMTP Gmail
*Ce cahier des charges constitue le référentiel technique et fonctionnel du projet Don Sang Plus. Toute modification doit être validée par le chef de projet et documentée dans l'historique des versions.*
## 📅 5. STATUT ACTUEL

✅ **MVP FONCTIONNEL** (Novembre 2025)
- Authentification complète
- Demandes de sang + réponses
- Chat donneur-hôpital
- Assistant vocal IA
- Système de badges
- Responsive design
- Déploiement Render ready## 💰 6. BUDGET DÉPLOIEMENT NATIONAL (ÉCHELLE CÔTE D'IVOIRE)

### 6.1 PHASE PILOTE (3 mois - Abidjan)

| Poste | Détail | Coût |
|-------|--------|------|
| **Infrastructure Technique** | | |
| Hébergement Render Pro | 21 USD/mois x 3 | 40,000 FCFA |
| Domaine .ci | donsangplus.ci (1 an) | 15,000 FCFA |
| Base données PostgreSQL | 512 MB RAM (inclus Render) | 0 FCFA |
| SSL/HTTPS | Let's Encrypt (gratuit) | 0 FCFA |
| **Communication** | | |
| SMS (Twilio) | 1,000 SMS test x 50 FCFA | 50,000 FCFA |
| Emails (SendGrid) | 10,000 emails gratuits/mois | 0 FCFA |
| **Formation & Sensibilisation** | | |
| Formation hôpitaux (5) | 2h/hôpital x 25,000 FCFA | 125,000 FCFA |
| Matériel formation | Guides, affiches | 50,000 FCFA |
| Campagne réseaux sociaux | Facebook Ads | 100,000 FCFA |
| **Personnel** | | |
| Support technique (3 mois) | Étudiant stagiaire | 150,000 FCFA |
| **Matériel** | | |
| Ordinateur portable | Pour support sur site | 300,000 FCFA |
| **Imprévus (10%)** | | 83,000 FCFA |

**TOTAL PILOTE (3 mois) : 913,000 FCFA (~1,400 EUR)**

---

### 6.2 DÉPLOIEMENT NATIONAL (Année 1)

| Poste | Détail | Coût Annuel |
|-------|--------|-------------|
| **Infrastructure (An 1)** | | |
| Hébergement Render Business | 85 USD/mois (1GB RAM, 100k req/mois) | 600,000 FCFA |
| Domaine .ci | Renouvellement | 15,000 FCFA |
| Backup automatique | Render Backup (7 jours) | 120,000 FCFA |
| CDN (Cloudflare Pro) | Cache statique, DDoS protection | 180,000 FCFA |
| Monitoring (Sentry) | Error tracking, 50k events/mois | 250,000 FCFA |
| **Communication (An 1)** | | |
| SMS (50,000 SMS) | Notifications urgentes x 50 FCFA | 2,500,000 FCFA |
| Emails (SendGrid) | 100,000 emails/mois | 300,000 FCFA |
| WhatsApp Business API | Notifications (future) | 500,000 FCFA |
| **Personnel (An 1)** | | |
| Développeur full-time | Maintenance + nouvelles features | 3,600,000 FCFA |
| Support utilisateurs | 2 personnes à mi-temps | 1,800,000 FCFA |
| Community manager | Réseaux sociaux, sensibilisation | 1,200,000 FCFA |
| **Formation & Déploiement** | | |
| Formation 50 hôpitaux | 2h x 25,000 FCFA | 1,250,000 FCFA |
| Formation 10 centres CNTS | 1 journée x 100,000 FCFA | 1,000,000 FCFA |
| Guides utilisateurs | Impression 1,000 exemplaires | 200,000 FCFA |
| Vidéos tutorielles | Production 10 vidéos | 500,000 FCFA |
| **Marketing (An 1)** | | |
| Campagne TV/Radio | Spots publicitaires nationaux | 3,000,000 FCFA |
| Réseaux sociaux (Ads) | Facebook, Instagram, Twitter | 1,500,000 FCFA |
| Partenariats écoles/universités | 50 universités x 50,000 FCFA | 2,500,000 FCFA |
| Événements de lancement | 5 villes (Abidjan, Bouaké, etc.) | 2,000,000 FCFA |
| Goodies (t-shirts, badges) | 5,000 unités | 1,000,000 FCFA |
| **Matériel & Équipement** | | |
| 3 ordinateurs portables | Équipe support | 900,000 FCFA |
| 3 smartphones | Tests + support mobile | 450,000 FCFA |
| Connexion internet pro | Fibre 50 Mbps x 12 mois | 600,000 FCFA |
| **Partenariats & Certifications** | | |
| Partenariat CNTS-CI | Convention officielle | 500,000 FCFA |
| Conformité RGPD | Audit + mise en conformité | 800,000 FCFA |
| Certification ISO 27001 | Sécurité des données (future) | 2,000,000 FCFA |
| **Assurance & Juridique** | | |
| Assurance responsabilité civile | Protection juridique | 400,000 FCFA |
| Frais juridiques | Contrats, CGU, RGPD | 300,000 FCFA |
| **Imprévus (15%)** | Réserve pour urgences | 4,125,000 FCFA |

**TOTAL ANNÉE 1 (National) : 31,990,000 FCFA (~48,750 EUR)**

---

### 6.3 SYNTHÈSE BUDGÉTAIRE

| Phase | Durée | Budget | Bénéficiaires |
|-------|-------|--------|---------------|
| **Pilote Abidjan** | 3 mois | 913,000 FCFA | 5 hôpitaux, 500 donneurs |
| **Déploiement National** | An 1 | 31,990,000 FCFA | 50 hôpitaux, 5,000 donneurs |
| **TOTAL INVESTISSEMENT** | **15 mois** | **32,903,000 FCFA** | **~50M FCFA** |

---

### 6.4 FINANCEMENT RECHERCHÉ

**Sources de financement possibles :**

## ✅ 7. IMPACT ATTENDU

**KPIs (Année 1) :**
- 5,000 donneurs inscrits
- 50 hôpitaux partenaires
- Délai recherche : 24-72h → < 2h (-95%)
- 2,000+ vies sauvées

---

## 📞 8. CONTACT

**KONAN Romuald**  
📧 romualdk059@gmail.com  
🎓 ESATIC - Promotion 2025  
💻 GitHub : github.com/romualdKO/ROMI

---

**Version :** 2.0 | **Date :** 29 Nov 2025 | **Statut :** ✅ MVP Opérationnel