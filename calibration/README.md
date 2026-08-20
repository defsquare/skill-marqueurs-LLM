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
python3 calibre.py --lexiques lexiques-en.json \
                   --corpus ../corpus/evans-ddd-2003.txt \
                   --sortie seuils-en.json \
                   --controle controle/caricature-en.md controle/traduction-du-fr.md
```

## Le résultat

| Métrique | Médiane humaine | Seuil | Sens |
|---|---|---|---|
| Longueur moyenne des phrases | 18,42 | 21,32 | suspect au-dessus |
| Écart-type des longueurs | 8,58 | 7,33 | suspect en dessous |
| Coefficient de variation | 0,47 | 0,40 | suspect en dessous |
| Part de phrases > 40 mots | 2,08 % | 4,88 % | suspect au-dessus |
| Part de phrases < 10 mots | 13,04 % | 6,52 % | suspect en dessous |
| Tirets cadratins / 1000 | 1,14 | 2,48 | suspect au-dessus |
| Intensificateurs / 1000 | 2,45 | 6,02 | suspect au-dessus |
| Contrastes / 1000 | 0,00 | 1,25 | suspect au-dessus |
| `not only… but also` / 1000 | 0,00 | 0,00 | toute occurrence |
| Connecteurs / paragraphe | 0,07 | 0,18 | suspect au-dessus |
| Triades / 1000 | 0,00 | 2,32 | suspect au-dessus |
| Hedging / 1000 | 8,71 | 14,96 | suspect au-dessus |
| Métaphores / 1000 | 0,00 | 1,12 | suspect au-dessus |
| Ouvertures toutes faites / 1000 | 0,00 | 0,00 | toute occurrence |
| Participiales finales / 1000 | 0,00 | 1,22 | suspect au-dessus |
| Noms propres + chiffres / 1000 | 35,24 | 11,22 | suspect en dessous |
| Variation des paragraphes | 0,44 | 0,29 | suspect en dessous |

**Validation** : sur les 119 échantillons d'Evans, score médian **1/17**, pire
échantillon 6/17, 0,8 % au-delà de 6. Le plancher ne crie pas au loup.

| Texte de contrôle | Score |
|---|---|
| Evans, médiane | 1/17 |
| Caricature écrite en anglais | 11/17 |
| Traduction d'un texte LLM français | 12/17 |

## Ce que la mesure a corrigé

Trois transpositions du français se sont révélées fausses.

**Le tiret cadratin.** On attendait un seuil bien plus permissif en anglais.
Evans est à 1,14 pour mille mots en médiane et 2,48 au 9ᵉ décile, soit la valeur
française. Le tiret reste discriminant.

**Les connecteurs de transition.** Le seuil français est de 0,8 par paragraphe.
L'anglais tient à 0,18, quatre fois plus sévère : Evans écrit dix-neuf
« however » et un seul « moreover » en cent mille mots.

**Le hedging.** Sens inverse. Le seuil français de 10 pour mille mots
signalerait la moitié des échantillons d'Evans, qui est à 8,71 en médiane.
L'écriture technique nuance, c'est son métier.

## Limites

**Un seul auteur, un seul registre, une seule époque.** Les seuils collent à la
prose technique de livre. Un billet de blog ou un post en anglais tolère plus de
tirets et de phrases courtes. Les registres `blog` et `marketing` restent à
calibrer sur d'autres corpus.

**La classe positive ne vaut rien.** Les huit textes de
`corpus/llm-synthetique.txt` ont été écrits après une longue conversation sur
ces marqueurs. Ils sortent à 1/17, le score d'Evans. C'est de la contamination,
pas une réussite. Pour une vraie classe positive il faut du texte produit sans
aucune connaissance de ces critères.

Cela ne bloque pas la calibration, puisque les seuils viennent du corpus humain.
Cela empêche seulement de classer les marqueurs par pouvoir discriminant.

**Les lexiques sont un brouillon.** `lexiques-en.json` est une première liste.
Un terme fréquent chez Evans n'est pas un marqueur, et le tri reste à faire
terme par terme.
