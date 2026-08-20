<!--
Texte-temoin : ecrit pour concentrer les marqueurs. Sert a verifier que
l'analyseur mord encore apres une modification du script (attendu :
9 metriques hors cible sur 13, registre prose).
-->

# L'observabilité : un pilier de l'ingénierie moderne

Dans un monde où les systèmes distribués deviennent la norme, l'observabilité s'impose comme une véritable pierre angulaire de l'ingénierie logicielle. Il ne s'agit pas simplement de collecter des logs — il s'agit de construire une compréhension profonde du comportement des systèmes en production.

L'observabilité repose sur trois piliers fondamentaux : les logs, les métriques et les traces. Chacun apporte un éclairage particulier, et c'est précisément leur combinaison qui permet de véritablement comprendre ce qui se passe au cœur de l'infrastructure. Autrement dit, aucun de ces piliers ne suffit isolément.

Les logs constituent la brique historique de l'observabilité — ils sont simples, universels et immédiatement exploitables. Toutefois, leur volume peut rapidement devenir problématique, particulièrement dans les architectures microservices où chaque requête traverse de nombreux services. Il convient de noter que le coût de stockage devient alors un levier d'arbitrage majeur.

Les métriques, quant à elles, offrent une vision agrégée, performante et peu coûteuse. Elles permettent de détecter les anomalies, de suivre les tendances et d'alerter les équipes. En revanche, elles ne permettent pas d'expliquer une anomalie — elles la signalent seulement.

Le tracing distribué, enfin, apporte la dimension qui manquait : la causalité. En suivant une requête à travers l'ensemble des services, il devient possible d'identifier précisément le maillon défaillant. Ce n'est pas un luxe, c'est une nécessité dans les architectures modernes.

En somme, l'observabilité n'est pas un outil, c'est une discipline. Elle demande des investissements réels, une culture d'équipe adaptée et une remise en cause permanente des pratiques établies. À l'heure où les systèmes gagnent en complexité, les organisations qui sauront investir dans cette discipline disposeront indéniablement d'un avantage considérable. L'avenir nous le dira.
