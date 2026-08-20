#!/usr/bin/env bash
#
# Installe la skill marqueurs-llm pour l'utilisateur courant.
# Elle devient disponible dans toutes les sessions Claude Code.
#
# Par défaut : lien symbolique. Vous continuez à modifier la skill dans ce
# dépôt et Claude voit les changements sans réinstallation. Utilisez --copy
# si vous préférez figer la version installée.

set -euo pipefail

SKILL_NAME="marqueurs-llm"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$SKILL_NAME"
SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
DEST="$SKILLS_DIR/$SKILL_NAME"

MODE="link"
FORCE=0

if [ -t 1 ]; then
  BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; OFF=$'\033[0m'
else
  BOLD=""; RED=""; GREEN=""; YELLOW=""; OFF=""
fi

usage() {
  cat <<EOF
${BOLD}install-for-user.sh${OFF} — installe la skill $SKILL_NAME pour l'utilisateur

  Destination : $SKILLS_DIR/$SKILL_NAME

Options
  --copy     copie les fichiers au lieu de créer un lien symbolique
  --link     force le lien symbolique (défaut)
  --force    remplace une installation existante sans rien demander
  -h, --help affiche cette aide

Variable d'environnement
  CLAUDE_CONFIG_DIR   racine de configuration Claude (défaut : \$HOME/.claude)

Désinstallation
  rm -rf "$DEST"
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --copy)  MODE="copy" ;;
    --link)  MODE="link" ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%sOption inconnue : %s%s\n\n' "$RED" "$1" "$OFF" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

die() { printf '%serreur :%s %s\n' "$RED" "$OFF" "$1" >&2; exit 1; }

# --- vérification de la source -------------------------------------------
[ -d "$SRC" ] || die "skill introuvable : $SRC"
[ -f "$SRC/SKILL.md" ] || die "$SRC ne contient pas de SKILL.md"
[ -f "$SRC/scripts/analyse.py" ] || die "$SRC/scripts/analyse.py est absent"

# --- destination déjà occupée --------------------------------------------
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  if [ "$FORCE" -eq 0 ]; then
    if [ -L "$DEST" ]; then
      printf '%s%s existe déjà et pointe vers :%s\n  %s\n' \
        "$YELLOW" "$DEST" "$OFF" "$(readlink "$DEST")"
    else
      printf '%s%s existe déjà (répertoire).%s\n' "$YELLOW" "$DEST" "$OFF"
    fi
    printf 'Remplacer ? [o/N] '
    if ! read -r answer </dev/tty 2>/dev/null; then
      printf '\n%sEntrée non interactive :%s relancez avec --force pour remplacer.\n' \
        "$YELLOW" "$OFF"
      exit 0
    fi
    case "$answer" in
      o|O|y|Y) ;;
      *) printf 'Installation annulée.\n'; exit 0 ;;
    esac
  fi
  rm -rf "$DEST"
fi

# --- installation ---------------------------------------------------------
mkdir -p "$SKILLS_DIR"

if [ "$MODE" = "link" ]; then
  ln -s "$SRC" "$DEST"
  printf '%s✓%s lien créé : %s -> %s\n' "$GREEN" "$OFF" "$DEST" "$SRC"
else
  cp -R "$SRC" "$DEST"
  rm -rf "$DEST/scripts/__pycache__"
  printf '%s✓%s fichiers copiés dans %s\n' "$GREEN" "$OFF" "$DEST"
fi

# --- test de fumée --------------------------------------------------------
# La skill est utilisable sans Python, mais son analyseur ne l'est pas.
# Autant le savoir maintenant plutôt qu'au premier diagnostic.
if command -v python3 >/dev/null 2>&1; then
  # Un témoin par langue : un en.json cassé ne se verrait pas sur le français.
  for t in "fr:9:13" "en:17:17"; do
    code="${t%%:*}"; reste="${t#*:}"; attendu="${reste%%:*}"; total="${reste#*:}"
    fixture="$DEST/references/exemple-texte-llm-$code.md"
    [ -f "$fixture" ] || continue
    # Sans le || true, pipefail ferait sortir le script en silence quand
    # l analyseur plante, et le message d avertissement ne sortirait jamais.
    score="$(python3 "$DEST/scripts/analyse.py" "$fixture" --langue "$code" 2>/dev/null \
             | sed -n 's/^SCORE : \([0-9]*\) metriques hors cible sur \([0-9]*\).*/\1\/\2/p' \
             || true)"
    if [ "$score" = "$attendu/$total" ]; then
      printf '%s✓%s analyseur fonctionnel en %s (témoin : %s hors cible)\n' \
        "$GREEN" "$OFF" "$code" "$score"
    elif [ -n "$score" ]; then
      printf '%s!%s analyseur fonctionnel mais le témoin %s donne %s au lieu de %s/%s.\n' \
        "$YELLOW" "$OFF" "$code" "$score" "$attendu" "$total"
      printf '  Les seuils ou les lexiques ont peut-être été modifiés.\n'
    else
      printf '%s!%s analyse.py ne répond pas comme attendu. Vérifiez :\n' "$YELLOW" "$OFF"
      printf '    python3 "%s" "%s"\n' "$DEST/scripts/analyse.py" "$fixture"
    fi
  done
else
  printf '%s!%s python3 introuvable. La skill est installée mais son analyseur\n' "$YELLOW" "$OFF"
  printf '  ne pourra pas tourner : le diagnostic chiffré sera indisponible.\n'
fi

printf '\n%sInstallée.%s Redémarrez Claude Code, puis vérifiez avec /skills.\n' "$BOLD" "$OFF"
printf 'Pour désinstaller : rm -rf "%s"\n' "$DEST"
