& {
    Set-StrictMode -Version Latest
    $ErrorActionPreference = "Stop"

    function Stop-WithMessage {
        param([string] $Message)
        Write-Error $Message
        throw $Message
    }

    function Read-EnvFile {
        param([string] $Path)

        $values = @{}

        foreach ($line in Get-Content -LiteralPath $Path) {
            $trimmed = $line.Trim()
            if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#")) {
                continue
            }

            $separator = $trimmed.IndexOf("=")
            if ($separator -lt 0) {
                continue
            }

            $name = $trimmed.Substring(0, $separator).Trim()
            $value = $trimmed.Substring($separator + 1).Trim()

            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }

            if ($name.Length -gt 0) {
                $values[$name] = $value
                [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }

        return $values
    }

    function Get-OrchestrateEnvironmentEntry {
        param(
            [string] $ListOutput,
            [string] $Name
        )

        foreach ($line in ($ListOutput -split "\r?\n")) {
            $trimmed = $line.Trim()
            if ($trimmed.Length -eq 0) {
                continue
            }

            $withoutActive = ($trimmed -replace "\s*\(active\)\s*", " ")
            $tokens = $withoutActive -split "[\s|]+" | Where-Object { $_.Length -gt 0 }
            if ($tokens -contains $Name) {
                return $trimmed
            }
        }

        return $null
    }

    $scriptDir = Split-Path -Parent $PSCommandPath
    $repoRoot = Split-Path -Parent $scriptDir

    $envPath = Join-Path $repoRoot ".env"
    $activatePath = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"
    $pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
    $orchestratePath = Join-Path $repoRoot ".venv\Scripts\orchestrate.exe"

    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        Stop-WithMessage "Missing .env. Copy .env.example to .env and fill the required local values."
    }

    if (-not (Test-Path -LiteralPath $activatePath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $pythonPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $orchestratePath -PathType Leaf)) {
        Stop-WithMessage "Missing repository .venv. Create or restore the project virtual environment before starting a development session."
    }

    $envValues = Read-EnvFile -Path $envPath
    $requiredNames = @(
        "WX_API_KEY",
        "WX_PROJECT_ID",
        "WX_URL",
        "WXO_ENV_NAME",
        "WXO_API_KEY"
    )

    $missing = @()
    foreach ($name in $requiredNames) {
        if (-not $envValues.ContainsKey($name) -or [string]::IsNullOrWhiteSpace([string] $envValues[$name])) {
            $missing += $name
        }
    }

    if ($missing.Count -gt 0) {
        Write-Error ("Missing required .env values: " + ($missing -join ", "))
        throw "Missing required .env values."
    }

    $envName = [string] $envValues["WXO_ENV_NAME"]
    $orchestrateKey = [string] $envValues["WXO_API_KEY"]

    . $activatePath

    $pythonVersion = (& $pythonPath --version 2>&1 | Out-String).Trim()
    $orchestrateVersionOutput = (& $orchestratePath --version 2>&1 | Out-String).Trim()
    $adkLine = ($orchestrateVersionOutput -split "\r?\n" | Where-Object { $_ -match "^ADK Version:" } | Select-Object -First 1)
    if ([string]::IsNullOrWhiteSpace($adkLine)) {
        Stop-WithMessage "Unable to verify Orchestrate ADK version with the repository-local executable."
    }

    $envListBefore = (& $orchestratePath env list 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "Unable to inspect local Orchestrate environment definitions."
    }

    $envEntryBefore = Get-OrchestrateEnvironmentEntry -ListOutput $envListBefore -Name $envName
    if ($null -eq $envEntryBefore) {
        Stop-WithMessage "Orchestrate environment '$envName' is not configured locally. Setup is required; this script will not create it."
    }

    $null = & $orchestratePath env activate $envName --api-key $orchestrateKey 2>&1
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "Failed to activate Orchestrate environment '$envName'."
    }

    $envListAfter = (& $orchestratePath env list 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "Unable to verify active Orchestrate environment."
    }

    $envEntryAfter = Get-OrchestrateEnvironmentEntry -ListOutput $envListAfter -Name $envName
    if ($null -eq $envEntryAfter -or $envEntryAfter -notmatch "\s\(active\)(\s|$)") {
        Stop-WithMessage "Orchestrate environment '$envName' was not reported as active after activation."
    }

    Write-Host "Development session ready."
    Write-Host "Python: $pythonVersion"
    Write-Host "Orchestrate ADK: $adkLine"
    Write-Host "Orchestrate environment: $envName (active)"
    Write-Host "watsonx.ai configuration: loaded"
    Write-Host "Project ID: loaded"
    Write-Host "Secrets: not displayed"
}
