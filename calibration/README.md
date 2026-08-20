# Calibration des seuils

Les seuils français de la skill viennent d'un jugement exercé. Ceux de
l'anglais sont mesurés. Ce répertoire contient la méthode, les outils et le
résultat, pour que les chiffres soient contestables plutôt qu'à croire.

## Le principe

Un seuil marque la frontière du légitime. Il se dérive donc du **corpus
humain**, pas des textes générés : un texte généré peut être propre, un texte
humain ne doit pas être accusé. La classe positive ne sert qu'à vérifier que
la séparation existe.

Concrètement, le corpus humain est découpé en échantillons de 800 mots, chaque
métrique est mesurée sur chacun, et la frontière est placée au 9ᵉ décile pour
les métriques où un excès est suspect, au 1ᵉʳ décile pour celles où c'est un
défaut. Par construction, 10 % des échantillons humains déclenchent sur chaque
métrique prise isolément, ce qui laisse un score global bas.

## Le corpus

**Classe humaine** : Eric Evans, *Domain-Driven Design*, Addison-Wesley, 2003.
99 965 mots de prose narrative, 119 échantillons. Antérieur de dix-neuf ans aux
LLM grand public, donc humain sans discussion possible, et dans le registre
technique visé.

Le livre n'est pas versionné. `extrait-pdf.py` régénère `corpus/` à partir du
PDF ; le répertoire est dans `.gitignore`.

```bash
python3 extrait-pdf.py livre.pdf ../corpus/evans-ddd-2003.txt
```

L'extraction écarte les en-têtes courants, le code Java, les légendes et les
paragraphes de moins de trente mots. Elle normalise aussi les petites capitales
du livre : Evans compose les noms de patterns en `ENTITY`, `VALUE OBJECT`, que
`pdftotext` rend en majuscules. Les laisser passer pour des acronymes gonflerait
la densité de noms propres, qui est précisément une des métriques à calibrer.

**Classe positive** : `corpus/llm-synthetique.txt`, huit textes générés. Elle ne
vaut rien et le dossier le dit franchement — voir *Limites*.

## Lancer la calibration

```bash
python3 calibre.py --lexiques ../marqueurs-llm/lexiques/en.json \
                   --corpus ../corpus/evans-ddd-2003.txt \
                   --sortie seuils-en.json \
                   --controle controle/caricature-en.md controle/traduction-du-fr.md
```

Les lexiques lus sont ceux de la skill, `marqueurs-llm/lexiques/en.json`, et le
bloc `seuils` produit se recolle dans ce même fichier. `lexiques-en.json` reste
ici comme trace du brouillon d'origine ; il n'alimente plus rien.

### Les deux outils mesurent la même chose

`calibre.py` dérive un seuil, `scripts/analyse.py` s'en sert. Si les deux ne
comptent pas de la même façon, le seuil dit une chose et l'outil en mesure une
autre — et personne ne s'en aperçoit, puisque les deux chiffres ont le même nom.
Trois divergences ont été corrigées dans `calibre.py` au moment d'intégrer les
lexiques triés :

- **les connecteurs** étaient comptés sous leur forme nue, n'importe où dans la
  phrase. `analyse.py` ne compte les connecteurs ordinaires qu'en tête de phrase,
  et les `connecteurs_forts` partout. `calibre.py` applique désormais la même
  règle. Un « in addition to » au milieu d'une phrase n'est pas une transition ;
- **les triades** ignoraient `triade_conjonctions_exclues`,
  `triade_espace_apres_determinant` et `triade_virgule_serie`, que le fichier de
  langue déclare et que `analyse.py` honore ;
- une entrée de `contraste` pouvait être une chaîne, pas un objet
  `{"motif": …, "detail": …}`. Les deux formes sont maintenant acceptées des
  deux côtés.

Il reste deux différences assumées. `analyse.py` déduplique les occurrences qui
se chevauchent sur une même ligne, pas `calibre.py` : sur les textes de contrôle
l'écart est d'un point (caricature, 11/17 mesuré ici, 10/17 par l'analyseur). Et
`calibre.py` exige les dix-sept métriques, là où un fichier de langue a le droit
de n'en déclarer que treize — `fr.json` n'est donc pas calibrable par cet outil,
ce qui est cohérent avec l'origine de ses seuils.

## Le résultat

Mesures du 20 août 2026, lexiques triés terme à terme contre le corpus.

| Métrique | Médiane humaine | Seuil | Sens |
|---|---|---|---|
| Longueur moyenne des phrases | 18,42 | 21,32 | suspect au-dessus |
| Écart-type des longueurs | 8,58 | 7,33 | suspect en dessous |
| Coefficient de variation | 0,47 | 0,40 | suspect en dessous |
| Part de phrases > 40 mots | 2,08 % | 4,88 % | suspect au-dessus |
| Part de phrases < 10 mots | 13,04 % | 6,52 % | suspect en dessous |
| Tirets cadratins / 1000 | 1,14 | 2,48 | suspect au-dessus |
| Intensificateurs / 1000 | 1,23 | 4,84 | suspect au-dessus |
| Contrastes / 1000 | 0,00 | 0,00 | toute occurrence |
| `not only… but also` / 1000 | 0,00 | 0,00 | toute occurrence |
| Connecteurs / paragraphe | 0,00 | 0,10 | suspect au-dessus |
| Triades / 1000 | 0,00 | 1,24 | suspect au-dessus |
| Hedging / 1000 | 3,39 | 6,50 | suspect au-dessus |
| Métaphores / 1000 | 0,00 | 0,00 | toute occurrence |
| Ouvertures toutes faites / 1000 | 0,00 | 0,00 | toute occurrence |
| Participiales finales / 1000 | 0,00 | 0,00 | toute occurrence |
| Noms propres + chiffres / 1000 | 35,24 | 11,22 | suspect en dessous |
| Variation des paragraphes | 0,44 | 0,29 | suspect en dessous |

**Validation** : sur les 119 échantillons d'Evans, score médian **1/17**, moyen
1,19, pire échantillon 5/17, aucun au-delà de 5. Métrique par métrique, la part
d'échantillons humains qui déclenchent va de 0 % (ouvertures) à 10,1 %
(hedging) : le budget de 10 % que la méthode s'accorde est tenu partout.

Le tri des lexiques a resserré tous les seuils qui dépendent d'une liste de
mots, sans toucher aux seuils de rythme, qui n'en dépendent pas. Cinq métriques
sont maintenant à zéro : sur un échantillon de 800 mots, une seule occurrence
suffit à les faire basculer. C'est voulu — un « In today's fast-moving world »
n'a pas besoin d'être répété pour poser une question à l'auteur.

| Texte de contrôle | Score |
|---|---|
| Evans, médiane des 119 échantillons | 1/17 |
| Caricature écrite en anglais | 11/17 |
| Traduction d'un texte LLM français | 12/17 |
| Texte-témoin `references/exemple-texte-llm-en.md` | 17/17 |

## Ce que la mesure a corrigé

Six intuitions se sont révélées fausses. Trois portaient sur des transpositions
du français, trois sur le tri des lexiques lui-même.

**Le tiret cadratin.** On attendait un seuil bien plus permissif en anglais.
Evans est à 1,14 pour mille mots en médiane et 2,48 au 9ᵉ décile, soit la valeur
française. Le tiret reste discriminant. Ce qui diffère est la forme, pas la
densité : chez Evans le tiret est collé aux mots et vient seul en fin de phrase,
là où le modèle préfère la paire encadrante.

**Les connecteurs de transition.** Le seuil français est de 0,8 par paragraphe.
L'anglais tient à 0,10, huit fois plus sévère : 95 des échantillons d'Evans sur
119 n'ont aucun connecteur en tête de phrase. Le seuil précédent, 0,18, avait
deux défauts cumulés — il comptait la forme nue n'importe où dans la phrase, et
sa liste contenait « on the other hand », qu'Evans emploie vingt fois, dont
dix-neuf en tête de phrase. C'est son connecteur, pas celui d'un modèle.

**Le hedging.** La conclusion de la première calibration disait que l'écriture
technique nuance et qu'il fallait un seuil haut. Elle mesurait autre chose : les
modaux. « may », « could » et « might » à eux seuls faisaient 5,54 des 9,06
occurrences pour mille mots de la médiane. Une fois ces trois mots retirés — ils
sont le métier de la prose technique, pas un tic — la métrique mesure enfin le
style atténuatif : médiane 3,39, seuil 6,50. Le chiffre a baissé de moitié parce
qu'il a changé de sens, pas parce qu'Evans a changé.

**Les faux positifs n'étaient pas les mots suspects.** L'intuition accusait
« essential », « critical », « fundamental », « significant ». La mesure les
innocente : tous sous 0,4 pour mille mots chez Evans. Les vrais coupables
étaient des homographes techniques — « key » (foreign key, primary key), « core »
(1,74 pour mille : c'est un nom de pattern chez Evans), « true » (l'adjectif de
vérité, jamais l'emphase). Trois mots retirés de la liste nue, remplacés par des
motifs étroits.

**Ajouter des mots absents du corpus ne coûte rien.** Trente-cinq termes
supplémentaires (« groundbreaking », « unparalleled », « best-in-class »…) n'ont
déplacé la médiane que de 2,46 à 2,35, parce qu'ils valent zéro chez Evans. La
couverture augmente, le seuil ne bouge pas. C'est l'argument entier de la
calibration sur la classe humaine, et il vaut d'être répété : le coût d'un terme
se mesure sur le texte légitime, pas sur le texte suspect.

**Le point-virgule correctif est la signature d'Evans.** « A domain model is not
a particular diagram; it is the idea that the diagram is intended to convey. »
Onze occurrences. Le motif de contraste avait été écrit pour la virgule ; en le
« réparant » pour qu'il accepte aussi le point-virgule, on aurait fait d'Eric
Evans le pire élève de la classe. Le motif retenu interdit la virgule et les
conjonctions dans le membre nié : il passe de 44 correspondances à 1 sur Evans,
sans perdre un seul contrôle positif. Les 44 précédentes ne détectaient pas la
figure LLM, elles détectaient la coordination anglaise ordinaire.

Deux autres résultats méritent d'être notés, faute de tenir dans une intuition
préalable. La participiale finale n'est pas un motif syntaxique mais **un motif
lexical déguisé** : sur 80 participes testés, 56 n'apparaissent jamais après une
virgule en cent mille mots (« enabling », « ensuring », « empowering »,
« streamlining »), alors qu'Evans écrit onze « making » et neuf « allowing ».
C'est le vocabulaire du bénéfice abstrait qui trahit, pas la construction. Et la
triade sans virgule d'Oxford a été **rejetée après mesure** : ses trois
correspondances chez Evans sont trois faux positifs, tous des appositions
(« two categories, commands and queries »). Aucune regex ne sépare l'apposition
de l'énumération sans étiquetage morphosyntaxique.

## Limites

**Un seul auteur, un seul registre, une seule époque.** Les seuils collent à la
prose technique de livre. Un billet de blog ou un post en anglais tolère plus de
tirets et de phrases courtes. Les registres `blog` et `marketing` restent à
calibrer sur d'autres corpus.

**La classe positive ne vaut rien.** Les huit textes de
`corpus/llm-synthetique.txt` ont été écrits après une longue conversation sur
ces marqueurs. Ils sortaient à 1/17 avec les lexiques d'origine, le score
d'Evans ; ils sortent à 5/17 avec les lexiques triés, sur 2 559 mots d'un seul
tenant. La progression ne prouve rien : c'est de la contamination mesurée avec
un instrument plus fin, pas une réussite. Pour une vraie classe positive il faut
du texte produit sans aucune connaissance de ces critères.

Cela ne bloque pas la calibration, puisque les seuils viennent du corpus humain.
Cela empêche seulement de classer les marqueurs par pouvoir discriminant.

**Les seuils valent pour 800 mots, pas pour un livre.** Cinq métriques sont à
zéro : elles signalent toute occurrence dans un échantillon de 800 mots.
Appliquées telles quelles aux cent mille mots d'Evans d'un seul tenant, elles
sortent toutes les cinq, et le livre entier note 4/17. Ce n'est pas un défaut du
seuil, c'est un défaut d'usage : analyser un texte long, c'est analyser ses
sections.

**Le tri des lexiques laisse deux dettes.** Douze termes de verdict
« surveiller » — trop présents chez Evans pour être signalés seuls, trop typés
pour être écartés — attendent dans le champ `_surveillance` de
`marqueurs-llm/lexiques/en.json`, avec leur fréquence mesurée. Le fichier y
garde aussi une trentaine de motifs plus étroits (« plays a crucial role »,
« cannot be overstated », « the ever-changing landscape ») écrits pour remplacer
des mots nus trop fréquents. Ils ne sont branchés sur rien : le format de langue
n'accepte une regex que dans `contraste`, `not_only` et `participiale_finale`.
Les brancher demande d'étendre le schéma des deux côtés à la fois, sinon le
seuil et la mesure divergent.

**Un mot ne compte que dans un lexique.** Six recouvrements ont été tranchés à
l'assemblage (« notably » et « crucially » vers les connecteurs, « myriad » et
« plethora » vers les métaphores, « transformative » vers les intensificateurs,
« by and large » vers les connecteurs forts). Sans cet arbitrage, un même mot
gonflait deux métriques à la fois et le score comptait deux fois la même faute.
Toute extension d'un lexique doit refaire cette vérification.
