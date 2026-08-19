# Réécritures commentées

Le catalogue dit quoi corriger. Ce fichier montre jusqu'où, et surtout où
s'arrêter. Chaque exemple isole un geste ; le dernier les combine.

---

## 1. Le contraste correctif [X]

> **Avant.** Il ne s'agit pas simplement de collecter des logs, mais de
> construire une compréhension du comportement des systèmes en production.

La phrase nie une position que personne n'a défendue. Personne n'a écrit que
l'observabilité se réduisait aux logs. La négation sert à donner du relief au
second terme, gratuitement.

> **Après.** Collecter des logs ne suffit pas à comprendre ce que fait un
> système en production.

Le sens est identique, la posture a disparu. Noter que la négation reste : elle
porte maintenant sur une affirmation réelle (« les logs suffisent »), qui est
bien ce que le texte veut contredire.

**Cas où la figure se garde :**

> Les partisans du monolithe soutiennent que la latence réseau annule les gains
> de découplage. Ce n'est pas la latence qui coûte, c'est le nombre d'allers-retours.

Ici X a été explicitement posé, par quelqu'un, deux phrases plus haut. La
correction serait une perte.

---

## 2. Le tiret cadratin en incise [T1]

> **Avant.** Les logs constituent la brique historique de l'observabilité — ils
> sont simples, universels et immédiatement exploitables.

Le tiret annonce une explication. Deux-points ou point font le même travail sans
la signature.

> **Après 1 (deux-points).** Les logs sont la brique historique de
> l'observabilité : simples, universels, immédiatement exploitables.

> **Après 2 (coupure).** Les logs sont la brique historique de l'observabilité.
> Simples, universels, exploitables sans outillage.

La version 2 est meilleure ici, parce qu'elle produit une phrase courte après une
phrase moyenne — elle règle T1 et R3 d'un même geste. Choisir la ponctuation en
fonction du lien logique réel : parenthèse pour l'aparté, deux-points pour
l'annonce, phrase autonome pour ce qui mérite d'être posé.

---

## 3. Intensificateurs et triade [I] [Y]

> **Avant.** L'observabilité repose sur trois piliers fondamentaux : les logs,
> les métriques et les traces. Chacun apporte un éclairage particulier, et c'est
> précisément leur combinaison qui permet de véritablement comprendre ce qui se
> passe au cœur de l'infrastructure.

Cinq marqueurs en deux phrases : `fondamentaux`, `particulier`, `c'est
précisément`, `véritablement`, `au cœur de`. Plus une triade.

> **Après.** L'observabilité repose sur les logs, les métriques et les traces.
> Aucun des trois ne se suffit : les métriques signalent l'anomalie, les traces
> disent où elle naît, les logs disent quoi.

Ici la triade se garde — il y a réellement trois piliers, et la seconde phrase
leur donne à chacun un rôle distinct au lieu de les additionner. La triade
fautive est celle dont le troisième terme est décoratif.

---

## 4. Le rythme [R3]

> **Avant.** (longueurs : 18, 21, 19, 17, 22 mots)
> Les métriques offrent une vision agrégée et peu coûteuse du système. Elles
> permettent de détecter les anomalies et de suivre les tendances dans le temps.
> Elles alimentent également les alertes qui préviennent les équipes d'astreinte.
> En revanche, elles n'expliquent pas les anomalies qu'elles signalent aux
> opérateurs. Le tracing distribué apporte alors la dimension causale qui manquait
> à l'ensemble.

Le contenu est correct. C'est le métronome qui trahit : cinq phrases entre 17 et
22 mots.

> **Après.** (longueurs : 12, 4, 26, 7)
> Les métriques donnent une vision agrégée pour un coût dérisoire. C'est leur
> intérêt. Elles détectent une anomalie, suivent une tendance, déclenchent
> l'astreinte à trois heures du matin, mais elles ne diront jamais pourquoi la
> latence du service de paiement a triplé. Le tracing, lui, le dit.

Même information, quatre phrases au lieu de cinq, écart de 4 à 26 mots. La
phrase de quatre mots (« C'est leur intérêt. ») ne porte presque rien : c'est
sa fonction. Elle casse le rythme et laisse respirer.

Vérifier avec le profil de rythme du script : les nombres doivent sauter.

---

## 5. Un paragraphe complet

> **Avant** (score 9/13 sur l'extrait)
>
> Dans un monde où les systèmes distribués deviennent la norme, l'observabilité
> s'impose comme une véritable pierre angulaire de l'ingénierie logicielle. Il ne
> s'agit pas simplement de collecter des logs — il s'agit de construire une
> compréhension profonde du comportement des systèmes en production. En somme,
> l'observabilité n'est pas un outil, c'est une discipline. Elle demande des
> investissements réels, une culture d'équipe adaptée et une remise en cause
> permanente des pratiques établies.

> **Après**
>
> Un système distribué tombe rarement d'un bloc. Il se dégrade par morceaux, et
> c'est ce qui rend le diagnostic pénible : les logs racontent ce qui s'est passé
> quelque part, jamais pourquoi la latence a doublé partout. L'observabilité est
> le travail qui consiste à rendre cette question répondable. Un travail
> d'ingénierie, pas un achat d'outil — la plupart des équipes que j'ai vues
> échouer avaient acheté Datadog avant d'avoir décidé ce qu'elles voulaient
> mesurer.

| Ce qui a changé | Pourquoi |
|---|---|
| « Dans un monde où » supprimé | Ouverture générique, remplacée par une affirmation qui engage |
| `véritable`, `profonde`, `réels` supprimés | Aucun ne modifie le sens |
| `pierre angulaire` supprimé | Métaphore usée |
| « ne… pas X, mais Y » (×2) → affirmations | Personne n'avait posé X |
| « En somme » supprimé | Le paragraphe ne se résume pas lui-même |
| Triade « investissements, culture, remise en cause » supprimée | Trois abstractions valent moins qu'un cas |
| Longueurs 24, 26, 12, 21 → 8, 27, 12, 33 | Variance injectée |
| Un tiret cadratin conservé | Un seul, sur 4 phrases : sous quota, et il marque une vraie rupture |
| « Datadog », « les équipes que j'ai vues » ajoutés | Passe 6 : un nom d'outil, une expérience située |

Le tiret conservé est le point important de cet exemple. La correction ne
consiste pas à éradiquer un signe, mais à ramener sa fréquence à ce qu'un auteur
ferait spontanément.

L'ajout de la passe 6 (« les équipes que j'ai vues échouer ») suppose que
l'utilisateur ait fourni ce fait. Sans lui, la dernière phrase s'arrête après
« pas un achat d'outil », et le rapport de correction signale que le paragraphe
reste sans ancrage concret.

---

## 6. Contre-exemple : la sur-correction

Le risque de la méthode est de produire des textes exsangues.

> **Original.** Le tracing distribué, enfin, apporte la dimension qui manquait :
> la causalité.

Trois marqueurs formels : un connecteur (« enfin »), des deux-points
rhétoriques, une phrase de longueur moyenne. Un correcteur zélé écrit :

> **Sur-corrigé.** Le tracing distribué apporte la causalité.

Sept mots, zéro marqueur, et la phrase ne dit plus rien. « La dimension qui
manquait » portait l'argument : le tracing complète ce que logs et métriques
laissent en suspens. Le supprimer, c'est supprimer le raisonnement.

> **Correctement corrigé.** Le tracing distribué comble ce qui manquait aux deux
> autres : la causalité.

Le connecteur saute, les deux-points restent parce qu'ils annoncent réellement,
l'argument est préservé.

**Le test.** Après chaque correction, se demander ce que le texte a perdu. Si la
réponse est « un tic », c'est bon. Si c'est « un tic et une idée », recommencer.
