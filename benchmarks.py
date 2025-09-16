#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmarks.py
=============
Automatise la comparaison des **générateurs** et **solveurs** :
- Générateurs: backtracking, kruskal (depuis maze_generator.py)
- Solveurs: backtracking, astar (depuis maze_solver.py)

Mesures collectées
------------------
- Temps réel (wall_time_s) et CPU (cpu_time_s)
- Mémoire peak (peak_mem_bytes, via tracemalloc)
- Dimensions ASCII, taille du texte (ascii_bytes)
- Longueur du chemin trouvé (path_len_cells) et cases explorées (explored_cells)

Sorties
-------
- CSV des résultats (par défaut: maze_metrics.csv)
- Résumé console

Usage
-----
python benchmarks.py --sizes 15 25 51 --reps 2 --seed 123 \
    --generators backtracking kruskal --solvers backtracking astar \
    --out maze_metrics.csv

Notes
-----
- Le script importe:
    - maze_generator.py  (carve_passages_recursive_backtracking, carve_maze_kruskal)
    - maze_solver.py     (solve_backtracking, solve_astar)
- Place benchmarks.py dans le même dossier que ces fichiers, ou ajoute leur chemin via PYTHONPATH.
"""

import argparse
import importlib
import sys
import time
import tracemalloc
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Tuple
from collections import Counter
import csv
import os
import math

# ---------------------------------
# Types / constantes
# ---------------------------------
WALL  = '#'
EMPTY = '.'
PATH  = 'o'
SEEN  = '*'

Grid = List[List[str]]

# ---------------------------------
# Utils
# ---------------------------------
def grid_to_str(grid: Grid) -> str:
    return "\n".join("".join(row) for row in grid)

def copy_grid(grid: Grid) -> Grid:
    return [row.copy() for row in grid]

def count_chars(grid: Grid) -> Dict[str, int]:
    return dict(Counter(ch for row in grid for ch in row))

# ---------------------------------
# Mesures
# ---------------------------------
@dataclass
class GenMetrics:
    phase: str
    algo: str
    n: int
    seed: int
    wall_time_s: float
    cpu_time_s: float
    peak_mem_bytes: int
    ascii_bytes: int
    H: int
    W: int
    grid_cells: int

@dataclass
class SolveMetrics:
    phase: str
    algo: str
    gen_algo: str
    n: int
    seed: int
    ok: bool
    wall_time_s: float
    cpu_time_s: float
    peak_mem_bytes: int
    path_len_cells: int
    explored_cells: int
    remaining_empty_cells: int
    wall_cells: int

def measure_generation(gen_fn: Callable[[int], Grid], n: int, seed: int, label: str) -> Tuple[GenMetrics, Grid]:
    start_cpu = time.process_time()
    start_wall = time.perf_counter()
    tracemalloc.start()
    grid = gen_fn(n, seed=seed)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_wall = time.perf_counter()
    end_cpu = time.process_time()

    ascii_txt = grid_to_str(grid)
    H, W = len(grid), len(grid[0]) if grid else (0, 0)
    gm = GenMetrics(
        phase="generation",
        algo=label,
        n=n,
        seed=seed,
        wall_time_s=end_wall - start_wall,
        cpu_time_s=end_cpu - start_cpu,
        peak_mem_bytes=int(peak),
        ascii_bytes=len(ascii_txt.encode("utf-8")),
        H=H, W=W, grid_cells=H*W
    )
    return gm, grid

def measure_solving(solve_fn: Callable[[Grid], bool], grid_in: Grid, n: int, seed: int,
                    label: str, gen_label: str) -> Tuple[SolveMetrics, Grid]:
    g = copy_grid(grid_in)
    start_cpu = time.process_time()
    start_wall = time.perf_counter()
    tracemalloc.start()
    ok = solve_fn(g)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end_wall = time.perf_counter()
    end_cpu = time.process_time()

    counts = count_chars(g)
    sm = SolveMetrics(
        phase="solving",
        algo=label,
        gen_algo=gen_label,
        n=n,
        seed=seed,
        ok=bool(ok),
        wall_time_s=end_wall - start_wall,
        cpu_time_s=end_cpu - start_cpu,
        peak_mem_bytes=int(peak),
        path_len_cells=counts.get(PATH, 0),
        explored_cells=counts.get(SEEN, 0),
        remaining_empty_cells=counts.get(EMPTY, 0),
        wall_cells=counts.get(WALL, 0)
    )
    return sm, g

# ---------------------------------
# Main
# ---------------------------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Benchmarks pour Amazing Mazes (générateurs & solveurs).")

    p.add_argument("--sizes", type=int, nargs="+", required=True,
                   help="Tailles n à tester (ex: --sizes 15 25 51 101)")
    p.add_argument("--reps", type=int, default=1,
                   help="Nombre de répétitions par taille (moyenne possible en post-traitement)")
    p.add_argument("--seed", type=int, default=123,
                   help="Seed de base (chaque run peut décaler cette seed)")

    p.add_argument("--generators", type=str, nargs="+",
                   choices=["backtracking", "kruskal"], default=["backtracking", "kruskal"],
                   help="Générateurs à comparer")
    p.add_argument("--solvers", type=str, nargs="+",
                   choices=["backtracking", "astar"], default=["backtracking", "astar"],
                   help="Solveurs à comparer")

    p.add_argument("--out", type=str, default="maze_metrics.csv",
                   help="Chemin du CSV de sortie")
    p.add_argument("--save_examples", action="store_true",
                   help="Sauvegarder quelques exemples ASCII (1er run de chaque combinaison)")
    p.add_argument("--examples_dir", type=str, default="examples",
                   help="Répertoire pour les exemples ASCII si --save_examples")
    p.add_argument("--verbose", action="store_true",
                   help="Affiche les mesures au fur et à mesure")

    # Modules à importer (si chemins custom)
    p.add_argument("--gen_module", type=str, default="maze_generator",
                   help="Module contenant les générateurs")
    p.add_argument("--sol_module", type=str, default="maze_solver",
                   help="Module contenant les solveurs")
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)

    # Import dynamique
    try:
        gen_mod = importlib.import_module(args.gen_module)
    except Exception as e:
        print(f"[ERREUR] Impossible d'importer le module générateur '{args.gen_module}': {e}")
        return 1

    try:
        sol_mod = importlib.import_module(args.sol_module)
    except Exception as e:
        print(f"[ERREUR] Impossible d'importer le module solveur '{args.sol_module}': {e}")
        return 1

    # Map des fonctions
    gen_map: Dict[str, Callable[[int], Grid]] = {}
    if "backtracking" in args.generators:
        if hasattr(gen_mod, "carve_passages_recursive_backtracking"):
            gen_map["backtracking"] = gen_mod.carve_passages_recursive_backtracking
        else:
            print("[WARN] Générateur backtracking introuvable dans", args.gen_module)
    if "kruskal" in args.generators:
        if hasattr(gen_mod, "carve_maze_kruskal"):
            gen_map["kruskal"] = gen_mod.carve_maze_kruskal
        else:
            print("[WARN] Générateur kruskal introuvable dans", args.gen_module)

    sol_map: Dict[str, Callable[[Grid], bool]] = {}
    if "backtracking" in args.solvers:
        if hasattr(sol_mod, "solve_backtracking"):
            sol_map["backtracking"] = sol_mod.solve_backtracking
        else:
            print("[WARN] Solveur backtracking introuvable dans", args.sol_module)
    if "astar" in args.solvers:
        if hasattr(sol_mod, "solve_astar"):
            sol_map["astar"] = sol_mod.solve_astar
        else:
            print("[WARN] Solveur astar introuvable dans", args.sol_module)

    if not gen_map or not sol_map:
        print("[ERREUR] Aucun générateur/solveur valide chargé.")
        return 1

    # Prépare sortie CSV
    out_path = args.out
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Exemples ASCII
    if args.save_examples and not os.path.exists(args.examples_dir):
        os.makedirs(args.examples_dir, exist_ok=True)

    # Boucle d'expériences
    rows: List[dict] = []

    run_id = 0
    for n in args.sizes:
        for rep in range(args.reps):
            # Décaler la seed par run pour varier un peu
            base_seed = int(args.seed + 10007*rep + 7919*n)

            for gen_name, gen_fn in gen_map.items():
                # Mesure génération
                gm, grid = measure_generation(gen_fn, n, base_seed, label=f"gen_{gen_name}")
                rows.append(asdict(gm))
                if args.verbose:
                    print(f"[GEN] n={n} rep={rep+1}/{args.reps} algo={gen_name} | "
                          f"wall={gm.wall_time_s:.4f}s cpu={gm.cpu_time_s:.4f}s mem={gm.peak_mem_bytes/1e6:.2f}MB")

                # Sauvegarder exemple ASCII si demandé (seulement le premier solveur pour ne pas tout écraser)
                saved_example = False

                for sol_name, sol_fn in sol_map.items():
                    sm, solved = measure_solving(sol_fn, grid, n, base_seed,
                                                 label=f"solve_{sol_name}", gen_label=f"gen_{gen_name}")
                    rows.append(asdict(sm))
                    if args.verbose:
                        print(f"  [SOLVE] with {sol_name} | ok={sm.ok} "
                              f"wall={sm.wall_time_s:.4f}s cpu={sm.cpu_time_s:.4f}s "
                              f"mem={sm.peak_mem_bytes/1e6:.2f}MB path={sm.path_len_cells} explored={sm.explored_cells}")

                    if args.save_examples and not saved_example:
                        # Fichier exemple : <examples_dir>/maze_n_<gen>_<sol>.txt
                        fname = os.path.join(args.examples_dir, f"maze_n{n}_{gen_name}_{sol_name}.txt")
                        with open(fname, "w", encoding="utf-8") as f:
                            f.write(grid_to_str(solved) + "\n")
                        saved_example = True

                run_id += 1

    # Écriture CSV
    fieldnames = sorted(set(k for row in rows for k in row.keys()))
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\n✅ Résultats écrits dans: {out_path}")
    print(f"  Total lignes: {len(rows)}")
    # Petit résumé console
    # (on regroupe par phase+algo et on affiche la moyenne du wall time par taille)
    try:
        from statistics import mean
        summary: Dict[Tuple[str,str,int], float] = {}
        for row in rows:
            key = (row.get("phase","?"), row.get("algo","?"), row.get("n",-1))
            summary.setdefault(key, []).append(float(row.get("wall_time_s", 0.0)))
        print("\nRésumé (moyenne wall_time_s par phase/algo/n):")
        for (phase, algo, n), vals in sorted(summary.items()):
            avg = mean(vals)
            print(f"  {phase:10s} | {algo:24s} | n={n:5d} | mean wall={avg:.6f}s")
    except Exception:
        pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
