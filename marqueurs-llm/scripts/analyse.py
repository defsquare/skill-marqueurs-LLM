#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse.py — Détection des marqueurs d'ecriture LLM dans un texte francais.

Calcule les metriques objectives (rythme, densite de tics) et localise les
occurrences avec leur numero de ligne, pour que la correction soit chirurgicale.

Ce script ne juge que la surface. Le fond (chiffres, sources, opinions,
aveux d'ignorance) reste a l'appreciation du lecteur.

Usage:
    python3 analyse.py texte.md
    python3 analyse.py texte.md --registre technique
    python3 analyse.py texte.md --json
    python3 analyse.py texte.md --max-occ 20
    cat texte.md | python3 analyse.py -

Sans dependance externe.
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Seuils par registre (section 6 du catalogue, ajustes selon le genre)
# --------------------------------------------------------------------------

BASE = {
    "mean_max": 25.0,        # longueur moyenne des phrases, suspect au-dela
    "std_min": 8.0,          # ecart-type des longueurs, suspect en deca
    "cv_min": 0.40,          # coefficient de variation, suspect en deca
    "pct_long_max": 15.0,    # % de phrases > 40 mots
    "pct_short_min": 10.0,   # % de phrases < 10 mots
    "emdash_1k_max": 2.0,
    "intens_1k_max": 8.0,
    "contrast_1k_max": 2.0,
    "connect_par_max": 0.8,
    "triad_1k_max": 4.0,
    "specific_1k_min": 5.0,  # noms propres + chiffres
    "par_cv_min": 0.25,      # ecart-type des longueurs de paragraphe / moyenne
    "hedge_1k_max": 10.0,
}

REGISTRES = {
    "prose": {},
    "technique": {"mean_max": 22.0, "pct_short_min": 15.0, "specific_1k_min": 10.0,
                  "connect_par_max": 0.6},
    "litteraire": {"mean_max": 32.0, "emdash_1k_max": 5.0, "pct_long_max": 25.0,
                   "specific_1k_min": 2.0},
    "academique": {"mean_max": 32.0, "pct_long_max": 25.0, "pct_short_min": 6.0,
                   "hedge_1k_max": 16.0, "specific_1k_min": 12.0},
}

# --------------------------------------------------------------------------
# Lexiques
# --------------------------------------------------------------------------

INTENSIFICATEURS = [
    "veritable", "veritables", "veritablement", "reel", "reelle", "reels", "reelles",
    "reellement", "authentique", "authentiques", "profond", "profonde", "profondement",
    "fondamental", "fondamentale", "fondamentaux", "fondamentalement",
    "crucial", "cruciale", "cruciaux", "essentiel", "essentielle", "essentiels",
    "essentiellement", "incontournable", "incontournables", "majeur", "majeure",
    "remarquable", "remarquablement", "fascinant", "fascinante", "puissant",
    "puissante", "robuste", "precisement", "particulierement", "notamment",
    "litteralement", "pleinement", "resolument", "indeniablement", "clairement",
    "assurement", "certainement", "considerable", "considerablement",
    "sans precedent", "a part entiere", "de premier plan",
]

CONNECTEURS = [
    "autrement dit", "en d'autres termes", "pour le dire autrement",
    "en somme", "en definitive", "au final", "a terme",
    "il convient de noter", "il convient de souligner", "il convient de rappeler",
    "il est important de noter", "il est important de souligner",
    "il est a noter", "notons que", "soulignons que", "rappelons que",
    "force est de constater", "cela etant dit", "ceci dit", "cela dit",
    "a l'inverse", "en revanche", "par ailleurs", "des lors", "de fait",
    "ainsi", "en effet", "toutefois", "neanmoins", "par consequent",
    "de plus", "en outre", "enfin", "bref", "en resume", "pour resumer",
    "en conclusion", "pour conclure", "en fin de compte",
]

# Connecteurs les plus caracteristiques : signales meme hors debut de phrase
CONNECTEURS_FORTS = [
    "autrement dit", "en d'autres termes", "pour le dire autrement",
    "il convient de noter", "il convient de souligner", "il convient de rappeler",
    "il est important de noter", "il est important de souligner",
    "force est de constater", "en somme", "en definitive", "au final",
]

HEDGING = [
    "pourrait", "pourraient", "peut-etre", "semble", "semblent", "tend a",
    "tendent a", "dans une certaine mesure", "generalement", "souvent",
    "dans bien des cas", "le plus souvent", "en general", "a priori",
    "relativement", "plutot", "quelque peu", "il se peut",
]

METAPHORES = [
    "au coeur de", "pierre angulaire", "fil rouge", "prisme", "paysage",
    "ecosysteme", "levier", "brique", "socle", "colonne vertebrale",
    "changement de paradigme", "revolution", "arsenal", "boite a outils",
    "garde-fou", "cercle vertueux", "terrain de jeu", "nouvelle donne",
    "a double tranchant", "veritable mine d'or", "epine dorsale",
    "tour de force", "coup de projecteur", "ligne de mire",
]

ANGLICISMES = {
    "adresser un probleme": "traiter, aborder",
    "adresser ce probleme": "traiter, aborder",
    "adresser les enjeux": "traiter, aborder",
    "supporte cette": "prend en charge",
    "supporter cette": "prendre en charge",
    "supporte le format": "prend en charge",
    "delivrer de la valeur": "fournir, produire",
    "delivrer une valeur": "fournir, produire",
    "impacter": "affecter, peser sur",
    "impacte": "affecte, pese sur",
    "impactent": "affectent",
    "en termes de": "pour, quant a, en matiere de",
    "base sur": "fonde sur, a partir de",
    "basee sur": "fondee sur, a partir de",
    "bases sur": "fondes sur",
    "basees sur": "fondees sur",
    "initier": "lancer, engager",
    "initie": "lance, engage",
    "challenger": "remettre en cause",
    "dedie a": "consacre a, reserve a",
    "dediee a": "consacree a, reservee a",
    "au final": "finalement, en fin de compte",
    "game changer": "(reformuler)",
    "opportunite de": "occasion de",
    "digital": "numerique",
    "digitale": "numerique",
    "supporter les": "prendre en charge les",
}

OUVERTURES = [
    "dans un monde ou", "a l'heure ou", "a l'ere du", "a l'ere de",
    "plongeons dans", "explorons ensemble", "decryptons",
    "dans cet article", "nous allons voir", "que vous soyez",
    "vous vous demandez peut-etre", "une chose est sure",
    "ce n'est qu'un debut", "l'avenir nous le dira",
    "la verite se situe entre les deux", "n'est pas un luxe",
    "reste a savoir si", "une question demeure",
]

CLOTURES_BILAN = [
    "ainsi", "en somme", "en definitive", "au final", "bref", "en resume",
    "on l'aura compris", "en conclusion", "pour resumer", "en bref",
    "vous l'aurez compris",
]

ABBREVS = [
    "M.", "MM.", "Mme.", "Mlle.", "Dr.", "Pr.", "St.", "Ste.", "etc.", "cf.",
    "p. ex.", "c.-a-d.", "ed.", "vol.", "fig.", "ref.", "art.", "chap.",
    "av. J.-C.", "ap. J.-C.", "env.", "min.", "max.", "Inc.", "Ltd.", "n°",
    "Jr.", "Sr.", "op. cit.", "ibid.", "p.", "pp.", "no.",
]

MOTS_COURANTS_CAPITALISES = {
    "Le", "La", "Les", "Un", "Une", "Des", "Ce", "Cette", "Ces", "Il", "Elle",
    "Ils", "Elles", "On", "Nous", "Vous", "Je", "Tu", "Et", "Ou", "Mais",
    "Or", "Donc", "Car", "Ni", "Si", "Quand", "Comme", "Dans", "Sur", "Pour",
    "Par", "Avec", "Sans", "Sous", "Chez", "Vers", "Entre", "Depuis", "Apres",
    "Avant", "Pendant", "Cependant", "Ainsi", "Alors", "Enfin", "Puis",
    "Toutefois", "Neanmoins", "Pourtant", "Lorsque", "Bien", "Plus", "Moins",
    "Tout", "Tous", "Toute", "Toutes", "Autre", "Autres", "Meme", "Aussi",
    "Voici", "Voila", "Cela", "Ceci", "Celui", "Celle", "Ceux", "Que", "Qui",
    "Quoi", "Dont", "Ou", "Non", "Oui", "En", "Au", "Aux", "Du", "De", "A",
}

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002190-\U000021FF\U00002300-\U000023FF"
    "\U00002460-\U000024FF\U000025A0-\U000027BF\U00002B00-\U00002BFF"
    "\U0000FE0F\U00002122\U000000AE]"
)

# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------

def deaccent(s):
    """Retire les accents pour la recherche lexicale (les lexiques sont sans accent)."""
    table = {
        "\u00e0": "a", "\u00e2": "a", "\u00e4": "a", "\u00e1": "a", "\u00e3": "a", "\u00e5": "a",
        "\u00e7": "c",
        "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00eb": "e",
        "\u00ee": "i", "\u00ef": "i", "\u00ec": "i", "\u00ed": "i",
        "\u00f4": "o", "\u00f6": "o", "\u00f2": "o", "\u00f3": "o", "\u00f5": "o",
        "\u00f9": "u", "\u00fb": "u", "\u00fc": "u", "\u00fa": "u",
        "\u00ff": "y", "\u00fd": "y",
        "\u00e6": "ae", "\u0153": "oe",
        "\u2019": "'", "\u2018": "'",
    }
    out = []
    for ch in s:
        low = ch.lower()
        rep = table.get(low)
        if rep is None:
            out.append(ch)
        else:
            out.append(rep.upper() if ch.isupper() else rep)
    return "".join(out)


CLASSES = {
    "a": "a\u00e0\u00e2\u00e4", "c": "c\u00e7", "e": "e\u00e9\u00e8\u00ea\u00eb",
    "i": "i\u00ee\u00ef", "o": "o\u00f4\u00f6", "u": "u\u00f9\u00fb\u00fc", "y": "y\u00ff",
}


def flex(term):
    """Rend un terme du lexique (ecrit sans accent) tolerant aux accents.

    On cherche directement dans la ligne d'origine : les positions restent
    exactes, donc les extraits affiches sont fidelement centres sur le marqueur.
    """
    out, i = [], 0
    while i < len(term):
        pair = term[i:i + 2]
        if pair == "oe":
            out.append("(?:oe|\u0153)"); i += 2; continue
        if pair == "ae":
            out.append("(?:ae|\u00e6)"); i += 2; continue
        ch = term[i]
        if ch in CLASSES:
            out.append("[" + CLASSES[ch] + "]")
        elif ch == "'":
            out.append("['\u2019]")
        elif ch == " ":
            out.append(r"\s+")
        else:
            out.append(re.escape(ch))
        i += 1
    return "".join(out)


WORD_RE = re.compile(r"[^\W\d_]+(?:['\u2019\-][^\W\d_]+)*|\d+(?:[.,]\d+)*", re.UNICODE)


def words(s):
    return WORD_RE.findall(s)


# --------------------------------------------------------------------------
# Decoupage du document
# --------------------------------------------------------------------------

def classify_lines(raw_lines):
    """Marque chaque ligne : prose, titre, code, tableau, frontmatter, puce."""
    kinds = []
    in_code = False
    in_front = False
    in_comment = False
    for i, line in enumerate(raw_lines):
        stripped = line.strip()
        # Les commentaires HTML ne sont pas du texte publie : les compter
        # diluerait les densites et fausserait le rythme.
        if in_comment:
            kinds.append("commentaire")
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            kinds.append("commentaire")
            if "-->" not in stripped:
                in_comment = True
            continue
        if i == 0 and stripped == "---":
            in_front = True
            kinds.append("frontmatter")
            continue
        if in_front:
            kinds.append("frontmatter")
            if stripped in ("---", "..."):
                in_front = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            kinds.append("code")
            continue
        if in_code:
            kinds.append("code")
            continue
        if stripped.startswith("|") or re.match(r"^\|?[\s:\-|]+\|[\s:\-|]*$", stripped):
            kinds.append("tableau")
            continue
        if re.match(r"^#{1,6}\s", stripped):
            kinds.append("titre")
            continue
        if not stripped:
            kinds.append("vide")
            continue
        if re.match(r"^([-*+]|\d+[.)])\s+", stripped):
            kinds.append("puce")
            continue
        kinds.append("prose")
    return kinds


INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
URL_RE = re.compile(r"https?://\S+")
IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def clean_inline(text):
    text = IMG_RE.sub(" ", text)
    text = LINK_RE.sub(r"\1", text)
    text = URL_RE.sub("URL", text)
    text = INLINE_CODE_RE.sub("code", text)
    return text


def build_paragraphs(raw_lines, kinds):
    """Regroupe les lignes de prose (et puces) en paragraphes."""
    paras, current = [], []
    for line, kind in zip(raw_lines, kinds):
        if kind in ("prose", "puce"):
            content = clean_inline(line.strip())
            content = re.sub(r"^([-*+]|\d+[.)])\s+", "", content)
            if kind == "puce" and content and content[-1] not in ".!?:;":
                content += "."
            current.append(content)
        else:
            if current:
                paras.append(" ".join(current).strip())
                current = []
    if current:
        paras.append(" ".join(current).strip())
    return [p for p in paras if words(p)]


SENT_SPLIT_RE = re.compile(
    r"(?<=[.!?\u2026])[\s\u00a0]+(?=[\u00ab\"\u201c(\[]?[A-Z\u00c0-\u00de0-9])"
)


def split_sentences(paragraph):
    protected = paragraph
    for ab in ABBREVS:
        protected = protected.replace(ab, ab.replace(".", "\x00"))
    protected = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + "\x00" + m.group(2), protected)
    protected = protected.replace("...", "\x01")
    parts = SENT_SPLIT_RE.split(protected)
    out = []
    for p in parts:
        s = p.replace("\x00", ".").replace("\x01", "...").strip()
        if words(s):
            out.append(s)
    return out


# --------------------------------------------------------------------------
# Reperage des occurrences (sur le texte original, avec numeros de ligne)
# --------------------------------------------------------------------------

def excerpt(line, start, end, width=34, cap=110):
    span = end - start
    if span > 70:
        width = 0
    elif span > 35:
        width = 10
    a = max(0, start - width)
    b = min(len(line), end + width)
    frag = line[a:b].strip()
    if len(frag) > cap:
        head = cap // 2 - 3
        frag = frag[:head] + " [...] " + frag[-head:]
    prefix = "..." if a > 0 else ""
    suffix = "..." if b < len(line) else ""
    return (prefix + frag + suffix).replace("\n", " ")


def alt_group(terms):
    parts = [flex(t) for t in sorted(terms, key=len, reverse=True)]
    return "(?:" + "|".join(parts) + ")"


BLANK_RE = re.compile(r"`[^`]*`|https?://\S+")
EMPH_SPAN_RE = re.compile(r"\*\*[^*]+\*\*|`[^`]+`")
LABEL_ONLY_RE = re.compile(
    r"^(?:\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]*\))\s*$")
LIST_MARK_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def label_dash(line, pos):
    """Un tiret qui separe une etiquette de sa definition n'est pas une incise.

    Deux formes : le tiret est a l'interieur d'un segment en gras ou en code
    (`**Passe 1 - Elagage**`), ou tout ce qui le precede sur la ligne est une
    etiquette isolee (`- `--json` - sortie machine`). Les compter gonflerait le
    quota sans qu'aucune phrase soit en cause.
    """
    for m in EMPH_SPAN_RE.finditer(line):
        if m.start() < pos < m.end():
            return True
    prefix = LIST_MARK_RE.sub("", line[:pos])
    return bool(LABEL_ONLY_RE.match(prefix.strip()))


def mask_inline(line):
    """Neutralise code et URL en preservant la longueur (offsets intacts)."""
    return BLANK_RE.sub(lambda m: " " * (m.end() - m.start()), line)


def scan(raw_lines, kinds):
    """Retourne un dict marqueur -> liste de (ligne, extrait, detail)."""
    hits = {}

    def add(key, lineno, line, m, detail=""):
        hits.setdefault(key, []).append({
            "ligne": lineno,
            "debut": m.start(),
            "fin": m.end(),
            "extrait": excerpt(line, m.start(), m.end()),
            "detail": detail or m.group(0).strip(),
        })

    re_intens = re.compile(r"\b" + alt_group(INTENSIFICATEURS) + r"\b", re.I)
    re_connect_forts = re.compile(r"\b" + alt_group(CONNECTEURS_FORTS) + r"\b", re.I)
    re_connect_debut = re.compile(
        r"(?:^|(?<=[.!?\u2026]\s))\s*" + alt_group(CONNECTEURS) + r"\b", re.I)
    re_hedge = re.compile(r"\b" + alt_group(HEDGING) + r"\b", re.I)
    re_metaph = re.compile(r"\b" + alt_group(METAPHORES) + r"\b", re.I)
    re_anglic = re.compile(r"\b" + alt_group(ANGLICISMES.keys()) + r"\b", re.I)
    re_ouvert = re.compile(r"\b" + alt_group(OUVERTURES) + r"\b", re.I)
    re_contrast = re.compile(
        r"\bn(?:e|['\u2019])[^.!?;]{0,90}?\bpas\b[^.!?;]{0,90}?"
        r"\b(?:mais|c['\u2019]est)\b", re.I)
    re_contrast2 = re.compile(
        r"\b(?:moins\s+\w+\s+que|plus\s+qu['\u2019]une?\s+simple|loin\s+d['\u2019][e\u00e9\u00ea]tre|"
        r"non\s+pas\s+\w+\s+mais|ce\s+n['\u2019]est\s+pas\s+tant|"
        r"il\s+ne\s+s['\u2019]agit\s+pas)\b", re.I)
    # negation suivie d'un tiret cadratin : meme figure, autre ponctuation
    re_contrast3 = re.compile(
        r"\bn(?:e|['\u2019])[^.!?;]{0,60}?\bpas\b[^.!?;]{0,60}?\u2014", re.I)
    # Une triade est une enumeration de trois termes paralleles. Sans exiger ce
    # parallelisme, le motif "A, B et C" attrape n'importe quelle subordonnee
    # suivie d'une coordination, ce qui noie les vraies triades.
    det = (r"(?:[dl]['\u2019]|(?:l[ea]s?|un[e]?|des|du|de|leurs?|ses|mes|tes"
           r"|nos|vos|cette|cet|ce|ces|aux|au|son|sa)\s+)")
    noconj = r"(?:(?!\s(?:et|ou|mais|donc|car|ni)\s)[^,;:.!?()\[\]\u2014])"
    item_nom = det + noconj + r"{2,40}"
    re_triade_nom = re.compile(
        r"\b(" + item_nom + r"),\s*(" + item_nom + r")\s+(?:et|ou)\s+("
        + item_nom + r")(?=[.,;:!?)\]]|$)", re.I)

    stop = (r"(?:l[ea]s?|un[e]?|des|du|de|d['\u2019]|aux?|[a\u00e0]|en|avec|pour"
            r"|par|sans|sur|sous|dans|chez|vers|entre|et|ou|qui|que|dont"
            r"|o[u\u00f9]|est|sont|c['\u2019]est)")
    word = r"(?!" + stop + r"\b)[^\W\d_][\w'\u2019-]*"
    item_adj = word + r"(?:\s+" + word + r"){0,2}"
    re_triade_adj = re.compile(
        r"\b(" + item_adj + r"),\s*(" + item_adj + r")\s+(?:et|ou)\s+("
        + item_adj + r")(?=[.,;:!?)\]]|$)", re.I)
    re_titre_binaire = re.compile(r"^#{1,6}\s+[^:\n]{2,60}\s*:\s*\S")

    for idx, (line, kind) in enumerate(zip(raw_lines, kinds), start=1):
        if kind in ("code", "frontmatter", "commentaire"):
            continue
        plain = mask_inline(line)

        if kind == "titre":
            m = re_titre_binaire.search(line)
            if m:
                add("T9", idx, line, m, line.strip())
            for m in EMOJI_RE.finditer(line):
                add("T8", idx, line, m)
            continue

        # T1 : tirets cadratins en incise. On exclut la puce en debut de ligne,
        # les cellules de tableau et les tirets d'etiquette : aucun n'est une
        # incise, et les compter fausserait le quota.
        if kind != "tableau":
            for m in re.finditer(r"\u2014", line):
                before = line[:m.start()].strip()
                if not before and m.start() < 4:
                    continue
                if label_dash(line, m.start()):
                    continue
                add("T1", idx, line, m, "tiret cadratin")

            # T2 : tiret colle aux mots (usage anglais)
            for m in re.finditer(r"\w\u2014|\u2014\w", line):
                add("T2", idx, line, m, "tiret non espace")

        # T4 : guillemets droits, points de suspension unicode
        for m in re.finditer(r'"|\u2026', line):
            add("T4", idx, line, m, "guillemet droit ou points de suspension")

        # T6 : gras hors titre / hors ouverture de puce
        if kind != "puce" or not re.match(r"^\s*([-*+]|\d+[.)])\s+\*\*", line):
            for m in re.finditer(r"\*\*[^*]+\*\*", line):
                add("T6", idx, line, m, "gras intra-paragraphe")
        else:
            m = re.search(r"\*\*[^*]+\*\*\s*:", line)
            if m:
                add("T7", idx, line, m, "puce a tete en gras")

        # T8 : emoji
        for m in EMOJI_RE.finditer(line):
            add("T8", idx, line, m, "emoji")

        if kind in ("tableau",):
            continue

        for m in re_intens.finditer(plain):
            add("I", idx, line, m)
        for m in re_connect_forts.finditer(plain):
            add("C", idx, line, m)
        for m in re_connect_debut.finditer(plain):
            add("C", idx, line, m)
        for m in re_hedge.finditer(plain):
            add("H", idx, line, m)
        for m in re_metaph.finditer(plain):
            add("M", idx, line, m)
        for m in re_anglic.finditer(plain):
            key = deaccent(m.group(0)).lower()
            key = re.sub(r"\s+", " ", key)
            suggestion = ANGLICISMES.get(key, "")
            add("A", idx, line, m, m.group(0).strip() +
                (" -> " + suggestion if suggestion else ""))
        for m in re_ouvert.finditer(plain):
            add("O", idx, line, m)
        for m in re_contrast.finditer(plain):
            add("X", idx, line, m)
        for m in re_contrast2.finditer(plain):
            add("X", idx, line, m)
        for m in re_contrast3.finditer(plain):
            add("X", idx, line, m, "negation + tiret")
        for m in re_triade_nom.finditer(plain):
            add("Y", idx, line, m, m.group(0).strip()[:80])
        for m in re_triade_adj.finditer(plain):
            add("Y", idx, line, m, m.group(0).strip()[:80])

    # Deduplication : plusieurs regex peuvent viser la meme tournure.
    # On elimine les doublons exacts, puis les spans qui se chevauchent sur
    # une meme ligne, en gardant le plus long (le plus informatif).
    for key, lst in hits.items():
        seen, uniq = set(), []
        for h in lst:
            sig = (h["ligne"], h["detail"].lower())
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append(h)
        uniq.sort(key=lambda h: (h["ligne"], h["debut"], -(h["fin"] - h["debut"])))
        kept = []
        for h in uniq:
            if kept and kept[-1]["ligne"] == h["ligne"] and h["debut"] < kept[-1]["fin"]:
                continue
            kept.append(h)
        hits[key] = kept
    return hits


# --------------------------------------------------------------------------
# Metriques
# --------------------------------------------------------------------------

def specificity_count(paragraphs):
    """Compte les noms propres et les nombres : ce qu'un LLM invente le moins."""
    n = 0
    for para in paragraphs:
        for sent in split_sentences(para):
            toks = re.findall(r"\S+", sent)
            for i, tok in enumerate(toks):
                bare = tok.strip(".,;:!?()[]{}\u00ab\u00bb\"'\u2019\u2014-")
                if not bare:
                    continue
                if re.search(r"\d", bare):
                    n += 1
                    continue
                if re.match(r"^[A-Z]{2,}$", bare):
                    n += 1
                    continue
                if i > 0 and re.match(r"^[A-Z\u00c0-\u00de]", bare) \
                        and bare not in MOTS_COURANTS_CAPITALISES:
                    n += 1
    return n


def compute(paragraphs, hits, thresholds):
    sentences = []
    para_lengths = []
    for para in paragraphs:
        sents = split_sentences(para)
        if not sents:
            continue
        para_lengths.append(len(sents))
        sentences.extend(sents)

    lengths = [len(words(s)) for s in sentences]
    nwords = sum(lengths)
    nsent = len(lengths)
    npar = len(para_lengths)
    k = max(nwords, 1) / 1000.0

    mean = statistics.fmean(lengths) if lengths else 0.0
    std = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    cv = std / mean if mean else 0.0
    pct_long = 100.0 * sum(1 for x in lengths if x > 40) / nsent if nsent else 0.0
    pct_short = 100.0 * sum(1 for x in lengths if x < 10) / nsent if nsent else 0.0

    pmean = statistics.fmean(para_lengths) if para_lengths else 0.0
    pstd = statistics.pstdev(para_lengths) if len(para_lengths) > 1 else 0.0
    pcv = pstd / pmean if pmean else 0.0

    n = lambda key: len(hits.get(key, []))

    t = thresholds
    metrics = [
        ("mean", "Longueur moyenne des phrases", mean, "mots",
         mean > t["mean_max"], "15-20", "> %.0f" % t["mean_max"]),
        ("std", "Ecart-type des longueurs", std, "mots",
         std < t["std_min"], "> 10", "< %.0f" % t["std_min"]),
        ("cv", "Coefficient de variation", cv, "",
         cv < t["cv_min"], "> 0.55", "< %.2f" % t["cv_min"]),
        ("pct_long", "Part de phrases > 40 mots", pct_long, "%",
         pct_long > t["pct_long_max"], "< 8 %", "> %.0f %%" % t["pct_long_max"]),
        ("pct_short", "Part de phrases < 10 mots", pct_short, "%",
         pct_short < t["pct_short_min"], "> 20 %", "< %.0f %%" % t["pct_short_min"]),
        ("emdash", "Tirets cadratins / 1000 mots", n("T1") / k, "",
         n("T1") / k > t["emdash_1k_max"], "<= 1", "> %.0f" % t["emdash_1k_max"]),
        ("intens", "Intensificateurs / 1000 mots", n("I") / k, "",
         n("I") / k > t["intens_1k_max"], "< 4", "> %.0f" % t["intens_1k_max"]),
        ("contrast", "Contrastes 'pas X mais Y' / 1000 mots", n("X") / k, "",
         n("X") / k > t["contrast_1k_max"], "<= 1", "> %.0f" % t["contrast_1k_max"]),
        ("connect", "Connecteurs de transition / paragraphe",
         n("C") / max(npar, 1), "",
         n("C") / max(npar, 1) > t["connect_par_max"], "< 0.4",
         "> %.1f" % t["connect_par_max"]),
        ("triad", "Triades / 1000 mots", n("Y") / k, "",
         n("Y") / k > t["triad_1k_max"], "< 2", "> %.0f" % t["triad_1k_max"]),
        ("hedge", "Hedging / 1000 mots", n("H") / k, "",
         n("H") / k > t["hedge_1k_max"], "< 6", "> %.0f" % t["hedge_1k_max"]),
        ("specific", "Noms propres + chiffres / 1000 mots",
         specificity_count(paragraphs) / k, "",
         specificity_count(paragraphs) / k < t["specific_1k_min"], "> 12",
         "< %.0f" % t["specific_1k_min"]),
        ("par_cv", "Variation des longueurs de paragraphe", pcv, "",
         pcv < t["par_cv_min"], "> 0.50", "< %.2f" % t["par_cv_min"]),
    ]

    return {
        "stats": {
            "mots": nwords, "phrases": nsent, "paragraphes": npar,
            "phrase_moyenne": round(mean, 1),
            "phrase_ecart_type": round(std, 1),
            "phrase_min": min(lengths) if lengths else 0,
            "phrase_max": max(lengths) if lengths else 0,
        },
        "metrics": [
            {"cle": c, "libelle": lab, "valeur": round(v, 2), "unite": u,
             "hors_cible": bool(bad), "cible": tgt, "suspect_si": susp}
            for (c, lab, v, u, bad, tgt, susp) in metrics
        ],
        "sentences": sentences,
        "lengths": lengths,
    }


LABELS = {
    "T1": "Tiret cadratin en incise",
    "T2": "Tiret cadratin non espace (usage anglais)",
    "T4": "Guillemets droits / points de suspension unicode",
    "T6": "Gras intra-paragraphe",
    "T7": "Puce ouverte par un terme en gras",
    "T8": "Emoji",
    "T9": "Titre binaire 'Concept : precision'",
    "I": "Intensificateur vide",
    "C": "Connecteur de transition",
    "H": "Hedging",
    "M": "Metaphore par defaut",
    "A": "Anglicisme de traduction",
    "O": "Ouverture / cloture toute faite",
    "X": "Contraste correctif 'pas X mais Y'",
    "Y": "Triade (X, Y et Z)",
}

ORDER = ["X", "I", "C", "T1", "Y", "A", "O", "M", "H", "T6", "T2", "T4", "T7", "T8", "T9"]


def verdict(nbad):
    if nbad <= 2:
        return "texte propre"
    if nbad <= 5:
        return "tics presents, corrigeables"
    return "reecriture profonde necessaire"


def render(path, registre, result, hits, max_occ):
    out = []
    st = result["stats"]
    out.append("=" * 66)
    out.append("ANALYSE DES MARQUEURS LLM")
    out.append("Fichier  : %s" % path)
    out.append("Registre : %s" % registre)
    out.append("Volume   : %d mots | %d phrases | %d paragraphes"
               % (st["mots"], st["phrases"], st["paragraphes"]))
    out.append("=" * 66)
    if st["mots"] < 200:
        out.append("")
        out.append("/!\\ Texte court (%d mots) : les densites pour 1000 mots et"
                   % st["mots"])
        out.append("    l'ecart-type sont peu fiables. Lire les occurrences,")
        out.append("    pas le score.")
    out.append("")
    out.append("--- METRIQUES ---")
    nbad = 0
    for m in result["metrics"]:
        flag = "!!" if m["hors_cible"] else "ok"
        if m["hors_cible"]:
            nbad += 1
        val = "%.2f" % m["valeur"] if m["valeur"] < 10 else "%.1f" % m["valeur"]
        out.append("  %s  %-42s %8s %-5s  (cible %s ; suspect %s)"
                   % (flag, m["libelle"], val, m["unite"], m["cible"], m["suspect_si"]))
    out.append("")
    out.append("SCORE : %d metriques hors cible sur %d  ->  %s"
               % (nbad, len(result["metrics"]), verdict(nbad)))
    out.append("")

    out.append("--- MARQUEURS LOCALISES ---")
    any_hit = False
    for key in ORDER:
        lst = hits.get(key, [])
        if not lst:
            continue
        any_hit = True
        out.append("")
        out.append("[%s] %s - %d occurrence(s)" % (key, LABELS[key], len(lst)))
        for h in lst[:max_occ]:
            out.append("   L%-5d %s" % (h["ligne"], h["extrait"]))
        if len(lst) > max_occ:
            out.append("   ... et %d autres (--max-occ pour tout voir)"
                       % (len(lst) - max_occ))
    if not any_hit:
        out.append("  (aucun)")
    out.append("")

    lengths = result["lengths"]
    if lengths:
        out.append("--- PROFIL DE RYTHME (longueur de chaque phrase, en mots) ---")
        row = []
        for i, L in enumerate(lengths):
            row.append("%3d" % L)
            if len(row) == 20:
                out.append("  " + " ".join(row))
                row = []
        if row:
            out.append("  " + " ".join(row))
        out.append("")
        out.append("  Une suite de nombres proches = rythme de machine.")
        out.append("  Un texte humain alterne brutalement (5, 34, 12, 8, 41...).")
    out.append("")
    out.append("--- CE QUE CE SCRIPT NE VOIT PAS ---")
    out.append("  Le fond : sources, dates, cas vecus, opinions tranchees,")
    out.append("  aveux d'ignorance, digressions. A juger a la lecture.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Detecte les marqueurs d'ecriture LLM (francais).")
    ap.add_argument("fichier", help="chemin du fichier, ou - pour l'entree standard")
    ap.add_argument("--registre", default="prose", choices=sorted(REGISTRES),
                    help="ajuste les seuils selon le genre (defaut: prose)")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    ap.add_argument("--max-occ", type=int, default=12,
                    help="occurrences affichees par marqueur (defaut: 12)")
    args = ap.parse_args()

    if args.fichier == "-":
        text = sys.stdin.read()
        label = "<stdin>"
    else:
        p = Path(args.fichier)
        if not p.exists():
            sys.exit("Fichier introuvable : %s" % p)
        text = p.read_text(encoding="utf-8")
        label = str(p)

    raw_lines = text.splitlines()
    kinds = classify_lines(raw_lines)
    paragraphs = build_paragraphs(raw_lines, kinds)
    if not paragraphs:
        sys.exit("Aucune prose exploitable dans %s" % label)

    hits = scan(raw_lines, kinds)
    thresholds = dict(BASE)
    thresholds.update(REGISTRES[args.registre])
    result = compute(paragraphs, hits, thresholds)

    if args.json:
        nbad = sum(1 for m in result["metrics"] if m["hors_cible"])
        payload = {
            "fichier": label,
            "registre": args.registre,
            "stats": result["stats"],
            "metriques": result["metrics"],
            "score": {"hors_cible": nbad, "total": len(result["metrics"]),
                      "verdict": verdict(nbad),
                      "fiable": result["stats"]["mots"] >= 200},
            "longueurs_phrases": result["lengths"],
            "marqueurs": {
                k: {"libelle": LABELS[k], "total": len(v), "occurrences": v[:args.max_occ]}
                for k, v in hits.items() if v
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(label, args.registre, result, hits, args.max_occ))


if __name__ == "__main__":
    main()
