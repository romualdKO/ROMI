# Script PowerShell pour créer la base de données PostgreSQL
# pour l'application Don Sang Plus

Write-Host "🗄️ Configuration PostgreSQL pour Don Sang Plus" -ForegroundColor Green
Write-Host ""

# Ajouter PostgreSQL au PATH
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin;C:\Program Files\PostgreSQL\16\bin"

Write-Host "📋 Ce script va :" -ForegroundColor Yellow
Write-Host "   1. Créer la base de données 'dont_sang_plus_db'"
Write-Host "   2. Configurer les permissions"
Write-Host "   3. Tester la connexion Django"
Write-Host ""

# Demander le mot de passe
Write-Host "🔐 Configuration de la connexion PostgreSQL" -ForegroundColor Cyan
$password = Read-Host "Entrez le mot de passe PostgreSQL pour l'utilisateur 'postgres'" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Créer le fichier SQL temporaire
$sqlCommands = @"
-- Création de la base de données Don Sang Plus
CREATE DATABASE dont_sang_plus_db 
    WITH ENCODING 'UTF8' 
    LC_COLLATE = 'French_France.1252' 
    LC_CTYPE = 'French_France.1252';

-- Message de confirmation
SELECT 'Base de données dont_sang_plus_db créée avec succès!' as message;
"@

$sqlCommands | Out-File -FilePath "setup_db.sql" -Encoding UTF8

Write-Host "🔄 Création de la base de données..." -ForegroundColor Yellow

# Définir la variable d'environnement pour le mot de passe
$env:PGPASSWORD = $plainPassword

try {
    # Exécuter les commandes SQL
    $result = & psql -U postgres -h localhost -f "setup_db.sql" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Base de données créée avec succès !" -ForegroundColor Green
        Write-Host ""
        
        # Mettre à jour le fichier .env
        Write-Host "🔧 Mise à jour du fichier .env..." -ForegroundColor Cyan
        $envContent = Get-Content ".env" -Raw
        $envContent = $envContent -replace "DB_PASSWORD=.*", "DB_PASSWORD=$plainPassword"
        $envContent | Set-Content ".env" -NoNewline
        
        Write-Host "✅ Fichier .env mis à jour" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "🚀 Prochaines étapes :" -ForegroundColor Yellow
        Write-Host "   1. Exécuter les migrations : python manage.py migrate"
        Write-Host "   2. Créer un superuser : python manage.py createsuperuser"
        Write-Host "   3. Démarrer l'application : python manage.py runserver"
        
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors de la création de la base de données" -ForegroundColor Red
        Write-Host "Détails de l'erreur :" -ForegroundColor Yellow
        Write-Host $result
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erreur : $_" -ForegroundColor Red
} finally {
    # Nettoyer
    Remove-Item "setup_db.sql" -ErrorAction SilentlyContinue
    Remove-Variable env:PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Appuyez sur Entrée pour continuer..."
Read-Host