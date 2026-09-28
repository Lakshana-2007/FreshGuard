"""
generate_synthetic_m3_data.py — Reproducible Generator for M3 Synthetic Datasets

DATA_TYPE = SYNTHETIC

IMPORTANT DISCLAIMER:
- All datasets produced by this script are purely SYNTHETIC demonstrations.
- Never represent these synthetic observations as real-world experimental measurements.
- Generated targets are calculated from physically plausible domain equations + controlled noise.
- Designed strictly for demonstration and software pipeline verification across 5 food categories:
    1. Vegetables (Leafy / Root / Cruciferous)
    2. Meat & Poultry (Chicken / Beef / Pork)
    3. Bakery Products (Bread / Pastry / Cake)
    4. Packaged Foods (Snacks / Ready-Meals / Canned)
    5. Beverages (Juice / Milk Alternative / Tea-Coffee)
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "synthetic_m3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
N_ROWS_PER_CATEGORY = 1200  # >= 1000 observations per category

np.random.seed(RANDOM_SEED)

CATEGORIES_CONFIG = {
    "vegetables": {
        "product_types": ["Spinach", "Lettuce", "Broccoli", "Carrot", "Bell Pepper"],
        "temp_range": (2.0, 12.0),       # °C
        "humidity_range": (80.0, 98.0),   # %
        "duration_range": (0.0, 14.0),    # days
        "packaging_types": ["perforated", "sealed", "open"],
        "base_shelf_life": 12.0,          # days at optimal (4°C, 95% RH, sealed, day 0)
        "optimal_temp": 4.0,
        "optimal_rh": 95.0,
        "temp_decay_rate": 0.70,          # days lost per °C deviation
        "rh_decay_rate": 0.15,            # days lost per % RH deviation
        "packaging_modifiers": {
            "perforated": 0.0,
            "sealed": 1.0,
            "open": -2.0
        },
        "noise_std": 0.45,
    },
    "meat_poultry": {
        "product_types": ["Chicken Breast", "Ground Beef", "Pork Chop", "Turkey Cutlet"],
        "temp_range": (0.0, 8.0),         # °C
        "humidity_range": (65.0, 85.0),   # %
        "duration_range": (0.0, 8.0),     # days
        "packaging_types": ["modified_atmosphere", "vacuum_sealed", "airtight", "open"],
        "base_shelf_life": 7.0,           # days at optimal (1°C, 75% RH, vacuum_sealed, day 0)
        "optimal_temp": 1.0,
        "optimal_rh": 75.0,
        "temp_decay_rate": 0.90,          # days lost per °C deviation above optimal
        "rh_decay_rate": 0.05,
        "packaging_modifiers": {
            "modified_atmosphere": 1.5,
            "vacuum_sealed": 2.0,
            "airtight": 0.5,
            "open": -1.5
        },
        "noise_std": 0.35,
    },
    "bakery": {
        "product_types": ["Whole Wheat Bread", "Sourdough", "Croissant", "Muffin", "Bagel"],
        "temp_range": (15.0, 30.0),       # °C (ambient)
        "humidity_range": (40.0, 75.0),   # %
        "duration_range": (0.0, 10.0),    # days
        "packaging_types": ["paper", "sealed", "airtight", "open"],
        "base_shelf_life": 7.0,           # days at optimal (20°C, 50% RH, sealed, day 0)
        "optimal_temp": 20.0,
        "optimal_rh": 50.0,
        "temp_decay_rate": 0.35,          # warmth accelerates mold & staling
        "rh_decay_rate": 0.10,            # high humidity accelerates mold
        "packaging_modifiers": {
            "paper": -0.5,
            "sealed": 0.5,
            "airtight": 0.8,
            "open": -2.0
        },
        "noise_std": 0.40,
    },
    "packaged_foods": {
        "product_types": ["Ready Meal", "Fresh Pasta", "Tofu Block", "Hummus Tub", "Salad Kit"],
        "temp_range": (2.0, 10.0),        # °C
        "humidity_range": (45.0, 70.0),   # %
        "duration_range": (0.0, 25.0),    # days
        "packaging_types": ["modified_atmosphere", "sealed", "vacuum_sealed"],
        "base_shelf_life": 21.0,          # days at optimal (4°C, 55% RH, sealed, day 0)
        "optimal_temp": 4.0,
        "optimal_rh": 55.0,
        "temp_decay_rate": 1.10,
        "rh_decay_rate": 0.04,
        "packaging_modifiers": {
            "modified_atmosphere": 3.0,
            "vacuum_sealed": 4.0,
            "sealed": 0.0
        },
        "noise_std": 0.60,
    },
    "beverages": {
        "product_types": ["Fresh Orange Juice", "Almond Milk", "Cold Brew Coffee", "Kombucha", "Smoothie"],
        "temp_range": (2.0, 10.0),        # °C
        "humidity_range": (40.0, 70.0),   # %
        "duration_range": (0.0, 18.0),    # days
        "packaging_types": ["airtight", "sealed", "open"],
        "base_shelf_life": 14.0,          # days at optimal (4°C, 50% RH, airtight, day 0)
        "optimal_temp": 4.0,
        "optimal_rh": 50.0,
        "temp_decay_rate": 0.95,
        "rh_decay_rate": 0.02,
        "packaging_modifiers": {
            "airtight": 1.0,
            "sealed": 0.0,
            "open": -5.0                  # once opened, beverage degrades rapidly
        },
        "noise_std": 0.50,
    }
}


def generate_category_dataset(category_name: str, config: dict, n_rows: int) -> pd.DataFrame:
    """Generate a single category synthetic dataset adhering to physical rules with controlled noise."""
    products = np.random.choice(config["product_types"], size=n_rows)
    temps = np.round(np.random.uniform(config["temp_range"][0], config["temp_range"][1], size=n_rows), 1)
    humidity = np.round(np.random.uniform(config["humidity_range"][0], config["humidity_range"][1], size=n_rows), 1)
    durations = np.round(np.random.uniform(config["duration_range"][0], config["duration_range"][1], size=n_rows), 1)
    packagings = np.random.choice(config["packaging_types"], size=n_rows)
    
    # Calculate RSL based on deterministic physical model
    opt_temp = config["optimal_temp"]
    opt_rh = config["optimal_rh"]
    base_sl = config["base_shelf_life"]
    t_rate = config["temp_decay_rate"]
    rh_rate = config["rh_decay_rate"]
    pkg_mods = config["packaging_modifiers"]
    
    temp_penalty = np.maximum(0, temps - opt_temp) * t_rate
    rh_penalty = np.abs(humidity - opt_rh) * rh_rate
    pkg_bonus = np.array([pkg_mods.get(p, 0.0) for p in packagings])
    
    # Theoretical initial shelf life under these conditions
    initial_shelf_life = np.maximum(1.0, base_sl - temp_penalty - rh_penalty + pkg_bonus)
    
    # Remaining shelf life = initial_shelf_life - storage_duration_days
    raw_rsl = initial_shelf_life - durations
    
    # Add controlled Gaussian noise (ensure realistic variance without artificial perfection)
    noise = np.random.normal(0, config["noise_std"], size=n_rows)
    noisy_rsl = raw_rsl + noise
    
    # Clip remaining shelf life to non-negative floats
    final_rsl = np.clip(np.round(noisy_rsl, 1), 0.0, base_sl + 5.0)
    
    # Group assignment for GroupKFold validation
    group_ids = np.random.randint(1, 21, size=n_rows)  # 20 distinct batches/groups
    
    df = pd.DataFrame({
        "product_type": products,
        "storage_temperature_c": temps,
        "humidity_pct": humidity,
        "storage_duration_days": durations,
        "packaging_type": packagings,
        "remaining_shelf_life_days": final_rsl,
        "group_id": group_ids,
        "data_type": "SYNTHETIC"
    })
    
    return df


def main():
    print("Generating Synthetic M3 Datasets...")
    summary_records = []
    
    for cat_name, config in CATEGORIES_CONFIG.items():
        df = generate_category_dataset(cat_name, config, N_ROWS_PER_CATEGORY)
        output_file = OUTPUT_DIR / f"{cat_name}_synthetic.csv"
        df.to_csv(output_file, index=False)
        print(f"  -> Saved {output_file.name}: {len(df)} rows, target range [{df['remaining_shelf_life_days'].min()}, {df['remaining_shelf_life_days'].max()}] days")
        
        summary_records.append({
            "category": cat_name,
            "rows": len(df),
            "file": str(output_file.name),
            "temp_range": f"{df['storage_temperature_c'].min()} - {df['storage_temperature_c'].max()} °C",
            "humidity_range": f"{df['humidity_pct'].min()} - {df['humidity_pct'].max()} %",
            "duration_range": f"{df['storage_duration_days'].min()} - {df['storage_duration_days'].max()} days",
            "packaging_types": ", ".join(sorted(df['packaging_type'].unique())),
            "rsl_mean": round(float(df['remaining_shelf_life_days'].mean()), 2),
            "rsl_std": round(float(df['remaining_shelf_life_days'].std()), 2)
        })
        
    # Write README in synthetic directory
    readme_path = OUTPUT_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Synthetic M3 Food Freshness Datasets\n\n")
        f.write("## ⚠️ CRITICAL NOTICE: ALL DATA IN THIS DIRECTORY IS PURELY SYNTHETIC\n\n")
        f.write("- **DATA_TYPE**: `SYNTHETIC`\n")
        f.write("- **Purpose**: Pipeline demonstration, testing, and multi-category UI extension for FreshGuard M3.\n")
        f.write("- **Provenance**: Algorithmic generation via `generate_synthetic_m3_data.py` (Fixed seed: 42).\n")
        f.write("- **DISCLAIMER**: NEVER represent these records as real-world empirical observations or laboratory measurements.\n\n")
        f.write("## Generated Categories Summary\n\n")
        f.write("| Category | Rows | Temp Range (°C) | Humidity Range (%) | Packaging Types | Mean RSL (Days) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for s in summary_records:
            f.write(f"| {s['category']} | {s['rows']} | {s['temp_range']} | {s['humidity_range']} | {s['packaging_types']} | {s['rsl_mean']} ± {s['rsl_std']} |\n")

    print(f"\nAll datasets and documentation generated successfully in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
