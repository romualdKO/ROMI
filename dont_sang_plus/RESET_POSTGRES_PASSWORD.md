# 🔐 Guide de réinitialisation du mot de passe PostgreSQL

## Méthode 1 : Réinitialisation via pg_hba.conf (Recommandée)

### Étape 1 : Localiser le fichier de configuration
```powershell
# Trouver le fichier pg_hba.conf
Get-ChildItem "C:\Program Files\PostgreSQL\17\data\" -Name "pg_hba.conf"
```

### Étape 2 : Modifier temporairement l'authentification
1. Ouvrir le fichier `C:\Program Files\PostgreSQL\17\data\pg_hba.conf` en tant qu'administrateur
2. Trouver la ligne qui ressemble à :
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   ```
3. Remplacer `scram-sha-256` par `trust` temporairement :
   ```
   host    all             all             127.0.0.1/32            trust
   ```

### Étape 3 : Redémarrer PostgreSQL
```powershell
Restart-Service postgresql-x64-17
```

### Étape 4 : Se connecter et changer le mot de passe
```powershell
psql -U postgres -h localhost
ALTER USER postgres PASSWORD 'nouveau_mot_de_passe';
\q
```

### Étape 5 : Remettre l'authentification sécurisée
1. Remettre `trust` en `scram-sha-256` dans pg_hba.conf
2. Redémarrer le service : `Restart-Service postgresql-x64-17`

---

## Méthode 2 : Via l'interface graphique pgAdmin

Si pgAdmin est installé :
1. Ouvrir pgAdmin
2. Clic droit sur le serveur PostgreSQL
3. Properties → Connection
4. Changer le mot de passe

---

## Méthode 3 : Réinstaller PostgreSQL (dernière option)

Si les autres méthodes échouent, réinstaller PostgreSQL avec un nouveau mot de passe.

---

## Script automatique de réinitialisation

Voulez-vous que je crée un script automatique pour faire cela ?