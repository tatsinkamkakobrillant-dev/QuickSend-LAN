# QuickSend LAN

Application Python de partage de fichiers sur un réseau local. Les fichiers sont
transmis en **UDP** : chaque datagramme est accusé réception par le destinataire
et renvoyé si l'accusement n'arrive pas, ce qui garantit une copie intacte même
si UDP ne garantit rien par lui-même.

## 1. Présentation du projet

QuickSend LAN facilite le transfert de fichiers entre plusieurs ordinateurs
connectés au même réseau local (Wi-Fi ou Ethernet), sans connexion Internet
obligatoire. Chaque machine peut à la fois envoyer et recevoir des fichiers via
une interface graphique simple ou en ligne de commande.

## 2. Objectifs

- Faciliter le partage de fichiers sur un réseau local.
- Permettre l'envoi et la réception de fichiers.
- Simplifier les échanges grâce à une interface graphique.
- Suivre la progression des transferts.
- Conserver l'historique des opérations.
- Gérer les erreurs et les interruptions.

## 3. Fonctionnalités

- Envoi/réception de fichiers de toute taille (découpe en paquets de 1200 octets).
- Détection des appareils QuickSend sur **tous les réseaux locaux** (broadcast de chaque carte WiFi/Ethernet + loopback).
- Scan des machines joignables du WiFi (ping parallèle) avec distinction « QuickSend » / « Autre appareil ».
- Reprise automatique sur perte de paquets (ACK par paquet + retransmission).
- Écriture atomique : fichier temporaire puis renommage après confirmation.
- Gestion des noms de fichiers en doublon (`rapport (1).pdf`, etc.).
- Barre de progression et validation de la taille des fichiers reçus.
- Historique des transferts dans `quicksend.db` (SQLite).
- Interface graphique CustomTkinter et mode ligne de commande.

## 4. Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Langage de programmation |
| UDP / Sockets | Communication réseau |
| CustomTkinter | Interface graphique |
| SQLite | Base de données et historique |
| Git / GitHub | Gestion de versions et hébergement |
| Visual Studio Code | Environnement de développement |

## 5. Architecture

QuickSend LAN adopte une architecture client-serveur décentralisée : chaque
ordinateur exécute un récepteur UDP et peut envoyer des fichiers à un autre
appareil. Les transferts utilisent un port de travail dédié par session afin de
permettre plusieurs envois simultanés.

## 6. Installation

```powershell
python -m pip install -r requirements.txt
```

Aucune dépendance n'est nécessaire pour le mode ligne de commande ; la seule
dépendance (`customtkinter`) sert à l'interface graphique.

## 7. Utilisation

### Interface graphique

```powershell
python main.py
```

Le récepteur UDP démarre automatiquement sur le port 5000. Les onglets permettent
de rechercher des appareils, choisir un fichier, l'envoyer et consulter
l'historique. Le dossier de réception par défaut est `~/Downloads/QuickSend`.

⚠️ L'onglet **Appareils** affiche toutes les machines joignables du WiFi. Celles
marquées « Prêt à recevoir » exécutent QuickSend : ce sont les seules auxquelles
un fichier peut être envoyé. Une machine « Autre appareil » est visible sur le
réseau mais n'a pas QuickSend lancé. Pour qu'elle apparaisse dans la liste
d'envoi, installez/lancez QuickSend dessus.

Le scan utilise le broadcast de chaque interface réseau puis un ping parallèle
du /24 local. Si certaines machines ne répondent pas, vérifiez leur pare-feu
(le ping ICMP doit être autorisé).

### Ligne de commande

Sur l'ordinateur qui reçoit :

```powershell
python main.py --mode receive --port 5000
```

Sur l'ordinateur qui envoie :

```powershell
python main.py --mode send --file C:\chemin\fichier.zip --to 192.168.1.10 --port 5000
```

Rechercher les appareils :

```powershell
python main.py --mode discover --discover-timeout 2
```

Options utiles : `--folder` (dossier de réception), `--db` (base SQLite),
`--name` (nom annoncé sur le réseau).

## 8. Protocole UDP (port 5000 par défaut)

Format d'un datagramme :

| Champ | Taille | Description |
|---|---|---|
| magic/version | 5 octets | `QSND` + version 1 |
| type | 1 octet | OFFER, ACCEPT, DATA, ACK, RESULT, DISCOVER... |
| session | 16 octets | identifiant unique du transfert |
| seq | 4 octets | numéro du morceau (0 pour le contrôle) |
| length | 4 octets | taille de la charge utile |
| payload | variable | métadonnées JSON ou morceau de fichier |

1. L'expéditeur envoie `OFFER` (nom, taille, taille des paquets).
2. Le récepteur répond `ACCEPT` avec son port de travail dédié.
3. Chaque `DATA` est écrit à sa position dans un fichier temporaire puis accusé
   par `ACK`. Un paquet perdu est renvoyé après un délai d'attente.
4. Le récepteur valide la taille, renomme le fichier et renvoie `RESULT`.

## 9. Tests

Les tests d'intégration tournent en local, sans matériel réseau supplémentaire :

```powershell
python -m unittest discover -s tests -v
```

Ils couvrent les petits et gros fichiers binaires, le fichier vide, les doublons
de noms, la découverte d'appareils, la progression, les transferts simultanés et
la retransmission après perte d'un datagramme.

## 10. Organisation de l'équipe

| Membre | Responsabilité |
|---|---|
| Etoundi | Backend et communication réseau |
| Kako | Frontend et interface graphique |
| Michelle | Base de données et historique |

## 11. Organisation du dépôt Git

| Branche | Description |
|---|---|
| `main` | Version stable du projet |
| `dev` | Intégration des développements |
| `feature` | Développement du backend et intégration |
| `frontend` | Interface graphique |

Les fonctionnalités sont développées sur leurs branches puis proposées à `dev`
via des pull requests.

## 12. État du projet

Projet académique : backend UDP, interface graphique et historique fonctionnels.

## 13. Environnement de développement

- Système d'exploitation : Windows
- Éditeur : Visual Studio Code
- Gestion du code source : Git et GitHub

## 14. Créer l'exécutable Windows

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name QuickSend-LAN --hidden-import frontend.windows.main_window --hidden-import customtkinter main.py
```

L'exécutable est généré dans `dist\QuickSend-LAN.exe`. Il peut être copié seul
sur un autre Windows 64 bits : Python n'est pas nécessaire sur la machine cible.
