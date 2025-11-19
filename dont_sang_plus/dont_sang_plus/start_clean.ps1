# Script de démarrage de Don Sang Plus
# Déconnecte automatiquement tous les utilisateurs et démarre le serveur

Write-Host "🚀 Démarrage de Don Sang Plus..." -ForegroundColor Cyan
Write-Host ""

# Déconnecter tous les utilisateurs
Write-Host "🔓 Déconnexion de tous les utilisateurs..." -ForegroundColor Yellow
python logout_all.py

Write-Host ""
Write-Host "✅ Prêt à démarrer!" -ForegroundColor Green
Write-Host "🌐 Serveur: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📢 Aucun compte n'est connecté par défaut" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur CTRL+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
python manage.py runserver 8001
