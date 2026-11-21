# QuickSend-LAN

Application de bureau développée en Python permettant le partage de fichiers entre plusieurs ordinateurs connectés au même réseau local grâce au protocole UDP.

## 1. Présentation du projet

QuickSend LAN est une application destinée à faciliter le transfert de fichiers entre plusieurs ordinateurs connectés au même réseau local (LAN).

Elle permet aux utilisateurs d'envoyer et de recevoir des fichiers à travers une interface graphique simple et accessible.

## 2. Objectifs

- Faciliter le partage de fichiers sur un réseau local.
- Permettre l'envoi et la réception de fichiers.
- Simplifier les échanges grâce à une interface graphique.
- Suivre la progression des transferts.
- Conserver l'historique des opérations.

## 3. Fonctionnalités prévues

- Détection des appareils disponibles sur le réseau local.
- Envoi de fichiers vers un autre ordinateur.
- Réception de fichiers.
- Affichage de la progression des transferts.
- Gestion des erreurs et des interruptions.
- Enregistrement de l'historique des transferts.
- Mécanismes de fiabilité et de sécurité des échanges.

## 4. Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Langage de programmation |
| UDP / Sockets | Communication réseau |
| Tkinter | Interface graphique |
| SQLite | Gestion de la base de données |
| Git | Gestion des versions |
| GitHub | Hébergement du code source |
| Visual Studio Code | Environnement de développement |

## 5. Architecture

QuickSend LAN adopte une architecture client-serveur décentralisée. Chaque ordinateur peut envoyer et recevoir des fichiers selon les besoins de l'utilisateur.

L'application est destinée à fonctionner sur un réseau local Wi-Fi ou Ethernet, sans nécessiter obligatoirement une connexion Internet.

## 6. Organisation de l'équipe

| Membre | Responsabilité |
|---|---|
| Etoundi | Backend et communication réseau |
| Kako | Frontend et interface graphique |
| Michelle | Base de données et historique |

## 7. Organisation du dépôt Git

| Branche | Description |
|---|---|
| `main` | Version stable du projet |
| `dev` | Intégration des développements |
| `feature/backend-etoundi` | Développement du backend |
| `feature/frontend-kako` | Développement du frontend |
| `feature/database-michelle` | Gestion de la base de données |
| `feature/security` | Sécurité des transferts |

Les membres développent leurs fonctionnalités sur leurs propres branches et proposent leurs modifications à la branche `dev` pour vérification et intégration.

## 8. État du projet

Projet académique en cours de développement.

## 9. Environnement de développement

- Système d'exploitation : Windows
- Éditeur de code : Visual Studio Code
- Gestion du code source : Git et GitHub
