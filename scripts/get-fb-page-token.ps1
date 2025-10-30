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

Write-Host "➡️  Exchanging short-lived token for a long-lived user token..."
try {
  $exchangeResponse = Invoke-WebRequest -Method Get -Uri $exchangeUrl -ErrorAction Stop
  $exchangeJson = $exchangeResponse.Content | ConvertFrom-Json
  if (-not $exchangeJson.access_token) { throw "No access_token returned. Full response: $($exchangeResponse.Content)" }

  $LongToken = $exchangeJson.access_token
  Write-Host ("✅ Got long-lived user token. Expires in: {0} seconds" -f $exchangeJson.expires_in)
} catch {
  Write-Host "❌ Exchange failed."
  if ($_.Exception.Response) {
    $sr = New-Object IO.StreamReader($_.Exception.Response.GetResponseStream())
    $body = $sr.ReadToEnd()
    Write-Host "HTTP Status: $([int]$_.Exception.Response.StatusCode) $([string]$_.Exception.Response.StatusDescription)"
    Write-Host "Response: $body"
  } else {
    Write-Host $_.Exception.Message
  }
  exit 1
}

# Fetch pages with that long-lived user token
Write-Host "`n➡️  Fetching Pages..."
$pageUrl = "https://graph.facebook.com/v18.0/me/accounts?access_token=$([uri]::EscapeDataString($LongToken))"
try {
  $pageResponse = Invoke-WebRequest -Method Get -Uri $pageUrl -ErrorAction Stop
  $pageJson = $pageResponse.Content | ConvertFrom-Json

  if (-not $pageJson.data -or $pageJson.data.Count -eq 0) { throw "No pages found for this user/token." }

  # Show pages (mask tokens)
  foreach ($p in $pageJson.data) {
    $tok = $p.access_token
    $masked = if ($tok.Length -gt 10) { $tok.Substring(0,6) + "..." + $tok.Substring($tok.Length-4,4) } else { "***" }
    Write-Host "-----------------------------------------"
    Write-Host "Page Name     : $($p.name)"
    Write-Host "Page ID       : $($p.id)"
    Write-Host "Access Token  : $masked   (stored in memory as `$p.access_token`)"
  }
  Write-Host "-----------------------------------------"
  Write-Host "🎯 Use the 'id' as FB_PAGE_ID and the raw 'access_token' value as FB_PAGE_ACCESS_TOKEN (do not print it)."

  # Extract VoyeKat token specifically
  $voyeKatPage = $pageJson.data | Where-Object { $_.name -eq "VoyeKat" }
  if ($voyeKatPage) {
    Write-Host ""
    Write-Host "========================================="
    Write-Host "VOYEKAT TOKEN (COPY THIS):"
    Write-Host $voyeKatPage.access_token
    Write-Host "========================================="
  }

} catch {
  Write-Host "❌ Fetch pages failed."
  if ($_.Exception.Response) {
    $sr = New-Object IO.StreamReader($_.Exception.Response.GetResponseStream())
    $body = $sr.ReadToEnd()
    Write-Host "HTTP Status: $([int]$_.Exception.Response.StatusCode) $([string]$_.Exception.Response.StatusDescription)"
    Write-Host "Response: $body"
  } else {
    Write-Host $_.Exception.Message
  }
  exit 1
}

# OPTIONAL: Debug the user token (checks scopes/expiry)
# $APP_ID = $AppId
# $APP_SECRET_PLAIN = $PlainSecret
# $appToken = "$APP_ID|$APP_SECRET_PLAIN"
# $debugUrl = "https://graph.facebook.com/v18.0/debug_token?input_token=$([uri]::EscapeDataString($LongToken))&access_token=$([uri]::EscapeDataString($appToken))"
# ($ (Invoke-WebRequest -Uri $debugUrl).Content | ConvertFrom-Json ).data | Format-List *
