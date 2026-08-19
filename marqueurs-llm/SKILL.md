---
name: marqueurs-llm
description: Détecte, mesure et corrige la « signature LLM » d'un texte en français — tirets cadratins en incise, « ne… pas X mais Y », intensificateurs vides, rythme trop régulier, triades, connecteurs de transition, anglicismes de traduction, absence de faits vérifiables. À utiliser dès qu'un utilisateur demande si un texte « sonne IA » ou « fait ChatGPT », veut humaniser, désIA-iser ou rendre plus naturel un texte français, demande une relecture stylistique, se plaint des tirets cadratins ou d'un ton générique, ou fait relire un article, un billet de blog, une newsletter, un post LinkedIn, un rapport ou une documentation en français. À consulter aussi avant de rédiger soi-même un texte long en français destiné à être publié, pour éviter de produire ces marqueurs. Ne pas utiliser pour une simple correction orthographique ou grammaticale, ni pour des textes en anglais.
version: 2.0
langue: fr
---

# Marqueurs d'écriture LLM — détecter, mesurer, corriger

Un texte « sonne IA » rarement à cause d'un mot. Le tiret cadratin est un usage
français ancien et respectable ; « essentiel » est un mot légitime. Ce qui
trahit, c'est la **densité** et surtout la **régularité** : trois tirets par
paragraphe, tous en incise, dans des phrases de longueur presque identique.

D'où la méthode : mesurer avant de corriger. Un score chiffré évite de
sur-corriger un texte qui va bien et de sous-corriger un texte qui pique les
yeux sans qu'on sache dire pourquoi.

## Choisir le mode

| Ce que demande l'utilisateur | Mode |
|---|---|
| « Est-ce que ça sonne IA ? », « analyse ce texte », « c'est écrit par une IA ? » | **1 — Diagnostic** |
| « Réécris », « humanise », « enlève les tics », « rends ça plus naturel » | **2 — Correction** |
| Il demande un article, un billet, une doc en français — sans parler de marqueurs | **3 — Rédaction** |

En cas de doute entre 1 et 2, faire le diagnostic et proposer la correction.
Le diagnostic est rapide et il oriente la réécriture ; l'inverse n'est pas vrai.

---

## Mode 1 — Diagnostic

### Lancer l'analyse

```bash
python3 <skill>/scripts/analyse.py <fichier.md>
```

`<skill>` est le répertoire qui contient ce SKILL.md. Le script n'a besoin
d'aucune dépendance. Il accepte aussi `-` pour lire l'entrée standard, ce qui
sert quand le texte est collé dans la conversation :

```bash
cat > /tmp/texte.md <<'EOF'
… le texte …
EOF
python3 <skill>/scripts/analyse.py /tmp/texte.md
```

Options utiles :

- `--registre technique|prose|litteraire|academique` — ajuste les seuils. Une
  documentation technique a le droit d'être plus dense en puces et plus courte
  en phrases ; un texte académique tolère des phrases longues et du hedging.
  Sans cette option, les seuils de la prose professionnelle s'appliquent, et
  une doc technique sera injustement sanctionnée.
- `--json` — sortie machine, utile pour comparer avant/après.
- `--max-occ N` — nombre d'occurrences affichées par marqueur (12 par défaut).

Le script ignore les blocs de code, le frontmatter et les tableaux : les
métriques portent sur la prose seule.

### Lire le rapport

Trois blocs :

**Les métriques.** Chacune est marquée `ok` ou `!!`. Le score final compte les
métriques hors cible : 0–2 texte propre, 3–5 tics présents et corrigeables,
6+ réécriture profonde.

**Les marqueurs localisés**, avec numéro de ligne et extrait. C'est la matière
première de la correction : chaque ligne citée est une décision à prendre.

**Le profil de rythme** : la longueur de chaque phrase, en mots, dans l'ordre.
C'est le signal le plus difficile à truquer et le plus parlant à l'œil. Une
suite de nombres serrés autour de la moyenne trahit la machine. Un texte humain
alterne brutalement.

Sur un texte de moins de 200 mots, le script prévient que les densités sont peu
fiables. Dans ce cas, lire les occurrences et ignorer le score.

### Compléter par la lecture

Le script ne mesure que la surface. Le fond se voit à la lecture, et c'est lui
qui décide. Chercher ce qu'un modèle n'invente pas :

- **Des faits situés** : un chiffre, une date, une version d'outil, un prix, un
  nom propre vérifiable. Leur absence totale est le marqueur le plus lourd.
- **Un exemple réel** plutôt que « une entreprise », « un développeur », « une
  équipe ».
- **Un aveu d'ignorance.** Un auteur compétent écrit « je ne sais pas », « je
  n'ai pas testé », « ça m'a surpris ». Un modèle ne le fait jamais spontanément.
- **Une position tranchée**, avec une cible désignée et un risque assumé.
- **Une digression.** Le texte généré ne bifurque pas.
- **Une asymétrie.** Autant d'avantages que d'inconvénients, trois points
  toujours, des sections de longueur égale : la symétrie parfaite est un aveu.
- **Une conclusion qui tranche** au lieu de renvoyer dos à dos.

`references/catalogue.md` contient la liste exhaustive des marqueurs avec leur
raison d'être. La consulter quand un cas sort de l'ordinaire ou qu'il faut
justifier un diagnostic à l'utilisateur.

### Rendre le diagnostic

Format à respecter, parce qu'il sépare ce qui est mesuré de ce qui est jugé :

```
## Diagnostic — <nom du texte>

**Score : N/13 métriques hors cible — <verdict>**

### Ce que mesure l'analyse
<2-4 puces sur les métriques hors cible, avec les chiffres et ce qu'ils veulent dire>

### Ce que montre la lecture
<2-4 puces sur le fond : faits, opinions, exemples, structure>

### Les trois corrections qui changeraient le plus
<par ordre d'impact décroissant, avec un exemple ligne à l'appui>
```

Trois corrections, pas dix. Une liste exhaustive de tics ne se traite pas ; une
courte liste hiérarchisée, si.

---

## Mode 2 — Correction

Toujours diagnostiquer d'abord : les numéros de ligne du script évitent de
relire le texte à l'aveugle, et le score de départ donne un point de
comparaison à la fin.

### Livrable

Écrire `<nom>.corrige.md` à côté de l'original, qui reste intact, puis rendre un
court rapport de ce qui a changé. L'utilisateur veut pouvoir diffé les deux
versions et refuser une correction sans tout perdre.

### Les six passes

Elles vont du mécanique au délicat. Les faire dans l'ordre : corriger le fond
avant le rythme oblige à refaire le rythme.

**Passe 1 — Élagage.** Supprimer sans remplacer : intensificateurs vides,
adverbes de renforcement, « il convient de noter que », gras superflu, emojis.
Le test : retirer le mot ; si le sens ne bouge pas, il était vide. C'est le cas
neuf fois sur dix. Cas particulier de « c'est précisément » : la formule
présente comme une déduction serrée ce qui n'est qu'une transition ; les deux
mots sautent.

**Passe 2 — Ponctuation.** Ramener les tirets cadratins sous le quota d'environ
un pour mille mots. Une incise devient une virgule, une parenthèse, des
deux-points, ou une phrase autonome. Choisir en fonction du lien logique réel :
la parenthèse pour l'aparté, les deux-points pour l'annonce, la phrase pour ce
qui mérite d'être posé.

**Passe 3 — Contrastes.** Traquer chaque « ne… pas X, mais Y ». La figure nie
une proposition que personne n'a avancée, pour donner à Y un relief qu'il n'a
pas gagné. Affirmer Y directement. Ne garder la négation que si X a été
explicitement posé plus haut, par l'auteur ou par quelqu'un qu'il cite.

**Passe 4 — Rythme.** D'abord couper toute phrase de plus de 40 mots. Ensuite,
et c'est le point que l'on oublie, **injecter délibérément de la variance** :
au moins une phrase de moins de huit mots tous les deux paragraphes. Couper les
longues ne suffit pas — cela produit un texte uniformément moyen, qui sonne
encore plus machine. Casser aussi l'uniformité des paragraphes : un d'une
ligne, un de dix. Relancer le script et regarder le profil de rythme : les
nombres doivent sauter.

**Passe 5 — Structure.** Supprimer les phrases-bilans en fin de paragraphe : la
dernière phrase doit apporter, pas résumer. Supprimer la conclusion si elle
répète l'introduction. Casser les symétries artificielles. Si un côté a plus à
dire, qu'il soit plus long. Passer de trois points à deux ou quatre quand c'est
plus juste.

**Passe 6 — Fond.** La seule passe qui compte vraiment, et la seule qui demande
de l'information que le texte ne contient pas. Il faut donc **demander à
l'utilisateur** plutôt qu'inventer : un chiffre plausible mais faux est pire
que l'absence de chiffre.

> Pour la passe 6, j'ai besoin de trois ou quatre choses que je ne peux pas
> inventer sans risquer de me tromper : un chiffre ou une date réels, un cas
> concret que tu as vécu, une position que tu assumes, une limite honnête de ce
> que tu avances. Donne-m'en ce que tu as et je les intègre.

Si l'utilisateur ne fournit rien, livrer quand même les passes 1 à 5 et dire
explicitement ce qui manque : le texte sera propre en surface et toujours creux
au fond. C'est une information utile, pas un échec à masquer.

### Contrôle final

Relancer le script sur la version corrigée et comparer les deux scores. Puis
vérifier trois choses que le script ne voit pas :

1. Le sens n'a pas bougé. Élaguer, ce n'est pas amputer.
2. Le rythme surprend au moins une fois par page. Sinon la passe 4 a échoué.
3. Le texte n'est pas devenu plat. Un texte débarrassé de tous ses tics mais
   devenu terne n'a rien gagné. C'est le risque principal de cette méthode, et
   mieux vaut le nommer que le subir.

### Rapport de correction

```
## Correction — <nom du texte>

Score : N/13 → M/13

| Passe | Changements |
|---|---|
| 1 Élagage | <n> intensificateurs, <n> connecteurs |
| 2 Ponctuation | <n> tirets cadratins sur <n> |
| … | |

**Ce que je n'ai pas corrigé, et pourquoi** : <les faux positifs assumés>
**Ce qui manque encore** : <ce qui relève de la passe 6 et attend l'utilisateur>
```

La ligne « ce que je n'ai pas corrigé » n'est pas de la modestie : elle protège
les usages légitimes que la prochaine relecture serait tentée d'écraser.

---

## Mode 3 — Rédaction

Quand il s'agit de produire un texte français plutôt que d'en réparer un, les
mêmes marqueurs servent de garde-fous. Trois réflexes suffisent à éviter
l'essentiel.

**Écrire les phrases de longueur inégale, volontairement.** C'est le marqueur le
plus fiable et le plus facile à contrôler à l'écriture. Après deux phrases
amples, en poser une courte. Trois mots suffisent.

**Refuser la triade automatique.** Quand trois éléments viennent naturellement,
se demander si le troisième apporte quelque chose. Souvent non ; il est là pour
le rythme ternaire. Deux termes justes valent mieux que trois dont un est
décoratif.

**Nommer.** Un chiffre, une version, une date, un nom d'outil, un cas précis :
c'est ce qui distingue un texte écrit par quelqu'un qui sait d'un texte écrit
par quelqu'un qui résume. Si l'information manque, le dire plutôt que de
combler avec du générique.

À éviter par construction : ouvrir sur « Dans un monde où » ou « À l'heure où »,
enchaîner « Autrement dit » après une formulation ratée (garder la meilleure des
deux et supprimer l'autre), clore chaque paragraphe sur une phrase-bilan,
terminer sur « L'avenir nous le dira ».

Sur un texte long ou destiné à publication, passer le script avant de rendre.
Deux minutes, et cela évite de livrer ce que la skill est censée corriger.

---

## Ne pas sur-corriger

Le risque de cette méthode est de produire des textes appauvris. Plusieurs
marqueurs sont légitimes selon le registre :

- Le **tiret cadratin** est un usage littéraire français établi. Le problème est
  la densité, pas l'existence.
- Les **puces à tête en gras** sont la norme en documentation technique.
- Le **parallélisme** est un outil rhétorique assumé dans un discours ou un
  manifeste.
- « **Autrement dit** » est utile après un passage réellement technique, pour un
  lecteur non spécialiste.
- Les **phrases longues** sont normales en juridique et en académique, d'où
  l'option `--registre`.

Règle de tranchage : ne corriger que ce qui, une fois corrigé, rend le texte
meilleur à la lecture. Une occurrence signalée par le script n'est pas une
faute, c'est une question posée à l'auteur.

---

## Ressources

- `scripts/analyse.py` — l'analyseur. Aucune dépendance. `--help` pour les options.
- `references/catalogue.md` — le catalogue complet des marqueurs, avec les
  regex de détection, les corrections types et la justification de chaque
  seuil. À lire quand un cas sort de l'ordinaire, qu'il faut argumenter un
  diagnostic, ou qu'il faut étendre les lexiques du script.
- `references/exemples.md` — des réécritures commentées, avant/après. Utile
  pour calibrer le geste : voir jusqu'où corriger, et où s'arrêter.
- `references/exemple-texte-llm.md` — un texte-témoin saturé de marqueurs.
  L'analyser doit rendre 9 métriques hors cible sur 13 en registre `prose` :
  c'est le test de non-régression après toute modification du script.
