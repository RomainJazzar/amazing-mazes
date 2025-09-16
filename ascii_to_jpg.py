#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ascii_to_jpg.py
===============
Convert an ASCII maze file into an image (PNG/JPG).

Conventions:
- '#' (WALL)    -> Black
- '.' (EMPTY)   -> White
- 'o' (PATH)    -> Red
- '*' (SEEN)    -> Light Gray

Usage (interactive):
--------------------
$ python ascii_to_jpg.py
Nom du fichier ASCII à convertir (ex: maze_25_solved.txt): maze_25_solved.txt
Nom du fichier image de sortie (ex: maze.png): maze.png
Taille d'une cellule (pixels) [10]: 10
"""

from PIL import Image

# Color mapping
COLORS = {
    '#': (0, 0, 0),         # walls = black
    '.': (255, 255, 255),   # corridors = white
    'o': (255, 0, 0),       # solution path = red
    '*': (200, 200, 200),   # explored but not path = gray
}

def load_ascii(filename):
    """Load an ASCII maze from file into a list of lists."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [list(line.rstrip('\n')) for line in f if line.strip() != '' or line == '\n']
    return lines

def maze_to_image(grid, cell_size=10, filename="maze.png"):
    """Convert an ASCII maze grid to an image and save it."""
    H, W = len(grid), len(grid[0])
    img = Image.new("RGB", (W * cell_size, H * cell_size), "white")
    pixels = img.load()

    for r in range(H):
        for c in range(W):
            color = COLORS.get(grid[r][c], (255, 255, 255))
            for y in range(r * cell_size, (r + 1) * cell_size):
                for x in range(c * cell_size, (c + 1) * cell_size):
                    pixels[x, y] = color

    img.save(filename)
    print(f"✅ Image sauvegardée dans '{filename}'")

def main():
    ascii_file = input("Nom du fichier ASCII à convertir (ex: maze_25_solved.txt): ").strip()
    if not ascii_file:
        print("Fichier ASCII requis.")
        return

    out_file = input("Nom du fichier image de sortie (ex: maze.png): ").strip()
    if not out_file:
        base = ascii_file.rsplit('.', 1)[0]
        out_file = f"{base}.png"

    try:
        cell_size = int(input("Taille d'une cellule (pixels) [10]: ").strip() or 10)
    except ValueError:
        cell_size = 10

    grid = load_ascii(ascii_file)
    maze_to_image(grid, cell_size=cell_size, filename=out_file)

if __name__ == "__main__":
    main()
