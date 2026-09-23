#!/usr/bin/env python3
"""
================================================================================
Rastreamento e Análise Tática da Origem dos Gols: Lionel Messi vs Cristiano Ronaldo
================================================================================
Mapeia os pontos onde cada jogador RECEBEU a bola antes de marcar o gol, cobrindo
suas carreiras através da fusão de dados da StatsBomb Open Data e WhoScored (Opta).

Regra da Posse Individual (Reset de Posse):
- O rastreamento parte do chute a gol e retrocede no tempo dentro do lance.
- Se o jogador passar a bola e recebê-la novamente, a posse anterior reseta:
  o ponto registrado é o da recepção final da bola que culminou na finalização.
- Se for cobrança de falta direta, pênalti ou rebote direto de primeira,
  o ponto registrado é o local da finalização.
"""

import os
import sys
import math
import pickle
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mplsoccer import VerticalPitch

# Paleta de Cores
COR_MESSI = "#00e5ff"       # Ciano vibrante
COR_CRISTIANO = "#ff3366"   # Rosa / Vermelho contrastante

def get_data_path(filename):
    """Busca o arquivo de dados na pasta data/ ou na raiz do projeto."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "data", filename),
        os.path.join(script_dir, filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

def get_output_path(filename):
    """Gera o caminho de saída na pasta assets/ e na raiz."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    return os.path.join(assets_dir, filename)

def save_plot_dual(fig, filename):
    """Salva a figura na pasta assets/."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(script_dir, "assets", filename)
    fig.savefig(path_assets, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"-> Gráfico salvo em assets/{filename}")



# ==============================================================================
# 1. PONTOS INDIVIDUAIS LIMPOS (SCATTER EM MEIO CAMPO ESCURO)
# ==============================================================================
def plot_receipt_points_individual(df_goals, player_name, color, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    fig, ax = pitch.draw(figsize=(9, 11))
    fig.set_facecolor("#0a0c11")
    
    dists = np.sqrt((120 - df_goals["receipt_x"])**2 + (40 - df_goals["receipt_y"])**2) * 0.9144
    avg_dist = dists.mean()
    
    pitch.scatter(
        df_goals["receipt_x"],
        df_goals["receipt_y"],
        s=68,
        color=color,
        edgecolors="#ffffff",
        linewidth=0.6,
        alpha=0.72,
        zorder=4,
        ax=ax
    )
    
    fig.text(0.5, 0.94, player_name.upper(), fontsize=21, fontweight="bold", color="#ffffff", ha="center")
    fig.text(0.5, 0.915, "BALL RECEIPT LOCATIONS IN GOALSCORING ACTIONS", fontsize=10, fontweight="bold", color=color, ha="center")
    fig.text(0.5, 0.89, f"Total: {len(df_goals)} Mapped Goals  |  Avg. Receipt Distance: {avg_dist:.1f}m  |  StatsBomb & WhoScored/Opta",
             fontsize=9, color="#94a3b8", ha="center")
    fig.text(0.5, 0.05, "* 1st touch in the final individual possession preceding the goal (resets if passed to a teammate)",
             fontsize=8.5, fontstyle="italic", color="#64748b", ha="center")
    
    save_plot_dual(fig, filename)


# ==============================================================================
# 2. PAINEL COMPARATIVO LADO A LADO (DISPERSÃO DE PONTOS)
# ==============================================================================
def plot_side_by_side_comparison(df_messi, df_cr7, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    fig, axs = pitch.draw(nrows=1, ncols=2, figsize=(16, 11))
    fig.set_facecolor("#0a0c11")
    
    # 1. Messi (Esquerda)
    dist_m = np.sqrt((120 - df_messi["receipt_x"])**2 + (40 - df_messi["receipt_y"])**2) * 0.9144
    pitch.scatter(
        df_messi["receipt_x"], df_messi["receipt_y"],
        s=65, color=COR_MESSI, edgecolors="#ffffff", linewidth=0.6, alpha=0.72, zorder=4, ax=axs[0]
    )
    axs[0].set_title(
        f"LIONEL MESSI\n{len(df_messi)} Mapped Goals | Avg. Dist: {dist_m.mean():.1f}m",
        fontsize=14, fontweight="bold", color=COR_MESSI, pad=15
    )
    
    # 2. Cristiano Ronaldo (Direita)
    dist_c = np.sqrt((120 - df_cr7["receipt_x"])**2 + (40 - df_cr7["receipt_y"])**2) * 0.9144
    pitch.scatter(
        df_cr7["receipt_x"], df_cr7["receipt_y"],
        s=75, color=COR_CRISTIANO, edgecolors="#ffffff", linewidth=0.7, alpha=0.8, zorder=4, ax=axs[1]
    )
    axs[1].set_title(
        f"CRISTIANO RONALDO\n{len(df_cr7)} Mapped Goals | Avg. Dist: {dist_c.mean():.1f}m",
        fontsize=14, fontweight="bold", color=COR_CRISTIANO, pad=15
    )
    
    fig.suptitle(
        "GOAL ORIGINS: CAREER BALL RECEIPT LOCATIONS",
        fontsize=19, fontweight="bold", color="#ffffff", y=0.98
    )
    fig.text(
        0.5, 0.935,
        "Comparison of 1st touch in final individual possession (resets upon pass) | Data: StatsBomb & WhoScored/Opta",
        fontsize=10, color="#94a3b8", ha="center"
    )
    
    save_plot_dual(fig, filename)


# ==============================================================================
# 3. MAPAS DE DENSIDADE (HEXBIN E JITTER) INDIVIDUAIS
# ==============================================================================
def plot_density_individual(df_goals, player_name, color, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    fig, axs = pitch.draw(nrows=1, ncols=2, figsize=(16, 11))
    fig.set_facecolor("#0a0c11")

    np.random.seed(42)
    jitter_x = df_goals["receipt_x"] + np.random.uniform(-0.6, 0.6, len(df_goals))
    jitter_y = df_goals["receipt_y"] + np.random.uniform(-0.6, 0.6, len(df_goals))

    pitch.scatter(
        jitter_x, jitter_y,
        s=55, color=color, edgecolors="#ffffff", linewidth=0.5, alpha=0.75, zorder=4, ax=axs[0]
    )
    axs[0].set_title(f"INDIVIDUAL SCATTER ({len(df_goals)} POINTS WITH JITTER)\nPrevents overlapping points from hiding",
                     fontsize=12, fontweight="bold", color=color, pad=15)

    hexmap = pitch.hexbin(
        df_goals["receipt_x"], df_goals["receipt_y"],
        ax=axs[1], edgecolors="#12151d", gridsize=(18, 18), cmap="magma", zorder=3, mincnt=1
    )
    axs[1].set_title("DENSITY MAP (HEXBIN)\nWarmer colors indicate accumulation of multiple goals",
                     fontsize=12, fontweight="bold", color="#ff70a6", pad=15)

    cbar = fig.colorbar(hexmap, ax=axs[1], orientation="vertical", shrink=0.6, pad=0.03)
    cbar.set_label("Number of Goals Received in Cell", color="#e2e8f0", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="#e2e8f0")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#e2e8f0")

    fig.suptitle(f"EVIDENCE & DENSITY OF {len(df_goals)} GOALS BY {player_name.upper()}",
                 fontsize=18, fontweight="bold", color="#ffffff", y=0.98)
    fig.text(0.5, 0.94, "Position of 1st touch in final individual possession | StatsBomb & WhoScored/Opta",
             fontsize=10, color="#94a3b8", ha="center")

    save_plot_dual(fig, filename)


# ==============================================================================
# 4. COMPARAÇÃO NORMALIZADA POR % RELATIVA (ANULA DISPARIDADE DE AMOSTRA)
# ==============================================================================
def plot_normalized_percentage_comparison(df_messi, df_cr7, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    n_m = len(df_messi)
    n_c = len(df_cr7)
    weights_m = np.ones(n_m) / n_m * 100.0
    weights_c = np.ones(n_c) / n_c * 100.0
    grid = (16, 16)

    # Identificar vmax conjunto
    test_fig, test_ax = plt.subplots()
    hb_m_test = test_ax.hexbin(df_messi["receipt_x"], df_messi["receipt_y"], C=weights_m, reduce_C_function=np.sum, gridsize=grid)
    max_m = hb_m_test.get_array().max() if len(hb_m_test.get_array()) > 0 else 10.0
    hb_c_test = test_ax.hexbin(df_cr7["receipt_x"], df_cr7["receipt_y"], C=weights_c, reduce_C_function=np.sum, gridsize=grid)
    max_c = hb_c_test.get_array().max() if len(hb_c_test.get_array()) > 0 else 10.0
    plt.close(test_fig)
    shared_vmax = max(max_m, max_c)

    fig, axs = pitch.draw(nrows=1, ncols=2, figsize=(16, 11))
    fig.set_facecolor("#0a0c11")

    # Messi
    pitch.hexbin(
        df_messi["receipt_x"], df_messi["receipt_y"],
        C=weights_m, reduce_C_function=np.sum,
        ax=axs[0], edgecolors="#12151d", gridsize=grid, cmap="magma",
        vmin=0, vmax=shared_vmax, zorder=3, mincnt=1
    )
    axs[0].set_title(
        f"LIONEL MESSI ({n_m} Goals)\nRelative Receipt Frequency by Zone",
        fontsize=13, fontweight="bold", color=COR_MESSI, pad=15
    )

    # Cristiano
    hb_c = pitch.hexbin(
        df_cr7["receipt_x"], df_cr7["receipt_y"],
        C=weights_c, reduce_C_function=np.sum,
        ax=axs[1], edgecolors="#12151d", gridsize=grid, cmap="magma",
        vmin=0, vmax=shared_vmax, zorder=3, mincnt=1
    )
    axs[1].set_title(
        f"CRISTIANO RONALDO ({n_c} Goals)\nRelative Receipt Frequency by Zone",
        fontsize=13, fontweight="bold", color=COR_CRISTIANO, pad=15
    )

    cbar_ax = fig.add_axes([0.92, 0.25, 0.015, 0.5])
    cbar = fig.colorbar(hb_c, cax=cbar_ax)
    cbar.set_label("% of Player's Total Goals Originating in Cell", color="#e2e8f0", fontsize=9.5)
    cbar.ax.yaxis.set_tick_params(color="#e2e8f0")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#e2e8f0")

    fig.suptitle("NORMALIZED PROPORTIONAL COMPARISON (% OF GOALS)",
                 fontsize=18, fontweight="bold", color="#ffffff", y=0.98)
    fig.text(
        0.5, 0.935,
        f"Data normalized by each player's individual total (eliminates sample size bias) | Identical scale: 0 to {shared_vmax:.1f}%",
        fontsize=10, color="#94a3b8", ha="center"
    )

    save_plot_dual(fig, filename)


# ==============================================================================
# 5. MAPA DE CONTRASTE TÁTICO DIRETO (DIFERENÇA LÍQUIDA % MESSI VS % CR7)
# ==============================================================================
def plot_tactical_contrast_map(df_messi, df_cr7, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    bins = (18, 14)
    stat_m = pitch.bin_statistic(df_messi["receipt_x"], df_messi["receipt_y"], statistic="count", bins=bins)
    stat_c = pitch.bin_statistic(df_cr7["receipt_x"], df_cr7["receipt_y"], statistic="count", bins=bins)

    pct_m = stat_m["statistic"] / len(df_messi) * 100.0
    pct_c = stat_c["statistic"] / len(df_cr7) * 100.0
    diff_pct = pct_m - pct_c

    mask = (stat_m["statistic"] == 0) & (stat_c["statistic"] == 0)
    diff_pct_masked = np.where(mask, np.nan, diff_pct)

    stat_diff = stat_m.copy()
    stat_diff["statistic"] = diff_pct_masked

    fig, ax = pitch.draw(figsize=(10, 12))
    fig.set_facecolor("#0a0c11")

    cmap_diff = mcolors.LinearSegmentedColormap.from_list(
        "messi_vs_cr7",
        [COR_CRISTIANO, "#1a1e29", COR_MESSI]
    )
    limit = np.nanmax(np.abs(diff_pct_masked))

    heatmap = pitch.heatmap(
        stat_diff, ax=ax, cmap=cmap_diff, vmin=-limit, vmax=limit,
        edgecolors="#12151d", linewidth=0.5
    )

    fig.text(0.5, 0.94, "TACTICAL CONTRAST: WHERE EACH PLAYER RECEIVES MORE", fontsize=18, fontweight="bold", color="#ffffff", ha="center")
    fig.text(0.5, 0.915, "Net Proportional Difference (% Messi vs % Cristiano Ronaldo)", fontsize=10, fontweight="bold", color="#94a3b8", ha="center")
    fig.text(0.5, 0.89, "Calculated using normalized bins: eliminates match volume disparity", fontsize=9, color="#64748b", ha="center")

    cbar = fig.colorbar(heatmap, ax=ax, orientation="horizontal", shrink=0.55, pad=0.04)
    cbar.set_label("← CR7 Dominance (% relative)       |       Messi Dominance (% relative) →", color="#e2e8f0", fontsize=9)
    cbar.ax.xaxis.set_tick_params(color="#e2e8f0")
    plt.setp(plt.getp(cbar.ax.axes, "xticklabels"), color="#e2e8f0")

    save_plot_dual(fig, filename)


# ==============================================================================
# 6. DENSIDADE CONTÍNUA (KDE / HEATMAP SUAVE)
# ==============================================================================
def plot_kde_comparison(df_messi, df_cr7, filename):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color="#12151d",
        line_color="#2b3242",
        linewidth=1.4,
        goal_type="box",
        pad_top=4,
        pad_bottom=3
    )
    fig, axs = pitch.draw(nrows=1, ncols=2, figsize=(16, 11))
    fig.set_facecolor("#0a0c11")

    # Messi KDE
    pitch.kdeplot(
        df_messi["receipt_x"], df_messi["receipt_y"],
        ax=axs[0], cmap="plasma", fill=True, levels=60, thresh=0.08, zorder=2, alpha=0.85
    )
    pitch.scatter(
        df_messi["receipt_x"], df_messi["receipt_y"],
        s=12, color=COR_MESSI, alpha=0.3, zorder=3, ax=axs[0]
    )
    axs[0].set_title(
        f"LIONEL MESSI ({len(df_messi)} Goals)\nContinuous Density Surface (KDE)",
        fontsize=13, fontweight="bold", color=COR_MESSI, pad=15
    )

    # CR7 KDE
    pitch.kdeplot(
        df_cr7["receipt_x"], df_cr7["receipt_y"],
        ax=axs[1], cmap="plasma", fill=True, levels=60, thresh=0.08, zorder=2, alpha=0.85
    )
    pitch.scatter(
        df_cr7["receipt_x"], df_cr7["receipt_y"],
        s=15, color=COR_CRISTIANO, alpha=0.3, zorder=3, ax=axs[1]
    )
    axs[1].set_title(
        f"CRISTIANO RONALDO ({len(df_cr7)} Goals)\nContinuous Density Surface (KDE)",
        fontsize=13, fontweight="bold", color=COR_CRISTIANO, pad=15
    )

    fig.suptitle("CONTINUOUS RECEIPT DENSITY (KDE / SMOOTH HEATMAP)",
                 fontsize=18, fontweight="bold", color="#ffffff", y=0.98)
    fig.text(0.5, 0.94, "Continuous spatial probability surface independent of raw sample count",
             fontsize=10, color="#94a3b8", ha="center")

    save_plot_dual(fig, filename)


# ==============================================================================
# FLUXO PRINCIPAL
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Analysis and Visualization of Goal Origins: Messi vs Cristiano Ronaldo")
    parser.add_argument("--jogador", type=str, default="ambos", choices=["messi", "cristiano", "ambos"],
                        help="Player to plot: 'messi', 'cristiano', or 'ambos'")
    parser.add_argument("--densidade", action="store_true", default=False,
                        help="Generate individual and comparative hexbin density maps")
    parser.add_argument("--normalizado", action="store_true", default=False,
                        help="Generate 100%% normalized comparisons (relative frequency & tactical contrast)")
    parser.add_argument("--todos", action="store_true", default=False,
                        help="Generate ALL charts (scatter, density, normalized, contrast, KDE)")
    args = parser.parse_args()
    
    path_messi = get_data_path("messi_goals.pkl")
    path_cr7_sb = get_data_path("cr7_goals.pkl")
    path_cr7_ws = get_data_path("cr7_whoscored_goals.pkl")
    
    if not os.path.exists(path_messi) or not os.path.exists(path_cr7_sb):
        print(f"[ERROR] Data files not found in data/ or root directory.")
        sys.exit(1)
        
    df_messi = pd.read_pickle(path_messi)
    df_cr7_sb = pd.read_pickle(path_cr7_sb)
    
    cols = ["receipt_x", "receipt_y", "shot_x", "shot_y"]
    if os.path.exists(path_cr7_ws):
        with open(path_cr7_ws, "rb") as fp:
            cr7_ws_data = pickle.load(fp)
        df_cr7_ws = pd.DataFrame(cr7_ws_data)
        df_cr7 = pd.concat([df_cr7_sb[cols], df_cr7_ws[cols]], ignore_index=True)
        print("=" * 70)
        print("Career Ball Receipt Mapping in Goalscoring Plays (StatsBomb + WhoScored/Opta)")
        print("=" * 70)
        print(f"-> Lionel Messi: {len(df_messi)} mapped goals (StatsBomb Open Data)")
        print(f"-> Cristiano Ronaldo: {len(df_cr7)} mapped goals ({len(df_cr7_sb)} StatsBomb + {len(df_cr7_ws)} WhoScored/Opta)")
        print("-" * 70)
    else:
        df_cr7 = df_cr7_sb[cols]
        print(f"-> Lionel Messi: {len(df_messi)} mapped goals")
        print(f"-> Cristiano Ronaldo: {len(df_cr7)} mapped goals")

    # 1. Gráficos de Dispersão Limpos
    if args.jogador in ["messi", "ambos"]:
        plot_receipt_points_individual(df_messi, "Lionel Messi", COR_MESSI, "gols_carreira_messi.png")
        if args.densidade or args.todos:
            plot_density_individual(df_messi, "Lionel Messi", COR_MESSI, "evidencia_505_gols_messi.png")
        
    if args.jogador in ["cristiano", "ambos"]:
        plot_receipt_points_individual(df_cr7, "Cristiano Ronaldo", COR_CRISTIANO, "gols_carreira_cristiano.png")
        if args.densidade or args.todos:
            plot_density_individual(df_cr7, "Cristiano Ronaldo", COR_CRISTIANO, "evidencia_289_gols_cristiano.png")
        
    if args.jogador == "ambos":
        plot_side_by_side_comparison(df_messi, df_cr7, "comparacao_messi_cristiano.png")
        if args.densidade or args.todos:
            # Mapa de densidade hexbin bruto comparativo
            from mplsoccer import VerticalPitch
            pitch = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color="#12151d", line_color="#2b3242", linewidth=1.4, goal_type="box", pad_top=4, pad_bottom=3)
            fig, axs = pitch.draw(nrows=1, ncols=2, figsize=(16, 11))
            fig.set_facecolor("#0a0c11")
            hex_m = pitch.hexbin(df_messi["receipt_x"], df_messi["receipt_y"], ax=axs[0], edgecolors="#12151d", gridsize=(18, 18), cmap="magma", zorder=3, mincnt=1)
            axs[0].set_title(f"LIONEL MESSI ({len(df_messi)} GOALS)\nConcentration: Box Edge & Zone 14", fontsize=13, fontweight="bold", color=COR_MESSI, pad=15)
            cbar_m = fig.colorbar(hex_m, ax=axs[0], orientation="vertical", shrink=0.6, pad=0.03)
            cbar_m.set_label("Goals in Cell", color="#e2e8f0", fontsize=9)
            cbar_m.ax.yaxis.set_tick_params(color="#e2e8f0")
            plt.setp(plt.getp(cbar_m.ax.axes, "yticklabels"), color="#e2e8f0")
            hex_c = pitch.hexbin(df_cr7["receipt_x"], df_cr7["receipt_y"], ax=axs[1], edgecolors="#12151d", gridsize=(18, 18), cmap="magma", zorder=3, mincnt=1)
            axs[1].set_title(f"CRISTIANO RONALDO ({len(df_cr7)} GOALS)\nConcentration: Center of Box & Penalty Spot", fontsize=13, fontweight="bold", color=COR_CRISTIANO, pad=15)
            cbar_c = fig.colorbar(hex_c, ax=axs[1], orientation="vertical", shrink=0.6, pad=0.03)
            cbar_c.set_label("Goals in Cell", color="#e2e8f0", fontsize=9)
            cbar_c.ax.yaxis.set_tick_params(color="#e2e8f0")
            plt.setp(plt.getp(cbar_c.ax.axes, "yticklabels"), color="#e2e8f0")
            fig.suptitle("TACTICAL DENSITY COMPARISON: CAREER BALL RECEIPT LOCATIONS", fontsize=18, fontweight="bold", color="#ffffff", y=0.98)
            save_plot_dual(fig, "comparacao_densidade_messi_cristiano.png")

    # 2. Gráficos de Normalização Estatística e Contraste
    if args.normalizado or args.todos:
        print("-> Generating normalized analyses (relative %, tactical contrast, and KDE)...")
        plot_normalized_percentage_comparison(df_messi, df_cr7, "comparacao_normalizada_percentual.png")
        plot_tactical_contrast_map(df_messi, df_cr7, "contraste_tatico_messi_vs_cr7.png")
        plot_kde_comparison(df_messi, df_cr7, "comparacao_kde_suave.png")

    print("=" * 70)
    print("Processing completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
