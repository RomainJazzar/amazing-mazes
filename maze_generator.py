#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
maze_generator.py
=================
Génère un labyrinthe **parfait** (un seul chemin entre deux cellules) au format ASCII,
selon l'algorithme choisi :
- "backtracking"  : Recursive Backtracking (DFS)
- "kruskal"       : Kruskal (avec DSU / Union-Find)

Conventions ASCII
-----------------
- Mur     : '#'
- Couloir : '.'
- Entrée  : ouverture sur la bordure du haut, au-dessus de la cellule (0,0)
- Sortie  : ouverture sur la bordure du bas, au-dessous de la cellule (n-1,n-1)
- Grille  : (2n+1) x (2n+1), les cellules sont aux coordonnées impaires (2r+1, 2c+1)

Utilisation (mode interactif)
-----------------------------
$ python maze_generator.py
> Taille n (nombre de couloirs par côté): 25
> Algorithme (backtracking / kruskal) [backtracking]:
> Nom du fichier de sortie (ex: maze_25.txt) [auto]:
> Seed aléatoire (entier, optionnel):

Le fichier ASCII sera écrit et contiendra le labyrinthe généré.
"""

from typing import List, Tuple, Optional
import random

WALL  = '#'
EMPTY = '.'

Grid = List[List[str]]

# -----------------------------
# Utilitaires I/O
# -----------------------------
def grid_to_str(grid: Grid) -> str:
    return '\n'.join(''.join(row) for row in grid)

def save_grid(grid: Grid, filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(grid_to_str(grid) + '\n')

# -----------------------------
# Helpers communs
# -----------------------------
def make_blank_grid(n: int) -> Grid:
    """Crée une grille ASCII (2n+1)x(2n+1) remplie de murs '#', avec les centres de cellules en '.'"""
    H, W = 2*n + 1, 2*n + 1
    grid = [[WALL for _ in range(W)] for _ in range(H)]
    for r in range(n):
        for c in range(n):
            gr, gc = 2*r + 1, 2*c + 1  # mapping cellule -> ASCII
            grid[gr][gc] = EMPTY
    return grid

def open_entry_exit(grid: Grid, n: int) -> None:
    """Ouvre l'entrée (haut au-dessus de (0,0)) et la sortie (bas au-dessous de (n-1,n-1))."""
    H = len(grid)
    # Entrée au-dessus de (0,0)
    grid[0][1] = EMPTY
    # Sortie en bas sous (n-1,n-1) -> colonne ASCII = 2*(n-1)+1 = 2n-1
    grid[H-1][2*n - 1] = EMPTY

def cell_to_grid(r: int, c: int) -> Tuple[int, int]:
    """Convertit coordonnées cellule -> coordonnées ASCII (impaires)."""
    return 2*r + 1, 2*c + 1

# -----------------------------
# Générateur 1 : Recursive Backtracking
# -----------------------------
def carve_passages_recursive_backtracking(n: int, seed: Optional[int] = None) -> Grid:
    if seed is not None:
        random.seed(seed)

    grid = make_blank_grid(n)
    visited = [[False]*n for _ in range(n)]

    def neighbors(r: int, c: int):
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc]:
                yield nr, nc

    def knock_between(r1: int, c1: int, r2: int, c2: int) -> None:
        g1r, g1c = cell_to_grid(r1, c1)
        g2r, g2c = cell_to_grid(r2, c2)
        wr, wc = (g1r + g2r)//2, (g1c + g2c)//2
        grid[wr][wc] = EMPTY

    stack = [(0,0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        progressed = False
        for nr, nc in neighbors(r, c):
            visited[nr][nc] = True
            knock_between(r, c, nr, nc)
            stack.append((nr, nc))
            progressed = True
            break
        if not progressed:
            stack.pop()

    open_entry_exit(grid, n)
    return grid

# -----------------------------
# Générateur 2 : Kruskal (DSU)
# -----------------------------
class DSU:
    def __init__(self, size: int):
        self.parent = list(range(size))
        self.rank = [0]*size
    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1
        return True

def carve_maze_kruskal(n: int, seed: Optional[int] = None) -> Grid:
    if seed is not None:
        random.seed(seed)

    grid = make_blank_grid(n)

    edges = []
    for r in range(n):
        for c in range(n):
            if r+1 < n: edges.append((r,c,r+1,c))
            if c+1 < n: edges.append((r,c,r,c+1))
    random.shuffle(edges)

    idx = lambda r, c: r*n + c
    dsu = DSU(n*n)

    def knock_between(r1: int, c1: int, r2: int, c2: int) -> None:
        g1r, g1c = cell_to_grid(r1, c1)
        g2r, g2c = cell_to_grid(r2, c2)
        wr, wc = (g1r + g2r)//2, (g1c + g2c)//2
        grid[wr][wc] = EMPTY

    for r1, c1, r2, c2 in edges:
        if dsu.union(idx(r1,c1), idx(r2,c2)):
            knock_between(r1,c1,r2,c2)

    open_entry_exit(grid, n)
    return grid

# -----------------------------
# CLI (mode interactif)
# -----------------------------
def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def main():
    # Taille n
    n_str = _ask("Taille n (nombre de couloirs par côté): ").strip()
    try:
        n = int(n_str)
        if n <= 0:
            raise ValueError
    except ValueError:
        print("Erreur: merci d'entrer un entier strictement positif pour n.")
        return

    # Choix algo
    algo = _ask("Algorithme (backtracking / kruskal) [backtracking]: ").lower() or "backtracking"
    if algo not in {"backtracking", "kruskal"}:
        print("Erreur: algorithme inconnu. Choisir 'backtracking' ou 'kruskal'.")
        return

    # Nom de sortie
    out_name = _ask("Nom du fichier de sortie (ex: maze_25.txt) [auto]: ")
    if not out_name:
        out_name = f"maze_{n}_{algo}.txt"

    # Seed optionnelle
    seed_in = _ask("Seed aléatoire (entier, optionnel): ")
    seed = None
    if seed_in:
        try:
            seed = int(seed_in)
        except ValueError:
            print("Avertissement: seed invalide, ignorée.")

    # Génération
    if algo == "backtracking":
        grid = carve_passages_recursive_backtracking(n, seed=seed)
    else:
        grid = carve_maze_kruskal(n, seed=seed)

    # Sauvegarde
    save_grid(grid, out_name)
    print(f"Labyrinthe {n}x{n} ({algo}) généré et sauvegardé dans '{out_name}'.")

if __name__ == "__main__":
    main()
