# skill-marqueurs-LLM

Une skill Claude Code qui détecte, mesure et corrige la « signature LLM » d'un
texte, en français comme en anglais : tirets cadratins en incise, « ne… pas X
mais Y » et son calque `not X, it's Y`, intensificateurs vides, rythme trop
régulier, triades, participiales de bénéfice, anglicismes de traduction, absence
de faits vérifiables.

Le principe : mesurer avant de corriger. Un tiret cadratin ne prouve rien, trois
par paragraphe si. Le score chiffré évite de sur-corriger un texte qui va bien
et de sous-corriger un texte qui gêne sans qu'on sache dire pourquoi.

Les deux langues ne se valent pas sur un point, et le dépôt le dit franchement.
Les seuils français viennent d'un jugement exercé. Les seuils anglais sont
mesurés sur cent mille mots de prose humaine — Eric Evans, *Domain-Driven
Design*, 2003 — découpés en 119 échantillons, frontière au 9ᵉ décile. La méthode
et les chiffres sont dans `calibration/`, pour qu'ils soient contestables
plutôt qu'à croire.

## Installation

```bash
./install-for-user.sh                      # ~/.claude/skills, lien symbolique
./install-for-project.sh ~/dev/mon-projet  # <projet>/.claude/skills, copie
```

Pour Claude Desktop, qui importe la skill sous forme d'archive :

```bash
./build-zip.sh          # dist/marqueurs-llm-<version>.zip
```

Le script valide le frontmatter et fait tourner l'analyseur sur les deux
textes-témoins, français et anglais, avant d'empaqueter. Une archive partie avec un script cassé ne se découvre
qu'après l'import, quand il est trop tard pour savoir ce qui a changé.
L'archive s'importe depuis Réglages, Capacités, Compétences.

Le lien symbolique garde la skill synchronisée avec ce dépôt pendant que vous
l'améliorez. La copie sert aux skills de projet, qui finissent versionnées avec
le dépôt et pour lesquelles un chemin absolu serait cassé après un clone.
`--copy` et `--link` inversent le comportement, `--help` détaille le reste.

## Usage direct de l'analyseur

L'analyseur tourne aussi seul, sans Claude, avec Python 3 et sans dépendance :

```bash
python3 marqueurs-llm/scripts/analyse.py article.md
python3 marqueurs-llm/scripts/analyse.py paper.md --langue en
python3 marqueurs-llm/scripts/analyse.py doc.md --registre technique
python3 marqueurs-llm/scripts/analyse.py article.md --json
cat texte.txt | python3 marqueurs-llm/scripts/analyse.py -
```

Il détecte la langue seul et l'affiche en tête du rapport ; `--langue fr|en` la
force. Il rend treize métriques en français et dix-sept en anglais, les
occurrences localisées à la ligne, et le profil de rythme : la longueur de
chaque phrase dans l'ordre. C'est ce profil qui trahit le plus sûrement une
machine, parce qu'un auteur humain suit son argument, qui n'a aucune raison
d'être régulier.

## Contenu

| Fichier | Rôle |
|---|---|
| `marqueurs-llm/SKILL.md` | les trois modes : diagnostic, correction, rédaction |
| `marqueurs-llm/scripts/analyse.py` | l'analyseur, qui ne connaît aucune langue |
| `marqueurs-llm/lexiques/fr.json`, `en.json` | lexiques, motifs et seuils de chaque langue |
| `marqueurs-llm/references/catalogue-fr.md`, `catalogue-en.md` | tous les marqueurs, seuils et justifications |
| `marqueurs-llm/references/exemples-fr.md`, `exemples-en.md` | réécritures commentées, dont un contre-exemple de sur-correction |
| `marqueurs-llm/references/exemple-texte-llm-fr.md` | texte-témoin français, 9/13 attendu |
| `marqueurs-llm/references/exemple-texte-llm-en.md` | texte-témoin anglais, 17/17 attendu |
| `calibration/` | la méthode, l'outil et le corpus qui produisent les seuils anglais |
| `marqueurs-llm.md` | le référentiel d'origine dont la skill est tirée |

## Limites

L'analyseur ne juge que la surface. Le fond ne se mesure pas : présence de
sources, de dates, d'un cas vécu, d'une opinion assumée, d'un aveu d'ignorance.
La procédure de correction demande donc ces éléments à l'auteur plutôt que de
les inventer, parce qu'un chiffre plausible mais faux est plus grave qu'un
texte sans chiffre.

Sous 200 mots, les densités et l'écart-type ne veulent rien dire. Le script le
signale.

Les seuils anglais sont dérivés d'échantillons de 800 mots. Cinq d'entre eux
sont à zéro, c'est-à-dire qu'une seule occurrence suffit à les faire basculer :
appliqués d'un bloc à un texte très long, ils sortent mécaniquement. Analyser un
livre, c'est analyser ses sections. Le corpus de référence est aussi celui d'un
seul auteur, dans un seul registre — la prose technique de livre. Un billet de
blog anglais tolère plus de tirets et de phrases courtes ; ces registres-là
restent à calibrer.
