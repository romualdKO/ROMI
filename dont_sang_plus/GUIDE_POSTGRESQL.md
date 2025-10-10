# 🗄️ Guide d'installation PostgreSQL pour Don Sang Plus

## Étape 1 : Installation de PostgreSQL

### Option A : Installation manuelle
1. Téléchargez PostgreSQL depuis : https://www.postgresql.org/download/windows/
2. Exécutez l'installateur
3. **IMPORTANT** : Notez le mot de passe que vous définissez pour l'utilisateur `postgres`
4. Port par défaut : 5432 (garder)
5. Cochez "Launch Stack Builder" à la fin (optionnel)

### Option B : Installation avec Chocolatey (si installé)
```powershell
choco install postgresql
```

## Étape 2 : Configuration du mot de passe dans .env

Après installation, éditez le fichier `.env` et remplacez :
```
DB_PASSWORD=your_password_here
```
par votre vraie mot de passe PostgreSQL.

## Étape 3 : Création de la base de données

Une fois PostgreSQL installé, exécutez ces commandes :

### Connexion à PostgreSQL
```powershell
# Remplacez "votre_mot_de_passe" par votre vrai mot de passe
psql -U postgres -h localhost
```

### Création de la base de données
```sql
CREATE DATABASE dont_sang_plus_db;
CREATE USER dont_sang_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE dont_sang_plus_db TO dont_sang_user;
\q
```

## Étape 4 : Test de connexion Django

```powershell
python manage.py migrate
```

## ⚠️ Dépannage courant

### Si "psql" n'est pas reconnu :
1. Ajoutez PostgreSQL au PATH :
   - Chemin typique : `C:\Program Files\PostgreSQL\16\bin`
2. Ou utilisez le chemin complet :
   ```powershell
   "C:\Program Files\PostgreSQL\16\bin\psql" -U postgres
   ```

### Si erreur de connexion :
1. Vérifiez que le service PostgreSQL est démarré
2. Vérifiez le mot de passe dans le fichier `.env`
3. Vérifiez que le port 5432 n'est pas bloqué

## 🔄 Prochaines étapes

Une fois PostgreSQL installé et configuré :
1. Exécuter les migrations Django
2. Créer un superutilisateur
3. Tester l'application

## 📞 Support

Si vous rencontrez des problèmes, vérifiez :
- Services Windows → PostgreSQL est en cours d'exécution
- Pare-feu → Port 5432 autorisé
- Mot de passe correct dans `.env`