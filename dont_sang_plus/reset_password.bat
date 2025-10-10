@echo off
echo 🔐 Réinitialisation du mot de passe PostgreSQL
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Privilèges administrateur détectés
) else (
    echo ❌ Ce script doit être exécuté en tant qu'administrateur !
    echo Clic droit sur ce fichier et choisir "Exécuter en tant qu'administrateur"
    pause
    exit /b 1
)

set PGPATH=C:\Program Files\PostgreSQL\17
set DATAPATH=%PGPATH%\data
set CONFIGFILE=%DATAPATH%\pg_hba.conf

echo 📂 Vérification des fichiers...
if not exist "%CONFIGFILE%" (
    echo ❌ Fichier de configuration non trouvé : %CONFIGFILE%
    pause
    exit /b 1
)

echo 💾 Sauvegarde de la configuration...
copy "%CONFIGFILE%" "%CONFIGFILE%.backup" >nul

echo 🔧 Modification temporaire de l'authentification...
REM Remplacer scram-sha-256 par trust temporairement
powershell -Command "(Get-Content '%CONFIGFILE%') -replace 'scram-sha-256', 'trust' | Set-Content '%CONFIGFILE%'"

echo 🔄 Redémarrage de PostgreSQL...
net stop postgresql-x64-17
timeout /t 2 /nobreak >nul
net start postgresql-x64-17
timeout /t 3 /nobreak >nul

echo.
set /p NEW_PASSWORD="🔑 Entrez le nouveau mot de passe pour postgres: "

echo 💾 Application du nouveau mot de passe...
set PATH=%PATH%;%PGPATH%\bin
echo ALTER USER postgres PASSWORD '%NEW_PASSWORD%'; | psql -U postgres -h localhost -d postgres

if %ERRORLEVEL% == 0 (
    echo ✅ Mot de passe modifié avec succès !
    
    REM Mettre à jour le fichier .env s'il existe
    if exist ".env" (
        echo 🔧 Mise à jour du fichier .env...
        powershell -Command "(Get-Content '.env') -replace 'DB_PASSWORD=.*', 'DB_PASSWORD=%NEW_PASSWORD%' | Set-Content '.env'"
        echo ✅ Fichier .env mis à jour
    )
) else (
    echo ❌ Erreur lors de la modification du mot de passe
)

echo 🔒 Restauration de la sécurité...
copy "%CONFIGFILE%.backup" "%CONFIGFILE%" >nul
del "%CONFIGFILE%.backup" >nul

echo 🔄 Redémarrage final de PostgreSQL...
net stop postgresql-x64-17
timeout /t 2 /nobreak >nul
net start postgresql-x64-17

echo.
echo ✅ Processus terminé !
echo 📋 Vos nouvelles informations de connexion :
echo    - Utilisateur : postgres
echo    - Mot de passe : %NEW_PASSWORD%
echo    - Host : localhost
echo    - Port : 5432
echo.
pause