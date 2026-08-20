#!/usr/bin/env python3
"""Extrait la prose narrative du PDF de Evans, en ecartant tout ce qui n'est
pas de la phrase ecrite : en-tetes courants, code Java, legendes, diagrammes.

Le livre compose les noms de patterns en petites capitales, que pdftotext rend
en majuscules. Les laisser telles quelles ferait passer 'ENTITY' pour un
acronyme et gonflerait la densite de noms propres, qui est justement une des
metriques a calibrer.
"""
import re, sys, pathlib

ACRONYMES = {"XML", "UML", "SQL", "API", "GUI", "JDBC", "CRUD", "OOP", "HTML",
             "HTTP", "EJB", "RDBMS", "CORBA", "CASE", "IEEE", "ACID", "URL",
             "JSP", "DTD", "SOAP", "RPC", "TCP", "MVC", "PDF", "CAD", "GPS"}

CODE = re.compile(
    r"(\{|\}|;\s*$|\breturn\b|\bpublic\b|\bprivate\b|\bprotected\b|\bvoid\b"
    r"|\bnew\s+[A-Z]|\bimport\b|\bpackage\b|\bclass\s+[A-Z]|//|\bnull\b"
    r"|==|!=|\+=|\(\)|\[\]|\bint\b|\bboolean\b|\bString\b)")
LEGENDE = re.compile(r"^\s*(Figure|Table|Listing|Example)\s+[\dIVX]+[.:]", re.I)
ENTETE = re.compile(r"^\s*(Part\s+[IVX]+:|Chapter\s+\w+\.|Domain-Driven Design)")
NUM_SEUL = re.compile(r"^\s*\d+\s*$")


def normalise_petites_capitales(texte):
    def repl(m):
        mot = m.group(0)
        if len(mot) >= 4 and mot not in ACRONYMES:
            return mot.capitalize()
        return mot
    texte = re.sub(r"\b[A-Z]{2,}\b", repl, texte)
    # pdftotext laisse une espace avant la ponctuation apres les petites capitales
    return re.sub(r"\s+([.,;:!?])", r"\1", texte)


def pages_utiles(brut, debut, fin):
    return brut.split("\f")[debut:fin]


def nettoie(pages):
    paragraphes, courant = [], []
    for page in pages:
        lignes = page.splitlines()
        for ligne in lignes:
            nu = ligne.strip()
            if not nu:
                if courant:
                    paragraphes.append(" ".join(courant))
                    courant = []
                continue
            if ENTETE.match(nu) or LEGENDE.match(nu) or NUM_SEUL.match(nu):
                if courant:
                    paragraphes.append(" ".join(courant)); courant = []
                continue
            if CODE.search(nu):
                if courant:
                    paragraphes.append(" ".join(courant)); courant = []
                continue
            # ligne tres courte et sans ponctuation finale : titre ou etiquette
            if len(nu.split()) <= 4 and not nu.endswith((".", "!", "?", ",")):
                if courant:
                    paragraphes.append(" ".join(courant)); courant = []
                continue
            courant.append(nu)
        if courant:
            paragraphes.append(" ".join(courant)); courant = []

    sortie = []
    for p in paragraphes:
        p = normalise_petites_capitales(p)
        mots = p.split()
        # Un paragraphe de prose fait au moins une trentaine de mots ; en deca
        # on ramasse des legendes, des puces tronquees et du bruit de mise en page.
        if len(mots) < 30:
            continue
        if not re.search(r"[.!?]\s*$", p):
            continue
        sortie.append(p)
    return sortie


if __name__ == "__main__":
    brut = pathlib.Path(sys.argv[1]).read_text(errors="replace")
    paras = nettoie(pages_utiles(brut, 25, 557))
    total = sum(len(p.split()) for p in paras)
    pathlib.Path(sys.argv[2]).write_text("\n\n".join(paras))
    print(f"{len(paras)} paragraphes, {total} mots retenus")
