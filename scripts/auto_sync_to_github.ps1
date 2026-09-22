param(
    [string]$Remote = "origin",
    [string]$Branch = "main"
)

$script:repoPath = (Get-Location).Path
$script:remoteName = $Remote
$script:branchName = $Branch

function Invoke-GitCommand {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')`n$output"
    }
    return $output
}

try {
    $remoteUrl = Invoke-GitCommand remote get-url $script:remoteName
    Write-Host "Remote actual: $remoteUrl"
} catch {
    Write-Host "No existe el remoto '$script:remoteName'. Primero crea el repositorio en GitHub y luego añade el remoto:"
    Write-Host "git remote add origin https://github.com/<usuario>/<repositorio>.git"
    Write-Host "git branch -M main"
    Write-Host "git push -u origin main"
    exit 1
}

Write-Host "Observando cambios en: $script:repoPath"
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $script:repoPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName, [System.IO.NotifyFilters]::DirectoryName, [System.IO.NotifyFilters]::LastWrite, [System.IO.NotifyFilters]::CreationTime

$action = {
    param($source, $eventArgs)

    try {
        Set-Location $script:repoPath

        $status = & git status --porcelain
        if (-not $status) {
            return
        }

        & git add -A
        $commitMessage = "Auto sync $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

        $commitResult = & git commit -m $commitMessage 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "No hubo cambios válidos para commitear: $commitResult"
            return
        }

        Write-Host "Commit creado: $commitMessage"
        & git push $script:remoteName $script:branchName

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Subido a GitHub correctamente."
        }
    } catch {
        Write-Host "Error durante la sincronización automática: $($_.Exception.Message)"
    }
}

Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action | Out-Null

Write-Host "El monitor está activo. Presiona Ctrl+C para detenerlo."
while ($true) { Start-Sleep -Seconds 2 }
