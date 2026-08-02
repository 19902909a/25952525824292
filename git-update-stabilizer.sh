#!/bin/bash
# Lovanet Stabilizer Script
# À exécuter après chaque mise à jour depuis GitHub ou VS Code pour garantir la vitesse et stabilité du site.

echo "========================================="
echo "🚀 DÉMARRAGE DU STABILISATEUR LOVANET..."
echo "========================================="

# 1. Nettoyage des caches (Évite les ralentissements dus aux vieux fichiers)
echo "🧹 Nettoyage des caches frontend et backend..."
rm -rf /app/frontend/node_modules/.cache
find /app/backend -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

# 2. Mise à jour propre des dépendances Frontend
echo "📦 Installation des dépendances Frontend optimisées..."
cd /app/frontend
yarn install --prefer-offline --frozen-lockfile

# 3. Mise à jour des dépendances Backend
echo "🐍 Vérification des dépendances Backend..."
cd /app/backend
pip install -r requirements.txt --upgrade

# 4. Redémarrage des services via Supervisor pour appliquer les changements proprement
echo "🔄 Redémarrage sécurisé des services..."
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

echo "========================================="
echo "✅ STABILISATION TERMINÉE AVEC SUCCÈS !"
echo "Le site Lovanet est optimisé et prêt à fonctionner sans ralentissement."
echo "========================================="
