# Script PowerShell pour resoudre l'authentification PostgreSQL
Write-Host "Resolution du probleme d'authentification PostgreSQL" -ForegroundColor Green
Write-Host ""

# Verifier les privileges administrateur
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Lancement en tant qu'administrateur..." -ForegroundColor Yellow
    Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$configFile = "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
$backupFile = "$configFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

try {
    Write-Host "Localisation du fichier de configuration..." -ForegroundColor Cyan
    if (-not (Test-Path $configFile)) {
        Write-Host "Fichier de configuration non trouve : $configFile" -ForegroundColor Red
        exit 1
    }

    Write-Host "Sauvegarde de la configuration..." -ForegroundColor Cyan
    Copy-Item $configFile $backupFile -Force
    Write-Host "Sauvegarde creee : $backupFile" -ForegroundColor Green

    Write-Host "Modification de l'authentification (trust temporaire)..." -ForegroundColor Cyan
    $content = Get-Content $configFile
    $newContent = $content -replace "scram-sha-256", "trust"
    $newContent | Set-Content $configFile -Force

    Write-Host "Redemarrage du service PostgreSQL..." -ForegroundColor Cyan
    Restart-Service postgresql-x64-17 -Force
    Start-Sleep -Seconds 3

    Write-Host "Definition du mot de passe..." -ForegroundColor Cyan
    $env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
    $result = echo "ALTER USER postgres PASSWORD 'dongsang2024';" | psql -U postgres -h localhost -d postgres 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Mot de passe defini avec succes !" -ForegroundColor Green
    } else {
        Write-Host "Resultat : $result" -ForegroundColor Yellow
    }

    Write-Host "Restauration de la securite..." -ForegroundColor Cyan
    Copy-Item $backupFile $configFile -Force
    Restart-Service postgresql-x64-17 -Force
    Start-Sleep -Seconds 2

    Write-Host "Configuration terminee !" -ForegroundColor Green
    Write-Host "Informations de connexion :" -ForegroundColor Yellow
    Write-Host "  - Base de donnees : dont_sang_plus_db" -ForegroundColor White
    Write-Host "  - Utilisateur : postgres" -ForegroundColor White
    Write-Host "  - Mot de passe : dongsang2024" -ForegroundColor White
    Write-Host ""
    Write-Host "Prochaine etape : python manage.py migrate" -ForegroundColor Green

} catch {
    Write-Host "Erreur : $($_.Exception.Message)" -ForegroundColor Red
    if (Test-Path $backupFile) {
        Write-Host "Restauration de la sauvegarde..." -ForegroundColor Yellow
        Copy-Item $backupFile $configFile -Force
        Restart-Service postgresql-x64-17 -Force
    }
}

Write-Host ""
Read-Host "Appuyez sur Entree pour continuer"