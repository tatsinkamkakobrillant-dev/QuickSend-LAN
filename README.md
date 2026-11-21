# QuickSend LAN

Application Python de partage de fichiers sur un réseau local. Les fichiers sont
transmis en **UDP** : chaque datagramme est accusé réception par le destinataire
et renvoyé si l'accusement n'arrive pas, ce qui garantit une copie intacte même
si UDP ne garantit rien par lui-même.

## Fonctionnalités

- Envoi/réception de fichiers de toute taille (découpe en paquets de 1200 octets).
- Détection des appareils QuickSend sur le LAN (messages UDP broadcast + loopback).
- Reprise automatique sur perte de paquets, vérification de la taille et écriture
  atomique (fichier temporaire puis renommage).
- Noms de fichiers doublons gérés (`rapport (1).pdf`, etc.).
- Historique des transferts dans `quicksend.db` (SQLite).
- Interface graphique CustomTkinter et mode ligne de commande.

## Installation

```powershell
python -m pip install -r requirements.txt
```

Aucune dépendance n'est nécessaire pour le mode ligne de commande ; la seule
dépendance (`customtkinter`) sert à l'interface graphique.

## Utilisation

### Interface graphique

```powershell
python main.py
```

Le récepteur UDP démarre automatiquement sur le port 5000. Les onglets permettent
de rechercher des appareils, choisir un fichier, l'envoyer et consulter
l'historique. Le dossier de réception par défaut est `~/Downloads/QuickSend`.

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

## Protocole UDP (port 5000 par défaut)

Format d'un datagramme :

| Champ        | Taille | Description                                  |
|--------------|--------|----------------------------------------------|
| magic/version| 5 octets | `QSND` + version 1                         |
| type         | 1 octet  | OFFER, ACCEPT, DATA, ACK, RESULT, DISCOVER... |
| session      | 16 octets| identifiant unique du transfert              |
| seq          | 4 octets | numéro du morceau (0 pour le contrôle)       |
| length       | 4 octets | taille de la charge utile                    |
| payload      | variable | métadonnées JSON ou morceau de fichier       |

1. L'expéditeur envoie `OFFER` (nom, taille, taille des paquets).
2. Le récepteur répond `ACCEPT` avec son port de travail dédié.
3. Chaque `DATA` est écrit à sa position dans un fichier temporaire puis accusé
   par `ACK`. Un paquet perdu est renvoyé après un délai d'attente.
4. Le récepteur valide la taille, renomme le fichier et renvoie `RESULT`.

## Tests

Les tests d'intégration tournent en local, sans matériel réseau supplémentaire :

```powershell
python -m unittest discover -s tests -v
```

Ils couvrent les petits et gros fichiers binaires, le fichier vide, les doublons
de noms, la découverte d'appareils, la progression et la retransmission après
perte d'un datagramme.
