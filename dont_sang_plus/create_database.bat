@echo off
echo 🗄️ Script de création de la base de données PostgreSQL
echo.

REM Ajouter PostgreSQL au PATH
set PATH=%PATH%;C:\Program Files\PostgreSQL\17\bin;C:\Program Files\PostgreSQL\16\bin

echo Tentative de création de la base de données...
echo.

REM Commandes SQL à exécuter
echo CREATE DATABASE dont_sang_plus_db; > create_db.sql
echo ALTER DATABASE dont_sang_plus_db OWNER TO postgres; >> create_db.sql

echo ⚠️  Vous allez être invité à saisir le mot de passe PostgreSQL
echo.

REM Exécuter le script SQL
psql -U postgres -h localhost -f create_db.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Base de données 'dont_sang_plus_db' créée avec succès !
    echo.
    echo 📋 Informations de connexion :
    echo    - Base de données : dont_sang_plus_db
    echo    - Utilisateur : postgres
    echo    - Host : localhost
    echo    - Port : 5432
    echo.
    echo 🔄 Prochaines étapes :
    echo    1. Mettez à jour le mot de passe dans le fichier .env
    echo    2. Exécutez : python manage.py migrate
    echo    3. Créez un superuser : python manage.py createsuperuser
) else (
    echo.
    echo ❌ Erreur lors de la création de la base de données
    echo 💡 Vérifiez :
    echo    - Le service PostgreSQL est démarré
    echo    - Le mot de passe est correct
    echo    - L'utilisateur postgres existe
)

REM Nettoyer le fichier temporaire
del create_db.sql 2>nul

echo.
pause