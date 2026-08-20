#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse.py — Detection des marqueurs d'ecriture LLM, en francais et en anglais.

Calcule les metriques objectives (rythme, densite de tics) et localise les
occurrences avec leur numero de ligne, pour que la correction soit chirurgicale.

Le moteur ne connait aucune langue. Tout ce qui est propre a une langue —
lexiques, motifs, seuils, liste des metriques scorees — vit dans
../lexiques/<code>.json. Analyser un texte anglais avec les lexiques francais
donnait un faux blanc-seing : le moteur ne trouvait rien parce qu'il ne
cherchait rien. D'ou la detection de langue, et le refus de deviner en silence.

Ce script ne juge que la surface. Le fond (chiffres, sources, opinions,
aveux d'ignorance) reste a l'appreciation du lecteur.

Usage:
    python3 analyse.py texte.md
    python3 analyse.py texte.md --registre technique
    python3 analyse.py texte.md --langue en
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

LEXIQUES_DIR = Path(__file__).resolve().parent.parent / "lexiques"

# --------------------------------------------------------------------------
# Table des metriques
#
# Le moteur sait calculer ces dix-sept metriques ; chaque langue declare
# lesquelles elle score, dans son champ "metriques". Le francais en garde
# treize (ses seuils viennent d'un jugement, pas d'une mesure), l'anglais
# dix-sept (seuils derives du corpus Evans, cf. calibration/README.md).
#
# Les libelles sont en francais : le rapport s'adresse a l'utilisateur, pas
# au texte analyse.
#
#   sens   : ">" suspect au-dessus du seuil, "<" suspect en dessous
#   cible  : la valeur souhaitable, affichee a titre de reperage
#   dec    : nombre minimal de decimales a l'affichage du seuil
#   source : cle de la valeur brute calculee par valeurs_brutes()
# --------------------------------------------------------------------------

METRIQUES = [
    ("phrase_moyenne",      "Longueur moyenne des phrases",            "mots", ">", "15-20",  0),
    ("phrase_ecart_type",   "Ecart-type des longueurs",                "mots", "<", "> 10",   0),
    ("cv",                  "Coefficient de variation",                "",     "<", "> 0.55", 2),
    ("pct_long",            "Part de phrases > 40 mots",               "%",    ">", "< 8 %",  0),
    ("pct_court",           "Part de phrases < 10 mots",               "%",    "<", "> 20 %", 0),
    ("tirets_1k",           "Tirets cadratins / 1000 mots",            "",     ">", "<= 1",   0),
    ("intensificateurs_1k", "Intensificateurs / 1000 mots",            "",     ">", "< 4",    0),
    ("contrastes_1k",       "Contrastes 'pas X mais Y' / 1000 mots",   "",     ">", "<= 1",   0),
    ("not_only_1k",         "'not only... but also' / 1000 mots",      "",     ">", "0",      1),
    ("connecteurs_par",     "Connecteurs de transition / paragraphe",  "",     ">", "< 0.4",  1),
    ("triades_1k",          "Triades / 1000 mots",                     "",     ">", "< 2",    0),
    ("hedging_1k",          "Hedging / 1000 mots",                     "",     ">", "< 6",    0),
    ("metaphores_1k",       "Metaphores par defaut / 1000 mots",       "",     ">", "< 1",    1),
    ("ouvertures_1k",       "Ouvertures toutes faites / 1000 mots",    "",     ">", "0",      1),
    ("participiales_1k",    "Participiales finales / 1000 mots",       "",     ">", "< 1",    1),
    ("specifique_1k",       "Noms propres + chiffres / 1000 mots",     "",     "<", "> 12",   0),
    ("par_cv",              "Variation des longueurs de paragraphe",   "",     "<", "> 0.50", 2),
]

META = {m[0]: {"libelle": m[1], "unite": m[2], "sens": m[3], "cible": m[4], "dec": m[5]}
        for m in METRIQUES}
ORDRE_METRIQUES = [m[0] for m in METRIQUES]

# Le vocabulaire des metriques est celui de calibration/calibre.py, pour qu'un
# fichier de seuils derive la-bas soit reutilisable tel quel. Les noms courts
# de l'ancienne version restent acceptes : un fichier de langue ecrit avec
# "emdash" ou "pct_short" continue de charger.
ALIAS = {
    "mean": "phrase_moyenne", "mean_max": "phrase_moyenne",
    "std": "phrase_ecart_type", "std_min": "phrase_ecart_type",
    "cv_min": "cv",
    "pct_long_max": "pct_long",
    "pct_short": "pct_court", "pct_short_min": "pct_court",
    "emdash": "tirets_1k", "emdash_1k_max": "tirets_1k",
    "intens": "intensificateurs_1k", "intens_1k_max": "intensificateurs_1k",
    "contrast": "contrastes_1k", "contrast_1k_max": "contrastes_1k",
    "connect": "connecteurs_par", "connect_par_max": "connecteurs_par",
    "triad": "triades_1k", "triad_1k_max": "triades_1k",
    "hedge": "hedging_1k", "hedge_1k_max": "hedging_1k",
    "metaph": "metaphores_1k", "ouvert": "ouvertures_1k",
    "particip": "participiales_1k", "not_only": "not_only_1k",
    "specific": "specifique_1k", "specific_1k_min": "specifique_1k",
    "par_cv_min": "par_cv",
}


def canon(cle):
    return ALIAS.get(cle, cle)


# --------------------------------------------------------------------------
# Marqueurs localises
# --------------------------------------------------------------------------

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
    "A": "Faux ami de traduction",
    "O": "Ouverture / cloture toute faite",
    "X": "Contraste correctif 'pas X mais Y'",
    "N": "Balancement 'not only... but also'",
    "P": "Participiale finale (', allowing...')",
    "Y": "Triade (X, Y et Z)",
}

ORDER = ["X", "N", "I", "C", "T1", "Y", "A", "O", "M", "P", "H",
         "T6", "T2", "T4", "T7", "T8", "T9"]

# Quelle metrique compte quel marqueur.
SOURCE_MARQUEUR = {
    "tirets_1k": "T1", "intensificateurs_1k": "I", "contrastes_1k": "X",
    "not_only_1k": "N", "connecteurs_par": "C", "triades_1k": "Y",
    "hedging_1k": "H", "metaphores_1k": "M", "ouvertures_1k": "O",
    "participiales_1k": "P",
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
    Reserve aux langues qui declarent "accents_tolerants": true.
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


def litteral(term):
    """Echappement simple, pour les langues sans variantes accentuees.

    On garde deux souplesses : l'espace absorbe un retour a la ligne, et
    l'apostrophe droite vaut l'apostrophe typographique.
    """
    esc = re.escape(term)
    # re.escape protege l'espace depuis Python 3.7 seulement : on couvre les deux.
    esc = esc.replace("\\ ", r"\s+").replace(" ", r"\s+")
    return esc.replace("\\'", "['\u2019]").replace("'", "['\u2019]")


WORD_RE = re.compile(r"[^\W\d_]+(?:['\u2019\-][^\W\d_]+)*|\d+(?:[.,]\d+)*", re.UNICODE)


def words(s):
    return WORD_RE.findall(s)


# --------------------------------------------------------------------------
# Chargement d'une langue
# --------------------------------------------------------------------------

class ErreurLangue(Exception):
    pass


class Langue:
    """Un fichier de langue : lexiques, motifs, seuils, metriques scorees.

    Tout est optionnel sauf le code de langue. Une langue qui ne declare pas
    de motif de triade n'aura pas de triades ; elle ne doit alors pas scorer
    la metrique correspondante. Mieux vaut un trou declare qu'un zero flatteur.
    """

    def __init__(self, chemin):
        try:
            d = json.loads(Path(chemin).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ErreurLangue("%s illisible : %s" % (chemin, e))
        self.chemin = Path(chemin)
        self.code = d.get("langue") or self.chemin.stem
        self.nom = d.get("nom", self.code)
        self.statut = d.get("statut", "")
        self.mots_outils = set(d.get("detection", {}).get("mots_outils", []))
        # Une langue peut taire un marqueur qui ne la concerne pas : le
        # guillemet droit (T4) est une faute en francais, la norme en anglais.
        self.desactives = set(d.get("marqueurs_desactives", []))
        # ... et renommer celui dont l'intitule est propre a sa langue
        # (« anglicisme » ne veut rien dire dans un texte anglais).
        self.labels = dict(LABELS)
        self.labels.update(d.get("libelles_marqueurs", {}))

        souple = bool(d.get("accents_tolerants", False))
        self.echappe = flex if souple else litteral

        lx = d.get("lexiques", {})
        self.re_intens = self._alt(lx.get("intensificateurs"))
        self.re_connect_forts = self._alt(lx.get("connecteurs_forts"))
        self.re_hedge = self._alt(lx.get("hedging"))
        self.re_metaph = self._alt(lx.get("metaphores"))
        self.re_ouvert = self._alt(lx.get("ouvertures"))
        self.faux_amis = lx.get("faux_amis") or {}
        self.re_faux_amis = self._alt(list(self.faux_amis)) if self.faux_amis else None

        # Les connecteurs "ordinaires" ne comptent qu'en tete de phrase : un
        # « ainsi » au milieu d'une phrase est du francais, pas un tic.
        groupe = self._groupe(lx.get("connecteurs"))
        self.re_connect_debut = re.compile(
            r"(?:^|(?<=[.!?\u2026]\s))\s*" + groupe + r"\b", re.I) if groupe else None

        m = d.get("motifs", {})
        self.re_contrast = []
        for item in m.get("contraste", []):
            if isinstance(item, dict):
                self.re_contrast.append((re.compile(item["motif"], re.I),
                                         item.get("detail", "")))
            else:
                self.re_contrast.append((re.compile(item, re.I), ""))
        self.re_not_only = re.compile(m["not_only"], re.I) if m.get("not_only") else None
        self.re_particip = (re.compile(m["participiale_finale"], re.I)
                            if m.get("participiale_finale") else None)
        self.re_triade_nom, self.re_triade_adj = self._triades(m)

        self.capitalises = set(d.get("mots_capitalises_courants", []))
        self.abreviations = d.get("abreviations", [])

        self.metriques = [canon(c) for c in d.get("metriques", [])]
        inconnues = [c for c in self.metriques if c not in META]
        if inconnues:
            raise ErreurLangue("%s : metrique inconnue %s"
                               % (self.chemin.name, ", ".join(inconnues)))
        self.seuils, self.registres = self._seuils(d.get("seuils", {}))
        if self.metriques and not self.seuils:
            raise ErreurLangue("%s declare des metriques mais aucun seuil"
                               % self.chemin.name)

    # -- construction des regex ---------------------------------------------

    def _groupe(self, termes):
        if not termes:
            return None
        parts = [self.echappe(t) for t in sorted(termes, key=len, reverse=True)]
        return "(?:" + "|".join(parts) + ")"

    def _alt(self, termes):
        g = self._groupe(termes)
        return re.compile(r"\b" + g + r"\b", re.I) if g else None

    def _triades(self, m):
        """Une triade est une enumeration de trois termes paralleles.

        Sans exiger ce parallelisme, le motif "A, B et C" attrape n'importe
        quelle subordonnee suivie d'une coordination, ce qui noie les vraies
        triades. D'ou les deux formes : nominale (determinant + tete) et
        adjectivale (mots pleins seulement).
        """
        coord = m.get("coordination")
        if not coord:
            return None, None
        oxford = ",?" if m.get("triade_virgule_serie", True) else ""
        queue = r"(?=[.,;:!?)\]]|$)"

        def triple(item):
            return re.compile(r"\b(" + item + r"),\s*(" + item + r")" + oxford
                              + r"\s+" + coord + r"\s+(" + item + r")" + queue, re.I)

        nom = adj = None
        det = m.get("triade_determinant")
        if det:
            # Le determinant francais absorbe deja son separateur (« l' » ou
            # « les »), l'anglais non : d'ou le drapeau.
            esp = r"\s+" if m.get("triade_espace_apres_determinant", True) else ""
            excl = m.get("triade_conjonctions_exclues") or coord
            nom = triple(det + esp + r"(?:(?!\s" + excl
                         + r"\s)[^,;:.!?()\[\]\u2014]){2,40}")
        vides = m.get("triade_mots_vides")
        if vides:
            mot = r"(?!" + vides + r"\b)[^\W\d_][\w'\u2019-]*"
            adj = triple(mot + r"(?:\s+" + mot + r"){0,2}")
        return nom, adj

    # -- seuils --------------------------------------------------------------

    def _seuils(self, bloc):
        """Accepte deux formes : {"base": ..., "registres": ...} ou un bloc plat
        de seuils (celui que produit calibration/calibre.py)."""
        brut = bloc.get("base", bloc.get("seuils", bloc))
        base = {}
        for cle, val in brut.items():
            if cle in ("registres", "base"):
                continue
            c = canon(cle)
            if c not in META:
                continue
            seuil = val.get("seuil") if isinstance(val, dict) else val
            base[c] = float(seuil)
        registres = {"prose": {}}
        for nom, over in (bloc.get("registres") or {}).items():
            registres[nom] = {canon(k): float(v) for k, v in over.items()
                              if canon(k) in META}
        return base, registres

    def seuils_pour(self, registre):
        t = dict(self.seuils)
        t.update(self.registres.get(registre, {}))
        return t

    def a_marqueur(self, cle):
        return cle not in self.desactives


def langues_disponibles():
    if not LEXIQUES_DIR.is_dir():
        return {}
    out = {}
    for p in sorted(LEXIQUES_DIR.glob("*.json")):
        out[p.stem] = p
    return out


# --------------------------------------------------------------------------
# Detection de la langue
#
# Les mots-outils sont les mots les plus frequents et les moins traduisibles
# d'une langue : "the/of/and" contre "le/de/et". Compter leur part dans le
# texte suffit, et se verifie a l'oeil.
# --------------------------------------------------------------------------

JETON_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
TAUX_PLANCHER = 0.08   # en dessous, aucune langue ne ressemble au texte
ECART_MINIMAL = 0.03   # deux langues trop proches : on ne tranche pas


def detecte_langue(texte, fichiers):
    """Retourne (code, taux, diagnostic) ; diagnostic vide si la mesure est nette."""
    jetons = [j.lower() for j in JETON_RE.findall(texte)]
    if not jetons:
        return None, 0.0, "aucun mot exploitable"
    taux = {}
    for code, chemin in fichiers.items():
        try:
            mots = set(json.loads(Path(chemin).read_text(encoding="utf-8"))
                       .get("detection", {}).get("mots_outils", []))
        except (json.JSONDecodeError, OSError):
            continue
        if mots:
            taux[code] = sum(1 for j in jetons if j in mots) / len(jetons)
    if not taux:
        return None, 0.0, "aucun fichier de langue ne declare de mots-outils"

    classe = sorted(taux.items(), key=lambda kv: kv[1], reverse=True)
    code, meilleur = classe[0]
    detail = ", ".join("%s %.1f %%" % (c, 100 * t) for c, t in classe)
    if meilleur < TAUX_PLANCHER:
        return code, meilleur, (
            "aucune langue installee ne correspond au texte (%s). "
            "Les lexiques utilises risquent de ne rien trouver, "
            "ce qui donnerait un score flatteur et faux." % detail)
    if len(classe) > 1 and meilleur - classe[1][1] < ECART_MINIMAL:
        return code, meilleur, (
            "detection incertaine, deux langues au coude a coude (%s). "
            "Forcer --langue si le resultat surprend." % detail)
    return code, meilleur, ""


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


def split_sentences(paragraph, abbrevs):
    protected = paragraph
    for ab in abbrevs:
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


BLANK_RE = re.compile(r"`[^`]*`|https?://\S+")
EMPH_SPAN_RE = re.compile(r"\*\*[^*]+\*\*|`[^`]+`")
LABEL_ONLY_RE = re.compile(
    r"^(?:\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]*\))\s*$")
LIST_MARK_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TITRE_BINAIRE_RE = re.compile(r"^#{1,6}\s+[^:\n]{2,60}\s*:\s*\S")


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


def scan(raw_lines, kinds, langue):
    """Retourne un dict marqueur -> liste de (ligne, extrait, detail)."""
    hits = {}

    def add(key, lineno, line, m, detail=""):
        if not langue.a_marqueur(key):
            return
        hits.setdefault(key, []).append({
            "ligne": lineno,
            "debut": m.start(),
            "fin": m.end(),
            "extrait": excerpt(line, m.start(), m.end()),
            "detail": detail or m.group(0).strip(),
        })

    def balaye(regex, key, lineno, line, plain, detail=""):
        if regex is None:
            return
        for m in regex.finditer(plain):
            add(key, lineno, line, m, detail)

    for idx, (line, kind) in enumerate(zip(raw_lines, kinds), start=1):
        if kind in ("code", "frontmatter", "commentaire"):
            continue
        plain = mask_inline(line)

        if kind == "titre":
            m = TITRE_BINAIRE_RE.search(line)
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

        balaye(langue.re_intens, "I", idx, line, plain)
        balaye(langue.re_connect_forts, "C", idx, line, plain)
        balaye(langue.re_connect_debut, "C", idx, line, plain)
        balaye(langue.re_hedge, "H", idx, line, plain)
        balaye(langue.re_metaph, "M", idx, line, plain)
        if langue.re_faux_amis is not None:
            for m in langue.re_faux_amis.finditer(plain):
                key = deaccent(m.group(0)).lower()
                key = re.sub(r"\s+", " ", key)
                suggestion = langue.faux_amis.get(key, "")
                add("A", idx, line, m, m.group(0).strip() +
                    (" -> " + suggestion if suggestion else ""))
        balaye(langue.re_ouvert, "O", idx, line, plain)
        for regex, detail in langue.re_contrast:
            balaye(regex, "X", idx, line, plain, detail)
        balaye(langue.re_not_only, "N", idx, line, plain)
        balaye(langue.re_particip, "P", idx, line, plain)
        for regex in (langue.re_triade_nom, langue.re_triade_adj):
            if regex is None:
                continue
            for m in regex.finditer(plain):
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

def specificity_count(phrases, capitalises):
    """Compte les noms propres et les nombres : ce qu'un LLM invente le moins."""
    n = 0
    for sent in phrases:
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
                    and bare not in capitalises:
                n += 1
    return n


def fmt_seuil(valeur, dec):
    """Affiche un seuil sans decimale inutile, mais sans en perdre non plus.

    Les seuils francais sont ronds (25, 0.8) ; ceux derives d'un corpus ne le
    sont pas (21.32). Arrondir a l'affichage ferait mentir le rapport.
    """
    ent, _, frac = ("%.2f" % valeur).partition(".")
    while len(frac) > dec and frac.endswith("0"):
        frac = frac[:-1]
    return ent + ("." + frac if frac else "")


def valeurs_brutes(paragraphs, hits, langue):
    sentences = []
    para_lengths = []
    for para in paragraphs:
        sents = split_sentences(para, langue.abreviations)
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
    pmean = statistics.fmean(para_lengths) if para_lengths else 0.0
    pstd = statistics.pstdev(para_lengths) if len(para_lengths) > 1 else 0.0

    n = lambda key: len(hits.get(key, []))

    valeurs = {
        "phrase_moyenne": mean,
        "phrase_ecart_type": std,
        "cv": std / mean if mean else 0.0,
        "pct_long": 100.0 * sum(1 for x in lengths if x > 40) / nsent if nsent else 0.0,
        "pct_court": 100.0 * sum(1 for x in lengths if x < 10) / nsent if nsent else 0.0,
        "specifique_1k": specificity_count(sentences, langue.capitalises) / k,
        "par_cv": pstd / pmean if pmean else 0.0,
    }
    for cle, marqueur in SOURCE_MARQUEUR.items():
        valeurs[cle] = (n(marqueur) / max(npar, 1) if cle == "connecteurs_par"
                        else n(marqueur) / k)

    stats = {
        "mots": nwords, "phrases": nsent, "paragraphes": npar,
        "phrase_moyenne": round(mean, 1),
        "phrase_ecart_type": round(std, 1),
        "phrase_min": min(lengths) if lengths else 0,
        "phrase_max": max(lengths) if lengths else 0,
    }
    return valeurs, stats, sentences, lengths


def compute(paragraphs, hits, langue, registre):
    valeurs, stats, sentences, lengths = valeurs_brutes(paragraphs, hits, langue)
    seuils = langue.seuils_pour(registre)

    metrics = []
    for cle in ORDRE_METRIQUES:
        if cle not in langue.metriques or cle not in seuils:
            continue
        meta = META[cle]
        s = seuils[cle]
        v = valeurs[cle]
        bad = v > s if meta["sens"] == ">" else v < s
        unite = " %" if meta["unite"] == "%" else ""
        metrics.append({
            "cle": cle,
            "libelle": meta["libelle"],
            "valeur": round(v, 2),
            "unite": meta["unite"],
            "hors_cible": bool(bad),
            "cible": meta["cible"],
            "seuil": s,
            "suspect_si": "%s %s%s" % (meta["sens"], fmt_seuil(s, meta["dec"]), unite),
        })

    return {
        "stats": stats,
        "metrics": metrics,
        "sentences": sentences,
        "lengths": lengths,
    }


def verdict(nbad, total):
    """Les paliers sont donnes pour treize metriques ; on les met a l'echelle
    du nombre reellement score, sinon l'anglais (dix-sept) serait juge plus
    severement pour la seule raison qu'il mesure plus de choses."""
    if not total:
        return "aucune metrique scoree"
    part = nbad / total
    if part <= 2 / 13.0:
        return "texte propre"
    if part <= 5 / 13.0:
        return "tics presents, corrigeables"
    return "reecriture profonde necessaire"


def render(path, langue, registre, avertissements, result, hits, max_occ):
    out = []
    st = result["stats"]
    out.append("=" * 66)
    out.append("ANALYSE DES MARQUEURS LLM")
    out.append("Fichier  : %s" % path)
    out.append("Langue   : %s (%s)" % (langue.code, langue.nom))
    out.append("Registre : %s" % registre)
    out.append("Volume   : %d mots | %d phrases | %d paragraphes"
               % (st["mots"], st["phrases"], st["paragraphes"]))
    out.append("=" * 66)
    for a in avertissements:
        out.append("")
        out.append("/!\\ %s" % a)
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
               % (nbad, len(result["metrics"]), verdict(nbad, len(result["metrics"]))))
    out.append("")

    out.append("--- MARQUEURS LOCALISES ---")
    any_hit = False
    for key in ORDER:
        lst = hits.get(key, [])
        if not lst:
            continue
        any_hit = True
        out.append("")
        out.append("[%s] %s - %d occurrence(s)" % (key, langue.labels[key], len(lst)))
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
    dispo = langues_disponibles()
    ap = argparse.ArgumentParser(
        description="Detecte les marqueurs d'ecriture LLM (francais, anglais).")
    ap.add_argument("fichier", help="chemin du fichier, ou - pour l'entree standard")
    ap.add_argument("--langue", default="auto",
                    help="auto|" + "|".join(sorted(dispo)) + " (defaut: auto)")
    ap.add_argument("--registre", default="prose",
                    help="ajuste les seuils selon le genre (defaut: prose)")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    ap.add_argument("--max-occ", type=int, default=12,
                    help="occurrences affichees par marqueur (defaut: 12)")
    args = ap.parse_args()

    if not dispo:
        sys.exit("Aucun fichier de langue dans %s" % LEXIQUES_DIR)

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

    # La langue se decide sur la prose seule : le code et les tableaux
    # fausseraient le comptage des mots-outils.
    diag_langue = ""
    if args.langue == "auto":
        code, _, diag_langue = detecte_langue("\n".join(paragraphs), dispo)
        if code is None:
            sys.exit("Langue indeterminable : %s. Utiliser --langue." % diag_langue)
    else:
        code = args.langue
        if code not in dispo:
            sys.exit("Langue inconnue : %s. Disponibles : %s"
                     % (code, ", ".join(sorted(dispo))))

    try:
        langue = Langue(dispo[code])
    except ErreurLangue as e:
        sys.exit(str(e))

    # Un registre qu'une langue n'a pas calibre n'est pas une erreur : ses
    # seuils de base restent applicables. Mais l'utilisateur doit savoir que
    # son --registre n'a rien ajuste, sinon il lit un chiffre qu'il croit
    # adapte a son genre.
    avertissements = []
    if diag_langue:
        avertissements.append("LANGUE : " + diag_langue)
    if args.registre not in langue.registres:
        avertissements.append(
            "registre '%s' non calibre pour %s (disponibles : %s) : "
            "seuils de base appliques tels quels."
            % (args.registre, code, ", ".join(sorted(langue.registres))))

    hits = scan(raw_lines, kinds, langue)
    result = compute(paragraphs, hits, langue, args.registre)

    if args.json:
        nbad = sum(1 for m in result["metrics"] if m["hors_cible"])
        payload = {
            "fichier": label,
            "langue": {"code": langue.code, "nom": langue.nom,
                       "detection": "auto" if args.langue == "auto" else "forcee",
                       "avertissement": diag_langue},
            "registre": args.registre,
            "stats": result["stats"],
            "metriques": result["metrics"],
            "score": {"hors_cible": nbad, "total": len(result["metrics"]),
                      "verdict": verdict(nbad, len(result["metrics"])),
                      "fiable": result["stats"]["mots"] >= 200 and not diag_langue},
            "avertissements": avertissements,
            "longueurs_phrases": result["lengths"],
            "marqueurs": {
                k: {"libelle": langue.labels[k], "total": len(v),
                    "occurrences": v[:args.max_occ]}
                for k, v in hits.items() if v
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(label, langue, args.registre, avertissements, result, hits,
                     args.max_occ))


if __name__ == "__main__":
    main()
