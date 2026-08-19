---
name: marqueurs-llm
description: Référentiel des marqueurs stylistiques d'un texte généré par LLM (français) et procédure de correction. À utiliser pour détecter, mesurer et corriger la "signature LLM" d'un texte — que ce soit un texte produit par un modèle ou un texte humain qui en a pris les tics.
version: 1.0
langue: fr
---

# Marqueurs d'écriture LLM — détection & correction

Ce document sert de référence pour deux usages :

1. **Diagnostic** : mesurer à quel point un texte "sonne LLM".
2. **Correction** : réécrire en supprimant les marqueurs sans appauvrir le fond.

Principe directeur : **le problème n'est jamais un marqueur isolé, c'est la densité et la régularité.** Un tiret cadratin ne prouve rien. Trois par paragraphe, tous en incise, dans des phrases de longueur identique, c'est une signature.

---

## 1. Typographie et ponctuation

| # | Marqueur | Détection | Correction |
|---|---|---|---|
| T1 | Tiret cadratin (—) en incise | `—` | Remplacer par virgule, parenthèse, deux-points, ou couper la phrase. Garder au maximum **1 par 1000 mots**. |
| T2 | Tirets cadratins non conformes à l'usage français (collés, ou utilisés comme en anglais) | `\w—\w` | En français : espace insécable avant et après, ou reformuler. |
| T3 | Incises multiples dans un même paragraphe | ≥ 2 incises / paragraphe, ≥ 3 tirets | Une incise par paragraphe maximum. Les autres deviennent des phrases autonomes. |
| T4 | Points de suspension unicode (…) et guillemets droits (`"`) | `…`, `"` | Guillemets français « » ; suspension rarement utile. |
| T5 | Deux-points comme moteur rhétorique systématique | ratio `:` / phrases > 0,15 | Alterner. Les deux-points annoncent, ils ne rythment pas. |
| T6 | Gras intra-paragraphe pour "signaler l'important" | `\*\*` hors titres et listes | Si tout est important, rien ne l'est. Supprimer 90 %. |
| T7 | Puces ouvertes par un terme en gras suivi de deux-points | `^[-*] \*\*.+\*\* ?:` | Acceptable en doc technique, suspect en prose. |
| T8 | Emoji en tête de titre ou de puce | `^[\p{Emoji}]` | Supprimer. |
| T9 | Titres binaires "Concept : précision" | `^#+ .+ : .+$` répété | Varier ou supprimer le sous-titre. |

---

## 2. Rythme et syntaxe

| # | Marqueur | Seuil / détection | Correction |
|---|---|---|---|
| R1 | Phrases longues | > 50 mots | Couper. Une idée par phrase. |
| R2 | Longueur moyenne élevée | > 25 mots/phrase | Viser 15–20 en moyenne. |
| R3 | **Faible variance de longueur** (marqueur le plus fiable) | écart-type < 8 mots, ou < 40 % de la moyenne | Injecter des phrases de 3–8 mots. Le texte humain alterne brutalement. |
| R4 | Paragraphes de taille uniforme | tous entre 3 et 5 phrases | Alterner : un paragraphe d'une ligne, puis un de dix. |
| R5 | Rythme ternaire systématique (triades) | `X, Y et Z` répété | Passer à deux termes, ou quatre, ou un seul bien choisi. |
| R6 | Parallélisme syntaxique entre phrases voisines | même moule répété 3× | Casser un des trois. |
| R7 | Paragraphe qui se clôt sur une phrase-bilan | dernière phrase = reformulation | Supprimer. La dernière phrase doit apporter, pas résumer. |
| R8 | Participiales et gérondifs en tête de phrase | `^(En |Ayant |Étant |Permettant )` répété | Sujet-verbe-complément. |
| R9 | Subordination empilée | > 3 propositions subordonnées | Découper. |

---

## 3. Formules rhétoriques

### 3.1 Contrastes correctifs (le tic n°1)

Structure : nier une proposition pour en poser une autre, alors que personne n'avait affirmé la première.

- « ne… pas X, **mais** Y »
- « il ne s'agit pas de X, mais de Y »
- « X n'est pas Y, c'est Z »
- « moins X que Y »
- « plus qu'une simple X, c'est un Y »
- « loin d'être X, Y »
- « non pas X, mais bien Y »
- « ce n'est pas tant X que Y »

**Regex** : `n(e|')(?:[^.!?]{0,80})pas[^.!?]{0,80}\b(mais|c'est)\b`

**Correction** : affirmer directement Y. Ne garder la négation que si X a réellement été avancé par quelqu'un dans le texte.

### 3.2 Intensificateurs vides

`véritable`, `réel`, `authentique`, `profond`, `fondamental`, `crucial`, `essentiel`, `incontournable`, `majeur`, `remarquable`, `fascinant`, `puissant`, `robuste`, `à part entière`, `de premier plan`, `sans précédent`

Adverbes : `véritablement`, `réellement`, `précisément`, `particulièrement`, `notamment`, `littéralement`, `pleinement`, `résolument`, `indéniablement`, `clairement`

**Regex** : `\b(véritable(ment)?|réel(le|lement)?|fondamental|crucial|essentiel|incontournable|précisément|particulièrement|indéniablement)\b`

**Test** : supprimer le mot. Si le sens ne change pas, il était vide. C'est le cas dans ~90 % des occurrences.

Cas particulier de « **c'est précisément** » : présente comme une déduction serrée ce qui n'est qu'une transition. Supprimer les deux mots.

### 3.3 Connecteurs et transitions

- « Autrement dit », « en d'autres termes », « pour le dire autrement »
- « En somme », « en définitive », « au final », « à terme »
- « Il convient de noter que », « il est important de souligner que », « notons que »
- « Force est de constater que »
- « Cela étant dit », « ceci dit »
- « À l'inverse », « en revanche », « par ailleurs » en début de chaque paragraphe
- « Ainsi », « dès lors », « de fait »

**Règle** : « Autrement dit » signale que la première formulation a échoué. Garder **la meilleure des deux versions**, supprimer l'autre et le connecteur.

### 3.4 Ouvertures et clôtures

- « Dans un monde où… », « À l'heure où… », « Alors que… »
- « Plongeons dans », « explorons », « décryptons »
- « Dans cet article, nous allons voir »
- « Que vous soyez X ou Y… »
- « Vous vous demandez peut-être… »
- « Une chose est sûre »
- « Ce n'est qu'un début »
- « L'avenir nous le dira »
- « comme souvent, la vérité se situe entre les deux »
- « X n'est pas un luxe, c'est une nécessité »

### 3.5 Métaphores et lexique par défaut

`au cœur de`, `pierre angulaire`, `fil rouge`, `prisme`, `paysage`, `écosystème`, `levier`, `brique`, `socle`, `colonne vertébrale`, `changement de paradigme`, `révolution`, `arsenal`, `boîte à outils`, `garde-fou`, `cercle vertueux`, `terrain de jeu`, `nouvelle donne`, `à double tranchant`

### 3.6 Anglicismes de traduction (indice fort de génération)

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
| c'est un game changer | (reformuler) |

---

## 4. Structure du discours

- **Symétrie obligatoire** : autant d'avantages que d'inconvénients, autant de "pour" que de "contre", chaque section de même longueur.
- **Introduction qui annonce le plan** puis **conclusion qui répète l'introduction**.
- **Trois points, toujours trois.** Jamais deux, jamais sept.
- **Conclusion en équilibriste** : ne tranche jamais, renvoie dos à dos.
- **Question rhétorique** en ouverture de section.
- **Adresse au lecteur** ("vous") injustifiée dans un texte technique.
- **Tableau comparatif** non demandé.
- **TL;DR / En résumé** systématique.

---

## 5. Contenu (les marqueurs les plus difficiles à truquer)

Ce sont les plus décisifs : la surface se corrige, le fond se voit.

- **Aucun chiffre daté, aucune source, aucun nom propre vérifiable.**
- **Exemples génériques** : « une entreprise », « un développeur », « une équipe » au lieu d'un cas réel.
- **Aucun aveu d'ignorance.** Un humain compétent écrit « je ne sais pas », « je n'ai pas vérifié », « ça m'a surpris ».
- **Aucune anecdote** située dans le temps ou l'espace.
- **Aucune opinion tranchée**, aucun risque pris, aucune cible désignée.
- **Aucune digression.** Le texte ne bifurque jamais.
- **Aucun coût cognitif visible** : pas de retour en arrière, pas de correction, pas d'hésitation assumée.
- **Hedging permanent** : `peut`, `pourrait`, `tend à`, `semble`, `dans une certaine mesure`, `souvent`, `généralement`, `dans bien des cas`.
- **Rien de daté ni de local** : pas de version d'outil, pas de prix, pas de contexte réglementaire précis.

---

## 6. Métriques de diagnostic

À calculer sur le texte complet. Les seuils sont indicatifs, calibrés sur de la prose professionnelle française.

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
| Noms propres + chiffres / 1000 mots | < 5 | > 12 |
| Écart-type des longueurs de paragraphe | < 25 % de la moyenne | > 50 % |

**Score global** : compter les métriques hors cible. 0–2 → texte propre. 3–5 → tics présents, corrigeables. 6+ → réécriture profonde nécessaire.

---

## 7. Procédure de correction

Appliquer dans cet ordre. Les passes 1–3 sont mécaniques, les passes 4–6 demandent du jugement.

### Passe 1 — Élagage mécanique
Supprimer sans remplacer : intensificateurs vides, adverbes de renforcement, « il convient de noter que », « autrement dit » (garder une seule des deux formulations), gras superflu, emojis.

### Passe 2 — Ponctuation
Éliminer les tirets cadratins au-delà du quota. Convertir les incises en phrases autonomes ou en subordonnées légères.

### Passe 3 — Contrastes
Traquer chaque « ne… pas X, mais Y ». Affirmer Y directement, sauf si X a été explicitement posé auparavant.

### Passe 4 — Rythme
Découper toute phrase > 40 mots. Puis **injecter délibérément de la variance** : au moins une phrase de moins de 8 mots tous les deux paragraphes. Casser l'uniformité des paragraphes.

### Passe 5 — Structure
Supprimer les phrases-bilans en fin de paragraphe. Supprimer la conclusion si elle ne fait que répéter. Casser les symétries artificielles : si un côté a plus à dire, qu'il soit plus long. Passer de trois points à deux ou quatre quand c'est plus juste.

### Passe 6 — Fond
La seule passe qui compte vraiment. Ajouter ce qu'un LLM ne peut pas inventer :
- un chiffre, une date, une version, un prix ;
- un cas concret vécu, avec son contexte ;
- une position tranchée assumée ;
- une limite honnête : ce qui n'a pas été testé, ce qui reste incertain ;
- une digression brève mais authentique.

### Contrôle final
Recalculer les métriques de la section 6. Puis lire à voix haute : si le rythme ne surprend jamais, la passe 4 a échoué.

---

## 8. Faux positifs — ne pas sur-corriger

Certains marqueurs sont légitimes selon le registre :

- Le **tiret cadratin** est un usage littéraire français ancien et respectable. Le problème est la densité, pas l'existence.
- Les **puces en gras** sont normales en documentation technique.
- Le **parallélisme** est un outil rhétorique volontaire dans un discours ou un manifeste.
- « **Autrement dit** » est légitime après un passage réellement technique, pour un lecteur non spécialiste.
- La **longueur des phrases** varie selon le genre : le juridique et l'académique tolèrent plus.

**Règle** : ne corriger que ce qui, une fois corrigé, rend le texte meilleur. Un texte débarrassé de tous ses tics mais devenu plat n'a rien gagné.

---

## 9. Grille de relecture rapide (checklist)

- [ ] Aucun tiret cadratin superflu
- [ ] Aucun paragraphe à ≥ 2 incises
- [ ] Aucune occurrence de « véritable », « c'est précisément », « il convient de »
- [ ] Aucun « ne… pas X, mais Y » non justifié
- [ ] Aucune phrase > 40 mots
- [ ] Au moins une phrase courte (< 8 mots) tous les 2 paragraphes
- [ ] Longueurs de paragraphes visiblement inégales
- [ ] Aucune phrase-bilan en fin de paragraphe
- [ ] Aucune triade non intentionnelle
- [ ] Aucun anglicisme de la liste 3.6
- [ ] Au moins un chiffre ou un nom propre vérifiable par section
- [ ] Au moins une position tranchée dans le texte
- [ ] Au moins une limite ou une incertitude assumée
- [ ] La conclusion ajoute quelque chose (ou n'existe pas)
