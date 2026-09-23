# Goal Origins: Tactical Tracking of Ball Receipt Locations (Lionel Messi vs. Cristiano Ronaldo)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![mplsoccer](https://img.shields.io/badge/mplsoccer-1.8.1-orange.svg)](https://mplsoccer.readthedocs.io/)
[![Data: StatsBomb](https://img.shields.io/badge/Data-StatsBomb_Open_Data-red.svg)](https://github.com/statsbomb/open-data)
[![Data: Opta/WhoScored](https://img.shields.io/badge/Data-Opta_via_WhoScored-green.svg)](https://www.whoscored.com/)

A spatial and tactical analytics study exploring **where football's greatest goalscorers actually receive the ball before scoring**.

Conventional football analytics relies heavily on standard *shot maps*, which only capture the terminal coordinates $(x, y)$ of the shot itself. This project investigates the preceding phase: tracking the **first touch of the final individual possession** that led to each goal across the multi-decade careers of **Lionel Messi** and **Cristiano Ronaldo**.

> *"Conventional shot maps show where goals end. This project investigates where the scorer's final individual action begins."*

---

## 💡 Context & Prior Art

Inspired by earlier visualizations—such as **Marius Fischer's 2021 map** of the first touch preceding Lionel Messi's 648 Barcelona goals—this project approaches the same underlying tactical question programmatically, formalizing an **individual-possession reset rule** and extending the analysis to both **Lionel Messi** and **Cristiano Ronaldo** using granular event-level data.

### From Visual Concept to Reproducible Data Engineering
While visual precedents established the compelling nature of this question (frequently constructed via manual or semi-manual tagging), this repository introduces an automated, reproducible pipeline:

```text
Goal Event ──(Backwards Traversal)──> Scorer Events ──(Possession Reset / Return Pass)──> Receipt Coordinate (x, y)
```

1. **Automated Algorithmic Traversal:** Programmatic state machine navigating chronological event streams from match feeds, eliminating manual tagging or subjective bias.
2. **Comparative Paradigm (Messi vs. CR7):** Extending the methodology to directly contrast two all-time finishing archetypes across 794 career goals.
3. **Sample-Invariant Normalization:** Mitigating match volume and data availability disparities through relative frequency (% of goals) hexbins, net tactical contrast differential maps, and continuous 2D Kernel Density Estimation (KDE).
4. **Open Science & Reproducibility:** Fully accessible Python codebase, reusable scrapers, and structured data artifacts for community research.

---

## 🎯 Methodology: The Individual Possession Reset Rule

To isolate the player's direct action leading up to the goal, the tracking pipeline enforces an **individual possession reset rule**:

1. **Backwards Event Traversal:** For every registered goal, the algorithm starts at the shot event and traverses backwards through the sequential event chain within the same team possession and match half.
2. **Individual Possession Reset:** If the player receives the ball, passes it to a teammate, and subsequently receives a return pass before shooting, the earlier sequence resets. The tracked coordinate is strictly the **final ball receipt** immediately preceding the finish.
3. **Assisted Chances:** If the goal is preceded by an assist pass from a teammate, the receipt location is mapped directly to the pass terminus (`pass_end_location` / `endX, endY`).
4. **Individual Runs & Take-Ons:** If the player dribbles, takes on defenders, or controls the ball over distance before shooting, the tracked coordinate is the initial touch of that continuous run.
5. **Direct Actions:** For direct free kicks, penalties, or immediate first-time rebound strikes, the receipt coordinate matches the shot location.

---

## 📊 Dataset & Career Scope

To achieve comprehensive career coverage without commercial data subscriptions, this project fuses **StatsBomb Open Data** with granular **Opta event streams (via WhoScored)**:

| Metric | Lionel Messi | Cristiano Ronaldo |
| :--- | :--- | :--- |
| **Total Mapped Goals** | **505 goals** | **289 goals** |
| **Primary Data Sources** | StatsBomb Open Data (100%) | StatsBomb Open Data (19%) + WhoScored/Opta (81%) |
| **Competitions Covered** | La Liga (2004/05 – 2020/21), FIFA World Cups (2014, 2018, 2022) | Real Madrid / La Liga (14/15–17/18), Juventus / Serie A (18/19–20/21), Man Utd / Premier League (21/22), World Cup (2018), Euro (2020) |
| **Average Receipt Distance** | **15.9 meters** from goal | **14.0 meters** from goal |
| **Primary Receipt Profile** | Zone 14, half-spaces & deep midfield | Penalty box, 6-yard box & central penalty spot |

---

## 🖼️ Tactical Visualizations

### 1. Side-by-Side Spatial Scatter (Minimalist Dark Pitch)
Discrete points showing the exact first-touch receipt coordinate for all mapped goals:

![Messi vs Cristiano Ronaldo Career Goal Origins](assets/comparacao_messi_cristiano.png)

---

### 2. Relative Frequency Comparison (% Normalized Hexbin)
To remove sample size bias between Messi (505 goals) and Cristiano (289 goals), each hexagonal bin calculates the **percentage of that player's total goals** (`% of Total Goals`) using a **unified shared scale (0% to 18%)**:

![Relative Frequency Hexbin Comparison](assets/comparacao_normalizada_percentual.png)

---

### 3. Tactical Contrast Map (Net Advantage / Dominance)
Direct cell-by-cell subtraction (`% Messi − % Cristiano Ronaldo`), highlighting relative spatial specialization:
* **Cyan:** Zones where **Lionel Messi** receives the ball with significantly higher relative frequency.
* **Pink/Red:** Zones where **Cristiano Ronaldo** receives the ball with significantly higher relative frequency.
* **Dark/Neutral:** Zones with comparable proportional reception rates.

![Tactical Contrast Map](assets/contraste_tatico_messi_vs_cr7.png)

---

### 4. Continuous Kernel Density Estimation (Smooth KDE Heatmap)
Continuous 2D probability density function (*PDF*) capturing the gravitational spatial centers of each player, independent of raw sample size:

![Continuous KDE Density Comparison](assets/comparacao_kde_suave.png)

---

### 5. Individual Evidence & Concentration Plots (Jitter vs. Hexbin)

#### Lionel Messi (505 Goals Mapped)
![Messi 505 Goals Evidence](assets/evidencia_505_gols_messi.png)

#### Cristiano Ronaldo (289 Goals Mapped)
![Cristiano Ronaldo 289 Goals Evidence](assets/evidencia_289_gols_cristiano.png)

---

## 🧠 Key Tactical Insights

### 🇦🇷 Lionel Messi: The Playmaker-Finisher
* **Zone 14 Gravitational Pull:** Heavy concentration of receipts outside the 18-yard box and across the central half-spaces.
* **Deep Progression:** Frequently receives in the middle third or half-way line before accelerating into shooting range.
* **Higher Receipt Distance:** Average distance of **15.9m** confirms his role as both the primary creator and terminal executor.

### 🇵🇹 Cristiano Ronaldo: The Box Dominator
* **Penalty Box Concentration:** Peak density is concentrated inside the 6-yard box and near the penalty spot.
* **Elite Off-Ball Movement:** High volume of first-touch finishes resulting from runs into the blind spots of center-backs.
* **Shorter Receipt Distance:** Average distance of **14.0m** reflects his evolution into a penalty-box operator and header/poacher specialist.

---

## 🚀 Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/Jvamg/goal-origins-messi-vs-cr7.git
cd goal-origins-messi-vs-cr7
```

### 2. Set up virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Generate Visualizations
The script loads the pre-processed datasets stored in `data/` and generates high-resolution figures in `assets/`:

```bash
# Generate all charts at once (scatter, hexbin density, normalized % and contrast):
python3 visualizar_origem_gols_carreira.py --todos

# Generate scatter and raw hexbin density plots:
python3 visualizar_origem_gols_carreira.py --densidade

# Generate normalized statistical comparisons (% relative, contrast map, KDE):
python3 visualizar_origem_gols_carreira.py --normalizado

# Generate individual player visualizations:
python3 visualizar_origem_gols_carreira.py --jogador messi
python3 visualizar_origem_gols_carreira.py --jogador cristiano
```

### 4. Scraping Additional Seasons (Optional)
If you wish to re-run the data collection pipelines or extend to other leagues:
* `src/scraper_whoscored.py`: Downloads schedule calendars and event feeds from Opta/WhoScored for top European leagues.
* `src/scraper_statsbomb.py`: Queries and parses match events from the StatsBomb Open Data archive.

---

## 📁 Repository Structure

```text
goal-origins-messi-vs-cr7/
├── .gitignore                          # Ignores virtualenvs, caches, and raw scrape locks
├── README.md                           # Documentation, tactical analysis, and embedded visuals
├── requirements.txt                    # Project dependencies
├── visualizar_origem_gols_carreira.py  # Unified CLI analysis & plotting application
├── data/                               # Clean, lightweight processed datasets (~92 KB)
│   ├── messi_goals.pkl                 # 505 Messi goals with receipt coords
│   ├── cr7_goals.pkl                   # 56 CR7 goals via StatsBomb
│   └── cr7_whoscored_goals.pkl         # 233 CR7 goals via WhoScored/Opta
├── assets/                             # High-resolution generated tactical visualizations
│   ├── comparacao_messi_cristiano.png
│   ├── comparacao_normalizada_percentual.png
│   ├── contraste_tatico_messi_vs_cr7.png
│   ├── comparacao_kde_suave.png
│   ├── comparacao_densidade_messi_cristiano.png
│   ├── evidencia_505_gols_messi.png
│   ├── evidencia_289_gols_cristiano.png
│   ├── gols_carreira_messi.png
│   └── gols_carreira_cristiano.png
└── src/                                # Reusable scraping and data processing modules
    ├── __init__.py
    ├── scraper_statsbomb.py            # StatsBomb event parser
    └── scraper_whoscored.py            # Opta/WhoScored event parser
```

---

## 🛠️ Built With
* **[mplsoccer](https://mplsoccer.readthedocs.io/):** Football pitch drawings and event visualizations.
* **[StatsBombPy](https://github.com/statsbomb/statsbombpy):** Wrapper for StatsBomb Open Data.
* **[SoccerData](https://soccerdata.readthedocs.io/):** Web scraping interface for Opta/WhoScored feeds.
* **[Matplotlib](https://matplotlib.org/):** Core plotting, colormaps, and multi-panel figures.
* **[Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/):** Coordinate transformations, 2D binning, and kernel density estimation.

---

## 📚 References & Prior Precedent
* **Marius Fischer (2021):** Conceptual inspiration and early visual mapping of the first touch preceding Lionel Messi's 648 Barcelona goals.
* **[StatsBomb Open Data](https://github.com/statsbomb/open-data):** Open football event dataset covering Lionel Messi's complete La Liga career (2004/05–2020/21) and FIFA World Cups.
* **[WhoScored](https://www.whoscored.com/) / Opta:** Granular match event feeds accessed via `soccerdata` for European domestic competitions.
* **[mplsoccer Documentation](https://mplsoccer.readthedocs.io/):** Reference library for pitch topologies and coordinate transformations.
