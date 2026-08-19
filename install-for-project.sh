#!/usr/bin/env bash
#
# Installe la skill marqueurs-llm dans un projet, sous .claude/skills/.
# Elle n'est active que pour les sessions Claude Code ouvertes sur ce projet.
#
# Par défaut : copie des fichiers. Une skill de projet a vocation à être
# versionnée avec le dépôt ; un lien symbolique pointerait vers un chemin
# absolu qui n'existe que sur cette machine, et serait cassé pour tous les
# autres. Utilisez --link si le projet reste strictement local.

set -euo pipefail

SKILL_NAME="marqueurs-llm"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$SKILL_NAME"

MODE="copy"
FORCE=0
PROJECT=""

if [ -t 1 ]; then
  BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; OFF=$'\033[0m'
else
  BOLD=""; RED=""; GREEN=""; YELLOW=""; OFF=""
fi

usage() {
  cat <<EOF
${BOLD}install-for-project.sh${OFF} — installe la skill $SKILL_NAME dans un projet

Usage
  ./install-for-project.sh [options] [chemin-du-projet]

  Sans argument, le projet est le répertoire courant.
  Destination : <projet>/.claude/skills/$SKILL_NAME

Options
  --link     lien symbolique au lieu d'une copie (projet local uniquement :
             le lien est absolu et ne survivra pas à un clone)
  --copy     force la copie (défaut)
  --force    remplace une installation existante sans rien demander
  -h, --help affiche cette aide

Désinstallation
  rm -rf <projet>/.claude/skills/$SKILL_NAME
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --link)  MODE="link" ;;
    --copy)  MODE="copy" ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) printf '%sOption inconnue : %s%s\n\n' "$RED" "$1" "$OFF" >&2; usage >&2; exit 2 ;;
    *)
      [ -z "$PROJECT" ] || { printf '%sUn seul projet à la fois.%s\n' "$RED" "$OFF" >&2; exit 2; }
      PROJECT="$1"
      ;;
  esac
  shift
done

die() { printf '%serreur :%s %s\n' "$RED" "$OFF" "$1" >&2; exit 1; }

PROJECT="${PROJECT:-$PWD}"
[ -d "$PROJECT" ] || die "répertoire de projet introuvable : $PROJECT"
PROJECT="$(cd "$PROJECT" && pwd)"

SKILLS_DIR="$PROJECT/.claude/skills"
DEST="$SKILLS_DIR/$SKILL_NAME"

# --- vérification de la source -------------------------------------------
[ -d "$SRC" ] || die "skill introuvable : $SRC"
[ -f "$SRC/SKILL.md" ] || die "$SRC ne contient pas de SKILL.md"
[ -f "$SRC/scripts/analyse.py" ] || die "$SRC/scripts/analyse.py est absent"

# Installer la skill dans le dépôt qui la produit créerait une copie qui
# diverge de l'originale au premier changement.
if [ "$PROJECT" = "$(cd "$(dirname "$SRC")" && pwd)" ]; then
  die "ce projet est le dépôt source de la skill. Utilisez install-for-user.sh."
fi

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
  printf '%s!%s ce lien est absolu : il sera cassé pour quiconque clone le dépôt.\n' \
    "$YELLOW" "$OFF"
else
  cp -R "$SRC" "$DEST"
  rm -rf "$DEST/scripts/__pycache__"
  printf '%s✓%s fichiers copiés dans %s\n' "$GREEN" "$OFF" "$DEST"
fi

# --- test de fumée --------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  fixture="$DEST/references/exemple-texte-llm.md"
  if [ -f "$fixture" ]; then
    score="$(python3 "$DEST/scripts/analyse.py" "$fixture" 2>/dev/null \
             | sed -n 's/^SCORE : \([0-9]*\) .*/\1/p')"
    if [ "$score" = "9" ]; then
      printf '%s✓%s analyseur fonctionnel (texte-témoin : 9/13 hors cible)\n' "$GREEN" "$OFF"
    elif [ -n "$score" ]; then
      printf '%s!%s analyseur fonctionnel mais le texte-témoin donne %s/13 au lieu de 9.\n' \
        "$YELLOW" "$OFF" "$score"
    else
      printf '%s!%s analyse.py ne répond pas comme attendu. Vérifiez :\n' "$YELLOW" "$OFF"
      printf '    python3 "%s" "%s"\n' "$DEST/scripts/analyse.py" "$fixture"
    fi
  fi
else
  printf '%s!%s python3 introuvable sur cette machine. La skill est installée mais\n' \
    "$YELLOW" "$OFF"
  printf '  son analyseur ne pourra pas tourner ici.\n'
fi

# --- versionnement --------------------------------------------------------
if [ -d "$PROJECT/.git" ] && [ "$MODE" = "copy" ]; then
  printf '\n%sDépôt git détecté.%s Pour versionner la skill avec le dépôt :\n' "$BOLD" "$OFF"
  printf '  git -C "%s" add .claude/skills/%s\n' "$PROJECT" "$SKILL_NAME"
fi

printf '\n%sInstallée dans %s.%s\n' "$BOLD" "$PROJECT" "$OFF"
printf 'Redémarrez Claude Code dans ce projet, puis vérifiez avec /skills.\n'
printf 'Pour désinstaller : rm -rf "%s"\n' "$DEST"
