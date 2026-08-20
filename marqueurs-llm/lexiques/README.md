# Fichiers de langue

`scripts/analyse.py` ne connaît aucune langue. Il charge `<code>.json` dans ce
répertoire et n'y cherche que ce que le fichier déclare. Ajouter une langue,
c'est déposer un fichier ici : aucune ligne de Python à toucher.

Le nom du fichier donne le code de langue (`fr.json` → `fr`). `--langue auto`
compare tous les fichiers présents ; `--langue fr` en force un.

## Ce que le moteur fournit, ce que la langue fournit

Le moteur garde ce qui ne dépend pas de la langue : le découpage du Markdown,
la typographie (tirets cadratins, gras, emoji, titres binaires), le rythme des
phrases, la déduplication des occurrences, le rendu du rapport. Les libellés du
rapport sont en français quelle que soit la langue analysée : le rapport
s'adresse à l'utilisateur, pas au texte.

La langue fournit ses lexiques, ses motifs, ses seuils, et **la liste des
métriques qu'elle accepte de scorer**.

## Champs

| Champ | Obligatoire | Rôle |
|---|---|---|
| `langue`, `nom` | oui | code et nom affiché |
| `statut` | non | d'où viennent les seuils, en une phrase |
| `detection.mots_outils` | oui | mots les plus fréquents et les moins traduisibles (`the/of/and` contre `le/de/et`). Sert à `--langue auto`. Éviter ceux qui existent dans les deux langues |
| `metriques` | oui | les métriques scorées, parmi les dix-sept que le moteur sait calculer |
| `seuils.base` | oui | `{"metrique": {"sens": ">", "seuil": 21.32}}`. `sens` vaut `>` (suspect au-dessus) ou `<` (suspect en dessous). Le bloc `seuils` de `calibration/seuils-en.json` s'y colle tel quel |
| `seuils.registres` | non | surcharges par genre : `{"technique": {"phrase_moyenne": 22.0}}`. Une valeur nue, le `sens` vient de la base. Un registre absent n'est pas une erreur : le rapport signale que rien n'a été ajusté |
| `accents_tolerants` | non | `true` : les termes du lexique s'écrivent sans accent et matchent les formes accentuées (français). `false` par défaut |
| `lexiques.*` | non | `intensificateurs`, `connecteurs`, `connecteurs_forts`, `hedging`, `metaphores`, `ouvertures` (listes), `faux_amis` (terme → correction proposée) |
| `motifs.*` | non | expressions régulières brutes, cf. ci-dessous |
| `mots_capitalises_courants` | non | les capitales à ne pas compter comme noms propres |
| `abreviations` | non | les points qui ne terminent pas une phrase |
| `libelles_marqueurs` | non | renomme un marqueur dont l'intitulé est propre à la langue |
| `marqueurs_desactives` | non | tait un marqueur hors sujet. Le guillemet droit (`T4`) est une faute en français, la norme en anglais |

Les `connecteurs` ne comptent qu'en tête de phrase ; les `connecteurs_forts`
comptent partout. Un « ainsi » au milieu d'une phrase est du français, pas un
tic.

## Motifs

- `contraste` : liste. Chaque entrée est une regex, ou
  `{"motif": "...", "detail": "..."}` quand l'occurrence mérite d'être nommée
  autrement que par le texte capturé.
- `not_only`, `participiale_finale` : une regex chacun.
- `coordination` (`(?:et|ou)`), `triade_determinant`, `triade_mots_vides`,
  `triade_conjonctions_exclues` : le moteur en construit les deux formes de
  triade, nominale et adjectivale.
- `triade_espace_apres_determinant` : `false` si le déterminant absorbe déjà
  son séparateur (`l'` en français), `true` sinon (défaut).
- `triade_virgule_serie` : `true` pour accepter la virgule d'Oxford (défaut).

## La règle qui compte

**Ne déclarer dans `metriques` que ce que la langue sait vraiment chercher.**
Une métrique dont le motif est absent vaut zéro, et zéro se lit comme un
compliment. C'est le bug que ce découpage corrige : un texte anglais passé aux
lexiques français ressortait à 4/13, non parce qu'il était propre, mais parce
que le moteur ne cherchait rien.

Les dix-sept métriques disponibles : `phrase_moyenne`, `phrase_ecart_type`,
`cv`, `pct_long`, `pct_court`, `tirets_1k`, `intensificateurs_1k`,
`contrastes_1k`, `not_only_1k`, `connecteurs_par`, `triades_1k`, `hedging_1k`,
`metaphores_1k`, `ouvertures_1k`, `participiales_1k`, `specifique_1k`,
`par_cv`. C'est le vocabulaire de `calibration/calibre.py`, pour qu'un fichier
de seuils dérivé là-bas soit réutilisable ici sans traduction.

## État

- `fr.json` — 13 métriques. Seuils issus d'un jugement exercé, pas d'une mesure.
  `lexiques.clotures_bilan` est conservé du code d'origine mais n'est branché
  sur aucun marqueur.
- `en.json` — 17 métriques, seuils mesurés sur le corpus Evans
  (`calibration/README.md`), lexiques triés terme à terme contre ce même corpus.
  Désactive `T2` (le tiret collé est l'usage anglais), `T4` (le guillemet droit
  est la norme) et `A` (« anglicisme » ne veut rien dire dans un texte anglais).
  Un seul registre, `prose`, qui est celui du corpus : la prose technique de
  livre.

Le champ `_surveillance` de `en.json` n'est lu par aucun script. Il conserve les
termes et motifs mesurés puis écartés — trop fréquents chez l'auteur humain pour
être signalés seuls — avec leur fréquence, ainsi que les motifs plus étroits
qu'aucun champ du schéma ne sait encore charger. C'est la matière de la
prochaine calibration, pas du bruit à supprimer.
