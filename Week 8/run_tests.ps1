# PowerShell script to run Newman tests for Library Management API
# Run this script after starting the Flask server

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Library API - Newman Test Runner" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Newman is installed
Write-Host "[1/4] Checking Newman installation..." -ForegroundColor Yellow
$newmanInstalled = Get-Command newman -ErrorAction SilentlyContinue

if (-not $newmanInstalled) {
    Write-Host "❌ Newman is not installed!" -ForegroundColor Red
    Write-Host "Please install Newman by running:" -ForegroundColor Yellow
    Write-Host "  npm install -g newman" -ForegroundColor White
    Write-Host ""
    Write-Host "For better reports, also install:" -ForegroundColor Yellow
    Write-Host "  npm install -g newman-reporter-htmlextra" -ForegroundColor White
    exit 1
}

Write-Host "✅ Newman is installed" -ForegroundColor Green
Write-Host ""

# Check if Flask server is running
Write-Host "[2/4] Checking Flask server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Flask server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Flask server is not running!" -ForegroundColor Red
    Write-Host "Please start the server first:" -ForegroundColor Yellow
    Write-Host "  python app.py" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host ""

# Reset data before running tests
Write-Host "[3/4] Resetting test data..." -ForegroundColor Yellow
try {
    $resetResponse = Invoke-RestMethod -Uri "http://localhost:5000/books/reset" -Method Post
    Write-Host "✅ Data reset successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not reset data, continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Run Newman tests
Write-Host "[4/4] Running Newman tests..." -ForegroundColor Yellow
Write-Host ""

# Check if htmlextra reporter is available
$htmlextraInstalled = Get-Command newman -ErrorAction SilentlyContinue | Select-String "htmlextra" -Quiet

if ($htmlextraInstalled) {
    Write-Host "Running with HTML Extra reporter..." -ForegroundColor Cyan
    newman run postman_collection.json `
        --reporters cli,htmlextra `
        --reporter-htmlextra-export "newman_report.html" `
        --reporter-htmlextra-title "Library API Test Report" `
        --color on
    
    Write-Host ""
    Write-Host "=======================================" -ForegroundColor Cyan
    Write-Host "  Test Report Generated!" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Cyan
    Write-Host "Open the report:" -ForegroundColor Yellow
    Write-Host "  newman_report.html" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to open the report
    $openReport = Read-Host "Do you want to open the HTML report? (Y/N)"
    if ($openReport -eq "Y" -or $openReport -eq "y") {
        Start-Process "newman_report.html"
    }
} else {
    Write-Host "Running with CLI reporter..." -ForegroundColor Cyan
    newman run postman_collection.json --color on
    
    Write-Host ""
    Write-Host "💡 Tip: Install htmlextra for better reports:" -ForegroundColor Yellow
    Write-Host "  npm install -g newman-reporter-htmlextra" -ForegroundColor White
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Tests Completed!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
