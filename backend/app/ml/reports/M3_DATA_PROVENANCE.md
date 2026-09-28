# FreshGuard M3 — Complete Data & Model Provenance Report

## 1. Executive Summary & Provenance Pipeline

This report provides complete, verifiable cryptographic SHA-256 hashes, filesystem timestamps, git tracking status, and transformation script lineage for all raw files, processed training datasets, and saved `.joblib` regression models used in FreshGuard M3.

```
[Raw Experimental Files] 
       ↓ (d:/infosys/scratch/update_phase3_provenance.py / build_phase3_datasets.py)
[Processed CSV Datasets in backend/app/ml/datasets/processed/]
       ↓ (d:/infosys/project 1/backend/app/ml/train_m3_models.py)
[Saved .joblib Pipelines in backend/app/ml/saved_models/]
```

---

## 2. Raw File Audit

### 2.1 Tomato Raw Files (8 files)

| File Name | Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Git Tracked? | Script Lineage |
|---|---|---:|---|---|:---:|---|
| `AA_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\AA_Tomato_NLED_BWC.xlsx` | 18687 | 2026-09-24T10:57:36.016111 | `75b268ee15d96a79...` | NO | Pre-existing in workspace dataset directory |
| `Decay_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\Decay_Tomato_NLED_BWC.xlsx` | 19585 | 2026-09-24T10:57:36.083858 | `06ac3414235384a3...` | NO | Pre-existing in workspace dataset directory |
| `Marketability_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\Marketability_Tomato_NLED_BWC.xlsx` | 17710 | 2026-09-24T10:57:36.165074 | `ee84533870b527c6...` | NO | Pre-existing in workspace dataset directory |
| `pH_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\pH_Tomato_NLED_BWC.xlsx` | 18214 | 2026-09-24T10:57:36.242075 | `0d28d3981f0e691d...` | NO | Pre-existing in workspace dataset directory |
| `Shelflife_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\Shelflife_Tomato_NLED_BWC.xlsx` | 15970 | 2026-09-24T10:57:36.385392 | `778553737d617153...` | NO | Pre-existing in workspace dataset directory |
| `TA_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\TA_Tomato_NLED_BWC.xlsx` | 21277 | 2026-09-24T10:57:35.940799 | `64833faa13d93f6a...` | NO | Pre-existing in workspace dataset directory |
| `TSS_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\TSS_Tomato_NLED_BWC.xlsx` | 18188 | 2026-09-24T10:57:35.776371 | `17c389b7e200b99f...` | NO | Pre-existing in workspace dataset directory |
| `WL_Tomato_NLED_BWC.xlsx` | `D:\infosys\project 1\dataset\WL_Tomato_NLED_BWC.xlsx` | 18497 | 2026-09-24T10:57:35.869679 | `2b8c6ce7bdfaaa33...` | NO | Pre-existing in workspace dataset directory |

### 2.2 Paneer Raw Files (2 files)

| File Name | Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Git Tracked? | Script Lineage |
|---|---|---:|---|---|:---:|---|
| `20241118_DataLog.csv` | `D:\infosys\scratch\paneer_data\20241118_DataLog.csv` | 68695 | 2026-09-24T14:27:59.690304 | `e9536ba25ddd2685...` | NO | Fetched / downloaded by audit script in scratch |
| `20241230_Testing_Data.xlsx` | `D:\infosys\scratch\paneer_data\20241230_Testing_Data.xlsx` | 29485 | 2026-09-24T14:28:01.603897 | `85aa7f7cf7c49a84...` | NO | Fetched / downloaded by audit script in scratch |

### 2.3 Chicken Raw Files (4 files)

| File Name | Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Git Tracked? | Script Lineage |
|---|---|---:|---|---|:---:|---|
| `Parameters from survival models.xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\round3_data\ds1_chicken\Parameters from survival models.xlsx` | 24017 | 2026-09-24T13:39:05.221388 | `713830f0c5d6c4af...` | NO | Fetched / downloaded by audit script in scratch |
| `Raw data consumer test.xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\round3_data\ds1_chicken\Raw data consumer test.xlsx` | 94930 | 2026-09-24T13:39:07.322073 | `ce8c9679643bebcc...` | NO | Fetched / downloaded by audit script in scratch |
| `Raw data microbial counts.xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\round3_data\ds1_chicken\Raw data microbial counts.xlsx` | 37419 | 2026-09-24T13:38:58.593827 | `692ac4ef3ad17f07...` | NO | Fetched / downloaded by audit script in scratch |
| `Raw data Microbiota.xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\round3_data\ds1_chicken\Raw data Microbiota.xlsx` | 178627 | 2026-09-24T13:38:56.985429 | `57c0247b93cc4819...` | NO | Fetched / downloaded by audit script in scratch |

### 2.4 Seafood Raw Files (15 files)

| File Name | Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Git Tracked? | Script Lineage |
|---|---|---:|---|---|:---:|---|
| `19-01-2024(Makarel).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\19-01-2024(Makarel).xlsx` | 27236 | 2026-09-24T13:46:39.605663 | `062d2c4e901ea809...` | NO | Fetched / downloaded by audit script in scratch |
| `19-01-2024(Mujair).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\19-01-2024(Mujair).xlsx` | 27738 | 2026-09-24T13:46:43.596548 | `f20c1933847c396d...` | NO | Fetched / downloaded by audit script in scratch |
| `19-01-2024(Tongkol).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\19-01-2024(Tongkol).xlsx` | 27626 | 2026-09-24T13:46:47.040127 | `e6560cf10a067066...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(MakarelSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(MakarelSesi1).xlsx` | 21215 | 2026-09-24T13:46:52.296514 | `c1e9a011ae261381...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(MakarelSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(MakarelSesi2).xlsx` | 21479 | 2026-09-24T13:46:57.656113 | `c08f986ff4cc27d1...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(MujairSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(MujairSesi1).xlsx` | 21264 | 2026-09-24T13:46:59.294995 | `ba5dd1a3d2fbade1...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(MujairSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(MujairSesi2).xlsx` | 21557 | 2026-09-24T13:47:01.638324 | `00b74e73ecc7d967...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(TongkolSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(TongkolSesi1).xlsx` | 21373 | 2026-09-24T13:47:03.557748 | `2ff0deeda78ccbb9...` | NO | Fetched / downloaded by audit script in scratch |
| `20-01-2024(TongkolSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\20-01-2024(TongkolSesi2).xlsx` | 21369 | 2026-09-24T13:47:05.543017 | `f80ec02727cac0db...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(MakarelSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(MakarelSesi1).xlsx` | 21358 | 2026-09-24T13:47:07.357505 | `43a49718f907b879...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(MakarelSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(MakarelSesi2).xlsx` | 21443 | 2026-09-24T13:47:10.004040 | `545f48ded38ec120...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(MujairSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(MujairSesi1).xlsx` | 21285 | 2026-09-24T13:47:14.541637 | `45c84a7d1d33f784...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(MujairSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(MujairSesi2).xlsx` | 21545 | 2026-09-24T13:47:16.383980 | `2f490c488f3b94de...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(TongkolSesi1).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(TongkolSesi1).xlsx` | 22028 | 2026-09-24T13:47:17.880490 | `bb5a1a4d4f6dbf37...` | NO | Fetched / downloaded by audit script in scratch |
| `21-01-2024(TongkolSesi2).xlsx` | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\21-01-2024(TongkolSesi2).xlsx` | 22186 | 2026-09-24T13:47:19.766855 | `fcc351b3c7c71c0d...` | NO | Fetched / downloaded by audit script in scratch |

---

## 3. Processed CSV Datasets (`backend/app/ml/datasets/processed/`)

| Category | Absolute File Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Generating Script |
|---|---|---:|---|---|---|
| **Tomato** | `D:\infosys\project 1\backend\app\ml\datasets\processed\tomato_training.csv` | 174272 | 2026-09-24T19:04:09.668585 | `411ecaee7639d49f9edf486be1cfa9b75597c5bd8f002473641d574d46ac5804` | `d:/infosys/scratch/update_phase3_provenance.py` |
| **Paneer** | `D:\infosys\project 1\backend\app\ml\datasets\processed\paneer_training.csv` | 3885 | 2026-09-24T19:04:09.673158 | `0446511195a9e218a92981e22d2123afa79cf4f26aaedbe1b8a4e2a0f10b18ef` | `d:/infosys/scratch/update_phase3_provenance.py` |
| **Chicken** | `D:\infosys\project 1\backend\app\ml\datasets\processed\chicken_training.csv` | 2736 | 2026-09-24T19:04:09.675160 | `c4eefe0502d6ff748d883251a8c18d85c8ca6d35d9496123e880b143a48fd580` | `d:/infosys/scratch/update_phase3_provenance.py` |
| **Seafood** | `D:\infosys\project 1\backend\app\ml\datasets\processed\seafood_training.csv` | 673230 | 2026-09-24T19:04:09.757100 | `262fdc2c870651600e6ab0b8ad8bb2a201b17e957b3b079f4da88c3d3f963343` | `d:/infosys/scratch/update_phase3_provenance.py` |

---

## 4. Saved `.joblib` Regression Models (`backend/app/ml/saved_models/`)

| Category | Absolute File Path | Size (bytes) | Modified Timestamp | SHA-256 Hash | Training Script | Input CSV |
|---|---|---:|---|---|---|---|
| **Tomato** | `D:\infosys\project 1\backend\app\ml\saved_models\tomato_rsl.joblib` | 5720666 | 2026-09-24T19:09:27.867646 | `dd46dc48b9b484c2ae75beffe65722b3e5e59e631279f8b876915a10da508578` | `d:/infosys/project 1/backend/app/ml/train_m3_models.py` | `D:\infosys\project 1\backend\app\ml\datasets\processed\tomato_training.csv` |
| **Paneer** | `D:\infosys\project 1\backend\app\ml\saved_models\paneer_rsl.joblib` | 3129 | 2026-09-24T19:09:28.344141 | `3642bf625a618671b1ab801a0e533300d4859e3d47ff0be923a16b508eab1de1` | `d:/infosys/project 1/backend/app/ml/train_m3_models.py` | `D:\infosys\project 1\backend\app\ml\datasets\processed\paneer_training.csv` |
| **Chicken** | `D:\infosys\project 1\backend\app\ml\saved_models\chicken_rsl.joblib` | 75220 | 2026-09-24T19:09:28.553679 | `b7d0287b72a05fcdd7d95abaf74087dab7907bfa3afeea999cc546d203c22f00` | `d:/infosys/project 1/backend/app/ml/train_m3_models.py` | `D:\infosys\project 1\backend\app\ml\datasets\processed\chicken_training.csv` |
| **Seafood** | `D:\infosys\project 1\backend\app\ml\saved_models\seafood_rsl.joblib` | 71242 | 2026-09-24T19:09:29.407363 | `91076c0ffec97367084fa1551be8c9da41737380c4df526bd79dff9127a29ab2` | `d:/infosys/project 1/backend/app/ml/train_m3_models.py` | `D:\infosys\project 1\backend\app\ml\datasets\processed\seafood_training.csv` |

---

## 5. External Origin Verification Statement

- **Tomato:** Files reside in `d:/infosys/project 1/dataset/`. Source: Dryad Digital Repository (`Shelflife_Tomato_NLED_BWC.xlsx`).
- **Paneer:** Files reside in `d:/infosys/scratch/paneer_data/`. Source: Mendeley Data Repository (DOI `10.17632/rd9dmr54xx.2`, `20241230_Testing_Data.xlsx`). Fetched via `scratch/fetch_mendeley_paneer.py`.
- **Chicken:** Files reside in `scratch/round3_data/ds1_chicken/`. Source: Dynamic MAP Chicken Breast Storage Study (`Raw data microbial counts.xlsx`).
- **Seafood:** Files reside in `scratch/dairy_seafood_audit/seafood/`. Source: DaFiF Fish Freshness Dataset (15 session `.xlsx` files). Fetched via `scratch/audit_fetch_dairy_seafood.py`.
- **Avocado:** *Origin could not be established from the local filesystem.* Raw dataset files are not available locally.
