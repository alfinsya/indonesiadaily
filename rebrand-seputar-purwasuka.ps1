# Script PowerShell untuk rebrand dari Warta Janten ke Seputar Purwasuka

# Pastikan encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$WorkspaceRoot = "c:\KULIAH\MAGANG\Magang di Perhutani\Seputar Purwasuka"

# Backup articles.json
$articlesJson = Join-Path $WorkspaceRoot "articles.json"
$backupPath = $articlesJson + ".bak." + [DateTime]::Now.ToString("yyyyMMddHHmmss")
Copy-Item $articlesJson $backupPath
Write-Host "Backup articles.json to $backupPath"

# Text-based logo baru
$textBasedLogo = @"
<span style="font-weight: bold; color: #059669; font-size: 24px; letter-spacing: -0.5px;">SEPUTAR<span style="color: #0EA5A4; font-weight: normal; font-size: 18px; margin-left: 2px;">PURWASUKA</span></span>
"@

# Counter untuk file yang diubah
$mainPagesChanged = 0
$articlePagesChanged = 0
$cssChanged = 0
$packageChanged = 0
$docsChanged = 0

# Fungsi untuk replace branding
function Replace-Branding {
    param($content)
    $content = $content -replace "Warta Janten", "Seputar Purwasuka"
    $content = $content -replace "wartajanten", "seputarpurwasuka"
    $content = $content -replace "WartaJanten", "SeputarPurwasuka"
    $content = $content -replace "wartajanten33@gmail\.com", "seputarpurwasuka@gmail.com"
    $content = $content -replace "- Warta Janten", "- Seputar Purwasuka"
    return $content
}

# Fungsi untuk fix encoding
function Fix-Encoding {
    param($content)
    $content = $content -replace [char]0x201C, '"'
    $content = $content -replace [char]0x201D, '"'
    $content = $content -replace [char]0x2018, "'"
    $content = $content -replace [char]0x2019, "'"
    $content = $content -replace [char]0x2013, "-"
    $content = $content -replace [char]0x2014, "-"
    $content = $content -replace "Â", ""
    $content = $content -replace "ï¿½", " "
    $content = $content -replace "&nbsp;", " "
    return $content
}

# Proses HTML files
$htmlFiles = Get-ChildItem -Path $WorkspaceRoot -Recurse -Include "*.html" -File
foreach ($file in $htmlFiles) {
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        $originalContent = $content
        
        # Replace branding
        $content = Replace-Branding $content
        
        # Fix encoding
        $content = Fix-Encoding $content
        
        # Replace logo
        $content = $content -replace '<img[^>]*src="img/logo\.png"[^>]*>', $textBasedLogo
        $content = $content -replace '<img[^>]*src="\.\./img/logo\.png"[^>]*>', $textBasedLogo
        
        # Replace old text-based logo
        $oldLogo = '<span style="font-weight: bold; color: #065F46; font-size: 24px; letter-spacing: -0.5px;">WARTA<span style="color: #1E3A5F; font-weight: normal; font-size: 18px; margin-left: 2px;">JANTEN</span></span>'
        $content = $content -replace [regex]::Escape($oldLogo), $textBasedLogo
        
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            if ($file.DirectoryName -like "*article*") {
                $articlePagesChanged++
            } else {
                $mainPagesChanged++
            }
            Write-Host "Updated: $($file.Name)"
        }
    } catch {
        Write-Host "Error processing $($file.FullName): $_" -ForegroundColor Red
    }
}

# Proses CSS files
$cssFiles = Get-ChildItem -Path $WorkspaceRoot -Recurse -Include "*.css" -File
foreach ($file in $cssFiles) {
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        $originalContent = $content
        
        # Update colors
        $content = $content -replace "--primary: #[0-9A-Fa-f]{6}", "--primary: #059669"
        $content = $content -replace "--dark: #[0-9A-Fa-f]{6}", "--dark: #064E3B"
        $content = $content -replace "--secondary: #[0-9A-Fa-f]{6}", "--secondary: #0EA5A4"
        
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            $cssChanged++
            Write-Host "Updated CSS: $($file.Name)"
        }
    } catch {
        Write-Host "Error processing $($file.FullName): $_" -ForegroundColor Red
    }
}

# Update package.json
$packageJson = Join-Path $WorkspaceRoot "package.json"
if (Test-Path $packageJson) {
    $content = Get-Content -Path $packageJson -Raw -Encoding UTF8
    $content = $content -replace '"name": "wartajanten"', '"name": "seputarpurwasuka"'
    Set-Content -Path $packageJson -Value $content -Encoding UTF8 -NoNewline
    $packageChanged++
}

$toolsPackageJson = Join-Path $WorkspaceRoot "tools\package.json"
if (Test-Path $toolsPackageJson) {
    $content = Get-Content -Path $toolsPackageJson -Raw -Encoding UTF8
    $content = Replace-Branding $content
    $content = $content -replace '"name": "wartajanten-article-generator"', '"name": "seputarpurwasuka-article-generator"'
    Set-Content -Path $toolsPackageJson -Value $content -Encoding UTF8 -NoNewline
    $packageChanged++
}

# Update docs
$docs = @("AUTOMATION_README.md", "GOOGLE_DRIVE_GUIDE.md", "netlify.toml")
foreach ($doc in $docs) {
    $docPath = Join-Path $WorkspaceRoot $doc
    if (Test-Path $docPath) {
        $content = Get-Content -Path $docPath -Raw -Encoding UTF8
        $content = Replace-Branding $content
        Set-Content -Path $docPath -Value $content -Encoding UTF8 -NoNewline
        $docsChanged++
    }
}

# Output hasil
Write-Host ""
Write-Host "Rebrand Seputar Purwasuka selesai ✅"
Write-Host ""
Write-Host "Jumlah file yang diubah:"
Write-Host "- Main pages: $mainPagesChanged"
Write-Host "- Article pages: $articlePagesChanged"
Write-Host "- CSS: $cssChanged"
Write-Host "- Package: $packageChanged"
Write-Host "- Docs: $docsChanged"