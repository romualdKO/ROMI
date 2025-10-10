# Script simple pour définir le mot de passe PostgreSQL
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"

Write-Host "🔑 Configuration du mot de passe PostgreSQL..." -ForegroundColor Yellow
Write-Host "Quand le mot de passe sera demandé, appuyez simplement sur ENTRÉE" -ForegroundColor Cyan
Write-Host ""

# Définir le mot de passe
$password = "dongsang2024"
$env:PGPASSWORD = ""

# Commande SQL
$sqlCommand = "ALTER USER postgres PASSWORD '$password';"

# Écrire dans un fichier temporaire
$sqlCommand | Out-File -FilePath "temp_password.sql" -Encoding UTF8

# Exécuter
try {
    Write-Host "Exécution de la commande..." -ForegroundColor Green
    & psql -U postgres -h localhost -d postgres -f temp_password.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mot de passe défini avec succès !" -ForegroundColor Green
        Write-Host "Nouveau mot de passe : $password" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Erreur lors de la définition du mot de passe" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erreur : $_" -ForegroundColor Red
} finally {
    Remove-Item "temp_password.sql" -ErrorAction SilentlyContinue
}

Write-Host ""
Read-Host "Appuyez sur Entrée pour continuer"