# 🎤 GUIDE DES COMMANDES VOCALES - DON SANG PLUS

## 📋 TABLE DES MATIÈRES
1. [Introduction](#introduction)
2. [Commandes de Navigation](#commandes-de-navigation)
3. [Commandes d'Action](#commandes-daction)
4. [Commandes d'Aide](#commandes-daide)
5. [Guide de Test](#guide-de-test)
6. [Scénarios de Test Complets](#scénarios-de-test-complets)
7. [Notes Importantes](#notes-importantes)

---

## 🌟 INTRODUCTION

L'assistant vocal IA de Don Sang Plus permet de naviguer dans l'application **uniquement avec la voix**, facilitant l'utilisation pour les personnes analphabètes ou novices en informatique.

### Activation de l'Assistant
1. Un **bouton rouge flottant** 🤖 apparaît en bas à droite de chaque page
2. Cliquez dessus pour ouvrir le panneau de contrôle
3. Cliquez sur **"🎤 Écouter"** pour activer le microphone
4. Autorisez l'accès au microphone dans votre navigateur
5. Parlez clairement en français

---

## 🧭 COMMANDES DE NAVIGATION

### Pour les Donneurs de Sang

| Commande | Action |
|----------|--------|
| **"tableau de bord"** | Retour au tableau de bord principal |
| **"demandes"** | Voir toutes les demandes de sang |
| **"demandes urgentes"** | Voir uniquement les demandes urgentes |
| **"historique"** | Consulter l'historique de vos dons |
| **"messages"** | Accéder à la messagerie/chat |
| **"avantages"** | Voir vos récompenses et avantages |
| **"récompenses"** | Voir vos récompenses et avantages |
| **"profil"** | Accéder à votre profil personnel |

### Pour les Hôpitaux

| Commande | Action |
|----------|--------|
| **"tableau de bord"** | Retour au tableau de bord hôpital |
| **"historique"** | Voir l'historique des demandes |
| **"messages"** | Accéder à la messagerie |
| **"classement"** | Voir le classement des donneurs |
| **"donneurs"** | Voir le classement des donneurs |

---

## 🚀 COMMANDES D'ACTION

### Pour les Donneurs de Sang

| Commande | Action |
|----------|--------|
| **"donner"** | Lancer le processus de don de sang |
| **"faire un don"** | Lancer le processus de don de sang |
| **"je veux donner"** | Lancer le processus de don de sang |

### Pour les Hôpitaux

| Commande | Action |
|----------|--------|
| **"créer demande"** | Ouvrir le formulaire de création de demande |
| **"nouvelle demande"** | Ouvrir le formulaire de création de demande |
| **"créer une demande de sang"** | Ouvrir le formulaire de création de demande |

---

## 📚 COMMANDES D'AIDE

| Commande | Action |
|----------|--------|
| **"aide"** | Obtenir de l'aide contextuelle selon la page actuelle |
| **"tutoriel"** | Lancer le tutoriel complet pas à pas |
| **"répéter"** | Répéter la dernière instruction donnée |
| **"encore"** | Répéter la dernière instruction donnée |

---

## 🧪 GUIDE DE TEST

### Étape 1 : Démarrer le Serveur

```powershell
cd C:\Users\HP\OneDrive - Ecole Supérieure Africaine des Technologies de l'Information et de la Communication (ESATIC)\Bureau\ROMI\dont_sang_plus\dont_sang_plus
python manage.py runserver 8001
```

### Étape 2 : Ouvrir le Navigateur

1. Allez sur `http://localhost:8001`
2. Connectez-vous avec un compte donneur ou hôpital

### Étape 3 : Activer l'Assistant Vocal

1. Repérez le **bouton rouge flottant** en bas à droite
2. Cliquez sur le bouton pour ouvrir le panneau
3. Cliquez sur **"🎤 Écouter"**
4. Autorisez l'accès au microphone quand le navigateur demande

### Étape 4 : Tests Basiques

#### Test 1 - Aide Contextuelle
- **Commande** : "aide"
- **Résultat attendu** : L'assistant explique la page actuelle

#### Test 2 - Tutoriel
- **Commande** : "tutoriel"
- **Résultat attendu** : Lance un tutoriel pas à pas
  - 6 étapes pour les donneurs
  - 7 étapes pour les hôpitaux

#### Test 3 - Navigation Simple
- **Commande** : "historique"
- **Résultat attendu** : Navigation vers la page historique
- **Commande** : "tableau de bord"
- **Résultat attendu** : Retour au tableau de bord

#### Test 4 - Action Donneur
- Sur le tableau de bord donneur
- **Commande** : "je veux donner"
- **Résultat attendu** : Affichage des demandes de sang disponibles

#### Test 5 - Action Hôpital
- Sur le tableau de bord hôpital
- **Commande** : "créer demande"
- **Résultat attendu** : Ouverture du formulaire de création

#### Test 6 - Répétition
- Après n'importe quelle instruction
- **Commande** : "répéter"
- **Résultat attendu** : L'assistant redit la dernière instruction

---

## 🎯 SCÉNARIOS DE TEST COMPLETS

### Scénario 1 : Parcours Complet Donneur

```
1. Connexion au compte donneur
2. Le bouton rouge apparaît en bas à droite
3. Clic sur le bouton → Le panneau s'ouvre
4. Commande : "tutoriel" → Lance le tutoriel (6 étapes)
5. Commande : "aide" → Explique le tableau de bord
6. Commande : "demandes" → Navigue vers les demandes urgentes
7. Commande : "historique" → Navigue vers l'historique des dons
8. Commande : "avantages" → Navigue vers les récompenses
9. Commande : "profil" → Navigue vers le profil
10. Commande : "tableau de bord" → Retour au tableau de bord
```

**Temps estimé** : 5-7 minutes

### Scénario 2 : Parcours Complet Hôpital

```
1. Connexion au compte hôpital
2. Le bouton rouge apparaît en bas à droite
3. Clic sur le bouton → Le panneau s'ouvre
4. Commande : "tutoriel" → Lance le tutoriel (7 étapes)
5. Commande : "aide" → Explique le tableau de bord
6. Commande : "créer demande" → Ouvre le formulaire de création
7. Commande : "historique" → Navigue vers l'historique
8. Commande : "classement" → Navigue vers le classement des donneurs
9. Commande : "messages" → Navigue vers la messagerie
10. Commande : "tableau de bord" → Retour au tableau de bord
```

**Temps estimé** : 6-8 minutes

### Scénario 3 : Test d'Accessibilité (Utilisateur Novice)

```
1. Utilisateur se connecte pour la première fois
2. Active l'assistant vocal
3. Commande : "tutoriel" → Apprentissage guidé
4. Suit les instructions vocales étape par étape
5. Commande : "aide" à chaque page pour comprendre
6. Utilise les suggestions cliquables comme alternative
7. Commande : "répéter" si instruction pas claire
```

**Objectif** : Vérifier que l'utilisateur peut naviguer sans connaissance préalable

---

## ⚠️ NOTES IMPORTANTES

### Compatibilité Navigateur

| Navigateur | Reconnaissance Vocale | Synthèse Vocale | Statut |
|------------|----------------------|-----------------|--------|
| **Chrome** | ✅ Excellent | ✅ Excellent | ✅ Recommandé |
| **Edge** | ✅ Excellent | ✅ Excellent | ✅ Recommandé |
| **Safari** | ✅ Bon | ✅ Bon | ⚠️ Nécessite webkit |
| **Firefox** | ⚠️ Limité | ✅ Bon | ⚠️ Support partiel |

### Configuration Requise

1. **Langue** : Parlez en **français** (l'assistant est configuré pour fr-FR)
2. **Clarté** : Parlez **clairement** et à vitesse normale
3. **Microphone** : Vérifiez que votre microphone fonctionne correctement
4. **Permissions** : Autorisez l'accès au microphone dans le navigateur
5. **Connexion** : Certaines fonctionnalités peuvent nécessiter HTTPS

### Conseils d'Utilisation

#### Pour une Meilleure Reconnaissance
- ✅ Parlez clairement et distinctement
- ✅ Attendez le signal sonore avant de parler
- ✅ Évitez les bruits de fond
- ✅ Utilisez un microphone de qualité si possible
- ❌ Ne parlez pas trop vite
- ❌ N'utilisez pas d'argot ou d'abréviations

#### En Cas de Problème
1. **L'assistant ne répond pas** :
   - Vérifiez les permissions du microphone
   - Rechargez la page (Ctrl + F5)
   - Essayez un autre navigateur

2. **Mauvaise reconnaissance** :
   - Parlez plus lentement
   - Répétez la commande plus clairement
   - Utilisez les suggestions cliquables

3. **Navigation ne fonctionne pas** :
   - Dites "aide" pour vérifier les commandes disponibles
   - Vérifiez que vous êtes sur la bonne page
   - Utilisez "tableau de bord" pour revenir à l'accueil

### Alternative Tactile

Si la reconnaissance vocale ne fonctionne pas, vous pouvez :
- **Cliquer** sur les suggestions affichées dans le panneau
- Les suggestions changent selon la page actuelle
- Alternative parfaite pour les environnements bruyants

### Fonctionnalités Avancées

#### Auto-Guide
- Cochez "Guide automatique" dans le pied du panneau
- L'assistant vous guidera automatiquement à chaque nouvelle page
- Pratique pour les utilisateurs complètement novices

#### Transcript
- Toutes les conversations sont enregistrées dans le transcript
- Vous pouvez relire ce qui a été dit
- Utile pour les utilisateurs sourds ou malentendants

---

## 📊 TABLEAU RÉCAPITULATIF DES COMMANDES

### Navigation Donneur
| Page Cible | Commandes Vocales |
|------------|-------------------|
| Tableau de bord | "tableau de bord" |
| Demandes de sang | "demandes", "demandes urgentes" |
| Historique | "historique" |
| Messages | "messages" |
| Récompenses | "avantages", "récompenses" |
| Profil | "profil" |

### Navigation Hôpital
| Page Cible | Commandes Vocales |
|------------|-------------------|
| Tableau de bord | "tableau de bord" |
| Historique | "historique" |
| Messages | "messages" |
| Classement | "classement", "donneurs" |

### Actions
| Type Utilisateur | Action | Commandes Vocales |
|------------------|--------|-------------------|
| Donneur | Faire un don | "donner", "faire un don", "je veux donner" |
| Hôpital | Créer demande | "créer demande", "nouvelle demande" |

### Aide
| Fonction | Commandes Vocales |
|----------|-------------------|
| Aide contextuelle | "aide" |
| Tutoriel complet | "tutoriel" |
| Répétition | "répéter", "encore" |

---

## 🎓 TUTORIELS INTÉGRÉS

### Tutoriel Donneur (6 Étapes)

1. **Bienvenue** : Introduction au tableau de bord
2. **Demandes urgentes** : Comment voir les demandes de sang
3. **Menu de navigation** : Explication du menu principal
4. **Navigation vocale** : Comment utiliser les commandes vocales
5. **Actions rapides** : Comment faire un don rapidement
6. **Récompenses** : Comprendre le système de points

**Durée** : ~3-4 minutes

### Tutoriel Hôpital (7 Étapes)

1. **Bienvenue** : Introduction au tableau de bord hôpital
2. **Créer une demande** : Comment créer une nouvelle demande
3. **Formulaire** : Remplir les informations nécessaires
4. **Historique** : Consulter l'historique des demandes
5. **Statuts** : Comprendre les différents statuts
6. **Classement** : Voir et gérer les donneurs réguliers
7. **Récompenses** : Créer des bons de réduction

**Durée** : ~4-5 minutes

---

## 🔧 DÉPANNAGE

### Problèmes Fréquents

#### Le bouton rouge n'apparaît pas
- **Solution** : Rechargez la page (Ctrl + F5)
- Vérifiez que vous êtes connecté
- Videz le cache du navigateur

#### Le microphone ne fonctionne pas
- **Solution** : 
  1. Vérifiez les paramètres du navigateur
  2. Allez dans Paramètres > Confidentialité > Microphone
  3. Autorisez l'accès pour le site
  4. Testez avec un autre navigateur

#### L'assistant ne comprend pas
- **Solution** :
  1. Parlez plus lentement et clairement
  2. Utilisez les commandes exactes du guide
  3. Vérifiez que votre langue est bien en français
  4. Utilisez les suggestions cliquables

#### La navigation ne fonctionne pas
- **Solution** :
  1. Vérifiez que vous avez les permissions nécessaires
  2. Dites "tableau de bord" pour revenir à l'accueil
  3. Utilisez "aide" pour voir les commandes disponibles

---

## 📞 SUPPORT

Pour toute question ou problème :
- Dites **"aide"** pour obtenir de l'aide contextuelle
- Dites **"tutoriel"** pour revoir les bases
- Contactez l'équipe de support : support@donssangplus.com

---

## 📝 NOTES DE VERSION

**Version 1.0** (14 Novembre 2025)
- ✅ Reconnaissance vocale en français (fr-FR)
- ✅ Synthèse vocale (text-to-speech)
- ✅ Navigation complète par commandes vocales
- ✅ Tutoriels intégrés pour donneurs et hôpitaux
- ✅ Aide contextuelle par page
- ✅ Suggestions cliquables
- ✅ Préférences persistantes
- ✅ Design responsive mobile

---

**Dernière mise à jour** : 14 Novembre 2025  
**Développé par** : Don Sang Plus Team  
**Objectif** : Rendre l'application accessible à tous, y compris les personnes analphabètes et novices en informatique.
