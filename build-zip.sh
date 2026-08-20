#!/usr/bin/env bash
#
# Construit l'archive de la skill marqueurs-llm pour Claude Desktop.
#
# Claude Desktop attend un .zip contenant un unique repertoire au nom de la
# skill, avec SKILL.md a sa racine. Le script valide le frontmatter et fait
# tourner l'analyseur avant d'empaqueter : une archive qui part avec un script
# casse ne se decouvre qu'apres l'import, quand il est trop tard pour comprendre
# ce qui a change.
#
# Sortie : dist/marqueurs-llm-<version>.zip

set -euo pipefail

SKILL_NAME="marqueurs-llm"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/$SKILL_NAME"
DIST="$ROOT/dist"

CLEAN=0
RUN_TESTS=1

if [ -t 1 ]; then
  BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; OFF=$'\033[0m'
else
  BOLD=""; RED=""; GREEN=""; YELLOW=""; OFF=""
fi

usage() {
  cat <<EOF
${BOLD}build-zip.sh${OFF} — construit l'archive de la skill $SKILL_NAME

  Sortie : dist/$SKILL_NAME-<version>.zip
  L'archive s'importe dans Claude Desktop via Réglages > Capacités > Compétences.

Options
  --clean       vide dist/ avant de construire
  --skip-tests  n'exécute pas l'analyseur avant d'empaqueter
  -h, --help    affiche cette aide
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --clean)      CLEAN=1 ;;
    --skip-tests) RUN_TESTS=0 ;;
    -h|--help)    usage; exit 0 ;;
    *) printf '%sOption inconnue : %s%s\n\n' "$RED" "$1" "$OFF" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

die() { printf '%serreur :%s %s\n' "$RED" "$OFF" "$1" >&2; exit 1; }
ok()  { printf '%s✓%s %s\n' "$GREEN" "$OFF" "$1"; }

# --- la source est-elle complète ? ---------------------------------------
[ -d "$SRC" ] || die "skill introuvable : $SRC"
[ -f "$SRC/SKILL.md" ] || die "$SRC ne contient pas de SKILL.md"
command -v zip >/dev/null 2>&1 || die "la commande zip est absente"

# --- frontmatter ----------------------------------------------------------
# Un nom qui ne correspond pas au répertoire, ou une description trop longue,
# se traduisent par un import refusé sans explication utilisable.
read_field() {
  awk -v key="$1" '
    NR == 1 && $0 == "---" { inside = 1; next }
    inside && $0 == "---"  { exit }
    inside && index($0, key ":") == 1 {
      sub("^" key ": *", ""); print; exit
    }
  ' "$SRC/SKILL.md"
}

NAME="$(read_field name)"
DESCRIPTION="$(read_field description)"
VERSION="$(read_field version)"

[ -n "$NAME" ] || die "SKILL.md n'a pas de champ 'name' dans son frontmatter"
[ -n "$DESCRIPTION" ] || die "SKILL.md n'a pas de champ 'description' dans son frontmatter"

if [ "$NAME" != "$SKILL_NAME" ]; then
  die "le champ name ($NAME) ne correspond pas au répertoire ($SKILL_NAME)"
fi

DESC_LEN=${#DESCRIPTION}
if [ "$DESC_LEN" -gt 1024 ]; then
  die "description de $DESC_LEN caractères, au-delà de la limite de 1024"
fi
ok "frontmatter valide (description : $DESC_LEN caractères sur 1024)"

if [ -z "$VERSION" ]; then
  VERSION="0"
  printf '%s!%s pas de champ version dans SKILL.md, archive nommée sans version.\n' \
    "$YELLOW" "$OFF"
  ARCHIVE="$SKILL_NAME.zip"
else
  ARCHIVE="$SKILL_NAME-$VERSION.zip"
fi

# --- l'analyseur fonctionne-t-il, dans les deux langues ? -----------------
# Un témoin par langue. Le score attendu est celui qui a été mesuré : s'il
# baisse, un détecteur a cessé de mordre ; s'il monte, un détecteur mord
# quelque chose qu'il ignorait. Les deux méritent un coup d'œil avant publication.
#
# La langue est forcée plutôt que détectée : un témoin mal classé donnerait un
# score flatteur, et le test passerait pour la mauvaise raison.
temoin() {           # temoin <code> <fixture> <score attendu> <total attendu>
  local code="$1" fixture="$2" attendu="$3" total="$4" ligne
  [ -f "$fixture" ] || die "texte-témoin absent : $fixture"
  # Sans le || true, pipefail ferait sortir le script en silence quand
  # l analyseur plante, et le die ci-dessous ne serait jamais atteint.
  ligne="$(python3 "$SRC/scripts/analyse.py" "$fixture" --langue "$code" 2>/dev/null \
           | sed -n 's/^SCORE : \([0-9]*\) metriques hors cible sur \([0-9]*\).*/\1\/\2/p' \
           || true)"
  [ -n "$ligne" ] || die "analyse.py ne répond pas sur le témoin $code. Archive non construite."
  if [ "$ligne" != "$attendu/$total" ]; then
    die "le témoin $code donne $ligne au lieu de $attendu/$total. Les seuils ou les lexiques ont bougé ; vérifiez avant de publier, ou passez --skip-tests."
  fi
  ok "analyseur vérifié en $code (témoin : $ligne hors cible)"
}

if [ "$RUN_TESTS" -eq 1 ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    printf '%s!%s python3 absent : impossible de vérifier l analyseur avant.\n' "$YELLOW" "$OFF"
  else
    for lang in fr en; do
      [ -f "$SRC/lexiques/$lang.json" ] || die "fichier de langue absent : $SRC/lexiques/$lang.json"
    done
    temoin fr "$SRC/references/exemple-texte-llm-fr.md" 9 21
    temoin en "$SRC/references/exemple-texte-llm-en.md" 17 24
  fi
fi

# --- construction ---------------------------------------------------------
if [ "$CLEAN" -eq 1 ] && [ -d "$DIST" ]; then
  rm -rf "$DIST"
  ok "dist/ vidé"
fi
mkdir -p "$DIST"

OUT="$DIST/$ARCHIVE"
rm -f "$OUT"

# -X écarte les métadonnées macOS, qui gonflent l'archive sans rien apporter.
( cd "$ROOT" && zip -r -q -X "$OUT" "$SKILL_NAME" \
    -x "$SKILL_NAME/**/__pycache__/*" "$SKILL_NAME/**/*.pyc" "*.DS_Store" )

# --- contrôle de l'archive produite ---------------------------------------
unzip -tq "$OUT" >/dev/null || die "l'archive produite est corrompue : $OUT"

if ! unzip -l "$OUT" | grep -q " $SKILL_NAME/SKILL.md$"; then
  die "SKILL.md n'est pas à la racine de $SKILL_NAME/ dans l'archive"
fi

if unzip -l "$OUT" | grep -qE "__pycache__|\.pyc|\.DS_Store"; then
  printf '%s!%s des fichiers indésirables ont été empaquetés.\n' "$YELLOW" "$OFF"
fi

ok "archive construite"
printf '\n%sContenu%s\n' "$BOLD" "$OFF"
unzip -l "$OUT" | awk 'NR > 3 && NF >= 4 && $4 != "" { printf "  %8s  %s\n", $1, $4 }' | grep -v '/$'

SIZE="$(du -h "$OUT" | awk '{print $1}')"
printf '\n%s%s%s  (%s)\n' "$BOLD" "$OUT" "$OFF" "$SIZE"
printf 'Import : Claude Desktop > Réglages > Capacités > Compétences > Importer.\n'
