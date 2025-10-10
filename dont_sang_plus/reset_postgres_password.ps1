# Script PowerShell pour réinitialiser le mot de passe PostgreSQL
# ATTENTION : Ce script doit être exécuté en tant qu'administrateur

Write-Host "🔐 Réinitialisation du mot de passe PostgreSQL" -ForegroundColor Red
Write-Host "⚠️  ATTENTION : Ce script modifie temporairement la sécurité PostgreSQL" -ForegroundColor Yellow
Write-Host ""

# Vérifier les privilèges administrateur
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Ce script doit être exécuté en tant qu'administrateur !" -ForegroundColor Red
    Write-Host "Clic droit sur PowerShell → 'Exécuter en tant qu'administrateur'" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

$postgrePath = "C:\Program Files\PostgreSQL\17"
$dataPath = "$postgrePath\data"
$configFile = "$dataPath\pg_hba.conf"
$backupFile = "$dataPath\pg_hba.conf.backup"

Write-Host "📂 Vérification des fichiers PostgreSQL..." -ForegroundColor Cyan

if (-not (Test-Path $configFile)) {
    Write-Host "❌ Fichier de configuration non trouvé : $configFile" -ForegroundColor Red
    Write-Host "Vérifiez que PostgreSQL 17 est installé" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

try {
    Write-Host "💾 Sauvegarde de la configuration actuelle..." -ForegroundColor Cyan
    Copy-Item $configFile $backupFile -Force
    
    Write-Host "🔧 Modification temporaire de l'authentification..." -ForegroundColor Cyan
    $config = Get-Content $configFile
    $newConfig = $config -replace "host\s+all\s+all\s+127\.0\.0\.1/32\s+scram-sha-256", "host    all             all             127.0.0.1/32            trust"
    $newConfig = $newConfig -replace "host\s+all\s+all\s+::1/128\s+scram-sha-256", "host    all             all             ::1/128                 trust"
    $newConfig | Set-Content $configFile
    
    Write-Host "🔄 Redémarrage du service PostgreSQL..." -ForegroundColor Cyan
    Restart-Service postgresql-x64-17 -Force
    Start-Sleep -Seconds 3
    
    Write-Host "🔑 Saisie du nouveau mot de passe..." -ForegroundColor Green
    $newPassword = Read-Host "Entrez le nouveau mot de passe pour 'postgres'" -AsSecureString
    $plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($newPassword))
    
    Write-Host "💾 Application du nouveau mot de passe..." -ForegroundColor Cyan
    $env:PATH += ";$postgrePath\bin"
    
    $sqlCommand = "ALTER USER postgres PASSWORD '$plainPassword';"
    $sqlCommand | & psql -U postgres -h localhost -d postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mot de passe modifié avec succès !" -ForegroundColor Green
        
        # Mettre à jour le fichier .env
        if (Test-Path ".env") {
            Write-Host "🔧 Mise à jour du fichier .env..." -ForegroundColor Cyan
            $envContent = Get-Content ".env" -Raw
            $envContent = $envContent -replace "DB_PASSWORD=.*", "DB_PASSWORD=$plainPassword"
            $envContent | Set-Content ".env" -NoNewline
            Write-Host "✅ Fichier .env mis à jour" -ForegroundColor Green
        }
        
    } else {
        Write-Host "❌ Erreur lors de la modification du mot de passe" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur : $_" -ForegroundColor Red
} finally {
    Write-Host "🔒 Restauration de la sécurité..." -ForegroundColor Cyan
    Copy-Item $backupFile $configFile -Force
    Restart-Service postgresql-x64-17 -Force
    Remove-Item $backupFile -ErrorAction SilentlyContinue
    
    Write-Host ""
    Write-Host "✅ Réinitialisation terminée !" -ForegroundColor Green
    Write-Host "📋 Informations de connexion :" -ForegroundColor Yellow
    Write-Host "   - Utilisateur : postgres"
    Write-Host "   - Mot de passe : [celui que vous avez saisi]"
    Write-Host "   - Host : localhost"
    Write-Host "   - Port : 5432"
}

Write-Host ""
Read-Host "Appuyez sur Entrée pour continuer"