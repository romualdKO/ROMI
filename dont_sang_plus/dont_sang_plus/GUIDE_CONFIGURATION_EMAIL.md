# 📧 GUIDE CONFIGURATION EMAIL GMAIL - DON SANG PLUS

## 🎯 Objectif
Recevoir automatiquement un email sur `romualdndri9@gmail.com` quand un hôpital s'inscrit.

## ✅ Étapes de configuration

### 1. Activer la validation en 2 étapes sur Gmail
1. Allez sur https://myaccount.google.com/security
2. Cliquez sur "Validation en 2 étapes"
3. Suivez les instructions pour activer

### 2. Créer un App Password
1. Allez sur https://myaccount.google.com/apppasswords
2. Sélectionnez "Mail" comme application
3. Sélectionnez "Autre" comme appareil
4. Nommez-le "Don Sang Plus"
5. Cliquez sur "Générer"
6. **COPIEZ** le mot de passe de 16 caractères (format: xxxx xxxx xxxx xxxx)

### 3. Configurer le fichier .env
1. Ouvrez le fichier `.env` dans le dossier `dont_sang_plus/`
2. Collez le mot de passe généré dans `EMAIL_HOST_PASSWORD=` (sans espaces)
   
   Exemple :
   ```
   EMAIL_HOST_USER=romualdndri9@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ```

3. Sauvegardez le fichier

### 4. Redémarrer le serveur Django
1. Dans le terminal PowerShell, appuyez sur `CTRL+C` pour arrêter le serveur
2. Relancez avec : `python manage.py runserver 8001`

## 🧪 Tester l'envoi d'email

### Option A : Inscription d'un nouvel hôpital
1. Allez sur http://127.0.0.1:8001/accounts/hospital-signup/
2. Remplissez le formulaire d'inscription
3. Soumettez le formulaire
4. ✅ Vous devriez recevoir un email sur `romualdndri9@gmail.com` avec :
   - Le nom de l'hôpital
   - Email et téléphone
   - Lien direct vers l'admin pour valider

### Option B : Mode console (si pas de mot de passe configuré)
- Les emails s'afficheront dans le terminal PowerShell
- Cherchez les lignes commençant par :
  ```
  Subject: 🚨 NOUVEAU HÔPITAL À VALIDER
  From: romualdndri9@gmail.com
  To: romualdndri9@gmail.com
  ```

## 📋 Que se passe-t-il après l'inscription d'un hôpital ?

1. **Email automatique à l'admin** (`romualdndri9@gmail.com`) :
   - Sujet : "🚨 NOUVEAU HÔPITAL À VALIDER - URGENT"
   - Contient toutes les infos de l'hôpital
   - Lien direct pour valider dans l'admin Django

2. **Email de confirmation à l'hôpital** :
   - Confirme que la demande a été reçue
   - Indique un délai de 24-48h pour validation

3. **L'hôpital ne peut PAS se connecter** tant que son compte n'est pas validé

## 🔐 Valider un hôpital dans l'admin

1. Allez sur http://127.0.0.1:8001/admin/
2. Connectez-vous avec votre compte superuser
3. Cliquez sur "Utilisateurs personnalisés" (CustomUser)
4. Trouvez l'hôpital avec `verification_status = pending`
5. Éditez l'hôpital :
   - ✅ Cochez `is_verified`
   - Changez `verification_status` de "pending" à "approved"
6. Sauvegardez
7. ✅ L'hôpital peut maintenant se connecter !

## ⚠️ Problèmes courants

### "SMTPAuthenticationError"
- Vérifiez que la validation en 2 étapes est activée
- Vérifiez que l'App Password est correct (16 caractères sans espaces)
- Assurez-vous d'utiliser `romualdndri9@gmail.com` pas un autre email

### "Connection refused"
- Vérifiez votre connexion Internet
- Vérifiez que le port 587 n'est pas bloqué par un firewall

### Les emails ne partent pas
- Vérifiez que `EMAIL_HOST_PASSWORD` n'est PAS vide dans `.env`
- Redémarrez le serveur après modification du `.env`

## 📝 Notes importantes

- Le fichier `.env` contient des informations sensibles (mot de passe)
- **NE JAMAIS** commiter `.env` sur Git
- Le `.gitignore` devrait déjà exclure `.env`
- Utilisez `.env.example` comme template sans les vrais mots de passe

## ✅ Configuration actuelle

- Email admin : `romualdndri9@gmail.com`
- Email envoyeur : `romualdndri9@gmail.com`
- Serveur SMTP : `smtp.gmail.com:587` (TLS)
- Mode : **SMTP si mot de passe configuré, sinon Console**

---

**🚀 Une fois configuré, vous recevrez automatiquement un email à chaque nouvelle inscription d'hôpital !**
