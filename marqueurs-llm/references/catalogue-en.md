# Catalogue des marqueurs de l'anglais généré

Référence pour l'analyse de textes en anglais. Les codes entre crochets sont
ceux du rapport d'analyse, pour passer d'une occurrence signalée à sa
correction.

Ce catalogue diffère du catalogue français sur un point de méthode. Les seuils
français viennent d'un jugement exercé ; ceux-ci sont mesurés. Le corpus de
référence est Eric Evans, *Domain-Driven Design*, Addison-Wesley, 2003 :
99 965 mots de prose technique, découpés en 119 échantillons de 800 mots.
Chaque chiffre cité ici sort de `calibration/seuils-en.json` ou d'un comptage
direct sur ce fichier. Aucun n'est transposé du français.

Le corollaire est contraignant. Un tour de phrase fréquent chez Evans n'est pas
un marqueur, même si l'intuition proteste. Plusieurs transpositions évidentes
du français se sont révélées fausses à la mesure, et la section 7 les liste.

## Sommaire

1. [Typographie et ponctuation](#1-typographie-et-ponctuation) — T1, T4, T6, T7, T8, T9
2. [Rythme et syntaxe](#2-rythme-et-syntaxe) — R1 à R9, P
3. [Formules rhétoriques](#3-formules-rhétoriques) — X, N, I, C, O, M, H
4. [Structure du discours](#4-structure-du-discours)
5. [Contenu](#5-contenu)
6. [Métriques et seuils](#6-métriques-et-seuils)
7. [Faux positifs](#7-faux-positifs)
8. [Checklist de relecture](#8-checklist-de-relecture)

---

## 1. Typographie et ponctuation

| Code | Marqueur | Détection | Correction |
|---|---|---|---|
| T1 | Tiret cadratin (—) | `—` hors début de ligne | Virgule, parenthèse, deux-points, ou coupure de phrase. Seuil : 2,48 / 1000 mots. |
| T3 | Incises multiples dans un paragraphe | ≥ 2 incises encadrées / paragraphe | Une par paragraphe au plus. |
| T4 | Points de suspension unicode, mélange de guillemets | `…`, cohabitation de `"` et `“` | Trois points, ou rien. Un seul style de guillemets par document. |
| T5 | Deux-points comme moteur rhétorique | ratio `:` / phrases > 0,15 | Alterner. Les deux-points annoncent, ils ne rythment pas. |
| T6 | Gras intra-paragraphe | `**` hors titre et hors tête de puce | Si tout est important, rien ne l'est. Supprimer 90 %. |
| T7 | Puce ouverte par un terme en gras suivi de deux-points | `^[-*] \*\*.+\*\* ?:` | Normal en doc technique, suspect en prose. |
| T8 | Emoji en tête de titre ou de puce | plage emoji | Supprimer. |
| T9 | Titre binaire « Concept: précision » | `^#+ .+: .+$` répété | Varier, ou supprimer le sous-titre. |

Le code T2 du catalogue français, qui signale le tiret collé aux mots, n'a pas
d'équivalent ici. Il est retiré. En anglais américain le tiret cadratin se colle,
et Evans le confirme sans nuance : sur ses 106 tirets, 93 sont directement
accolés à une lettre des deux côtés, et **aucun** n'est entouré d'espaces.
Détecter `\w—\w` en anglais reviendrait à détecter l'orthographe correcte.

### 1.1 Ce qui reste vrai du tiret cadratin

L'intuition voulait que le tiret soit banal en anglais et donc inutilisable
comme signal. La mesure dit l'inverse. Evans est à 1,14 tiret pour mille mots
en médiane d'échantillon, 2,48 au 9ᵉ décile : les valeurs françaises, à la
décimale près. Un texte anglais à 5 tirets pour mille mots est aussi anormal
qu'un texte français au même taux.

La forme diffère davantage que la densité. Chez Evans, 64 phrases contiennent
un seul tiret et 21 en contiennent deux ou plus. Le tiret unique arrive en fin
de phrase et y ajoute une réserve, une précision, un doute :

> they use the jargon of their field—probably in various flavors.

> These diagrams can be somewhat casual—even hand-drawn.

Le tiret apporte une information que la phrase n'avait pas. Le modèle, lui,
préfère la paire, qui encadre un segment amovible :

> The ubiquitous language—the shared vocabulary of the team—becomes the
> foundation of the design.

Ce segment tient entre virgules ou entre parenthèses sans rien perdre. C'est
le test : si les deux tirets peuvent devenir des virgules sans que la phrase
proteste, ils décoraient.

### 1.2 Guillemets

Le marqueur français « guillemets droits au lieu de guillemets français »
disparaît. Evans emploie 437 guillemets droits et zéro guillemet courbe, sur
un livre composé chez Addison-Wesley. Le guillemet droit est la norme de la
prose anglaise en texte brut, et le signaler produirait 437 faux positifs sur
un seul livre.

Ce qui reste : l'ellipse `…` en un seul caractère (zéro occurrence chez Evans),
et surtout la **cohabitation** des deux styles dans un même document. Un texte
où les guillemets courbes apparaissent par îlots au milieu de guillemets droits
a été assemblé par copier-coller depuis une interface qui compose les siens.

---

## 2. Rythme et syntaxe

| Code | Marqueur | Seuil mesuré | Correction |
|---|---|---|---|
| R1 | Trop de phrases longues | part de phrases > 40 mots au-delà de 4,88 % | Couper. Evans est à 2,08 % en médiane. |
| R2 | Longueur moyenne élevée | > 21,32 mots/phrase | Viser 18. Evans : 18,42 en médiane, 18,49 sur l'ensemble. |
| R3 | **Faible variance des longueurs** | écart-type < 7,33 mots, ou σ/μ < 0,40 | Injecter des phrases de 3 à 8 mots. Evans : 8,58 et 0,47. |
| R4 | Paragraphes de taille uniforme | variation des longueurs < 0,29 | Alterner. Evans : 0,44. |
| R5 | Rythme ternaire systématique | > 1,24 triade / 1000 mots | Deux termes, ou quatre. Médiane humaine : 0. |
| R6 | Parallélisme entre phrases voisines | même moule 3 fois | Casser l'une des trois. |
| R7 | Paragraphe clos sur une phrase-bilan | dernière phrase = reformulation | Supprimer. |
| R8 | Participiales en tête de phrase | `^(By |Having |Given |Leveraging |Understanding )` répété | Sujet-verbe-complément. |
| R9 | Subordination empilée | > 3 subordonnées | Découper. |
| P | **Participiale de bénéfice en fin de phrase** | toute occurrence | Voir 2.1. Evans : 0,06 avec le motif restreint. |

R3 reste le marqueur le plus fiable et le plus coûteux à truquer. Un modèle
produit des phrases régulières parce qu'il optimise la fluidité locale ; Evans
va de 2 mots à 66 dans le même chapitre, parce que son argument n'a aucune
raison d'être régulier. Le rapport affiche le profil complet des longueurs :
l'œil repère l'anomalie plus vite qu'un écart-type.

### 2.1 [P] La participiale de bénéfice — marqueur propre à l'anglais

Le français n'a pas d'équivalent commode de cette construction, et elle est
devenue l'un des tics les plus visibles de l'anglais généré.

Structure : proposition principale, virgule, participe présent qui annonce un
avantage.

> The system caches results, **allowing** faster response times.

> Teams adopt a shared vocabulary, **enabling** clearer communication and
> **reducing** rework.

Le problème n'est pas grammatical. Il est argumentatif. La proposition
participiale n'est pas *affirmée*, elle est *accrochée*. Elle échappe donc à la
réfutation : personne n'a dit que le cache accélérait les réponses, la phrase
l'a seulement laissé entendre en passant. Le modèle apprécie cette construction
parce qu'elle ajoute une justification sans engager de sujet, ni de temps, ni
de mesure. Empilée, elle transforme une description en argumentaire.

Evans en produit 22 en 100 000 mots, et les siennes portent un contenu :

> …, resulting in a $50MM Loan divided among the lenders.

> …, allowing concentration on different parts of the design in isolation.

> …, making refactoring harder.

La première contient un chiffre. La troisième annonce une conséquence
défavorable, ce qu'aucun argumentaire ne fait spontanément.

Le lexique sépare les deux usages mieux que la syntaxe. Evans emploie
`making` 11 fois, `allowing` 9, `resulting in` 3, `providing` 3, `helping` 3.
Sept verbes de la liste de détection n'apparaissent **jamais** derrière une
virgule chez lui, pas une seule fois en 100 000 mots :

`ensuring`, `enabling`, `empowering`, `streamlining`, `delivering`,
`fostering`, `offering`.

Ces sept-là sont le cœur du marqueur. Ils promettent un bénéfice au lecteur
plutôt que de décrire un effet.

**Correction** : convertir la participiale en phrase complète, avec un sujet.
La question « qui fait quoi » se pose alors d'elle-même, et la moitié des
clauses ne survivent pas à la question. `Teams adopt a shared vocabulary,
enabling clearer communication` devient `Teams adopt a shared vocabulary.
Communication gets clearer`, et l'auteur voit tout de suite qu'il n'a rien
mesuré.

---

## 3. Formules rhétoriques

### 3.1 [X] Contrastes correctifs

Nier une proposition pour en poser une autre, alors que personne n'avait
affirmé la première. Le second terme reçoit un relief qu'il n'a pas gagné.

- `not just X, but Y`
- `it's not X — it's Y`
- `X isn't about Y, it's about Z`
- `more than just a X`
- `less about X than about Y`
- `rather than X, Y`
- `X is not a Y; it's a Z`

**Correction** : affirmer Y directement. Garder la négation seulement si X a
été réellement avancé plus haut, par l'auteur ou par quelqu'un qu'il cite.

Seuil : **0,00**, c'est-à-dire toute occurrence. Le motif a été resserré après
mesure : dans sa version large il faisait 44 correspondances sur Evans, en
attrapant la coordination anglaise ordinaire (`does not lead to the removal of
the Itinerary object, but to a change in its definition`). Interdire la virgule
et les conjonctions à l'intérieur du membre nié le ramène à une seule
correspondance sur cent mille mots — et celle-là est un faux positif. La
section 7 détaille le tri.

### 3.2 [N] `Not only X but also Y` — marqueur propre à l'anglais

Assez fréquent et assez caractéristique pour mériter son propre code, alors
que le français ne connaît pas de tour aussi stéréotypé.

Seuil mesuré : **0,00 pour mille mots**. Ce n'est pas une coquetterie de
calibration. Sur 119 échantillons de 800 mots tirés d'Evans, le 9ᵉ décile est à
zéro, ce qui signifie que plus de neuf dixièmes de sa prose n'en contiennent
aucune occurrence. Le livre entier en compte deux sous la forme stricte
`not only … but also`, et neuf si l'on accepte toutes les variantes de
`not only`.

Ce qui distingue les siennes :

> **Not only** is it unrealistic to expect one to adopt the domain model of the
> other, **it may be** undesirable for both parties.

Les deux termes disent des choses différentes, et le second est le plus fort.
La version générée fait l'inverse : elle reformule le premier terme dans un
registre plus élevé.

> This approach **not only** improves performance **but also** enhances
> maintainability.

**Test** : échanger les deux termes. Si la phrase ne perd rien, la construction
était décorative. `improves maintainability but also enhances performance`
fonctionne aussi bien, donc la structure ne portait rien.

**Correction** : `and`, ou deux phrases. Si les deux termes sont vraiment de
force inégale, dire lequel est le plus fort et pourquoi.

Un seuil à zéro veut dire « regarde », pas « supprime ». Evans lui-même passe
au-dessus deux fois.

### 3.3 [I] Intensificateurs vides

Le lexique se scinde en deux moitiés qui ne se traitent pas de la même façon.

**Ceux qu'Evans emploie**, avec leur compte sur 100 000 mots :
`essential` 36, `true` 33, `especially` 26, `fundamental` 24, `critical` 24,
`particularly` 23, `meaningful` 18, `highly` 17, `significant` 16, `crucial` 14,
`powerful` 10, `comprehensive` 8, `robust` 7, `compelling` 6.

Cinq de ces mots ont depuis été **retirés du lexique** : `true`, `especially`,
`particularly` et `highly` sont trop fréquents chez Evans pour être signalés
nus, et `robust` reste sous surveillance. Pour les autres, seule la densité
compte. La médiane humaine est à 1,23 pour mille mots, le seuil à 4,84.

**Ceux qui n'apparaissent pas une seule fois** en 100 000 mots de prose
technique :
`remarkable`, `unprecedented`, `pivotal`, `invaluable`, `innovative`,
`incredibly`, `undoubtedly`, `genuine`, `arguably`, `utmost`.

Pour ceux-là, la présence suffit à poser la question. `paramount` et `notably`
figurent chacun une fois dans le livre, ce qui les met à la limite.

Le reste du lexique de détection : `truly`, `profound`, `profoundly`,
`fundamentally`, `essentially`, `vital`, `critically`, `significantly`,
`remarkably`, `seamless`, `cutting-edge`, `state-of-the-art`, `extremely`,
`sheer`.

**Test** : supprimer le mot. Si le sens ne bouge pas, il était vide.
`seamless`, `robust` et `comprehensive` placés devant un nom survivent presque
toujours à la suppression, et c'est ce qui les rend suspects même à faible
dose.

### 3.4 [C] Connecteurs et transitions

C'est ici que l'écart avec le français est le plus violent. Le seuil français
tolère 0,8 connecteur par paragraphe. L'anglais tient à **0,10**, huit fois plus
sévère, parce que la prose technique anglaise en emploie très peu : 95 des 119
échantillons d'Evans n'ont aucun connecteur en tête de phrase.

Evans, sur 100 000 mots :
`on the other hand` 20, `however` 19, `therefore` 17, `ultimately` 12,
`in contrast` 8, `in addition` 8, `in other words` 4, `furthermore` 4,
`thus` 2, `moreover` 1, `in short` 1, `importantly` 1, `by contrast` 1,
`that said` 1.

Un `moreover` en cent mille mots. Dix-neuf `however`, soit un tous les cinq
mille mots.

Ceux qu'il n'emploie **jamais**, et qui constituent donc le cœur du marqueur :

`additionally`, `consequently`, `as such`, `in essence`, `at its core`,
`when it comes to`, `needless to say`, `all in all`, `at the end of the day`,
`in summary`, `in conclusion`, `to summarize`, `simply put`, `put simply`,
`it's worth noting`, `it is important to note`, `that being said`.

**Pourquoi.** Un auteur qui tient son argument relie ses idées par leur
contenu ; le connecteur ferait doublon avec le raisonnement. `Moreover`
n'ajoute rien que la phrase suivante ne dise déjà. `It's worth noting that`
avoue que l'auteur ne sait pas s'il doit garder la remarque. `In other words`
signale que la première formulation a échoué : garder la meilleure des deux
versions, jeter l'autre et le connecteur avec.

La métrique est une densité par paragraphe, pas par millier de mots, parce
qu'un connecteur ouvrant chaque paragraphe trahit un plan récité même quand le
total reste bas.

### 3.5 [O] Ouvertures et clôtures toutes faites

Seuil : **0,00**. Aucune de ces formules n'apparaît chez Evans.

- `In today's fast-paced…`, `In an era where…`, `In the age of…`,
  `In a world where…`
- `Let's dive in`, `Let's delve into`, `Let's explore`, `Buckle up`
- `In this article, we'll explore…`
- `Whether you're a X or a Y…`
- `You might be wondering…`
- `One thing is certain`, `Only time will tell`,
  `This is just the beginning`, `The possibilities are endless`
- `As we've seen`, `Rest assured`

### 3.6 [M] Métaphores et lexique par défaut

Seuil : **0,00**, c'est-à-dire toute occurrence. La liste a été réduite aux
seuls termes qu'Evans n'écrit jamais ou presque : elle sort à 0,03 pour mille
mots sur son livre, et ne touche que 3 échantillons sur 124. Sur cette métrique,
le taux d'échantillons touchés *est* le taux de faux positifs.

| Terme | Occurrences chez Evans | Statut |
|---|---|---|
| `cornerstone`, `at the heart of`, `backbone` figuré | 0 | marqueur |
| `landscape`, `ecosystem`, `paradigm shift`, `game changer` | 0 | marqueur |
| `tapestry`, `testament to`, `underscore`, `showcase`, `boasts` | 0 | marqueur |
| `unlock`, `harness`, `empower`, `streamline`, `foster` | 0 | marqueur |
| `silver bullet`, `treasure trove`, `north star`, `low-hanging fruit` | 0 | marqueur |
| `bridge the gap`, `moving forward`, `double-edged sword`, `dive into` | 0 | marqueur |
| `myriad`, `plethora` | 0 | marqueur |
| `leverage` (8, dont 3 comme nom) | 8 | **retiré du lexique** |
| `navigate` (au figuré, sur un modèle) | 7 | **retiré** ; reste `navigating the complexity` |
| `building block` | 6 | terme du domaine, **retiré**, voir §7 |
| `delve` (toutes formes) | 6 | **sous surveillance**, usage littéral, voir §3.6.1 |
| `realm` nu | 1 | **retiré** ; reste `in the realm of` |
| `intricate`, `meticulous` | 9 et 3 | **non validé comme marqueur** |
| `foundation`, `the power of`, `streamline`, `backbone` | 4, 7, 3, 2 | **retirés ou sous surveillance** |

Les termes à zéro occurrence forment la liste utile. Ils ne sont pas fautifs ;
ils sont usés, et leur absence complète d'un livre technique de cent mille mots
dit quelque chose. Le test reste le même qu'en français : l'auteur aurait-il pu
écrire autre chose à cet endroit ? Si le mot est le premier qui vient, il est
probablement le premier qui est venu au modèle aussi.

La dernière ligne du tableau est un avertissement. `intricate` et `meticulous`
circulent dans les listes de détection publiées sur le web ; le corpus les
contredit.

#### 3.6.1 La famille `delve` / `tapestry` / `testament to`

Ce sous-groupe mérite un traitement séparé, parce que son statut n'est pas
celui d'une métaphore fatiguée. Ce sont des mots que l'anglais généré emploie
hors de toute proportion avec l'anglais écrit, y compris l'anglais soutenu.
L'inflation de registre introduite par l'entraînement sur préférences humaines
favorise le mot rare et cérémonieux, et ces termes-là sont devenus des
signatures.

Le noyau : `delve into`, `tapestry`, `testament to`, `underscore` (verbe),
`showcase` (verbe), `boasts`, `harness`, `foster`, `garner`, `myriad`,
`plethora`, `embark on`, `elevate`, `unlock`, `realm`, `landscape` (figuré).

Le contre-test sur Evans est net : `tapestry` 0, `testament` 0, `underscore` 0,
`showcase` 0, `boasts` 0, `harness` 0, `foster` 0, `garner` 0, `myriad` 0,
`plethora` 0, `embark` 0, `unlock` 0. Douze termes, zéro occurrence, cent mille
mots.

Et pourtant `delve` y figure six fois. Voilà la nuance :

> The point here is not to **delve** deeply into designing Factories…

> (Chapter 14 **delves** into how to decide and how to manage the result.)

> …without **delving** into its internals.

C'est le verbe ordinaire, au sens de creuser une question, avec un complément
réel. Le marqueur est l'emploi cérémoniel (`let's delve into`,
`in this section we delve into`), et surtout l'accumulation avec le reste de
la famille. Un `delve` isolé dans un texte par ailleurs sobre ne dit rien.
Trois membres de la famille dans le même paragraphe disent beaucoup.

### 3.7 [H] Hedging

`tends to`, `seems to`, `appears to`, `generally`, `typically`, `usually`,
`in many cases`, `to some extent`, `arguably`, `relatively`, `somewhat`,
`perhaps`, `likely`, `in some cases`, `not necessarily`, `for the most part`,
`broadly speaking`, `one could argue`.

Seuil : 6,50 pour mille mots, médiane humaine 3,39.

Ces deux chiffres ont remplacé 14,96 et 8,71, et la baisse n'est pas un
durcissement : c'est un changement de ce qui est mesuré. `may`, `might`,
`could`, `can`, `would`, `should`, `often` et `sometimes` ont été **retirés du
lexique**. À eux seuls, `may`, `could` et `might` faisaient 5,54 des 9,06
occurrences pour mille mots de l'ancienne médiane. Le modal n'est pas un tic :
c'est le métier de l'écriture technique, où une affirmation d'ingénierie sans
condition est presque toujours fausse. Evans totalise 268 `may`, 177 `could` et
109 `might` ; les compter revenait à mesurer sa densité de modaux et à l'appeler
du hedging. Ce qui reste mesure le style atténuatif proprement dit.

Le hedging ne compte donc qu'en combinaison. Un texte à 18 pour mille mots qui
est par ailleurs propre sur toutes les autres métriques mérite le bénéfice du
doute. Le même chiffre avec des connecteurs à 0,4 par paragraphe et zéro fait
vérifiable est un texte qui s'arrange pour n'être jamais réfutable.

---

## 4. Structure du discours

- **Symétrie obligatoire** : autant d'avantages que d'inconvénients, chaque
  section de même longueur. Le réel est rarement symétrique.
- **Introduction qui annonce le plan**, puis **conclusion qui répète
  l'introduction**.
- **Trois points, toujours trois.** Jamais deux, jamais sept.
- **Conclusion en équilibriste** : ne tranche jamais, renvoie dos à dos.
- **Question rhétorique** en ouverture de section.
- **Titres en Title Case à tous les niveaux**, y compris pour des titres qui
  sont des phrases entières.
- **Section `Key Takeaways` ou `TL;DR`** non demandée.
- **Liste à puces là où une phrase suffisait.** Le modèle passe en liste dès
  qu'il énumère plus de deux choses ; un auteur garde souvent la prose.
- **Tableau comparatif** non demandé.
- **Emphase par le gras** sur le premier mot de chaque puce.

L'adresse au lecteur (`you`) ne figure pas dans cette liste, contrairement au
catalogue français. Evans l'emploie 435 fois. Voir section 7.

---

## 5. Contenu

Les marqueurs les plus décisifs, et les plus difficiles à truquer : la surface
se corrige en une heure, le fond se voit.

- **Aucun chiffre daté, aucune source, aucun nom propre vérifiable.**
- **Exemples génériques** : `a company`, `a developer`, `a team` au lieu d'un
  cas réel avec un nom.
- **Aucun aveu d'ignorance.** Un auteur compétent écrit `I don't know`,
  `I haven't verified this`, `this surprised me`.
- **Aucune anecdote** située dans le temps ou l'espace.
- **Aucune opinion tranchée**, aucun risque pris, aucune cible désignée.
- **Aucune digression.** Le texte ne bifurque jamais.
- **Aucun coût cognitif visible** : pas de retour en arrière, pas de
  correction, pas d'hésitation assumée.
- **Rien de daté ni de local** : pas de version d'outil, pas de prix, pas de
  contexte réglementaire précis.

La métrique correspondante est celle qui sépare le plus nettement les deux
classes. Noms propres et chiffres, chez Evans : **35,24 pour mille mots** en
médiane, contre un seuil d'alerte à 11,22. Un facteur trois. Il nomme des
projets, des personnes, des chapitres, des classes Java, et écrit
`a $50MM Loan divided among the lenders` là où un modèle aurait écrit
`a large loan`.

C'est la raison pour laquelle la passe de correction demande de l'information à
l'utilisateur au lieu de l'inventer. Un chiffre plausible mais faux est plus
grave qu'un texte sans chiffre.

---

## 6. Métriques et seuils

Dix-sept métriques, calculées sur la prose seule (hors code, tableaux,
frontmatter). Source : `calibration/seuils-en.json`.

| Métrique | Médiane humaine | Seuil | Déclenche |
|---|---|---|---|
| Longueur moyenne des phrases | 18,42 | 21,32 | au-dessus |
| Écart-type des longueurs | 8,58 | 7,33 | en dessous |
| Coefficient de variation (σ/μ) | 0,47 | 0,40 | en dessous |
| Part de phrases > 40 mots | 2,08 % | 4,88 % | au-dessus |
| Part de phrases < 10 mots | 13,04 % | 6,52 % | en dessous |
| Variation des longueurs de paragraphe | 0,44 | 0,29 | en dessous |
| Tirets cadratins / 1000 mots | 1,14 | 2,48 | au-dessus |
| Intensificateurs / 1000 mots | 1,23 | 4,84 | au-dessus |
| Contrastes correctifs / 1000 mots | 0,00 | 0,00 | toute occurrence |
| `not only … but also` / 1000 mots | 0,00 | 0,00 | toute occurrence |
| Connecteurs / paragraphe | 0,00 | 0,10 | au-dessus |
| Triades / 1000 mots | 0,00 | 1,24 | au-dessus |
| Hedging / 1000 mots | 3,39 | 6,50 | au-dessus |
| Métaphores / 1000 mots | 0,00 | 0,00 | toute occurrence |
| Ouvertures toutes faites / 1000 mots | 0,00 | 0,00 | toute occurrence |
| Participiales de bénéfice / 1000 mots | 0,00 | 0,00 | toute occurrence |
| Noms propres + chiffres / 1000 mots | 35,24 | 11,22 | en dessous |

**Score global** : nombre de métriques hors seuil, sur 17. Les seuils étant
placés aux déciles du corpus humain, 10 % des échantillons d'Evans déclenchent
sur chaque métrique prise isolément, et pourtant le score médian reste à 1.

| Texte | Score |
|---|---|
| Evans, médiane des 119 échantillons | 1 / 17 |
| Evans, pire échantillon | 5 / 17 |
| Caricature écrite en anglais | 11 / 17 |
| Traduction anglaise d'un texte LLM français | 12 / 17 |
| Texte-témoin `exemple-texte-llm-en.md` | 17 / 17 |

Lecture : 0–2 texte propre, 3–6 tics présents et corrigeables, 7 ou plus
réécriture profonde. Aucun échantillon humain ne dépasse 5. Les paliers sont
proportionnels à ceux du français, qui ne compte que treize métriques : une
langue qui mesure plus de choses ne doit pas être jugée plus sévèrement pour
cette seule raison.

### Ce que ces seuils ne couvrent pas

Un seul auteur, un seul registre, une seule époque. Les valeurs collent à la
prose technique de livre. Un billet de blog anglais admet davantage de tirets
et de phrases courtes ; le marketing admet des ouvertures que ce catalogue
condamne. Les registres `blog` et `marketing` ne sont pas calibrés, et il vaut
mieux le dire que produire un chiffre inventé.

Sur un texte de moins de 200 mots, les densités par millier de mots et
l'écart-type ne veulent rien dire. S'en tenir alors aux occurrences repérées.

---

## 7. Faux positifs

Un marqueur signalé est une question, pas une faute. Le corpus a produit des
réponses qui contredisent l'intuition, et les voici.

**Le motif de contraste large fait 44 faux positifs à lui seul.** Le motif
`not … but` se déclenche 44 fois sur Evans, presque toujours sur une négation
ordinaire : `does not lead to the removal of the Itinerary object, but to a
change in its definition`. C'est une correction factuelle, pas une figure. Le
critère de tri est unique : X a-t-il été affirmé quelque part ? Si oui, la
négation est légitime.

**`delve` est un verbe anglais.** Six occurrences chez Evans, toutes littérales.
Le marqueur est l'emploi cérémoniel, pas le mot.

**`leverage` aussi.** Huit occurrences, dont trois comme nom
(`provide leverage for the implementation`). Le verbe figure cinq fois. Le mot a
été **retiré du lexique** : à lui seul il consommait la moitié du budget de faux
positifs de la métrique. Ne reste que la collocation `leveraging the power of`.

**`building block` est un terme du domaine.** Six occurrences, et une partie
entière du livre s'intitule *The Building Blocks of Model-Driven Design*. Un
terme technique établi n'est pas une métaphore usée.

**`intricate` et `meticulous` ne sont pas des marqueurs.** Neuf et trois
occurrences. Ils figurent dans beaucoup de listes circulant sur le web ; le
corpus ne les valide pas.

**Les guillemets droits ne sont pas un marqueur.** 437 chez Evans, zéro
guillemet courbe.

**L'adresse au lecteur non plus.** 435 `you`. La deuxième personne est la norme
de la documentation technique anglaise, contrairement au français.

**Le hedging est un métier.** 9,06 pour mille mots chez Evans quand on compte
les modaux, 3,39 sans eux. Les modaux ont été retirés du lexique ; ils ne
doivent jamais être montrés à un auteur comme une faute.

**`however` et `on the other hand` sont légitimes** au rythme d'Evans, soit un
tous les cinq mille mots. Le seuil vise l'accumulation.

**Le tiret cadratin existe en anglais littéraire et technique** depuis toujours.
106 chez Evans. Le problème est la densité et la forme appariée.

**Les participiales finales existent chez les humains.** 37 chez Evans avec le
motif large, dont onze `making` et neuf `allowing`. Le motif retenu ne garde que
les participes de bénéfice abstrait — `enabling`, `ensuring`, `empowering`,
`streamlining` — et tombe à 6. La construction est innocente ; c'est le
vocabulaire qui trahit.

**`not only` est une construction anglaise valide.** Neuf occurrences chez
Evans, deux sous la forme complète. Un seuil à zéro demande un regard, pas une
suppression.

**Les triades sont parfois exactes.** Quand il y a vraiment trois éléments, il
y en a trois. Evans en écrit 0,25 pour mille mots avec virgule d'Oxford, et en
les relisant une par une, ce sont vingt-cinq vraies énumérations. Le seuil est à
1,24 pour mille mots : c'est un marqueur de densité, jamais d'occurrence isolée.
La triade sans virgule d'Oxford, elle, a été abandonnée — aucune regex ne
distingue `speed, quality and cost` de `two categories, commands and queries`.

**Le parallélisme** est un outil rhétorique volontaire dans un discours, un
manifeste, un texte destiné à être lu à voix haute.

**Règle de tranchage** : ne corriger que ce qui, une fois corrigé, rend le texte
meilleur. Un texte débarrassé de tous ses tics mais devenu plat n'a rien gagné.

---

## 8. Checklist de relecture

- [ ] Densité de tirets cadratins sous 2,5 pour mille mots
- [ ] Aucune paire de tirets remplaçable par des virgules
- [ ] Aucun `not only … but also` décoratif
- [ ] Aucune participiale en `ensuring`, `enabling`, `empowering`,
      `streamlining`, `delivering`, `fostering`, `offering`
- [ ] Aucune occurrence de `remarkable`, `unprecedented`, `pivotal`,
      `invaluable`, `innovative`, `undoubtedly`
- [ ] Aucun `additionally`, `it's worth noting`, `in essence`,
      `at the end of the day`, `that being said`
- [ ] Aucun `tapestry`, `testament to`, `underscore`, `showcase`, `myriad`
- [ ] Aucun `not X but Y` dont le X n'a jamais été affirmé
- [ ] Au moins une phrase de moins de 10 mots tous les sept ou huit
- [ ] Longueurs de paragraphes visiblement inégales
- [ ] Aucune phrase-bilan en fin de paragraphe
- [ ] Aucune ouverture de la liste 3.5
- [ ] Au moins un chiffre ou un nom propre vérifiable par section
- [ ] Au moins une position tranchée dans le texte
- [ ] Au moins une limite ou une incertitude assumée
- [ ] La conclusion ajoute quelque chose, ou n'existe pas
