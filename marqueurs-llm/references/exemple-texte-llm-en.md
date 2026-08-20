<!--
Texte-témoin anglais. Il concentre volontairement les marqueurs, pour servir de
test de non-régression : si une modification des lexiques, des seuils ou du
script fait baisser son score, c'est qu'un détecteur a cessé de mordre.

Score mesuré : 17/17 sur 561 mots, registre prose. Les dix-sept métriques de
lexiques/en.json sont hors cible. Reproduire depuis la racine du dépôt :

    python3 marqueurs-llm/scripts/analyse.py \
        marqueurs-llm/references/exemple-texte-llm-en.md --langue en

build-zip.sh vérifie ce score avant d'empaqueter, en même temps que le 9/13 du
témoin français. L'analyseur ignore ce commentaire HTML ; calibre.py, lui, le
traiterait comme de la prose, et ces quelques lignes de français suffiraient à
décaler la variation des longueurs de paragraphe.

Deux marges sont étroites et méritent surveillance : l'écart-type des longueurs
de phrase sort à 6,81 pour un seuil de 7,33, la longueur moyenne à 23,38 pour
21,32. Une réécriture même légère du corps peut les faire repasser du bon côté.
Points de comparaison : les textes de calibration/controle/ sortent à 10/17 et
12/17, la médiane des 119 échantillons d'Evans à 1/17.

Le sujet, la revue de code, est choisi pour ne recouper ni celui de
controle/caricature-en.md (observabilité) ni les exemples de bases de données
du catalogue.
-->

# Code Review: The Cornerstone of Healthy Engineering Teams

In today's fast-moving engineering organizations, code review has quietly become the single most powerful lever a team has at its disposal. It is not merely a gate that guards the main branch — it is the place where a team's collective understanding of its own software is continuously rebuilt. Reviewers who approach the practice thoughtfully tend to shape not only the code in front of them but also the habits of everyone who reads it later. At its core, review is a conversation about intent, and that conversation usually deserves far more care than it receives.

A healthy review culture rests on three essential habits that are easy to name and surprisingly hard to sustain in practice. Before typing a single word of feedback, the strongest reviewers read the change, the tests, and the surrounding code. They comment on what genuinely matters and leave the rest alone, allowing the team to build momentum instead of resentment. It is worth noting that this restraint is far more difficult than it sounds, particularly when a reviewer is tired, when the deadline is close, and when the change under discussion touches a part of the system that nobody on the team fully understands.

At the heart of every truly durable codebase there is a review process that people actually trust rather than merely tolerate. Trust is the backbone of the whole exercise, because a reviewer who is not trusted will simply be routed around. Teams often assume that stricter rules will unlock better outcomes, yet the evidence generally points in a rather different direction. What seems to matter is not simply the strictness of the policy but the quality of the attention behind it.

Junior engineers, in particular, may read a terse review comment as a verdict on their competence rather than a note about a few lines of code. This is arguably the most underestimated cost of a careless review culture, and it compounds quietly over months. The reviews that actually change behaviour are the ones that explain the reasoning, the tradeoff, and the alternative. A reviewer who writes three sentences of explanation will usually save the author an hour of confusion, and will often prevent the same mistake from appearing again in the next change and in the work of every engineer who later reads the thread.

However, none of this means that review should become an exercise in endless discussion — the cost of delay is significant and it lands on someone. In other words, the goal is not merely perfection but a shared floor of quality that the whole team can stand on. Reviews that drag on for days tend to be a symptom of an unclear standard, not a sign of unusually careful engineers. Therefore the most useful thing a team can do is write down what it actually cares about, reducing the number of arguments that have to be relitigated.

Ultimately, code review is not a process — it is a habit of mutual respect expressed in small, repeated acts of attention. Teams that treat it as paperwork will get paperwork, and teams that treat it as teaching will get engineers who teach. Whatever tooling a team adopts, the practice will still demand patience, humility, and candour. Only time will tell whether the industry learns to value that kind of attention, but the teams that already do are quietly pulling ahead.
