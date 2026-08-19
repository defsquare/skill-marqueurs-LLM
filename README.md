# skill-marqueurs-LLM

Une skill Claude Code qui détecte, mesure et corrige la « signature LLM » d'un
texte français : tirets cadratins en incise, « ne… pas X mais Y »,
intensificateurs vides, rythme trop régulier, triades, anglicismes de
traduction, absence de faits vérifiables.

Le principe : mesurer avant de corriger. Un tiret cadratin ne prouve rien, trois
par paragraphe si. Le score chiffré évite de sur-corriger un texte qui va bien
et de sous-corriger un texte qui gêne sans qu'on sache dire pourquoi.

## Installation

```bash
./install-for-user.sh                      # ~/.claude/skills, lien symbolique
./install-for-project.sh ~/dev/mon-projet  # <projet>/.claude/skills, copie
```

Le lien symbolique garde la skill synchronisée avec ce dépôt pendant que vous
l'améliorez. La copie sert aux skills de projet, qui finissent versionnées avec
le dépôt et pour lesquelles un chemin absolu serait cassé après un clone.
`--copy` et `--link` inversent le comportement, `--help` détaille le reste.

## Usage direct de l'analyseur

L'analyseur tourne aussi seul, sans Claude, avec Python 3 et sans dépendance :

```bash
python3 marqueurs-llm/scripts/analyse.py article.md
python3 marqueurs-llm/scripts/analyse.py doc.md --registre technique
python3 marqueurs-llm/scripts/analyse.py article.md --json
cat texte.txt | python3 marqueurs-llm/scripts/analyse.py -
```

Il rend treize métriques, les occurrences localisées à la ligne, et le profil
de rythme : la longueur de chaque phrase dans l'ordre. C'est ce profil qui
trahit le plus sûrement une machine, parce qu'un auteur humain suit son
argument, qui n'a aucune raison d'être régulier.

## Contenu

| Fichier | Rôle |
|---|---|
| `marqueurs-llm/SKILL.md` | les trois modes : diagnostic, correction, rédaction |
| `marqueurs-llm/scripts/analyse.py` | l'analyseur |
| `marqueurs-llm/references/catalogue.md` | tous les marqueurs, seuils et justifications |
| `marqueurs-llm/references/exemples.md` | réécritures commentées, dont un contre-exemple de sur-correction |
| `marqueurs-llm/references/exemple-texte-llm.md` | texte-témoin, 9/13 attendu |
| `marqueurs-llm.md` | le référentiel d'origine dont la skill est tirée |

## Limites

L'analyseur ne juge que la surface. Le fond ne se mesure pas : présence de
sources, de dates, d'un cas vécu, d'une opinion assumée, d'un aveu d'ignorance.
La procédure de correction demande donc ces éléments à l'auteur plutôt que de
les inventer, parce qu'un chiffre plausible mais faux est plus grave qu'un
texte sans chiffre.

Sous 200 mots, les densités et l'écart-type ne veulent rien dire. Le script le
signale.
