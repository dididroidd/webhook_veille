"""Récupère les articles du jour depuis des flux RSS et les poste sur Discord.

Usage :
    python veille.py            # poste sur Discord (variable DISCORD_WEBHOOK_URL)
    python veille.py --test     # affiche le résultat dans le terminal, sans poster
"""

import calendar
import os
import sys
import time
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests

CONFIG = Path(__file__).with_name("config.toml")

# Limites imposées par Discord
MAX_EMBEDS_PAR_MESSAGE = 10
MAX_CARACTERES_PAR_MESSAGE = 6000
MAX_DESCRIPTION_EMBED = 4096


def date_article(entree):
    """Renvoie la date de publication en timestamp UTC, ou None."""
    for champ in ("published_parsed", "updated_parsed"):
        valeur = entree.get(champ)
        if valeur:
            return calendar.timegm(valeur)
    return None


def recuperer_articles(urls, depuis):
    articles = []
    for url in urls:
        flux = feedparser.parse(url, agent="Mozilla/5.0 (veille-discord)")
        if flux.bozo and not flux.entries:
            print(f"⚠️  Flux illisible : {url} ({flux.bozo_exception})", file=sys.stderr)
            continue
        for entree in flux.entries:
            date = date_article(entree)
            if date is None or date < depuis:
                continue
            lien = entree.get("link", url)
            articles.append({
                "titre": " ".join(entree.get("title", "Sans titre").split()),
                "lien": lien,
                "source": urlparse(lien).netloc.removeprefix("www."),
                "date": date,
            })
    return articles


def construire_embeds(config):
    depuis = time.time() - config["fenetre_heures"] * 3600
    exclure = [mot.lower() for mot in config.get("exclure", [])]
    vus = set()
    embeds = []

    for categorie in config["categorie"]:
        articles = recuperer_articles(categorie["flux"], depuis)
        articles.sort(key=lambda a: a["date"], reverse=True)

        lignes = []
        for article in articles:
            cle = article["titre"].lower()
            if cle in vus:
                continue
            texte = f"{cle} {article['lien'].lower()}"
            if any(mot in texte for mot in exclure):
                continue
            vus.add(cle)
            titre = article["titre"].replace("[", "(").replace("]", ")")
            ligne = f"• [{titre}]({article['lien']}) — *{article['source']}*"
            if sum(len(l) + 1 for l in lignes) + len(ligne) > MAX_DESCRIPTION_EMBED:
                break
            lignes.append(ligne)
            if len(lignes) >= config["max_par_categorie"]:
                break

        if lignes:
            embeds.append({
                "title": categorie["nom"],
                "description": "\n".join(lignes),
                "color": int(categorie.get("couleur", "#5865F2").lstrip("#"), 16),
            })
    return embeds


def taille_embed(embed):
    return len(embed["title"]) + len(embed["description"])


def decouper_en_messages(embeds):
    """Regroupe les embeds en messages qui respectent les limites Discord."""
    messages, courant, taille = [], [], 0
    for embed in embeds:
        t = taille_embed(embed)
        if courant and (len(courant) >= MAX_EMBEDS_PAR_MESSAGE or taille + t > MAX_CARACTERES_PAR_MESSAGE):
            messages.append(courant)
            courant, taille = [], 0
        courant.append(embed)
        taille += t
    if courant:
        messages.append(courant)
    return messages


def main():
    test = "--test" in sys.argv
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    embeds = construire_embeds(config)
    entete = f"☀️ **Ta veille tech du {datetime.now():%d/%m/%Y}**"

    if not embeds:
        entete += "\nRien de neuf aujourd'hui."

    if test:
        print(entete)
        for embed in embeds:
            print(f"\n## {embed['title']}\n{embed['description']}")
        return

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        sys.exit("❌ La variable DISCORD_WEBHOOK_URL n'est pas définie.")

    for i, groupe in enumerate(decouper_en_messages(embeds) or [[]]):
        charge = {"embeds": groupe}
        if i == 0:
            charge["content"] = entete
        reponse = requests.post(webhook, json=charge, timeout=30)
        reponse.raise_for_status()
        time.sleep(1)
    print(f"✅ {len(embeds)} catégorie(s) envoyée(s) sur Discord.")


if __name__ == "__main__":
    main()
