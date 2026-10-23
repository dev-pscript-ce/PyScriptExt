param(
    [Parameter(Position = 0)]
    [string]$ThemeFile,

    [Parameter(Position = 1)]
    [string]$PscriptTheme
)



# $pscriptTheme = "E:\PackagesJP3\PscriptExtension\themes\pscript-color-theme.json"

# ==========================================
# Configuration
# ==========================================


function Show-Menu {

    Clear-Host

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "       Pscript Theme Tools"  -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "1. Xem dark_modern.json" -ForegroundColor Green
    Write-Host "2. Mở Pscript theme" -ForegroundColor Blue
    Write-Host "3. Copy dark_modern -> Pscript theme" -ForegroundColor Cyan
    Write-Host "4. Copy và mở Pscript theme" -ForegroundColor Green
    Write-Host "5. Mở file JSON tùy chọn" -ForegroundColor Cyan
    Write-Host "6. Tìm thư mục theme-defaults của VS Code Insiders:" -ForegroundColor Blue
    Write-Host "0. Thoát" -ForegroundColor Red
    Write-Host ""
}
function Main{
    $themeDefaults = code-insiders --locate-extension vscode.theme-defaults

    $darkModern = Join-Path $themeDefaults "themes\dark_modern.json"

    $pscriptTheme = "E:\PackagesJP3\PscriptExtension\themes\dark_pscript.json"

    while ($true) {

        Show-Menu

        $choice = Read-Host "Chọn"

        switch ($choice) {

            # --------------------------------
            # 1. Xem dark_modern.json
            # --------------------------------
        
            "1" {

                Write-Host ""
                Write-Host ">>> $darkModern" -ForegroundColor Cyan
                Write-Host ""

                Get-Content $darkModern

                Write-Host ""
                Read-Host "Enter để tiếp tục"
            }


            # --------------------------------
            # 2. Mở Pscript theme
            # --------------------------------

            "2" {

                code-insiders $pscriptTheme

            }


            # --------------------------------
            # 3. Copy theme
            # --------------------------------

            "3" {

                Copy-Item `
                    $darkModern `
                    $pscriptTheme `
                    -Force

                Write-Host ""
                Write-Host "Đã copy:" -ForegroundColor Green
                Write-Host $darkModern
                Write-Host "->"
                Write-Host $pscriptTheme

                Read-Host "Enter để tiếp tục"
            }


            # --------------------------------
            # 4. Copy và mở
            # --------------------------------

            "4" {

                Copy-Item `
                    $darkModern `
                    $pscriptTheme `
                    -Force

                Write-Host ""
                Write-Host "Đã copy theme." -ForegroundColor Green

                code-insiders $pscriptTheme
            }


            # --------------------------------
            # 5. JSON tùy chọn
            # --------------------------------

            "5" {

                Write-Host ""
                $jsonFile = Read-Host "Nhập đường dẫn file .json"

                if (Test-Path $jsonFile) {

                    code-insiders $jsonFile

                }
                else {

                    Write-Host ""
                    Write-Host "Không tìm thấy file:" -ForegroundColor Red
                    Write-Host $jsonFile

                    Read-Host "Enter để tiếp tục"
                }
            }

            "6"{
                Get-ChildItem `
                    (Join-Path $themeDefaults "themes") `
                    -Filter "*.json" |
                    Select-Object -ExpandProperty Name

                exit 1
            }


            # --------------------------------
            # 0. Thoát
            # --------------------------------

            "0" {

                break
            }


            default {

                Write-Host ""
                Write-Host "Lựa chọn không hợp lệ!" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    }
}

#  ------------------------------------------------------------#

function Menu-Main{

    $PscriptThemeDirectory = "E:\PackagesJP3\PscriptExtension\themes"
    $DefaultPscriptTheme = "pscript-color-theme.json"

    # ==========================================
    # Nếu không truyền ThemeFile -> hỏi người dùng
    # ==========================================

    if ([string]::IsNullOrWhiteSpace($ThemeFile)) {

        Write-Host ""
        Write-Host "Nhập tên theme JSON."
        Write-Host "Ví dụ: dark_modern.json"
        Write-Host "       dark_plus.json"
        Write-Host ""

        $ThemeFile = Read-Host "Theme"
    }


    # ==========================================
    # Nếu không truyền file đích
    # -> dùng pscript-color-theme.json
    # ==========================================

    if ([string]::IsNullOrWhiteSpace($PscriptTheme)) {

        $PscriptTheme = $DefaultPscriptTheme
    }


    # ==========================================
    # Kiểm tra .json
    # ==========================================

    if (-not $ThemeFile.EndsWith(
        ".json",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $ThemeFile += ".json"
    }


    if (-not $PscriptTheme.EndsWith(
        ".json",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $PscriptTheme += ".json"
    }


    # ==========================================
    # Nếu chỉ nhập tên file
    # -> đưa vào thư mục themes của Pscript
    # ==========================================

    if (-not [System.IO.Path]::IsPathRooted($PscriptTheme)) {

        $PscriptTheme = Join-Path `
            $PscriptThemeDirectory `
            $PscriptTheme
    }


    # ==========================================
    # Tìm thư mục VS Code theme-defaults
    # ==========================================

    $themeDefaults = code-insiders --locate-extension vscode.theme-defaults


    if ([string]::IsNullOrWhiteSpace($themeDefaults)) {

        Write-Host ""
        Write-Host "Không tìm thấy vscode.theme-defaults." -ForegroundColor Red
        exit 1
    }


    $themeDefaults = $themeDefaults.Trim()


    # ==========================================
    # File theme nguồn
    # ==========================================

    $SourceTheme = Join-Path `
        $themeDefaults `
        "themes\$ThemeFile"


    # ==========================================
    # Kiểm tra file nguồn
    # ==========================================

    if (-not (Test-Path $SourceTheme)) {

        Write-Host ""
        Write-Host "Không tìm thấy theme:" -ForegroundColor Red
        Write-Host $SourceTheme
        Write-Host ""

        Write-Host "Các theme hiện có:" -ForegroundColor Yellow

        Get-ChildItem `
            (Join-Path $themeDefaults "themes") `
            -Filter "*.json" |
            Select-Object -ExpandProperty Name

        exit 1
    }


    # ==========================================
    # Hiển thị thông tin
    # ==========================================

    Write-Host ""
    Write-Host "VS Code Theme:" -ForegroundColor Cyan
    Write-Host $SourceTheme

    Write-Host ""
    Write-Host "Pscript Theme:" -ForegroundColor Cyan
    Write-Host $PscriptTheme

    Write-Host ""


    # ==========================================
    # Copy
    # ==========================================

    Copy-Item `
        $SourceTheme `
        $PscriptTheme `
        -Force


    Write-Host "Đã copy theme thành công!" -ForegroundColor Green


    # ==========================================
    # Mở bằng VS Code Insiders
    # ==========================================

    code-insiders $PscriptTheme
}

Menu-Main