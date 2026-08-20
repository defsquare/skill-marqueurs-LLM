#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibre.py — Derive des seuils de detection a partir d'un corpus humain.

Principe : un seuil doit dire ou se situe la prose legitime, pas ce que vaut
en moyenne un texte genere. On decoupe donc un corpus humain en echantillons,
on mesure chaque metrique, et on place la frontiere au 1er ou au 9e decile
selon le sens de la metrique. Par construction, 10 % des echantillons humains
declenchent sur chaque metrique — ce qui laisse un score global bas.

La classe positive (textes generes) ne sert qu'a verifier la separation. Elle
ne fixe aucun seuil : un texte genere peut etre propre, un texte humain ne
doit pas etre accuse.

Usage
    python3 calibre.py --lexiques lexiques-en.json \\
                       --corpus ../corpus/evans-ddd-2003.txt \\
                       --sortie seuils-en.json
    python3 calibre.py --lexiques lexiques-en.json \\
                       --corpus ../corpus/evans-ddd-2003.txt \\
                       --controle texte1.md texte2.md
"""

import argparse
import importlib.util
import json
import pathlib
import re
import statistics
import sys

# Le moteur de la skill EST la mesure. Deriver les seuils avec une seconde
# implementation les faisait diverger : la mediane de hedging differait de 27 %
# entre les deux outils, si bien que le seuil derive ici ne voulait pas dire la
# meme chose une fois applique la-bas.
MOTEUR = pathlib.Path(__file__).resolve().parent.parent / "marqueurs-llm" / "scripts" / "analyse.py"
_spec = importlib.util.spec_from_file_location("analyse", MOTEUR)
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)

Langue = an.Langue


def sens_de(cle):
    return an.META[cle]["sens"]


def mesure(langue, paragraphes_):
    """Mesure un lot de paragraphes exactement comme le fait analyse.py."""
    texte = "\n\n".join(paragraphes_)
    lignes = texte.splitlines()
    kinds = an.classify_lines(lignes)
    paras = an.build_paragraphs(lignes, kinds)
    if not paras:
        return None
    hits, structure = an.scan(lignes, kinds, langue)
    valeurs, stats, _, _ = an.valeurs_brutes(paras, hits, langue, structure)
    valeurs["mots"] = stats["mots"]
    return valeurs


def paragraphes(chemin):
    t = pathlib.Path(chemin).read_text()
    return [p.strip() for p in t.split("\n\n")
            if p.strip() and not p.lstrip().startswith("#")]


def echantillonne(paras, taille):
    lots, courant, n = [], [], 0
    for p in paras:
        courant.append(p)
        n += len(p.split())
        if n >= taille:
            lots.append(courant)
            courant, n = [], 0
    if n >= taille // 2:
        lots.append(courant)
    return lots


def score(seuils, m):
    return sum(1 for c, s in seuils.items()
               if (m[c] > s["seuil"] if s["sens"] == ">" else m[c] < s["seuil"]))


def main():
    ap = argparse.ArgumentParser(description="Derive des seuils depuis un corpus humain.")
    ap.add_argument("--lexiques", required=True)
    ap.add_argument("--corpus", required=True, help="corpus humain de reference")
    ap.add_argument("--sortie", help="fichier JSON de seuils a ecrire")
    ap.add_argument("--controle", nargs="*", default=[],
                    help="textes a scorer contre les seuils derives")
    ap.add_argument("--taille", type=int, default=800, help="mots par echantillon")
    ap.add_argument("--decile", type=float, default=0.10,
                    help="marge laissee a la prose humaine (defaut 0.10)")
    a = ap.parse_args()

    langue = Langue(a.lexiques)
    paras = paragraphes(a.corpus)
    lots = echantillonne(paras, a.taille)
    ech = [m for m in (mesure(langue, l) for l in lots) if m]
    if len(ech) < 20:
        sys.exit(f"corpus trop mince : {len(ech)} echantillons, il en faut au moins 20")

    def quantile(cle, f):
        v = sorted(m[cle] for m in ech)
        return v[min(len(v) - 1, int(f * len(v)))]

    seuils = {}
    for cle in langue.metriques:
        sens = sens_de(cle)
        f = (1 - a.decile) if sens == ">" else a.decile
        seuils[cle] = {"sens": sens, "seuil": round(quantile(cle, f), 2),
                       "median": round(quantile(cle, 0.5), 2),
                       "d1": round(quantile(cle, 0.1), 2),
                       "d9": round(quantile(cle, 0.9), 2),
                       "max": round(quantile(cle, 1.0), 2)}

    sc = sorted(score(seuils, m) for m in ech)
    total = sum(m["mots"] for m in ech)
    validation = {
        "echantillons": len(ech), "mots": total,
        "score_median": statistics.median(sc),
        "score_moyen": round(statistics.fmean(sc), 2),
        "score_max": sc[-1],
        "part_au_dela_de_6": round(100 * sum(1 for x in sc if x >= 6) / len(sc), 1),
    }

    print(f"corpus : {total} mots, {len(ech)} echantillons de ~{a.taille} mots\n")
    print(f"{'metrique':22s} {'sens':>5s} {'median':>9s} {'seuil':>9s}")
    print("-" * 48)
    for c, s in seuils.items():
        print(f"{c:22s} {s['sens']:>5s} {s['median']:9.2f} {s['seuil']:9.2f}")
    print(f"\nvalidation sur le corpus humain : median {validation['score_median']:.0f}"
          f"/{len(seuils)}, max {validation['score_max']}, "
          f"{validation['part_au_dela_de_6']} % au-dela de 6")

    for chemin in a.controle:
        m = mesure(langue, paragraphes(chemin))
        if m:
            print(f"  {pathlib.Path(chemin).name:32s} {score(seuils, m):2d}/{len(seuils)}"
                  f"  ({m['mots']} mots)")

    if a.sortie:
        pathlib.Path(a.sortie).write_text(json.dumps({
            "langue": langue.code,
            "methode": "1er/9e decile d'un corpus humain, marge %.0f %%" % (100 * a.decile),
            "corpus": pathlib.Path(a.corpus).name,
            "validation": validation,
            "seuils": seuils,
        }, ensure_ascii=False, indent=2))
        print(f"\nseuils ecrits dans {a.sortie}")


if __name__ == "__main__":
    main()
