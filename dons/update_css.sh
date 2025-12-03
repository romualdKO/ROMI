#!/bin/bash
# Script pour mettre à jour le CSS et redémarrer le serveur Django

echo "🎨 Mise à jour du CSS..."

# 1. Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
cd /home/volbis/Documents/Docs/romi/dons/dont_sang_plus
/home/volbis/Documents/Docs/romi/dons/.venv/bin/python manage.py collectstatic --noinput --clear

# 2. Arrêter le serveur Django
echo "🛑 Arrêt du serveur Django..."
pkill -f "manage.py runserver"
sleep 2

# 3. Redémarrer le serveur Django
echo "🚀 Redémarrage du serveur Django..."
/home/volbis/Documents/Docs/romi/dons/.venv/bin/python manage.py runserver 0.0.0.0:8000 &
sleep 2

echo "✅ Mise à jour terminée !"
echo "💡 N'oubliez pas de faire un Hard Refresh (Ctrl+Shift+R) dans votre navigateur !"
echo "🌐 Accédez au site : http://localhost:8000"
