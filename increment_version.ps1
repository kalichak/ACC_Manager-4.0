# increment_version.ps1
$path = Join-Path (Get-Location).Path 'version.json'
$json = Get-Content $path -Raw | ConvertFrom-Json

# Divide a versão (ex: 4.0.1)
$parts = $json.current_version.Split('.')
$major = [int]$parts[0]
$minor = [int]$parts[1]
$patch = [int]$parts[2]

# Incrementa o patch
$patch++
$newVersion = "$major.$minor.$patch"
$json.current_version = $newVersion

# Salva
$json | ConvertTo-Json | Set-Content $path
Write-Output $newVersion