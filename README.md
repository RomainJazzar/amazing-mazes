# amazing-mazes

# 🌀 Amazing Mazes

> *Quel est le meilleur labyrinthe au monde ? Un A-maze-ing !*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)  
[![Status](https://img.shields.io/badge/Statut-En%20développement-brightgreen)]()  
[![License](https://img.shields.io/badge/License-MIT-yellow)]()  

Projet académique et technique visant à générer et résoudre des **labyrinthes parfaits** en Python.  
Il combine **algorithmique**, **théorie des graphes**, **pathfinding** et **visualisation**, tout en mettant l’accent sur la **mesure de performance**.

---

## 🚀 Fonctionnalités

- ✅ **Générateurs de labyrinthes**
  - Backtracking récursif (DFS)
  - Kruskal (Union–Find / DSU)

- ✅ **Solveurs**
  - Backtracking récursif
  - A* (heuristique de Manhattan)

- ✅ **Sorties**
  - ASCII (`#`, `.`, `o`, `*`)
  - Export PNG (`ascii_to_jpg.py`)

- ✅ **Benchmarks**
  - Temps (mur + CPU)
  - Mémoire (consommation max)
  - Longueur du chemin, cases explorées
  - Comparaison entre générateurs et solveurs

---

## 🖼️ Exemple

**Labyrinthe 25×25 (Kruskal + A*)**

#######################
#.....#...............#
###.#.###.###.###.###.#
#.#.#.#.#.#.#.#.#.#.#.#
#o#o#o#o#o#o#o#o#o#o#o#
#######################

yaml
Copy code

🖼️ Export PNG :  

![maze_example](examples/maze_25.png)

---

## 📊 Benchmarks

| Taille n | Générateur    | Solveur      | Temps (s) | Mémoire (KB) | Longueur chemin | Cases explorées |
|----------|---------------|--------------|-----------|--------------|-----------------|-----------------|
| 15       | Backtracking  | Backtracking | 0.003     | 412          | 57              | 64              |
| 15       | Kruskal       | A*           | 0.006     | 529          | 57              | 42              |
| 51       | Kruskal       | A*           | 0.152     | 1380         | 179             | 96              |
| 51       | Backtracking  | A*           | 0.178     | 1422         | 182             | 114             |

👉 Tests jusqu’à **n = 10 000** pour étudier la scalabilité.

---

## ⚙️ Utilisation

### 1. Cloner le projet
```bash
git clone https://github.com/ton-username/amazing-mazes.git
cd amazing-mazes
2. Générer un labyrinthe
bash
Copy code
python maze_generator.py
3. Résoudre un labyrinthe
bash
Copy code
python maze_solver.py
4. Convertir ASCII → Image
bash
Copy code
python ascii_to_jpg.py
5. Lancer les benchmarks
bash
Copy code
python benchmarks.py --sizes 15 25 51 --reps 2 --seed 123 \
  --generators backtracking kruskal \
  --solvers backtracking astar \
  --out resultats.csv --verbose
🎯 Compétences mises en avant
Théorie des graphes (arbres couvrants, disjoint sets)

Algorithmes de recherche (DFS, A*)

Analyse de performance (temps, mémoire, scalabilité)

Visualisation de données (ASCII, matplotlib, export PNG)

Bonnes pratiques d’ingénierie (modularité, benchmarks, documentation)

📌 Contexte
Projet réalisé dans le cadre du Bachelor Intelligence Artificielle à La Plateforme, Marseille.
Ce projet illustre ma capacité à :

Implémenter des algorithmes de bout en bout

Mesurer et comparer des performances

Présenter des résultats de façon claire et impactante

📬 Contact
👤 Romain Jazzar
📍 Marseille, France
🔗 LinkedIn • Portfolio • 📧 roman.jazzar@outlook.com

⭐ Si ce projet vous a intéressé, pensez à lui donner une star sur GitHub !

yaml
Copy code

---

⚡ Résultat :  
- Badges colorés en haut → attire l’œil  
- Tableaux + codeblocks → faciles à lire  
- Mélange de technique et de storytelling → ça montre **savoir-faire + communication**  
- Contact + portfolio → oriente directement les recruteurs vers toi  
