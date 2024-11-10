import yaml
import numpy as np
import subprocess
import sys, os

######################################################################################################################

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--n-cards", type=int, default=1)

args = parser.parse_args()

######################################################################################################################
# Configurations

# Number of traits drawn from each category
n_easy = 9 
n_medium = 13
n_hard = 3

n_rows = 5
cell_size = 2 #cm
######################################################################################################################

if n_easy + n_hard + n_medium < n_rows**2:
    print(f"Sum of traits from the categories easy/medium/hard ({n_easy + n_hard + n_medium}) is smaller than the number of cells ({n_rows**2:.0f}). Exiting.")
    exit(1)

with open("traits.yaml", "r") as f:
    traits = yaml.safe_load(f)

for category, nr in zip(["easy", "medium", "hard"], [n_easy, n_medium, n_hard]):
    if len(traits[category].keys()) < nr:
        print(f"Not enough traits specified for category {category}: {nr} needed, {len(traits[category].keys())} available. Exiting.")
        exit(1)

def select_random_categories(traits):
    chosen_traits = []
    for category, n_entries in zip(["easy", "medium", "hard"], [n_easy, n_medium, n_hard]):
        chosen_traits.extend(np.random.choice(list(traits[category].keys()), size=n_entries, replace=False))
    
    # Convert to 1D array and shuffle
    chosen_traits = np.array(chosen_traits)
    np.random.shuffle(chosen_traits)
    
    return list(chosen_traits)


def generate_latex_bingo_card():
    bingo_board = select_random_categories(traits)  # Choose 25 for 5x5 board
    latex_code = r"\begin{center}" + "\n"
    latex_code += r"\begin{tikzpicture}" + "\n"
    latex_code += "% Set the grid dimensions\n"
    latex_code += r"\def\cellsize{" + f"{cell_size}" + r"cm} % Each cell will be 2x2 cm" + "\n\n"
    latex_code += "% Draw the grid and insert the numbers\n"
    
    for row in range(n_rows):
        for col in range(n_rows):
            number = bingo_board[row * n_rows + col]
            x_pos = col * cell_size  # x-coordinate for the rectangle
            y_pos = -row * cell_size  # y-coordinate for the rectangle (negative for downward rows)
            
            latex_code += r"\draw[thick] (" + str(x_pos) + ", " + str(y_pos) + f") rectangle +({cell_size}, {cell_size});" + "\n"
            latex_code += r"\node[anchor=north, font=\Large, align=center] at (" + str(x_pos + cell_size/2) + ", " + str(y_pos + cell_size-0.1) + ") {" + str(number) + "};" + "\n"
    latex_code += r"\node[anchor=north, font = \Huge] at ("+ f"{n_rows*cell_size/2:.1f}, {n_rows*cell_size/3:.1f})" r"{\textbf{EoY Human Bingo}};" + "\n"
    latex_code += r"\end{tikzpicture}" + "\n"
    latex_code += r"\end{center}" + "\n"
    return latex_code


def create_bingo_card(filename="bingo.tex"):
    latex_code = ""
    for i in range(args.n_cards):
        latex_code += generate_latex_bingo_card()
        latex_code += r"\newpage" if i < args.n_cards-1 else ""
    with open(filename, "w") as f:
        f.write(latex_code)
    subprocess.run(["lualatex", "--output-directory=build", "bingo_card.tex"])

def create_traits_card(filename="traits.tex"):
    latex_code = ""
    for category in ["easy", "medium", "hard"]:
        for key in traits[category].keys():
            latex_code += r"\item " + f"{key}: {traits[category][key]}" + r"\\" + "\n"
    with open(filename, "w") as f:
        f.write(latex_code)
    subprocess.run(["lualatex", "--output-directory=build", "traits_card.tex"])

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    create_traits_card()
    create_bingo_card()
