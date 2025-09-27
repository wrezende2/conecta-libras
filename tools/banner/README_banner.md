# Banner Generator (Conecta Libras)

This folder contains the Python generator and PowerShell helper to export all social sizes.

## Quick start

```powershell
pip install -r tools/banner/requirements.txt
powershell -ExecutionPolicy Bypass -File tools/banner/run_exports.ps1
```

Outputs are placed under `assets/banner/` and zipped for convenience.

## One‑liners

- All social sizes (PNG+JPG + ZIP):
```powershell
python tools/banner/make_banner.py --preset all_social --logo "assets/logo/wss_studio_art_logo.png" --title "Conecta Libras" --subtitle "Comunicação inclusiva sem barreiras" --logo-scale 0.20 --subtitle-gap 1.6 --outdir assets/banner/Exports_Preset_S_s020_Full --zip
```

- Final kit (PNG+JPG + ZIP):
```powershell
python tools/banner/make_banner.py --preset final_kit --logo "assets/logo/wss_studio_art_logo.png" --title "Conecta Libras" --subtitle "Comunicação inclusiva sem barreiras" --logo-scale 0.20 --subtitle-gap 1.6 --outdir assets/banner/Exports_Final --zip
```

- Dark theme + EXIF:
```powershell
python tools/banner/make_banner.py --preset final_kit --logo "assets/logo/wss_studio_art_logo.png" --title "Conecta Libras" --subtitle "Comunicação inclusiva sem barreiras" --logo-scale 0.20 --subtitle-gap 1.6 --dark --exif-artist "WSS Studio Art" --exif-copyright "© WSS Studio Art. Todos os direitos reservados." --exif-description "Conecta Libras — Comunicação inclusiva sem barreiras" --outdir assets/banner/Exports_Final_Dark --zip
```

## GitHub Action

This repo includes `.github/workflows/banner-build.yml`. On each push that touches `tools/banner/**` or `assets/logo/**`, the workflow builds and uploads artifacts with the whole set (light and dark).
