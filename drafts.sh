#!/bin/bash

echo "Draft posts:"
echo ""

grep -rl "^draft: true" content/posts/*/index.md \
  | sort \
  | while read -r file; do
      dir=$(dirname "$file")
      title=$(grep "^title:" "$file" | sed 's/^title: *//' | tr -d '"')
      date=$(grep "^date:" "$file" | sed 's/^date: *//')
      printf "  %-12s  %s\n" "$date" "$title"
    done
