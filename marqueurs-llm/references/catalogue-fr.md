# Catalogue des marqueurs d'écriture LLM

Référence exhaustive. Les codes entre crochets sont ceux que `scripts/analyse.py`
affiche dans son rapport, pour passer d'une occurrence signalée à sa correction.

## Sommaire

1. [Typographie et ponctuation](#1-typographie-et-ponctuation) — T1, T2, T4, T6, T7, T8, T9
2. [Rythme et syntaxe](#2-rythme-et-syntaxe) — R1 à R9
3. [Formules rhétoriques](#3-formules-rhétoriques) — X, I, C, O, M, A
4. [Structure du discours](#4-structure-du-discours)
5. [Contenu](#5-contenu)
6. [Métriques et seuils](#6-métriques-et-seuils)
7. [Faux positifs](#7-faux-positifs)
8. [Checklist de relecture](#8-checklist-de-relecture)

---

## 1. Typographie et ponctuation

| Code | Marqueur | Détection | Correction |
|---|---|---|---|
| T1 | Tiret cadratin (—) en incise | `—` hors début de ligne | Virgule, parenthèse, deux-points, ou coupure de phrase. Quota : 1 pour 1000 mots. |
| T2 | Tiret cadratin collé aux mots (usage anglais) | `\w—` ou `—\w` | En français : espace insécable de part et d'autre, ou reformuler. |
| T3 | Incises multiples dans un paragraphe | ≥ 2 incises / paragraphe | Une par paragraphe au plus. Les autres deviennent des phrases. |
| T4 | Guillemets droits, points de suspension unicode | `"`, `…` | Guillemets français « ». Les points de suspension sont rarement utiles. |
| T5 | Deux-points comme moteur rhétorique | ratio `:` / phrases > 0,15 | Alterner. Les deux-points annoncent, ils ne rythment pas. |
| T6 | Gras intra-paragraphe | `**` hors titre et hors tête de puce | Si tout est important, rien ne l'est. Supprimer 90 %. |
| T7 | Puce ouverte par un terme en gras suivi de deux-points | `^[-*] \*\*.+\*\* ?:` | Normal en doc technique, suspect en prose. |
| T8 | Emoji en tête de titre ou de puce | plage emoji | Supprimer. |
| T9 | Titre binaire « Concept : précision » | `^#+ .+ : .+$` répété | Varier, ou supprimer le sous-titre. |

T3 et T5 ne sont pas détectés automatiquement : le script compte les tirets par
ligne, à l'œil de voir s'ils forment des incises. Le repérage manuel reste rapide.

---

## 2. Rythme et syntaxe

| Code | Marqueur | Seuil | Correction |
|---|---|---|---|
| R1 | Phrases longues | > 50 mots | Couper. Une idée par phrase. |
| R2 | Longueur moyenne élevée | > 25 mots/phrase | Viser 15–20. |
| R3 | **Faible variance des longueurs** | écart-type < 8 mots, ou σ/μ < 0,40 | Injecter des phrases de 3 à 8 mots. |
| R4 | Paragraphes de taille uniforme | tous entre 3 et 5 phrases | Alterner : un paragraphe d'une ligne, un de dix. |
| R5 | Rythme ternaire systématique | `X, Y et Z` répété | Deux termes, ou quatre, ou un seul bien choisi. |
| R6 | Parallélisme entre phrases voisines | même moule 3 fois | Casser l'une des trois. |
| R7 | Paragraphe clos sur une phrase-bilan | dernière phrase = reformulation | Supprimer. |
| R8 | Participiales et gérondifs en tête | `^(En |Ayant |Étant |Permettant )` répété | Sujet-verbe-complément. |
| R9 | Subordination empilée | > 3 subordonnées | Découper. |

R3 est le marqueur le plus fiable de tous, et le plus coûteux à truquer pour un
modèle. Les modèles produisent des phrases de longueur régulière parce qu'ils
optimisent la fluidité locale ; un auteur humain suit son souffle et son
argument, qui n'ont aucune raison d'être réguliers. C'est pourquoi le script
affiche le profil complet des longueurs : le regard repère l'anomalie plus vite
qu'un écart-type.

---

## 3. Formules rhétoriques

### 3.1 [X] Contrastes correctifs — le tic numéro un

Structure : nier une proposition pour en poser une autre, alors que personne
n'avait affirmé la première. Le procédé donne au second terme un relief qu'il
n'a pas gagné.

- « ne… pas X, **mais** Y »
- « il ne s'agit pas de X, mais de Y »
- « X n'est pas Y, c'est Z »
- « moins X que Y »
- « plus qu'une simple X, c'est un Y »
- « loin d'être X, Y »
- « non pas X, mais bien Y »
- « ce n'est pas tant X que Y »
- « ne… pas X — Y » (même figure, ponctuation différente)

**Correction** : affirmer Y directement. Ne garder la négation que si X a été
réellement avancé plus haut, par l'auteur ou par quelqu'un qu'il cite.

### 3.2 [I] Intensificateurs vides

Adjectifs : `véritable`, `réel`, `authentique`, `profond`, `fondamental`,
`crucial`, `essentiel`, `incontournable`, `majeur`, `remarquable`, `fascinant`,
`puissant`, `robuste`, `considérable`, `à part entière`, `de premier plan`,
`sans précédent`.

Adverbes : `véritablement`, `réellement`, `précisément`, `particulièrement`,
`notamment`, `littéralement`, `pleinement`, `résolument`, `indéniablement`,
`clairement`, `assurément`, `certainement`, `considérablement`.

**Test** : supprimer le mot. Si le sens ne change pas, il était vide — c'est le
cas dans environ 90 % des occurrences.

**« c'est précisément »** mérite une mention à part : la formule présente comme
une déduction serrée ce qui n'est qu'une transition. Les deux mots sautent.

### 3.3 [C] Connecteurs et transitions

- « Autrement dit », « en d'autres termes », « pour le dire autrement »
- « En somme », « en définitive », « au final », « à terme »
- « Il convient de noter que », « il est important de souligner que », « notons que »
- « Force est de constater que »
- « Cela étant dit », « ceci dit »
- « À l'inverse », « en revanche », « par ailleurs » en tête de chaque paragraphe
- « Ainsi », « dès lors », « de fait », « en effet », « par conséquent »

**Règle** : « Autrement dit » signale que la première formulation a échoué.
Garder la meilleure des deux versions, supprimer l'autre et le connecteur.

Le script compte ces connecteurs en tête de phrase, plus les plus
caractéristiques partout. La métrique est une densité par paragraphe : un
connecteur au début de chaque paragraphe est le signe d'un plan récité.

### 3.4 [O] Ouvertures et clôtures toutes faites

- « Dans un monde où… », « À l'heure où… », « À l'ère de… »
- « Plongeons dans », « explorons », « décryptons »
- « Dans cet article, nous allons voir »
- « Que vous soyez X ou Y… »
- « Vous vous demandez peut-être… »
- « Une chose est sûre », « ce n'est qu'un début », « l'avenir nous le dira »
- « comme souvent, la vérité se situe entre les deux »
- « X n'est pas un luxe, c'est une nécessité »

### 3.5 [M] Métaphores et lexique par défaut

`au cœur de`, `pierre angulaire`, `fil rouge`, `prisme`, `paysage`,
`écosystème`, `levier`, `brique`, `socle`, `colonne vertébrale`,
`changement de paradigme`, `révolution`, `arsenal`, `boîte à outils`,
`garde-fou`, `cercle vertueux`, `terrain de jeu`, `nouvelle donne`,
`à double tranchant`, `épine dorsale`, `tour de force`, `ligne de mire`.

Ces images ne sont pas fautives ; elles sont usées. Le test : l'auteur
aurait-il pu écrire autre chose à cet endroit ? Si le mot est le premier qui
vient, il est probablement le premier qui est venu au modèle aussi.

### 3.6 [A] Anglicismes de traduction

Indice fort de génération, parce qu'ils trahissent un raisonnement mené en
anglais puis rendu en français.

| À bannir | Remplacer par |
|---|---|
| adresser un problème | traiter, aborder |
| supporter (une fonctionnalité) | prendre en charge |
| délivrer (de la valeur) | fournir, produire, livrer |
| impacter | affecter, peser sur |
| en termes de | pour, quant à, en matière de |
| basé sur | fondé sur, à partir de |
| initier | lancer, engager |
| challenger | remettre en cause |
| dédié à | consacré à, réservé à |
| au final | finalement, en fin de compte |
| opportunité de | occasion de |
| digital | numérique |
| c'est un game changer | (reformuler entièrement) |

### 3.7 [H] Hedging

`peut`, `pourrait`, `tend à`, `semble`, `dans une certaine mesure`, `souvent`,
`généralement`, `dans bien des cas`, `le plus souvent`, `a priori`,
`relativement`, `plutôt`, `quelque peu`.

Une prudence occasionnelle est honnête. Un hedging permanent est une manière de
n'être jamais réfutable, donc de ne rien dire. Le seuil est plus haut en
registre académique, où la prudence est une convention du genre.

---

## 4. Structure du discours

- **Symétrie obligatoire** : autant d'avantages que d'inconvénients, chaque
  section de même longueur. Le réel est rarement symétrique.
- **Introduction qui annonce le plan**, puis **conclusion qui répète
  l'introduction**.
- **Trois points, toujours trois.** Jamais deux, jamais sept.
- **Conclusion en équilibriste** : ne tranche jamais, renvoie dos à dos.
- **Question rhétorique** en ouverture de section.
- **Adresse au lecteur** (« vous ») injustifiée dans un texte technique.
- **Tableau comparatif** non demandé.
- **TL;DR / En résumé** systématique.

---

## 5. Contenu

Les marqueurs les plus décisifs, et les plus difficiles à truquer : la surface
se corrige en une heure, le fond se voit.

- **Aucun chiffre daté, aucune source, aucun nom propre vérifiable.**
- **Exemples génériques** : « une entreprise », « un développeur », « une
  équipe » au lieu d'un cas réel.
- **Aucun aveu d'ignorance.** Un auteur compétent écrit « je ne sais pas »,
  « je n'ai pas vérifié », « ça m'a surpris ».
- **Aucune anecdote** située dans le temps ou l'espace.
- **Aucune opinion tranchée**, aucun risque pris, aucune cible désignée.
- **Aucune digression.** Le texte ne bifurque jamais.
- **Aucun coût cognitif visible** : pas de retour en arrière, pas de correction,
  pas d'hésitation assumée.
- **Rien de daté ni de local** : pas de version d'outil, pas de prix, pas de
  contexte réglementaire précis.

C'est la raison pour laquelle la passe 6 de correction demande de l'information
à l'utilisateur au lieu de l'inventer. Un chiffre plausible mais faux est plus
grave qu'un texte sans chiffre : le premier est une erreur factuelle, le second
seulement un texte creux.

---

## 6. Métriques et seuils

Calculés sur la prose seule (hors code, tableaux, frontmatter). Calibrés sur de
la prose professionnelle française.

| Métrique | Suspect si | Cible |
|---|---|---|
| Longueur moyenne des phrases | > 25 mots | 15–20 |
| Écart-type des longueurs | < 8 mots | > 10 |
| Coefficient de variation (σ/μ) | < 0,40 | > 0,55 |
| Part de phrases > 40 mots | > 15 % | < 8 % |
| Part de phrases < 10 mots | < 10 % | > 20 % |
| Tirets cadratins / 1000 mots | > 2 | ≤ 1 |
| Intensificateurs / 1000 mots | > 8 | < 4 |
| Contrastes « pas X mais Y » / 1000 mots | > 2 | ≤ 1 |
| Connecteurs de transition / paragraphe | > 0,8 | < 0,4 |
| Triades / 1000 mots | > 4 | < 2 |
| Hedging / 1000 mots | > 10 | < 6 |
| Noms propres + chiffres / 1000 mots | < 5 | > 12 |
| Variation des longueurs de paragraphe | < 0,25 | > 0,50 |

**Score global** : nombre de métriques hors cible. 0–2 texte propre, 3–5 tics
présents et corrigeables, 6 ou plus réécriture profonde.

### Ajustements par registre

`--registre` modifie les seuils, parce qu'un même chiffre ne veut pas dire la
même chose selon le genre :

| Registre | Ce qui change |
|---|---|
| `prose` (défaut) | seuils du tableau ci-dessus |
| `technique` | phrases plus courtes attendues (moyenne max 22), plus de phrases brèves (≥ 15 %), beaucoup plus de faits attendus (≥ 10 noms propres et chiffres / 1000 mots), moins de connecteurs tolérés |
| `litteraire` | phrases longues admises (moyenne max 32), tirets cadratins tolérés jusqu'à 5 / 1000 mots, peu de faits attendus |
| `academique` | phrases longues admises, hedging toléré jusqu'à 16 / 1000 mots, faits nombreux attendus |

Sur un texte de moins de 200 mots, les densités par millier de mots et
l'écart-type ne veulent rien dire. Le script le signale ; s'en tenir alors aux
occurrences repérées.

---

## 7. Faux positifs

Un marqueur signalé est une question, pas une faute.

- Le **tiret cadratin** est un usage littéraire français ancien. Le problème est
  la densité, pas l'existence.
- Les **puces à tête en gras** sont normales en documentation technique — le
  registre `technique` en tient compte.
- Le **parallélisme** est un outil rhétorique volontaire dans un discours, un
  manifeste, un texte oral.
- « **Autrement dit** » est légitime après un passage réellement technique,
  pour un lecteur non spécialiste.
- La **longueur des phrases** varie selon le genre : le juridique et
  l'académique en tolèrent davantage.
- Le **hedging** est une convention du discours scientifique.
- Les **triades** sont parfois exactes : quand il y a vraiment trois éléments,
  il y en a trois.

**Règle de tranchage** : ne corriger que ce qui, une fois corrigé, rend le texte
meilleur. Un texte débarrassé de tous ses tics mais devenu plat n'a rien gagné.

---

## 8. Checklist de relecture

- [ ] Aucun tiret cadratin superflu
- [ ] Aucun paragraphe à deux incises ou plus
- [ ] Aucune occurrence de « véritable », « c'est précisément », « il convient de »
- [ ] Aucun « ne… pas X, mais Y » non justifié
- [ ] Aucune phrase de plus de 40 mots
- [ ] Au moins une phrase courte (moins de 8 mots) tous les deux paragraphes
- [ ] Longueurs de paragraphes visiblement inégales
- [ ] Aucune phrase-bilan en fin de paragraphe
- [ ] Aucune triade non intentionnelle
- [ ] Aucun anglicisme de la liste 3.6
- [ ] Au moins un chiffre ou un nom propre vérifiable par section
- [ ] Au moins une position tranchée dans le texte
- [ ] Au moins une limite ou une incertitude assumée
- [ ] La conclusion ajoute quelque chose, ou n'existe pas
