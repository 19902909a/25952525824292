#!/bin/bash
# Script de restauration rapide du site Lovanet

echo "========================================="
echo "♻️  RESTAURATION RAPIDE DU SITE LOVANET..."
echo "========================================="

if [ ! -f "lovanet-backup-complet.tar.gz" ]; then
    echo "❌ Erreur : L'archive 'lovanet-backup-complet.tar.gz' est introuvable !"
    exit 1
fi

echo "📦 Extraction de l'archive (remplacement des fichiers modifiés)..."
tar -xzf lovanet-backup-complet.tar.gz -C /app

echo "🚀 Lancement du script de stabilisation pour réinstaller et optimiser le site..."
chmod +x /app/git-update-stabilizer.sh
/app/git-update-stabilizer.sh

echo "========================================="
echo "✅ RESTAURATION TERMINÉE AVEC SUCCÈS !"
echo "========================================="
