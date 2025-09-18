#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
maze_solver.py
==============
Solve a maze in ASCII format using either:
- Recursive Backtracking (DFS)
- A* (Manhattan)

Conventions
-----------
- Walls: '#'
- Empty: '.'
- Final path: 'o'
- Explored (not on final path): '*'
- Entry opening: on top border (row 0)
- Exit opening: on bottom border (row H-1)
- The maze grid is typically (2n+1)x(2n+1) with cells on odd coordinates.

Usage
-----
Run the script and answer prompts:
    python maze_solver.py
    > Nom du fichier labyrinthe à résoudre: maze_25.txt
    > Algorithme (backtracking / astar): astar
    > Nom du fichier de sortie: maze_25_solved.txt
"""

from typing import List, Tuple, Optional
import heapq
import sys

WALL = '#'
EMPTY = '.'
PATH = 'o'
SEEN = '*'
Coord = Tuple[int, int]
Grid = List[List[str]]
sys.setrecursionlimit(10000)
# --------------------
# I/O utilities
# --------------------
def read_grid(filename: str) -> Grid:
    """Read an ASCII maze file into a list of list of chars."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    # Keep exact characters; don't strip spaces; ensure list of list
    return [list(line) for line in lines if line != '']

def save_grid(grid: Grid, filename: str) -> None:
    """Write the maze grid back to a text file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for row in grid:
            f.write(''.join(row) + '\n')

def find_entry_exit(grid: Grid) -> Tuple[Coord, Coord]:
    """Find entry (first '.' on top row) and exit (first '.' from right on bottom row)."""
    H, W = len(grid), len(grid[0])

    entry: Optional[Coord] = None
    for c in range(W):
        if grid[0][c] == EMPTY:
            entry = (0, c)
            break

    exit_: Optional[Coord] = None
    for c in range(W - 1, -1, -1):
        if grid[H - 1][c] == EMPTY:
            exit_ = (H - 1, c)
            break

    if entry is None or exit_ is None:
        raise ValueError("Entrée/sortie introuvables sur les bords du labyrinthe.")

    return entry, exit_

def neighbors4(r: int, c: int):
    """Yield 4-neighbors (up, down, left, right)."""
    yield r - 1, c
    yield r + 1, c
    yield r, c - 1
    yield r, c + 1

# --------------------
# Backtracking (DFS)
# --------------------
def solve_backtracking(grid: Grid) -> bool:
    """
    Solve the maze using DFS backtracking.
    Mutates 'grid' in-place:
      - marks explored '.' as '*' (SEEN)
      - overwrites final path cells as 'o' (PATH)
    Returns True if a path was found, False otherwise.
    """
    H, W = len(grid), len(grid[0])
    (sr, sc), (er, ec) = find_entry_exit(grid)

    def is_empty(r: int, c: int) -> bool:
        return 0 <= r < H and 0 <= c < W and grid[r][c] == EMPTY

    # Start just inside the maze (below entry) if possible; target just above exit
    start = (1, sc) if sr == 0 and is_empty(1, sc) else (sr, sc)
    goal = (H - 2, ec) if er == H - 1 and is_empty(H - 2, ec) else (er, ec)

    visited = [[False] * W for _ in range(H)]
    parent: dict[Coord, Coord] = {}

    found = False

    def dfs(r: int, c: int) -> None:
        nonlocal found
        if found:
            return
        visited[r][c] = True
        if (r, c) == goal:
            found = True
            return
        for nr, nc in neighbors4(r, c):
            if 0 <= nr < H and 0 <= nc < W and not visited[nr][nc] and grid[nr][nc] == EMPTY:
                parent[(nr, nc)] = (r, c)
                dfs(nr, nc)
                if found:
                    return

    if is_empty(start[0], start[1]):
        dfs(start[0], start[1])
    else:
        return False

    # Mark explored cells as SEEN
    for r in range(H):
        for c in range(W):
            if visited[r][c] and grid[r][c] == EMPTY:
                grid[r][c] = SEEN

    if not found:
        return False

    # Reconstruct final path and mark as PATH
    cur = goal
    while cur != start:
        r, c = cur
        grid[r][c] = PATH
        cur = parent[cur]
    # Mark start too
    grid[start[0]][start[1]] = PATH

    return True

# --------------------
# A* (Manhattan)
# --------------------
def solve_astar(grid: Grid) -> bool:
    """
    Solve the maze using A* with Manhattan heuristic.
    Mutates 'grid' in-place:
      - marks explored '.' as '*' (SEEN)
      - overwrites final path cells as 'o' (PATH)
    Returns True if a path was found, False otherwise.
    """
    H, W = len(grid), len(grid[0])
    (sr, sc), (er, ec) = find_entry_exit(grid)

    def is_empty(r: int, c: int) -> bool:
        return 0 <= r < H and 0 <= c < W and grid[r][c] == EMPTY

    # Start just inside the maze (below entry) if possible; target just above exit
    start = (1, sc) if sr == 0 and is_empty(1, sc) else (sr, sc)
    goal = (H - 2, ec) if er == H - 1 and is_empty(H - 2, ec) else (er, ec)

    def h(a: Coord, b: Coord) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_heap: list[tuple[int, int, Coord]] = []
    heapq.heappush(open_heap, (h(start, goal), 0, start))

    came: dict[Coord, Optional[Coord]] = {start: None}
    g_score: dict[Coord, int] = {start: 0}
    closed: set[Coord] = set()

    while open_heap:
        f, g, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)

        if cur == goal:
            # Mark explored
            for (r, c) in closed:
                if grid[r][c] == EMPTY:
                    grid[r][c] = SEEN
            # Reconstruct path
            node = cur
            while node is not None:
                r, c = node
                grid[r][c] = PATH
                node = came[node]
            return True

        r, c = cur
        for nr, nc in neighbors4(r, c):
            if not (0 <= nr < H and 0 <= nc < W):
                continue
            if grid[nr][nc] != EMPTY:
                continue
            tentative_g = g + 1
            if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                g_score[(nr, nc)] = tentative_g
                came[(nr, nc)] = cur
                heapq.heappush(open_heap, (tentative_g + h((nr, nc), goal), tentative_g, (nr, nc)))

    return False

# --------------------
# Small CLI
# --------------------
def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def main():
    in_name = _ask("Nom du fichier labyrinthe à résoudre (ex: maze_25.txt): ")
    if not in_name:
        print("Fichier d'entrée requis.")
        return

    algo = _ask("Algorithme (backtracking / astar) [astar]: ").lower() or "astar"
    if algo not in {"backtracking", "astar"}:
        print("Algorithme inconnu. Choisir 'backtracking' ou 'astar'.")
        return

    out_name = _ask("Nom du fichier de sortie (ex: maze_25_solved.txt): ")
    if not out_name:
        base = in_name.rsplit('.', 1)[0]
        out_name = f"{base}_{algo}.txt"

    grid = read_grid(in_name)

    if algo == "backtracking":
        ok = solve_backtracking(grid)
    else:
        ok = solve_astar(grid)

    if not ok:
        print("Aucun chemin trouvé.")
        return

    save_grid(grid, out_name)
    print(f"Solution sauvegardée dans '{out_name}'.")

if __name__ == "__main__":
    main()
