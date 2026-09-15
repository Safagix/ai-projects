[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -Raw "$ProjectRoot\models\manifest.json" | ConvertFrom-Json
$drive = Get-Volume -DriveLetter D
$gpu = Get-CimInstance Win32_VideoController | Where-Object Name -match 'NVIDIA' | Select-Object -First 1
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
$gpuMemory = if ($nvidiaSmi) { (& $nvidiaSmi.Source --query-gpu=memory.total --format=csv,noheader,nounits | Select-Object -First 1).Trim() } else { 'unavailable' }

[pscustomobject]@{
  FreeDiskGB = [math]::Round($drive.SizeRemaining / 1GB, 2)
  Gpu = $gpu.Name
  NvidiaMemoryMiB = $gpuMemory
  CpuThreads = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
  ModelsDeclared = $manifest.models.Count
} | Format-List

foreach ($model in $manifest.models) {
  $target = Join-Path $ProjectRoot $model.target_directory
  [pscustomobject]@{ Model = $model.id; Installed = Test-Path $target; Runtime = $model.runtime; Target = $target } | Format-Table -AutoSize
}
