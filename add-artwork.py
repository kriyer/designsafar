"""
ADD ARTWORK — Art SAFAR Gallery Helper
======================================
Scans the Art/Florals folder for new images, generates thumbnail (400x400)
and medium (800x800) versions, and outputs JavaScript entries you can paste
into art-safar.html.

REQUIREMENTS (one-time setup):
    pip install Pillow

USAGE:
    1. Drop your new images (JPEG or PNG — not HEIC) into:
       Art/Florals/

    2. Open a terminal, cd to the website folder, and run:
       python add-artwork.py

    3. The script will:
       - Show you which new images it found
       - Generate thumbs and medium versions automatically
       - Print JavaScript entries for each new image
       - Save those entries to a file called NEW_ENTRIES.txt

    4. Open art-safar.html, find the end of the artworks array (just
       before the closing "];"), and paste the entries from NEW_ENTRIES.txt.

    5. Edit the titles, mediums, categories, prices, and descriptions
       to your liking — the script fills in placeholders.

NOTES:
    - The script only processes images that don't already have a thumbnail.
      Running it twice won't create duplicates.
    - Supported formats: .jpg, .jpeg, .png
    - HEIC files are skipped (convert them to JPEG first).
    - The script figures out the next available ID number automatically
      by reading art-safar.html.
"""

import os
import sys
import re
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("\n  Pillow is not installed. Run this first:")
    print("  pip install Pillow\n")
    sys.exit(1)


# ── Paths (relative to this script's location in the website folder) ──
SCRIPT_DIR = Path(__file__).resolve().parent
ART_DIR = SCRIPT_DIR / "Art"
THUMBS_DIR = ART_DIR / "thumbs"
MEDIUM_DIR = ART_DIR / "medium"
HTML_FILE = SCRIPT_DIR / "art-safar.html"
OUTPUT_FILE = SCRIPT_DIR / "NEW_ENTRIES.txt"

SUPPORTED = {".jpg", ".jpeg", ".png"}
THUMB_SIZE = (400, 400)
MEDIUM_SIZE = (800, 800)


def get_next_id():
    """Read art-safar.html and find the highest existing artwork ID."""
    if not HTML_FILE.exists():
        return 1
    text = HTML_FILE.read_text(encoding="utf-8")
    ids = [int(m) for m in re.findall(r'\bid:\s*(\d+)', text)]
    return max(ids) + 1 if ids else 1


def find_new_images():
    """Return list of full-res image files that don't have a thumbnail yet."""
    if not ART_DIR.exists():
        print(f"  Art folder not found: {ART_DIR}")
        sys.exit(1)

    THUMBS_DIR.mkdir(exist_ok=True)
    MEDIUM_DIR.mkdir(exist_ok=True)

    # Existing thumbs (lowercase stems for comparison)
    existing = {p.stem.lower() for p in THUMBS_DIR.iterdir() if p.suffix.lower() in SUPPORTED}

    new_files = []
    for f in sorted(ART_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED:
            if f.stem.lower() not in existing:
                new_files.append(f)
    return new_files


def generate_resized(src_path, basename):
    """Create thumbnail and medium versions of an image."""
    try:
        img = Image.open(src_path)
        img = img.convert("RGB")  # handle RGBA PNGs

        # Thumbnail
        thumb = img.copy()
        thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
        thumb_path = THUMBS_DIR / f"{basename}.jpg"
        thumb.save(thumb_path, "JPEG", quality=85)

        # Medium
        med = img.copy()
        med.thumbnail(MEDIUM_SIZE, Image.LANCZOS)
        med_path = MEDIUM_DIR / f"{basename}.jpg"
        med.save(med_path, "JPEG", quality=85)

        return True
    except Exception as e:
        print(f"  ERROR processing {src_path.name}: {e}")
        return False


def make_entry(art_id, basename, filename):
    """Generate a JavaScript object entry with placeholder values."""
    # Guess a readable title from the filename
    title = basename.replace("-", " ").replace("_", " ").strip()
    if title.startswith("IMG "):
        title = f"Untitled #{art_id}"

    return (
        f'      {{ id: {art_id}, basename: "{basename}", '
        f'title: "{title}", '
        f'medium: "MEDIUM_HERE", '
        f'category: "CATEGORY_HERE", '
        f'price: "$PRICE", '
        f'fullRes: "{filename}", '
        f'description: "DESCRIPTION_HERE" }},'
    )


def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   Add Artwork — Art SAFAR Gallery    ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    new_files = find_new_images()

    if not new_files:
        print("  No new images found. Everything is already synced!")
        print()
        print("  To add art, drop JPEG or PNG files into:")
        print(f"  {ART_DIR}")
        print()
        return

    print(f"  Found {len(new_files)} new image(s):\n")
    for f in new_files:
        print(f"    • {f.name}")
    print()

    next_id = get_next_id()
    entries = []
    processed = 0

    for i, f in enumerate(new_files):
        art_id = next_id + i
        basename = f.stem
        print(f"  [{i+1}/{len(new_files)}] Processing {f.name}...", end=" ")

        if generate_resized(f, basename):
            entries.append(make_entry(art_id, basename, f.name))
            processed += 1
            print("OK")
        else:
            print("SKIPPED")

    print(f"\n  Generated thumbs & medium for {processed} image(s).\n")

    if entries:
        # Print to console
        print("  ── Paste these into the artworks array in art-safar.html ──\n")
        for e in entries:
            print(e)
        print()

        # Save to file
        OUTPUT_FILE.write_text("\n".join(entries) + "\n", encoding="utf-8")
        print(f"  Also saved to: {OUTPUT_FILE.name}")
        print()
        print("  NEXT STEPS:")
        print("  1. Open art-safar.html")
        print('  2. Find the end of the artworks array (before the closing "];")' )
        print("  3. Paste the entries above")
        print("  4. Replace the placeholder values:")
        print('     - MEDIUM_HERE  → e.g. "Watercolor on Paper"')
        print('     - CATEGORY_HERE → one of: Floral Study, Ink Study, Botanical,')
        print("                       Abstract, Landscape, Collection")
        print('     - $PRICE → e.g. "$480"')
        print("     - DESCRIPTION_HERE → a short description of the piece")
        print('     - Update the title if "Untitled" doesn\'t fit')
        print()


if __name__ == "__main__":
    main()
