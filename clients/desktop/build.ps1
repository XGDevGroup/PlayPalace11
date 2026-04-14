$ErrorActionPreference = "Stop"

# build.ps1 may be run from repo root; ensure uv uses the client/ pyproject.toml
$ClientDir = $PSScriptRoot

Write-Host "Building PlayPalace..."

Push-Location $ClientDir
try {
	uv run --no-sync --with pyinstaller --with pyinstaller-hooks-contrib --project $ClientDir pyinstaller -y --clean --onedir --noconsole --name PlayPalace --add-data "sounds;sounds" --add-data "defaults;defaults" client.py
	if ($LASTEXITCODE -ne 0) {
		throw "PyInstaller failed."
	}
} finally {
	Pop-Location
}

$dist = Join-Path $ClientDir "dist\PlayPalace"

# PyInstaller's directory layout can vary by version/options.
# The sounds folder might already be in the correct place, or it might be under _internal.
# Newer PyInstaller versions may also place --add-data into "<appname>\_internal\<dest>".
$srcCandidates = @(
	(Join-Path $dist "_internal\sounds"),
	(Join-Path $dist "sounds"),
	(Join-Path $dist "_internal\sounds\sounds")
)

$src = $srcCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
$dst = Join-Path $dist "sounds"

if (-not $src) {
	throw "Expected sounds folder not found. Looked for: $($srcCandidates -join ', ')"
}

# If the sounds folder is already at the destination, nothing to do.
if ((Resolve-Path $src).Path -eq (Resolve-Path $dst -ErrorAction SilentlyContinue).Path) {
	Write-Host "Build complete. Output in $dist"
	return
}

if (Test-Path $dst) {
	Remove-Item -Recurse -Force $dst
}

Move-Item -Force $src $dst

$defaultsSrc = Join-Path $dist "_internal\\defaults"
$defaultsDst = Join-Path $dist "defaults"
if (Test-Path $defaultsSrc) {
	if (Test-Path $defaultsDst) {
		Remove-Item -Recurse -Force $defaultsDst
	}
	Move-Item -Force $defaultsSrc $defaultsDst
}

Write-Host "Build complete. Output in $dist"
