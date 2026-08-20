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
import json
import pathlib
import re
import statistics
import sys

# Sens de chaque metrique : ">" suspect au-dessus, "<" suspect en dessous.
SENS = {
    "phrase_moyenne": ">", "tirets_1k": ">", "intensificateurs_1k": ">",
    "contrastes_1k": ">", "not_only_1k": ">", "connecteurs_par": ">",
    "triades_1k": ">", "hedging_1k": ">", "metaphores_1k": ">",
    "ouvertures_1k": ">", "participiales_1k": ">", "pct_long": ">",
    "phrase_ecart_type": "<", "cv": "<", "pct_court": "<",
    "specifique_1k": "<", "par_cv": "<",
}

MOT = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*|\d+(?:[.,]\d+)*")


def groupe(termes):
    # re.escape ne protege plus l'espace depuis Python 3.7 : on couvre les deux
    # formes, sinon un terme en deux mots ne survit pas a un retour a la ligne.
    parts = [re.escape(t).replace(r"\ ", r"\s+").replace(" ", r"\s+")
             .replace("\\'", "['’]").replace("'", "['’]")
             for t in sorted(termes, key=len, reverse=True)]
    return "(?:" + "|".join(parts) + ")"


class Langue:
    """Charge un fichier de lexiques et compile ses motifs une fois pour toutes."""

    def __init__(self, chemin):
        d = json.loads(pathlib.Path(chemin).read_text())
        self.code = d["langue"]
        lx = d["lexiques"]
        self.re_intens = re.compile(r"\b" + groupe(lx["intensificateurs"]) + r"\b", re.I | re.M)
        self.re_metaph = re.compile(r"\b" + groupe(lx["metaphores"]) + r"\b", re.I | re.M)
        self.re_hedge = re.compile(r"\b" + groupe(lx["hedging"]) + r"\b", re.I | re.M)
        self.re_ouvert = re.compile(r"\b" + groupe(lx["ouvertures"]) + r"\b", re.I | re.M)
        # Les connecteurs ordinaires ne comptent qu'en tete de phrase, les
        # "forts" partout. C'est la regle de scripts/analyse.py, et un seuil
        # doit mesurer exactement ce que mesure l'outil qui s'en sert : compter
        # ici la forme nue gonflait le numerateur d'un "in addition to" ou d'un
        # "however" en incise, qui ne sont pas des connecteurs de transition.
        self.re_connect_debut = re.compile(
            r"(?:^|(?<=[.!?…]\s))\s*" + groupe(lx["connecteurs"]) + r"\b", re.I | re.M)
        forts = lx.get("connecteurs_forts")
        self.re_connect_forts = (re.compile(r"\b" + groupe(forts) + r"\b", re.I | re.M)
                                 if forts else None)
        m = d["motifs"]
        # Une entree de "contraste" est une regex, ou {"motif": ..., "detail": ...}
        # quand l'occurrence merite d'etre nommee. Meme forme que dans analyse.py.
        self.re_contrast = [
            re.compile(p["motif"] if isinstance(p, dict) else p, re.I | re.M)
            for p in m["contraste"]]
        self.re_not_only = re.compile(m["not_only"], re.I | re.M)
        self.re_particip = re.compile(m["participiale_finale"], re.I | re.M)
        coord = m["coordination"]
        oxford = ",?" if m.get("triade_virgule_serie", True) else ""

        def triple(item):
            return re.compile(r"\b(" + item + r"),\s*(" + item + r")" + oxford
                              + r"\s+" + coord + r"\s+(" + item + r")"
                              + r"(?=[.,;:!?)\]]|$)", re.I | re.M)

        det = m["triade_determinant"]
        esp = r"\s+" if m.get("triade_espace_apres_determinant", True) else ""
        excl = m.get("triade_conjonctions_exclues") or coord
        self.re_triade_nom = triple(
            det + esp + r"(?:(?!\s" + excl + r"\s)[^,;:.!?()\[\]—]){2,40}")
        mv = m["triade_mots_vides"]
        w = r"(?!" + mv + r"\b)[^\W\d_][\w'’-]*"
        self.re_triade_adj = triple(w + r"(?:\s+" + w + r"){0,2}")
        self.capitalises = set(d["mots_capitalises_courants"])
        self.abreviations = d["abreviations"]

    def phrases(self, texte):
        p = texte
        for a in self.abreviations:
            p = p.replace(a, a.replace(".", "\x00"))
        p = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + "\x00" + m.group(2), p)
        bouts = re.split(r"(?<=[.!?…])\s+(?=[\"'«(\[]?[A-ZÀ-Þ0-9])", p)
        return [b.replace("\x00", ".").strip() for b in bouts if MOT.search(b)]

    def specificite(self, phr):
        """Noms propres, acronymes et nombres : ce qu'un modele invente le moins."""
        n = 0
        for s in phr:
            for i, tok in enumerate(re.findall(r"\S+", s)):
                nu = tok.strip(".,;:!?()[]{}\"'’—-")
                if not nu:
                    continue
                if re.search(r"\d", nu) or re.match(r"^[A-Z]{2,}$", nu):
                    n += 1
                elif i > 0 and re.match(r"^[A-ZÀ-Þ]", nu) \
                        and nu not in self.capitalises:
                    n += 1
        return n


def mesure(langue, paragraphes):
    texte = "\n\n".join(paragraphes)
    phr, par_long = [], []
    for p in paragraphes:
        ph = langue.phrases(p)
        if ph:
            par_long.append(len(ph))
            phr.extend(ph)
    L = [len(MOT.findall(s)) for s in phr]
    if not L:
        return None
    k = sum(L) / 1000
    moy = statistics.fmean(L)
    et = statistics.pstdev(L) if len(L) > 1 else 0.0
    pmoy = statistics.fmean(par_long)
    pet = statistics.pstdev(par_long) if len(par_long) > 1 else 0.0
    n_contrast = sum(len(r.findall(texte)) for r in langue.re_contrast)
    n_connect = len(langue.re_connect_debut.findall(texte))
    if langue.re_connect_forts is not None:
        n_connect += len(langue.re_connect_forts.findall(texte))
    return {
        "mots": sum(L),
        "phrase_moyenne": moy,
        "phrase_ecart_type": et,
        "cv": et / moy if moy else 0.0,
        "pct_long": 100 * sum(1 for x in L if x > 40) / len(L),
        "pct_court": 100 * sum(1 for x in L if x < 10) / len(L),
        "tirets_1k": texte.count("—") / k,
        "intensificateurs_1k": len(langue.re_intens.findall(texte)) / k,
        "contrastes_1k": n_contrast / k,
        "not_only_1k": len(langue.re_not_only.findall(texte)) / k,
        "connecteurs_par": n_connect / len(paragraphes),
        "triades_1k": (len(langue.re_triade_nom.findall(texte))
                       + len(langue.re_triade_adj.findall(texte))) / k,
        "hedging_1k": len(langue.re_hedge.findall(texte)) / k,
        "metaphores_1k": len(langue.re_metaph.findall(texte)) / k,
        "ouvertures_1k": len(langue.re_ouvert.findall(texte)) / k,
        "participiales_1k": len(langue.re_particip.findall(texte)) / k,
        "specifique_1k": langue.specificite(phr) / k,
        "par_cv": pet / pmoy if pmoy else 0.0,
    }


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
    for cle, sens in SENS.items():
        f = (1 - a.decile) if sens == ">" else a.decile
        seuils[cle] = {"sens": sens, "seuil": round(quantile(cle, f), 2),
                       "median": round(quantile(cle, 0.5), 2)}

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
          f"/{len(SENS)}, max {validation['score_max']}, "
          f"{validation['part_au_dela_de_6']} % au-dela de 6")

    for chemin in a.controle:
        m = mesure(langue, paragraphes(chemin))
        if m:
            print(f"  {pathlib.Path(chemin).name:32s} {score(seuils, m):2d}/{len(SENS)}"
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
