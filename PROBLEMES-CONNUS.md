# Problèmes connus — détecteur anglais

État au 20 août 2026, après la passe de correction.

Sept des quinze constats de la passe adverse sont réglés et mesurés. Les huit
autres tiennent à des limites de méthode plus qu'à des bugs, et sont décrits
ici avec ce qu'il faudrait pour les lever.

---

## Réglés

### La métrique de spécificité ne pèse plus dans le score

`specifique_1k` est devenue une **observation** : le rapport l'affiche sous le
score, avec sa raison d'être.

> Un script compte les chiffres, il ne sait pas s'ils renvoient à quelque chose.
> Les scorer reviendrait à récompenser un chiffre inventé.

Le cas qui l'a motivée : ajouter à un billet une phrase aux chiffres entièrement
fabriqués le faisait passer de « tics présents » à « texte propre ». La
vérification revient au lecteur, qui est le seul à pouvoir la faire.

### Les sept marqueurs orphelins comptent

T2, T4, T6, T7, T8, T9 et A pesaient zéro tout en étant affichés. Ils entrent
maintenant dans le score par cinq métriques :

| Métrique | Marqueurs | Seuil |
|---|---|---|
| `gras_1k` | T6 | 6 pour mille mots, 18 en registre technique |
| `puces_gabarit_pct` | T7 | 40 % des puces sur le même gabarit |
| `titres_binaires_1k` | T9 | 1 pour mille mots |
| `typographie_1k` | T2, T4, T8 | 3 pour mille mots, 6 en technique |
| `faux_amis_1k` | A | 1 pour mille mots (français seul) |

`puces_gabarit_pct` mesure une **part**, pas un décompte. La doctrine dit que
les puces en gras sont normales en documentation technique, et la mesure lui
donne raison : la documentation légitime du dépôt est entre 0 et 9 %, la doc
générée à 100 %. Ce qui trahit n'est pas la puce en gras, c'est leur
uniformité. Sous quatre puces, la part n'est pas calculée.

### Cinq registres anglais sur six sont maintenant signalés

| texte | avant | après |
|---|---|---|
| billet de blog | 3/17 tics présents | **4/24 tics présents** |
| doc technique | **0/17 texte propre** | **4/24 tics présents** |
| post LinkedIn | 1/17 texte propre | **4/24 tics présents** |
| newsletter | 1/17 texte propre | 2/24 texte propre |
| rapport de conseil | 3/17 tics présents | **7/24 tics présents** |
| billet « future of work » | 3/17 tics présents | **5/24 tics présents** |

La newsletter reste propre, et c'est un choix argumenté — voir plus bas.

### Le contraste correctif rate moins

Trois formes ajoutées : la construction en deux phrases à sujet non pronominal
(« Your network is not your contacts. It is the people who have seen you
work. »), le « X is not A, but B » sans adverbe, et le titre en contraste
(« The estimate is a story, not a measurement »). Plus deux tournures mesurées
à zéro chez Evans : « has less to do with X and more to do with Y » et
« do not X because Y. They X because Z ».

La sonde de treize contrastes passe de 0,00 à **30,3 pour mille mots**.

### Trois marqueurs de structure entrent en jeu

Ils étaient dans la section 4 du catalogue depuis le début, sans être
implémentés dans aucune des deux langues.

| Marqueur | Fréquence chez Evans | Seuil |
|---|---|---|
| Section de clôture rituelle (`Summary`, `Key takeaways`, `TL;DR`) | **0 en 100 000 mots** | toute occurrence |
| Question rhétorique | d9 = 2,49 | 2,5 pour mille mots |
| Anaphore (phrases enchaînées sur les mêmes mots) | d9 = 1,25 | 1,25 pour mille mots |

L'anaphore couvre deux formes : deux phrases consécutives ouvrant sur les deux
mêmes mots, et trois d'affilée sur le même premier mot (« No flaky test. No
half-documented API. No Slack thread… »).

### Les tirets de substitution comptent

T1 ne cherchait que le cadratin U+2014. Le demi-cadratin espacé et le double
trait d'union sont ajoutés : Evans n'en écrit que trois en cent mille mots, le
coût était nul. La sonde passe de 0,00 à 25,0.

### Les deux outils mesurent enfin pareil

`calibre.py` importe désormais le moteur de `analyse.py` au lieu d'en
réimplémenter la mesure. La médiane de hedging différait de 27 % entre les
deux, si bien qu'un seuil dérivé d'un côté ne voulait pas dire la même chose
appliqué de l'autre.

---

## Ouverts

### Les lexiques contiennent encore de l'anglais technique ordinaire

Sept mots portent 75 % des intensificateurs relevés chez Evans : `essential`,
`fundamental`, `critical`, `meaningful`, `crucial`, `powerful`, `significant`.
La mesure a montré la différence, mais une liste de mots ne sait pas la voir :
chez Evans ils **comparent ou restreignent** (« more critical *than* storage
space »), l'anglais généré qualifie à vide. Il faudrait des motifs contextuels,
pas des listes. Même chose côté métaphores, où `silver bullet` est le titre de
l'article de Brooks et `harness` un *test harness*.

Le budget de faux positifs tient malgré tout (9,3 %), parce que ces mots sont
rares chez Evans. Le problème est ailleurs : ils diluent le signal.

### Le hedging ne sépare pas les deux classes

Les douze mots qui portent 84 % des occurrences chez Evans sont ceux qui
portent les occurrences des textes générés. En prose technique ce sont des
instruments de précision. La métrique reste dans le score parce qu'elle tient
son budget, mais elle n'apporte presque rien.

### Le dénominateur des connecteurs est le paragraphe

`connecteurs_par` vaut 0,10 par paragraphe, dérivé d'un livre de 1 100
paragraphes. Sur un billet de huit paragraphes, un seul « However » en tête
suffit. Le dénominateur devrait être le nombre de mots.

### Quatre métriques ne sont pas calibrées sur corpus

`gras_1k`, `puces_gabarit_pct`, `titres_binaires_1k` et `cloture_1k` ne se
déclenchent jamais sur Evans, pour une raison structurelle : le corpus vient
d'un PDF, il n'a ni gras, ni puces, ni titres markdown. Leurs seuils viennent
du jugement, validés contre la documentation technique du dépôt — la seule
référence markdown humaine disponible, et elle est mince. Un corpus de README
et de documentation antérieurs à 2022 les mettrait sur le même pied que les
autres.

### La newsletter reste à 2/24, et c'est délibéré

`t4-newsletter.md` a été écrite pour être un faux négatif. À la lecture c'en
est un mauvais exemple : elle cite Adobe, Microsoft, Figma, Stripe, Patrick
Campbell, 91 % contre 54 %, sept jours, 2019, et contient une section « One
thing I changed my mind about », c'est-à-dire un aveu de révision. Son seul
tic est un « What this means for you: » répété trois fois.

La signaler demanderait des seuils qui condamneraient aussi la bonne prose. La
règle de tranchage de la skill s'applique à la skill elle-même : ne signaler que
ce qui, une fois corrigé, rend le texte meilleur.

### Le texte court reçoit quand même un verdict

L'avertissement « densités peu fiables » s'affiche, puis le verdict est rendu
sur ces mêmes densités.

### La détection de langue est déséquilibrée

Trente-six mots-outils français contre onze anglais : un texte anglais citant
abondamment une source française bascule vers le français, et le score devient
flatteur faute de charger les bons lexiques.

### Le témoin anglais sature encore

17/24. Mieux que 17/17, mais un témoin saturé détecte mal une régression.

---

## Le plancher

Sur 118 échantillons de 800 mots d'Evans, passés par `analyse.py` :

| score | 0/24 | 1/24 | 2/24 | 3/24 | 4/24 | 5/24 |
|---|---|---|---|---|---|---|
| échantillons | 28 | 36 | 29 | 18 | 5 | 2 |

Médiane 1/24, maximum 5/24. Aucune métrique ne dépasse le budget de 10 % de
faux positifs : la plus haute est à 10,2 %.

Ajouter sept métriques n'a pas dégradé le plancher.
