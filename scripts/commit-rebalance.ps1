# commit-rebalance.ps1
# Automates the commit and push of quarterly portfolio updates.
#
# Usage:
#   .\commit-rebalance.ps1 -Quarter "2026 Q2" `
#       -Sold "META,IBE" `
#       -Bought "ORCL,SCYR" `
#       -ValueBefore 2000.00 `
#       -ValueAfter 1997.20 `
#       -CashRemaining 100.30 `
#       -EurUsd 1.1758
#
# For the first rebalance (no sells), omit -Sold or pass an empty string.
#
# Note: this script does NOT create git tags. Quarterly updates are tracked
# only via commit history. Tags/releases are reserved for code changes
# (versioned in CHANGELOG.md).

param(
    [Parameter(Mandatory=$true)]
    [string]$Quarter,                # e.g. "2026 Q2"

    [string]$Sold = "",              # e.g. "META,IBE" or "" if first run

    [Parameter(Mandatory=$true)]
    [string]$Bought,                 # e.g. "NVDA,MSFT,AVGO,META,BBVA,IBE"

    [Parameter(Mandatory=$true)]
    [decimal]$ValueBefore,

    [Parameter(Mandatory=$true)]
    [decimal]$ValueAfter,

    [Parameter(Mandatory=$true)]
    [decimal]$CashRemaining,

    [Parameter(Mandatory=$true)]
    [decimal]$EurUsd
)

# Auto-generate today's date
$Date = Get-Date -Format "yyyy-MM-dd"

# Build commit subject (one line)
if ($Sold -eq "") {
    $CommitSubject = "$Quarter rebalance: bought $Bought"
} else {
    $CommitSubject = "$Quarter rebalance: sold $Sold; bought $Bought"
}

# Build commit body (multi-line, appears under the subject in git log -p)
$SoldLine = if ($Sold -eq "") { "(none - first run)" } else { $Sold }
$CommitBody = @"

$Quarter rebalance executed on $Date

Portfolio value before:  $ValueBefore EUR
Portfolio value after:   $ValueAfter EUR
Cash remaining:          $CashRemaining EUR
Positions sold:          $SoldLine
Positions bought:        $Bought
EUR/USD at execution:    $EurUsd
"@

Write-Host "===== About to execute =====" -ForegroundColor Cyan
Write-Host "Commit subject:" -ForegroundColor Yellow
Write-Host "  $CommitSubject"
Write-Host ""
Write-Host "Commit body:" -ForegroundColor Yellow
Write-Host $CommitBody
Write-Host ""

# Confirmation prompts (3 separate y/N to avoid mistakes)
$confirmationportfoliojson = Read-Host "data/portfolio.json updated with new positions/cash? (y/N)"
if ($confirmationportfoliojson -ne 'y' -and $confirmationportfoliojson -ne 'Y') {
    Write-Host "Aborted: update data/portfolio.json first." -ForegroundColor Red
    exit 1
}

$confirmationhistoryjson = Read-Host "data/history.json updated with new entry appended? (y/N)"
if ($confirmationhistoryjson -ne 'y' -and $confirmationhistoryjson -ne 'Y') {
    Write-Host "Aborted: update data/history.json first (new data appended, never overwritten)." -ForegroundColor Red
    exit 1
}

$confirmation = Read-Host "Proceed with commit and push? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Aborted." -ForegroundColor Red
    exit 1
}

# Execute git operations
git add data/portfolio.json data/history.json
git commit -m $CommitSubject -m $CommitBody
git push

Write-Host "Done. Commit pushed to GitHub." -ForegroundColor Green
