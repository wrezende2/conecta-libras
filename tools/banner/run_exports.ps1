param(
  [string]$LogoPath = "C:\Users\Wellington\Downloads\Imagens Conecta-Libras\Blue and Orange Abstract Shape Studio.png",
  [string]$ProjectDir = "C:\Users\Wellington\CascadeProjects\conecta-libras-banner",
  [string]$OutAll = "C:\Users\Wellington\CascadeProjects\conecta-libras-banner\Exports_Preset_S_s020_Full",
  [string]$OutFinal = "C:\Users\Wellington\CascadeProjects\conecta-libras-banner\Exports_Final",
  [string]$Title = "Conecta Libras",
  [string]$Subtitle = "Comunicação inclusiva sem barreiras",
  [double]$LogoScale = 0.20,
  [double]$SubtitleGap = 1.6,
  [double]$TextShift = 0.0
)

$ErrorActionPreference = 'Stop'

Write-Host "Running exports from" $ProjectDir -ForegroundColor Cyan

# Ensure Python can import Pillow and script exists
$script = Join-Path $ProjectDir 'make_banner.py'
if (-not (Test-Path -LiteralPath $script)) {
  throw "make_banner.py not found at $script"
}

# 1) All social sizes (complete)
Write-Host "Generating ALL_SOCIAL preset..." -ForegroundColor Yellow
python $script --preset all_social --logo "$LogoPath" --title "$Title" --subtitle "$Subtitle" --logo-scale $LogoScale --subtitle-gap $SubtitleGap --text-shift $TextShift --zip --outdir "$OutAll"

# 2) Final kit (curated)
Write-Host "Generating FINAL_KIT preset..." -ForegroundColor Yellow
python $script --preset final_kit --logo "$LogoPath" --title "$Title" --subtitle "$Subtitle" --logo-scale $LogoScale --subtitle-gap $SubtitleGap --text-shift $TextShift --zip --outdir "$OutFinal"

Write-Host "Done. Folders: " -ForegroundColor Green
Write-Host "  All social -> $OutAll"
Write-Host "  Final kit  -> $OutFinal"
