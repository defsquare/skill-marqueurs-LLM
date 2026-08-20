---
name: marqueurs-llm
description: Détecte, mesure et corrige la « signature LLM » d'un texte en français ou en anglais — tirets cadratins en incise, « ne… pas X mais Y » ou « not X, it's Y », intensificateurs vides, rythme trop régulier, triades, connecteurs de transition, participiales de bénéfice, anglicismes de traduction, absence de faits vérifiables. À utiliser dès qu'un utilisateur demande si un texte « sonne IA », « fait ChatGPT » ou « sounds AI-generated », veut humaniser, désIA-iser ou rendre plus naturel un texte français ou anglais, demande une relecture stylistique, se plaint des tirets cadratins ou d'un ton générique, ou fait relire un article, un billet de blog, une newsletter, un post LinkedIn, un rapport ou une documentation dans l'une de ces deux langues. À consulter aussi avant de rédiger soi-même un texte long destiné à être publié, pour éviter de produire ces marqueurs. Ne pas utiliser pour une simple correction orthographique ou grammaticale, ni pour une langue autre que le français et l'anglais.
version: 2.0
langues: fr, en
---

# Marqueurs d'écriture LLM — détecter, mesurer, corriger

Un texte « sonne IA » rarement à cause d'un mot. Le tiret cadratin est un usage
français ancien et respectable ; « essentiel » est un mot légitime. Ce qui
trahit, c'est la **densité** et surtout la **régularité** : trois tirets par
paragraphe, tous en incise, dans des phrases de longueur presque identique.

D'où la méthode : mesurer avant de corriger. Un score chiffré évite de
sur-corriger un texte qui va bien et de sous-corriger un texte qui pique les
yeux sans qu'on sache dire pourquoi.

## Deux langues, une seule méthode

La skill traite le français et l'anglais. Les trois modes, les six passes et la
règle de tranchage sont les mêmes : ce sont des habitudes d'écriture, pas des
faits de langue. Ce qui change tient en trois points.

Les **lexiques et les motifs** sont propres à chaque langue et vivent dans
`lexiques/fr.json` et `lexiques/en.json`. Le script détecte la langue tout seul
et le rapport l'affiche en tête ; `--langue fr|en` la force quand la détection
hésite ou quand le texte est court.

Le **nombre de métriques** diffère, donc le score aussi : **13 en français, 17
en anglais**. Toujours citer le dénominateur : « 9/13 » et « 9/17 » ne disent
pas la même chose.

La **provenance des seuils** diffère, et c'est ce qui autorise ou non à trancher.
Les seuils français viennent d'un jugement exercé ; les seuils anglais sont
mesurés sur un corpus humain de cent mille mots (Eric Evans, *Domain-Driven
Design*, 2003), au 9ᵉ décile. En anglais, dire « ce texte est au-delà de ce
qu'écrit un auteur humain neuf fois sur dix » est une affirmation vérifiable.
En français, c'est un avis argumenté. Ne pas maquiller l'un en l'autre.

## Choisir le mode

| Ce que demande l'utilisateur | Mode |
|---|---|
| « Est-ce que ça sonne IA ? », « analyse ce texte », « c'est écrit par une IA ? » | **1 — Diagnostic** |
| « Réécris », « humanise », « enlève les tics », « rends ça plus naturel » | **2 — Correction** |
| Il demande un article, un billet, une doc — sans parler de marqueurs | **3 — Rédaction** |

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

- `--langue fr|en` — force la langue. Par défaut le script la détecte, sur la
  prose seule, et l'affiche en tête du rapport. Vérifier cette ligne avant de
  lire le score : un texte anglais passé aux lexiques français ressortirait
  propre, non parce qu'il l'est, mais parce que le moteur n'aurait rien
  cherché. Le script prévient quand les deux langues sont au coude à coude ;
  sur un texte court ou truffé de termes anglais, forcer.
- `--registre technique|prose|litteraire|academique` — ajuste les seuils. Une
  documentation technique a le droit d'être plus dense en puces et plus courte
  en phrases ; un texte académique tolère des phrases longues et du hedging.
  Sans cette option, les seuils de la prose professionnelle s'appliquent, et
  une doc technique sera injustement sanctionnée. Seul le français a des
  registres calibrés ; en anglais, le script le signale et applique ses seuils
  de base, qui sont ceux d'un livre technique.
- `--json` — sortie machine, utile pour comparer avant/après.
- `--max-occ N` — nombre d'occurrences affichées par marqueur (12 par défaut).

Le script ignore les blocs de code, le frontmatter et les tableaux : les
métriques portent sur la prose seule.

### Lire le rapport

Trois blocs :

**Les métriques.** Chacune est marquée `ok` ou `!!`. Le score final compte les
métriques hors cible. Les paliers sont donnés en proportion, pour que l'anglais
ne soit pas jugé plus sévèrement au seul motif qu'il mesure dix-sept choses là
où le français en mesure treize : jusqu'à 2/13 ou 2/17 le texte est propre,
jusqu'à 5/13 ou 6/17 les tics sont présents et corrigeables, au-delà il faut
réécrire. Le script affiche déjà le verdict ; le reprendre tel quel.

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

Le catalogue de la langue analysée, `references/catalogue-fr.md` ou
`references/catalogue-en.md`, contient la liste exhaustive des marqueurs avec
leur raison d'être. Le consulter quand un cas sort de l'ordinaire ou qu'il faut
justifier un diagnostic à l'utilisateur. Ne pas transposer d'un catalogue à
l'autre : plusieurs transpositions évidentes se sont révélées fausses à la
mesure, et le catalogue anglais les liste.

### Rendre le diagnostic

Format à respecter, parce qu'il sépare ce qui est mesuré de ce qui est jugé :

```
## Diagnostic — <nom du texte>

**Langue : <fr|en> — Score : N/<13 en français, 17 en anglais> métriques hors
cible — <verdict>**

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

Score : N/T → M/T   (T = 13 en français, 17 en anglais)

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

Quand il s'agit de produire un texte plutôt que d'en réparer un, les mêmes
marqueurs servent de garde-fous, dans les deux langues. Trois réflexes suffisent
à éviter l'essentiel.

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

À éviter par construction, en français : ouvrir sur « Dans un monde où » ou
« À l'heure où », enchaîner « Autrement dit » après une formulation ratée
(garder la meilleure des deux et supprimer l'autre), clore chaque paragraphe sur
une phrase-bilan, terminer sur « L'avenir nous le dira ».

Et en anglais, où les mêmes réflexes prennent d'autres formes : ouvrir sur
« In today's… » ou « In an era where… », meubler avec « It's worth noting
that… », clore une phrase sur un participe de bénéfice (« …, enabling teams to
move faster »), terminer sur « Only time will tell ». Ces quatre tournures sont
absentes des cent mille mots du corpus de référence. Pas rares : absentes.

Sur un texte long ou destiné à publication, passer le script avant de rendre.
Deux minutes, et cela évite de livrer ce que la skill est censée corriger.

---

## Ne pas sur-corriger

Le risque de cette méthode est de produire des textes appauvris. Plusieurs
marqueurs sont légitimes selon le registre :

- Le **tiret cadratin** est un usage littéraire français établi, et l'anglais
  américain le colle aux mots sans espace. Le problème est la densité, pas
  l'existence, et l'analyseur ne signale pas le tiret collé quand il analyse de
  l'anglais.
- Les **guillemets droits** sont la norme en anglais : le corpus de référence en
  compte 437 et pas un seul guillemet courbe. Le marqueur est tu dans cette
  langue.
- Les **puces à tête en gras** sont la norme en documentation technique.
- Le **parallélisme** est un outil rhétorique assumé dans un discours ou un
  manifeste. En anglais, la triade avec virgule d'Oxford est une énumération
  ordinaire : le corpus en aligne vingt-cinq, toutes justifiées. C'est un
  marqueur de densité, jamais d'occurrence isolée.
- « **Autrement dit** » est utile après un passage réellement technique, pour un
  lecteur non spécialiste. Son équivalent anglais « in other words » aussi.
- Les **phrases longues** sont normales en juridique et en académique, d'où
  l'option `--registre`, calibrée en français seulement.
- Les **modaux anglais** « may », « might », « could » ne sont pas du hedging :
  ils sont le métier de l'écriture technique. Ils ont été retirés du lexique
  après mesure, et ne doivent jamais être montrés à un auteur comme une faute.

Règle de tranchage : ne corriger que ce qui, une fois corrigé, rend le texte
meilleur à la lecture. Une occurrence signalée par le script n'est pas une
faute, c'est une question posée à l'auteur.

---

## Ressources

- `scripts/analyse.py` — l'analyseur. Aucune dépendance. `--help` pour les options.
- `lexiques/fr.json`, `lexiques/en.json` — les lexiques, motifs et seuils de
  chaque langue. Le moteur n'en connaît aucune : ajouter une langue, c'est
  déposer un fichier ici. `lexiques/README.md` décrit le format et la règle qui
  compte : ne déclarer que ce que la langue sait vraiment chercher, parce qu'une
  métrique sans motif vaut zéro, et que zéro se lit comme un compliment.

Un jeu de trois fichiers par langue, à ne pas croiser :

| | Français | Anglais |
|---|---|---|
| Catalogue des marqueurs | `references/catalogue-fr.md` | `references/catalogue-en.md` |
| Réécritures commentées | `references/exemples-fr.md` | `references/exemples-en.md` |
| Texte-témoin | `references/exemple-texte-llm-fr.md` | `references/exemple-texte-llm-en.md` |

Le **catalogue** donne les regex de détection, les corrections types et la
justification de chaque seuil. À lire quand un cas sort de l'ordinaire, qu'il
faut argumenter un diagnostic, ou qu'il faut étendre les lexiques. Le catalogue
anglais cite ses mesures ; le français, ses raisons.

Les **exemples** montrent jusqu'où corriger, et surtout où s'arrêter.

Les **textes-témoins** sont saturés de marqueurs et servent de test de
non-régression : 9 métriques hors cible sur 13 pour le français en registre
`prose`, 17 sur 17 pour l'anglais. `build-zip.sh` vérifie les deux avant
d'empaqueter. Un score qui baisse veut dire qu'un détecteur a cessé de mordre.
