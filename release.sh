#!/usr/bin/env bash
# Release script — bump version, build, tag, push, and optionally create GitHub release.
#
# Usage:
#   ./release.sh patch      # 1.1.0 → 1.1.1
#   ./release.sh minor      # 1.1.0 → 1.2.0
#   ./release.sh major      # 1.1.0 → 2.0.0
#   ./release.sh 1.2.3      # explicit version

set -euo pipefail

INIT_FILE="opguia/__init__.py"
CURRENT=$(grep -oP '(?<=__version__ = ")[^"]+' "$INIT_FILE")

echo "Current version: $CURRENT"

# ── Resolve target version ──
BUMP="${1:?Usage: ./release.sh <patch|minor|major|version>}"

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP" in
    patch) VERSION="$MAJOR.$MINOR.$((PATCH + 1))" ;;
    minor) VERSION="$MAJOR.$((MINOR + 1)).0" ;;
    major) VERSION="$((MAJOR + 1)).0.0" ;;
    *)     VERSION="$BUMP" ;;
esac

echo "==> Bumping version to $VERSION"
sed -i '' "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" "$INIT_FILE"

echo "==> Cleaning old builds"
rm -rf dist/ build/ *.egg-info

echo "==> Building"
python3 -m build

# ── Generate release notes from commits since last tag ──
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    NOTES=$(git log "$LAST_TAG"..HEAD --pretty=format:"- %s" --no-merges | grep -v "^- v[0-9]")
else
    NOTES=$(git log --pretty=format:"- %s" --no-merges -20 | grep -v "^- v[0-9]")
fi

echo ""
echo "Release notes for v$VERSION:"
echo "$NOTES"
echo ""

echo "==> Committing"
git add "$INIT_FILE"
git commit -m "v$VERSION"

echo "==> Tagging v$VERSION"
git tag -a "v$VERSION" -m "v$VERSION

$NOTES"

echo "==> Pushing"
git push && git push --tags

# ── Create GitHub release if gh is available ──
if command -v gh &>/dev/null; then
    echo "==> Creating GitHub release"
    gh release create "v$VERSION" dist/* \
        --title "v$VERSION" \
        --notes "$NOTES"
else
    echo ""
    echo "Install gh CLI to auto-create GitHub releases."
fi

echo ""
echo "Done! v$VERSION released."
echo "GitHub Actions will publish to PyPI, or manually: twine upload dist/*"
