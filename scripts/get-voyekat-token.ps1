# Simple script to get VoyeKat token directly
# Prompts (input is hidden for secret & token)
$AppId       = Read-Host "Enter your Facebook App ID"
$AppSecret   = Read-Host "Enter your App Secret (input hidden)" -AsSecureString
$ShortToken  = Read-Host "Paste your SHORT-LIVED user token (input hidden)" -AsSecureString

# Convert SecureStrings -> plaintext for the HTTP call
Add-Type -AssemblyName System.Runtime.InteropServices
function Unsecure([SecureString]$s) {
  if (-not $s) { return "" }
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
  try   { [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
  finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }  # important!
}
$PlainSecret = Unsecure $AppSecret
$PlainShort  = Unsecure $ShortToken

# URL-encode all query values
$enc = { param($v) [uri]::EscapeDataString($v) }
$qs = @(
  "grant_type=fb_exchange_token"
  "client_id=$(& $enc $AppId)"
  "client_secret=$(& $enc $PlainSecret)"
  "fb_exchange_token=$(& $enc $PlainShort)"
) -join '&'
$exchangeUrl = "https://graph.facebook.com/v18.0/oauth/access_token?$qs"

Write-Host "Getting long-lived token..."
try {
  $exchangeResponse = Invoke-WebRequest -Method Get -Uri $exchangeUrl -ErrorAction Stop
  $exchangeJson = $exchangeResponse.Content | ConvertFrom-Json
  if (-not $exchangeJson.access_token) { throw "No access_token returned." }

  $LongToken = $exchangeJson.access_token
  Write-Host "✅ Got long-lived token"
} catch {
  Write-Host "❌ Exchange failed: $($_.Exception.Message)"
  exit 1
}

# Fetch pages with that long-lived user token
Write-Host "Getting pages..."
$pageUrl = "https://graph.facebook.com/v18.0/me/accounts?access_token=$([uri]::EscapeDataString($LongToken))"
try {
  $pageResponse = Invoke-WebRequest -Method Get -Uri $pageUrl -ErrorAction Stop
  $pageJson = $pageResponse.Content | ConvertFrom-Json

  if (-not $pageJson.data -or $pageJson.data.Count -eq 0) { throw "No pages found." }

  # Find VoyeKat page specifically
  $voyeKatPage = $pageJson.data | Where-Object { $_.name -eq "VoyeKat" }
  
  if ($voyeKatPage) {
    Write-Host ""
    Write-Host "========================================="
    Write-Host "VoyeKat Page Found!"
    Write-Host "Page Name: $($voyeKatPage.name)"
    Write-Host "Page ID: $($voyeKatPage.id)"
    Write-Host ""
    Write-Host "PLAIN ACCESS TOKEN (copy this):"
    Write-Host $voyeKatPage.access_token
    Write-Host "========================================="
  } else {
    Write-Host "❌ VoyeKat page not found. Available pages:"
    foreach ($p in $pageJson.data) {
      Write-Host "  - $($p.name) (ID: $($p.id))"
    }
  }

} catch {
  Write-Host "❌ Failed to fetch pages: $($_.Exception.Message)"
  exit 1
}