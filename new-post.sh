#!/bin/bash

set -e

# ── helpers ──────────────────────────────────────────────────────────────────

slugify() {
  echo "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/[^a-z0-9 -]//g' \
    | sed 's/  */ /g' \
    | tr ' ' '-' \
    | sed 's/--*/-/g' \
    | sed 's/^-//;s/-$//'
}

yaml_list() {
  echo "$1" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | while read -r item; do
    [ -n "$item" ] && echo "  - $item"
  done
}

prompt() {
  local label="$1" default="$2" value
  if [ -n "$default" ]; then
    read -rp "$label [$default]: " value
    echo "${value:-$default}"
  else
    read -rp "$label: " value
    echo "$value"
  fi
}

# ── inputs ────────────────────────────────────────────────────────────────────

echo ""
echo "New post"
echo "────────"

title=$(prompt "Title")
if [ -z "$title" ]; then
  echo "Error: title is required." >&2
  exit 1
fi

description=$(prompt "Description")
if [ -z "$description" ]; then
  echo "Error: description is required." >&2
  exit 1
fi

today=$(date +%Y-%m-%d)
date=$(prompt "Date" "$today")

categories=$(prompt "Categories (comma-separated)")
tags=$(prompt "Tags (comma-separated)")

read -rp "Series (leave blank to skip): " series
if [ -n "$series" ]; then
  series_order=$(prompt "Series order")
fi

read -rp "Include cover image? [Y/n]: " cover_answer
cover_answer="${cover_answer:-Y}"

# ── build path ────────────────────────────────────────────────────────────────

slug=$(slugify "$title")
dir="content/posts/${date}-${slug}"
file="${dir}/index.md"

if [ -d "$dir" ]; then
  echo "Error: directory already exists: $dir" >&2
  exit 1
fi

mkdir -p "$dir"

# ── write frontmatter ─────────────────────────────────────────────────────────

{
  echo "---"
  echo "title: \"$title\""
  echo "description: $description"
  echo "date: $date"
  echo "draft: true"

  if [[ "$cover_answer" =~ ^[Yy] ]]; then
    echo "cover: cover.svg"
  fi

  if [ -n "$categories" ]; then
    echo "categories:"
    yaml_list "$categories"
  fi

  if [ -n "$tags" ]; then
    echo "tags:"
    yaml_list "$tags"
  fi

  if [ -n "$series" ]; then
    echo "series:"
    echo "  - $series"
    if [ -n "$series_order" ]; then
      echo "series_order: $series_order"
    fi
  fi

  echo "---"
  echo ""
} > "$file"

echo ""
echo "Created: $file"
