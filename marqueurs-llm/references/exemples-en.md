# Réécritures commentées — anglais

Le catalogue dit quoi corriger. Ce fichier montre jusqu'où, et surtout où
s'arrêter. Les textes avant/après sont en anglais, le commentaire en français.

Tous les chiffres cités ici sont mesurés, jamais estimés : sur
`corpus/evans-ddd-2003.txt` (Eric Evans, *Domain-Driven Design*, 2003, 99 724
mots de prose narrative) pour la référence humaine, sur
`calibration/controle/` pour les textes fautifs. La règle de lecture est
toujours la même. Ce qu'Evans fait souvent est légitime, quelle que soit
l'intuition qu'on en avait avant de compter.

Les codes entre crochets sont ceux du catalogue. [P] et [N] désignent les deux
motifs propres à l'anglais : la participiale finale et le `not only… but also`.

---

## 1. Le contraste correctif [X]

> **Avant.** It's not just about collecting logs — it's about building a
> profound understanding of how systems behave in production.

La phrase nie une position que personne n'a défendue. Aucun auteur n'a soutenu
que l'observabilité se réduisait à la collecte de logs. La négation sert à
donner du relief au second terme, gratuitement.

> **Après.** Collecting logs will not tell you why a request took four seconds.

Même contenu, posture en moins. La négation subsiste, mais elle porte sur une
affirmation réelle et réfutable.

**Additif contre correctif.** Le motif retenu ne trouve qu'une occurrence de
`not just X but Y` chez Evans en cent mille mots, pour un seuil à zéro — toute
occurrence pose une question. La sienne est instructive :

> A Shared Kernel imposes a much greater burden of coordination, not just in
> development but also in deployment.

Les deux termes tiennent ensemble. Le fardeau existe au développement *et* au
déploiement, la figure additionne. Celle du modèle remplace : elle pose X pour
le retirer aussitôt et faire briller Y. D'où un test rapide : X reste-t-il vrai
après la phrase ? Chez Evans, oui. Dans la caricature, non, plus personne ne
collecte de logs une fois la phrase finie.

**Cas où la figure se garde :**

> Most objections to tracing focus on the cost of sampling. The cost is not in
> the sampling, it is in getting the instrumentation into the code.

X a été posé, par quelqu'un, une phrase plus haut. Corriger serait perdre.

---

## 2. Le tiret cadratin [T1]

> **Avant.** Logs are the historical backbone of observability — they're
> simple, universal, and immediately actionable.

Le tiret introduit une glose : la seconde moitié redit la première en la
détaillant. C'est l'emploi typique du modèle, reconnaissable même isolé.

> **Après 1 (deux-points).** Logs came first, and they are the easiest signal
> to produce: no schema, no agreement with anyone else.

> **Après 2 (coupure).** Logs came first. They are also the easiest thing to
> drown in.

La seconde vaut mieux ici, parce qu'elle règle le tiret et le rythme d'un même
geste : trois mots, puis neuf. Choisir la ponctuation selon le lien logique
réel, parenthèse pour l'aparté, deux-points pour l'annonce, phrase autonome
pour ce qui mérite d'être posé.

**Ce que fait Evans.** 106 tirets pour 99 724 mots, 1,06 pour mille. La médiane
par échantillon est à 1,14, le seuil à 2,48, et la caricature anglaise à 15,46.
L'écart se compte en facteur quinze, pas en pourcentage.

L'emploi diffère autant que la densité :

> These diagrams can be somewhat casual—even hand-drawn.

> …they should use Language and raise concerns when they find it awkward or
> incomplete—or wrong.

Le tiret d'Evans ouvre une rupture : un ajout après coup, une correction que
l'auteur se fait à lui-même. Celui du modèle ouvre une apposition qui reformule
le sujet. Un tiret qu'on remplacerait par *that is* est suspect ; un tiret
qu'on remplacerait par *or even* ne l'est pas.

**Typographie.** 98 des 106 tirets d'Evans sont collés aux mots
(`delays—say`), huit sont espacés. Les guides de style divergent sur ce point,
donc l'espacement seul ne prouve rien. Compter, plutôt que juger à l'œil.

---

## 3. Intensificateurs et triade [I] [Y]

> **Avant.** Observability rests on three fundamental pillars: logs, metrics,
> and traces. Each offers a unique lens, and it's precisely their combination
> that unlocks a comprehensive picture of what's happening at the heart of your
> infrastructure.

Le script compte quatre marqueurs ici : `fundamental`, `comprehensive`,
`at the heart of`, plus la triade `logs, metrics, and traces`. L'œil en voit
deux de plus, `unique` et `unlocks`, que les lexiques ne connaissent pas
encore. Les listes sont un brouillon, la lecture reste nécessaire.

> **Après.** Observability rests on logs, metrics and traces. None of the three
> is enough alone: metrics say the latency doubled, traces say where, logs say
> what the code was doing at the time.

La triade se garde. Il y a bien trois signaux, et la phrase suivante donne à
chacun un rôle que les deux autres ne remplissent pas. La triade
fautive est celle dont le troisième terme est décoratif, pas celle qui compte
trois objets qui existent. Le script comptera quand même une triade sur cette
version corrigée : c'est un faux positif assumé, et le rapport de correction
doit le dire, sinon la relecture suivante l'écrasera.

**Le mot n'est pas le marqueur.** Evans écrit `essential` 36 fois et
`fundamental` 24 fois. Sa densité médiane d'intensificateurs est de 1,23 pour
mille et le seuil à 4,84 ; la caricature est dix fois au-dessus. Supprimer
`essential` d'un texte anglais parce que le mot figure sur une liste est une
faute de méthode. Le supprimer parce qu'il y en a huit dans le même paragraphe,
non. C'est aussi pourquoi `true`, `key`, `core`, `particularly` et `especially`
ont quitté le lexique après mesure : trop fréquents chez Evans pour qu'une
occurrence isolée veuille dire quoi que ce soit.

---

## 4. Le rythme [R3]

> **Avant.** (longueurs : 15, 16, 18, 13, 14 ; moyenne 15,2, écart-type 1,7)
>
> Metrics offer an aggregated view of a running system at a comparatively low
> storage cost. They allow teams to detect anomalies early and to follow trends
> over long periods of time. They also feed the alerting rules that wake the
> on-call engineer up in the middle of the night. However, they do not explain
> the anomalies that they surface to the operators. Distributed tracing then
> brings the causal dimension that the other two signals were missing.

Le contenu est juste. C'est le métronome qui trahit : cinq phrases entre 13 et
18 mots, coefficient de variation 0,11 quand le seuil est à 0,40.

> **Après.** (longueurs : 10, 5, 28, 4 ; cv 0,82)
>
> Metrics cost almost nothing to store and answer in milliseconds. That is
> their whole point. They will catch the anomaly and wake the on-call engineer
> at 3 a.m., and they will still not tell you why checkout latency tripled
> after Tuesday's deploy. Tracing tells you that.

Même information, quatre phrases au lieu de cinq. *That is their whole point*
ne porte presque rien, et c'est sa fonction : casser la mesure et laisser
respirer avant la phrase de vingt-huit mots.

**L'étalon humain.** Un paragraphe d'Evans, longueurs 21, 6, 36, 5, 17, 31 :

> It seems clear enough that errors will result if you take some data from one
> system and misinterpret it in another. You may even corrupt the database. But
> even so, this problem tends to sneak up on us because we think that what we
> are transporting between systems is primitive data, whose meaning is
> unambiguous and must be the same on both sides. This assumption is usually
> wrong. Subtle yet important differences in meaning arise from the way the
> data are associated in each system. And even if primitive data elements do
> have exactly the same meaning, it is usually a mistake to make the interface
> to the other system operate at such a low level.

Deux phrases de cinq et six mots, plantées entre des phrases de trente. Elles
tranchent, elles ne résument pas. C'est le geste d'un auteur qui s'interrompt
pour trancher, et il ne coûte rien à imiter puisqu'il suffit de le vouloir.

Vérifier avec le profil de rythme du script : les nombres doivent sauter.

---

## 5. La participiale finale [P]

Propre à l'anglais, et absente du catalogue français.

> **Avant.** It demands genuine investment, a robust engineering culture, and a
> continuous willingness to challenge established practices, ensuring that
> teams can navigate the complexities of modern systems.

La participiale finale (`, ensuring…`, `, allowing…`, `, enabling…`) accroche
une conséquence à la phrase sans lui donner de sujet. Personne n'assure rien,
la chose s'assure toute seule. C'est commode pour un modèle : la proposition
n'a plus à être vraie de quelqu'un en particulier.

> **Après.** It demands instrumentation that nobody wants to own, and a team
> that treats an unexplained incident as unfinished work.

**Le test** consiste à rendre la participiale à un sujet explicite.

`, ensuring that teams can navigate the complexities of modern systems`
devient *This ensures that teams can navigate the complexities of modern
systems*. Personne ne peut vérifier cette phrase, et elle annonce le résultat
comme automatique. Elle saute.

Même construction chez Evans :

> Creating programs that can handle very complex tasks calls for separation of
> concerns, allowing concentration on different parts of the design in
> isolation.

Rendue à un sujet : *Separation of concerns lets you work on one part of the
design at a time*. Vrai, vérifiable, et c'est exactement ce que l'auteur veut
dire. La participiale ne fait que compacter.

La forme est donc innocente. Evans en écrit 0,37 pour mille avec le motif large
— `making`, `allowing`, `keeping` — et 0,06 seulement avec le motif retenu, qui
ne garde que les participes de bénéfice abstrait. Le seuil est à zéro sur ce
motif restreint. La construction devient un marqueur quand elle sert à conclure :
en fin de paragraphe, pour poser un bénéfice que rien n'établit.

---

## 6. Un texte complet

Le texte de contrôle `calibration/controle/caricature-en.md`, mesuré à
**11/17** par `calibration/calibre.py`, **10/17** par `scripts/analyse.py`, qui
déduplique les occurrences superposées sur une même ligne.

> **Avant**
>
> In today's fast-paced world of distributed systems, observability has emerged
> as a truly essential pillar of software engineering. It's not just about
> collecting logs — it's about building a profound understanding of how systems
> behave in production. Let's delve into what this really means.
>
> Observability rests on three fundamental pillars: logs, metrics, and traces.
> Each offers a unique lens, and it's precisely their combination that unlocks
> a comprehensive picture of what's happening at the heart of your
> infrastructure. In other words, no single pillar suffices on its own.
>
> Logs are the historical backbone of observability — they're simple,
> universal, and immediately actionable. That said, their volume can quickly
> become problematic, particularly in microservice architectures where each
> request traverses numerous services, making storage costs a pivotal
> consideration.
>
> Metrics, meanwhile, offer an aggregated, performant, and inexpensive view.
> They enable teams to detect anomalies, track trends, and trigger alerts.
> However, they don't explain the anomalies they surface — they merely signal
> them.
>
> Ultimately, observability isn't a tool, it's a discipline. It demands genuine
> investment, a robust engineering culture, and a continuous willingness to
> challenge established practices, ensuring that teams can navigate the
> complexities of modern systems. Only time will tell.

> **Après** (mesuré à 1/17)
>
> A distributed system rarely fails all at once. It rots in pieces. A few
> requests get slower, one queue backs up, and the dashboard stays green
> because the average hides the tail. That is the question observability has to
> answer, and no purchase order answers it.
>
> Three signals are usually available: logs, metrics, traces. Metrics say that
> latency doubled. Traces say where. Logs say what the code was doing at the
> time, assuming someone thought to log it.
>
> Logs are the oldest of the three and the easiest to produce. They are also
> the easiest to drown in. When one user request touches 12 services, volume
> grows with traffic and again with the number of hops, so retention stops
> being an engineering decision and becomes a budget one. We keep 7 days of
> logs, 30 days of traces, 13 months of metrics, and I picked those numbers by
> watching what people actually opened during postmortems, which was never
> anything older than a week except the metrics.
>
> Metrics are cheap to store and fast to query, which is why alerting is built
> on Prometheus and not on the log pipeline. They will not tell you why the
> payment service slowed down.
>
> Tracing will, when the instrumentation is there, and instrumenting an
> existing Java codebase with OpenTelemetry is where most of the work actually
> sits. So, the honest version. Observability is a practice before it is a
> product, and the practice is mostly instrumentation plus deciding which
> questions you want answered before the incident, not during it. I have never
> seen a team do the second part well. I include my own.

| Ce qui a changé | Mesure | Pourquoi |
|---|---|---|
| `In today's`, `Let's delve`, `Only time will tell` supprimés | ouvertures 15,46 → 0 | Trois formules d'ouverture ou de clôture toutes faites, seuil à zéro |
| 9 intensificateurs supprimés | 46,39 → 0 pour mille | Aucun ne modifie le sens de sa phrase |
| `cornerstone`, `backbone`, `at the heart of`, `navigate the`, `delve` supprimés | métaphores 20,62 → 0 | Images usées, aucune n'est choisie |
| `It's not just about X — it's about Y` et `isn't a tool, it's a discipline` réécrits | contrastes 5,15 → 0 | Personne n'avait posé X |
| Les 3 tirets cadratins supprimés | 15,46 → 0 pour mille | Tous en apposition explicative, aucun en rupture |
| 4 triades ramenées à zéro | 20,62 → 0 pour mille | `logs, metrics, traces` survit sans le `and` : c'est une liste, plus une cadence |
| `, making…` et `, ensuring…` supprimés | participiales 10,31 → 0 | Deux conséquences sans sujet, dont une invérifiable |
| `In other words`, `That said`, `However`, `Ultimately` supprimés | connecteurs 0,80 → 0 par paragraphe | Un plan récité ; les phrases s'enchaînent sans aide |
| Longueurs de paragraphes 43 / 44 / 37 / 32 / 38 → 46 / 32 / 88 / 34 / 70 mots | par_cv 0,14 → 0,26 | Un paragraphe long, deux courts |
| Écart-type des phrases 6,72 → 9,90 | seuil 7,33 | Longueurs étalées de 4-26 mots à 3-38 |
| `12 services`, `7 days`, `Prometheus`, `OpenTelemetry`, `Java` ajoutés | spécificité 0 → 25,93 pour mille | Passe 6 : sans faits, le texte reste creux même propre |
| `I have never seen a team do the second part well. I include my own.` ajouté | non mesuré | Une position tranchée et un aveu, que le script ne voit pas et que la lecture cherche |

Deux remarques, qui comptent plus que le tableau.

**Le score final n'est pas 0/17.** Il reste `par_cv` à 0,26 pour un seuil de
0,29. Sur 270 mots et cinq paragraphes, cette métrique ne veut pas dire
grand-chose, et couper un paragraphe en deux pour la satisfaire serait
travailler pour le chiffre. On la laisse, et on l'écrit dans le rapport.

**Les faits de la passe 6 ne s'inventent pas.** Les chiffres de rétention, les
douze services, le nom du langage : ici, ils illustrent la méthode, et dans une
vraie correction ils viendraient de l'utilisateur. Sans eux, `specifique_1k`
retombe à 3,97 pour mille et le texte reste creux sous une surface propre.
Livrer les passes 1 à 5 en le disant vaut mieux que combler avec du plausible.

---

## 7. Contre-exemple : la sur-correction

C'est le risque principal de la méthode, et il produit des textes exsangues
avec un excellent score.

### 7.1 La phrase amputée

> **Original.** Distributed tracing, finally, brings the dimension the other
> two were missing: causality.

Trois marqueurs formels : un connecteur (`finally`), des deux-points
rhétoriques, une phrase de longueur moyenne. Le correcteur zélé écrit :

> **Sur-corrigé.** Distributed tracing adds causality.

Quatre mots, zéro marqueur, et l'argument a disparu. `The dimension the other
two were missing` portait le raisonnement : le tracing complète ce que les logs
et les métriques laissent en suspens. Le supprimer supprime le lien.

> **Correctement corrigé.** Tracing fills in what logs and metrics leave out:
> which call caused which.

Le connecteur saute, les deux-points restent parce qu'ils annoncent réellement
quelque chose, l'argument survit.

### 7.2 Le hedging arraché

Le piège propre à l'anglais. Evans écrit :

> …it is usually a mistake to make the interface to the other system operate at
> such a low level.

Un correcteur qui traite `usually` comme du remplissage écrit :

> **Sur-corrigé.** It is a mistake to make the interface to the other system
> operate at such a low level.

La phrase est devenue fausse. La mesure le disait déjà, mais elle disait aussi
autre chose : `usually` compte, `may` et `could` non. Ces modaux-là, 268 et 177
occurrences chez Evans, ont été retirés du lexique parce qu'ils font le métier
de l'écriture technique, pas un tic. La médiane d'Evans est de 3,39 marques de
hedging pour mille mots une fois les modaux écartés, le seuil à 6,50 ; avec les
modaux elle était à 9,06, et la simple transposition du seuil français (10)
aurait signalé la moitié de ses échantillons. L'anglais technique nuance parce
que les exceptions existent, et c'est son métier. Le hedging devient un marqueur quand il porte sur tout, y compris
sur ce que l'auteur sait de première main. Pas quand il calibre une affirmation
qui souffre des exceptions.

### 7.3 La figure qu'on croyait interdite

> The design has to be robust enough to handle not only the scenarios presented
> in development, but also any scenario for which a user could configure the
> software in the future.

`not only… but also` a un seuil de zéro : toute occurrence est signalée. Ce
zéro vient du 9ᵉ décile d'échantillons de 800 mots, et il vaut zéro parce que
la figure est rare. Le motif strict que mesure le script n'apparaît que deux
fois chez Evans, et la famille entière (`not only… but`) neuf fois, soit 0,09
pour mille. Un seuil à zéro ne dit donc pas « interdit », il dit « une
occurrence dans un texte court se remarque, va voir ». Ici les deux termes
tiennent ensemble, la figure est additive, et il n'y a rien à corriger.

Trois occurrences de la même figure dans un texte de 600 mots, en revanche, et
aucune qui additionne : là il y a matière.

### Le test

Après chaque correction, se demander ce que le texte a perdu. Si la réponse est
« un tic », c'est bon. Si c'est « un tic et une idée », recommencer.

En anglais, une seconde question s'impose, parce que les lexiques sont
explicitement un brouillon : le mot a-t-il été supprimé parce qu'il figurait
sur une liste, ou parce qu'il gênait la lecture ? Un mot supprimé pour cause de
liste est une correction non motivée, et elle se voit à la relecture suivante.

Un texte tombé à 0/17 en perdant son argument est un échec mesuré comme une
réussite. C'est la seule manière de rater complètement cette méthode, et elle
est facile.
