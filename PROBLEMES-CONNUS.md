# Problèmes connus — détecteur anglais

État au 20 août 2026, après la passe de validation adverse du portage bilingue.

**Le français fonctionne et n'a pas bougé** : témoin 9/13, SKILL.md 0/13,
README 1/13, sortie octet pour octet identique à la version d'avant sur
28 combinaisons fichier × registre.

**Le détecteur anglais n'est pas fiable.** Sa structure est en place, ses
lexiques et ses seuils ne le sont pas. Ce fichier liste ce qui a été mesuré,
pour que la prochaine passe attaque par le haut. Chaque constat est
reproductible : la commande est donnée.

---

## Bloquants

### 1. La métrique de spécificité récompense l'invention

`specifique_1k` compte les noms propres et les chiffres sans pouvoir vérifier
qu'ils renvoient à quoi que ce soit. Produire un chiffre plausible est
précisément ce qu'un modèle fait le mieux, et le plus dangereusement.

```bash
analyse.py t1-blog.md              # 3/17 — tics présents, corrigeables
analyse.py t1-blog-chiffres.md     # 2/17 — texte propre
```

L'unique différence entre les deux fichiers est une phrase entièrement
fabriquée : « A 2023 DORA-style survey of 214 teams put it plainly: 68 percent
of missed dates were known internally at least 9 days in advance. »

Le défaut est antérieur au portage : la métrique existe en français depuis la
première version. C'est la passe adverse qui l'a rendu visible. Il contredit
frontalement la passe 6 de la procédure, qui interdit d'inventer un chiffre.

Piste : distinguer un chiffre *vérifiable* d'un chiffre *plausible* est hors
de portée d'un script. La métrique devrait donc sortir du score et devenir une
observation rendue à la lecture, ou exiger une forme ancrée (version d'outil,
date complète, nom propre récurrent dans le texte).

### 2. Sept marqueurs sont affichés mais ne pèsent rien

T2, T4, T6, T7, T8, T9 et A sont détectés, localisés, imprimés — et absents du
score. Le rapport se contredit lui-même.

```bash
analyse.py t2-doc.md
# [T7] Puce ouverte par un terme en gras - 13 occurrence(s)
# [T9] Titre binaire 'Concept : precision' - 1 occurrence(s)
# SCORE : 0 metriques hors cible sur 17  ->  texte propre
```

Une documentation technique bâtie sur le squelette canonique, treize puces à
tête en gras, titre binaire, résumé final : « texte propre ».

### 3. Cinq registres anglais passent sous les seuils

Cinq textes écrits d'un jet, chargés de la signature courante, mesurés :

| texte | mots | score | verdict rendu |
|---|---|---|---|
| billet de blog | 555 | 3/17 | tics présents |
| doc technique | 492 | **0/17** | **texte propre** |
| post LinkedIn | 231 | 1/17 | texte propre |
| newsletter | 383 | 1/17 | texte propre |
| rapport de conseil | 457 | 3/17 | tics présents |

Aucun ne dépasse 3/17, quand la caricature de référence est à 10/17.

---

## Majeurs

### 4. Le contraste correctif rate sa forme la plus courante

Le motif couvre la reprise pronominale dans une même phrase
(« Observability is not a tool, it is a discipline » → détecté, 26,3/1000).
Il rate la forme en deux phrases à sujet non pronominal :

```bash
analyse.py p1-contrastes.md   # 13 contrastes correctifs -> 0,00/1000
```

« Your network is not your contacts. It is the people who have seen you work. »

C'est le marqueur vitrine de la skill, celui que sa description met en avant.

### 5. Six seuils sur dix-sept valent 0,00 — présence, non densité

`contrastes_1k`, `not_only_1k`, `metaphores_1k`, `ouvertures_1k`,
`participiales_1k` et `triades_1k` (à 1,24, soit une occurrence par échantillon)
se déclenchent sur une seule occurrence. Mesuré sur 120 échantillons d'Evans :
métaphores 4 fois sur 4, `not only` 5 sur 5, participiales 9 sur 9.

Cela contredit la doctrine inscrite en tête de SKILL.md : « le problème n'est
jamais un marqueur isolé, c'est la densité et la régularité ».

Cause probable : dériver un seuil au 9ᵉ décile d'un corpus où le marqueur est
quasi absent donne mécaniquement zéro. Il faut un plancher d'occurrences, ou
un seuil dérivé sur un corpus plus large.

### 6. Les lexiques contiennent de l'anglais technique ordinaire

Sept mots portent 75 % des 189 occurrences d'intensificateurs relevées chez
Evans : `essential` (31), `fundamental` (25), `critical` (25), `meaningful`
(17), `crucial` (17), `powerful` (15), `significant` (12). En contexte ils
comparent ou restreignent — « more critical than storage space », « essential
to the concept » — là où l'anglais généré qualifie sans terme de comparaison.
Une liste de mots ne voit pas cette différence.

Même défaut côté métaphores : `silver bullet` est le titre de l'article de
Fred Brooks que tout texte sur le génie logiciel cite, `harness` est un nom
commun (*test harness*), `paradigm shift` est le terme de Kuhn.

### 7. Les triades ne détectent rien d'utile

48 correspondances sur les 99 965 mots d'Evans, dont **zéro triade décorative** :
34 % sont des analyses ratées, 60 % des énumérations légitimes. Et au-delà du
syntagme, la triade générée échappe entièrement : triade de propositions
(« It is faster, it is cheaper, and it is easier to explain »), d'impératifs,
de phrases.

### 8. Le hedging ne sépare pas les deux classes

Les douze mots qui portent 84 % des 353 occurrences chez Evans sont exactement
ceux qui portent les occurrences des témoins générés. En prose technique ce
sont des instruments de précision.

### 9. Trois substitutions typographiques suffisent à échapper à T1

T1 ne cherche que U+2014. Le tiret demi-cadratin espacé (`–`) et le double
trait d'union (`--`), produits par défaut par plusieurs éditeurs, ne sont pas
comptés. Un texte n'a qu'à substituer ses tirets pour mettre `tirets_1k` à zéro.
Evans n'écrit que 3 demi-cadratins en 100 000 mots : le coût d'ajout est nul.

### 10. Le seuil de connecteurs ne survit pas au changement de format

`connecteurs_par` vaut 0,10 par paragraphe, dérivé d'un livre de 1 100
paragraphes. Sur un billet de huit paragraphes, un seul « However » en tête
suffit à passer hors cible. Le dénominateur devrait être le nombre de mots.

---

## Mineurs

11. `mission-critical` est compté comme une occurrence de `critical` : la
    limite de mot tombe sur le trait d'union. Idem `business-critical`.
12. Sur un texte court, l'avertissement « densités peu fiables » s'affiche puis
    le verdict est rendu quand même, sur ces mêmes densités.
13. La détection de langue bascule vers le français sur un texte anglais citant
    abondamment une source française : la liste française compte 36 mots-outils
    contre 11 pour l'anglais, ce qui gonfle mécaniquement le taux français.
14. `calibre.py` et `analyse.py` divergent sur `hedging_1k` (médiane 3,39 contre
    2,49, soit 27 %). Les seuils sont dérivés par le premier et appliqués par le
    second.
15. Le témoin anglais sature à 17/17. Un témoin saturé ne détecte aucune
    régression : viser 12 ou 13 sur 17.

---

## Ce qui tient

Le plancher de faux positifs, lui, est bon. Sur 118 échantillons d'Evans passés
par `analyse.py` :

| score | échantillons |
|---|---|
| 0/17 | 38 |
| 1/17 | 48 |
| 2/17 | 15 |
| 3/17 | 10 |
| 4/17 | 4 |
| 5/17 | 3 |

Médiane 1/17, maximum 5/17, aucun au-delà. Le détecteur n'accuse pas la bonne
prose. Son problème est l'inverse : il laisse passer la mauvaise.
