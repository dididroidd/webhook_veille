# Veille tech quotidienne sur Discord

Chaque matin, un message arrive dans un salon Discord avec les articles tech et IA des dernières 24 h, classés par catégorie.

## Fichiers

| Fichier | Rôle |
|---|---|
| `config.toml` | **Le seul fichier à modifier** : catégories, flux RSS, mots exclus, nombre d'articles |
| `veille.py` | Le script qui lit les flux et poste sur Discord |
| `.github/workflows/veille.yml` | Lance le script chaque jour sur GitHub Actions |

## Installation (environ 10 minutes)

### 1. Créer le webhook Discord
1. Sur ton serveur Discord, va dans **Paramètres du salon** (l'engrenage à côté du salon) → **Intégrations** → **Webhooks** → **Nouveau webhook**.
2. Donne-lui un nom (par ex. « Veille Tech ») et un avatar si tu veux.
3. Clique sur **Copier l'URL du webhook**. ⚠️ Garde cette URL secrète : toute personne qui l'a peut poster dans ton salon.

### 2. Mettre le code sur GitHub
1. Crée un compte sur [github.com](https://github.com) si tu n'en as pas.
2. Crée un nouveau dépôt (**New repository**). Il peut être privé.
3. Envoie tous les fichiers de ce dossier, y compris le dossier `.github` : **Add file → Upload files**, puis glisse-dépose les fichiers.

### 3. Ajouter l'URL du webhook en secret
Dans ton dépôt : **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
- Name : `DISCORD_WEBHOOK_URL`
- Secret : l'URL copiée à l'étape 1

### 4. Tester
Onglet **Actions** → **Veille quotidienne** → **Run workflow**. Au bout d'environ 30 secondes, le message doit apparaître dans Discord.

Ensuite, ça tourne tout seul chaque jour vers **7 h (hiver) / 8 h (été)**. GitHub peut parfois avoir un peu de retard.

## Personnaliser

Tout se passe dans `config.toml` :
- **Ajouter un flux** : ajoute son URL dans la liste `flux` d'une catégorie.
- **Nouvelle catégorie** : copie un bloc `[[categorie]]` complet.
- **Changer l'heure** : modifie la ligne `cron` dans `.github/workflows/veille.yml`. L'heure est en UTC, donc 2 h de moins que Paris en été et 1 h de moins en hiver.

Pour trouver le flux RSS d'un site, essaie d'ajouter `/feed` ou `/rss` à son adresse, ou cherche « nom du site RSS ».

## Tester sur ton PC (facultatif)

```bash
pip install -r requirements.txt
python veille.py --test
```

`--test` affiche le résultat dans le terminal sans rien poster.
