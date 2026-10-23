function RemVsix-Update{
    # ============================================
    # Pscript VSCode Extension - Update Script
    # ============================================

    $ErrorActionPreference = "Stop"

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " Pscript Extension Update" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    # --------------------------------------------
    # 1. Xóa các file VSIX cũ
    # --------------------------------------------

    Write-Host "[1/4] Removing old VSIX files..." -ForegroundColor Yellow

    $oldVsix = Get-ChildItem -Path "." -Filter "*.vsix" -File

    if ($oldVsix) {
        $oldVsix | Remove-Item -Force
        Write-Host "      Removed old VSIX files." -ForegroundColor Green
    }
    else {
        Write-Host "      No old VSIX files found." -ForegroundColor DarkGray
    }

    # --------------------------------------------
    # 2. Đóng gói extension
    # --------------------------------------------

    Write-Host ""
    Write-Host "[2/4] Packaging extension..." -ForegroundColor Yellow

    npx @vscode/vsce package

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: vsce package failed." -ForegroundColor Red
        exit 1
    }

    # --------------------------------------------
    # 3. Tìm VSIX vừa tạo
    # --------------------------------------------

    Write-Host ""
    Write-Host "[3/4] Finding generated VSIX..." -ForegroundColor Yellow

    $vsix = Get-ChildItem -Path "." -Filter "*.vsix" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $vsix) {
        Write-Host ""
        Write-Host "ERROR: No VSIX file found." -ForegroundColor Red
        exit 1
    }

    Write-Host "      VSIX: $($vsix.Name)" -ForegroundColor Green

    # --------------------------------------------
    # 4. Cài / update extension
    # --------------------------------------------

    Write-Host ""
    Write-Host "[4/4] Installing extension..." -ForegroundColor Yellow

    code --install-extension $vsix.FullName --force

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: VSCode extension installation failed." -ForegroundColor Red
        exit 1
    }

    # --------------------------------------------
    # Done
    # --------------------------------------------

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host " Pscript Extension updated successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installed: $($vsix.Name)" -ForegroundColor Cyan
    Write-Host ""

}

function UnExt-RemVsix-Update{
    # ============================================
    # Pscript VSCode Extension - Update Script
    # ============================================

    $ErrorActionPreference = "Stop"

    # --------------------------------------------
    # Extension ID
    # --------------------------------------------

    $extensionId = "selfdevjps.pscript"

    # ============================================
    # Header
    # ============================================

    Clear-Host

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " Pscript Extension Update" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    # ============================================
    # Menu
    # ============================================

    Write-Host "Choose an action:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] Remove old .vsix files only"
    Write-Host "  [2] Uninstall extension + remove old .vsix"
    Write-Host "  [3] Exit"
    Write-Host ""

    $choice = Read-Host "Select option"

    switch ($choice) {

        # ----------------------------------------
        # OPTION 1
        # ----------------------------------------

        "1" {
            Write-Host ""
            Write-Host "[1/4] Removing old VSIX files..." -ForegroundColor Yellow

            $oldVsix = Get-ChildItem -Path "." -Filter "*.vsix" -File

            if ($oldVsix) {
                $oldVsix | Remove-Item -Force

                Write-Host "      Removed old VSIX files." -ForegroundColor Green
            }
            else {
                Write-Host "      No old VSIX files found." -ForegroundColor DarkGray
            }
        }

        # ----------------------------------------
        # OPTION 2
        # ----------------------------------------

        "2" {

            # ------------------------------------
            # Uninstall extension
            # ------------------------------------

            Write-Host ""
            Write-Host "[1/4] Uninstalling Pscript extension..." -ForegroundColor Yellow
            Write-Host "      Extension: $extensionId" -ForegroundColor DarkGray
            Write-Host ""

            code --uninstall-extension $extensionId

            if ($LASTEXITCODE -ne 0) {
                Write-Host ""
                Write-Host "ERROR: Failed to uninstall extension." -ForegroundColor Red
                exit 1
            }

            Write-Host "      Extension uninstalled." -ForegroundColor Green

            # ------------------------------------
            # Remove old VSIX
            # ------------------------------------

            Write-Host ""
            Write-Host "[2/4] Removing old VSIX files..." -ForegroundColor Yellow

            $oldVsix = Get-ChildItem -Path "." -Filter "*.vsix" -File

            if ($oldVsix) {
                $oldVsix | Remove-Item -Force

                Write-Host "      Removed old VSIX files." -ForegroundColor Green
            }
            else {
                Write-Host "      No old VSIX files found." -ForegroundColor DarkGray
            }
        }

        # ----------------------------------------
        # OPTION 3
        # ----------------------------------------

        "3" {
            Write-Host ""
            Write-Host "Update cancelled." -ForegroundColor Yellow
            exit 0
        }

        # ----------------------------------------
        # INVALID OPTION
        # ----------------------------------------

        default {
            Write-Host ""
            Write-Host "ERROR: Invalid option." -ForegroundColor Red
            exit 1
        }
    }

    # ============================================
    # 2/4 - Package extension
    # ============================================

    Write-Host ""
    Write-Host "[2/4] Packaging extension..." -ForegroundColor Yellow

    npx @vscode/vsce package

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: vsce package failed." -ForegroundColor Red
        exit 1
    }

    Write-Host "      Package created successfully." -ForegroundColor Green

    # ============================================
    # 3/4 - Find generated VSIX
    # ============================================

    Write-Host ""
    Write-Host "[3/4] Finding generated VSIX..." -ForegroundColor Yellow

    $vsix = Get-ChildItem -Path "." -Filter "*.vsix" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $vsix) {
        Write-Host ""
        Write-Host "ERROR: No VSIX file found." -ForegroundColor Red
        exit 1
    }

    Write-Host "      VSIX: $($vsix.Name)" -ForegroundColor Green

    # ============================================
    # 4/4 - Install / Update extension
    # ============================================

    Write-Host ""
    Write-Host "[4/4] Installing extension..." -ForegroundColor Yellow

    code --install-extension $vsix.FullName --force

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: VSCode extension installation failed." -ForegroundColor Red
        exit 1
    }

    # ============================================
    # Done
    # ============================================

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host " Pscript Extension updated successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""

    Write-Host "Installed: $($vsix.Name)" -ForegroundColor Cyan
    Write-Host "Extension: $extensionId" -ForegroundColor Cyan

    Write-Host ""
}

function UnExt-RemVsix-Update1 {

    # ============================================
    # Pscript VSCode Extension - Update Script
    # ============================================

    $ErrorActionPreference = "Stop"

    # --------------------------------------------
    # Extension ID
    # --------------------------------------------

    $extensionId = "selfdevjps.pscript"

    # --------------------------------------------
    # Source directory
    # --------------------------------------------

    $sourceDir = (Get-Location).Path

    # --------------------------------------------
    # Extension directories
    # --------------------------------------------

    $defaultExtensionsDir = Join-Path $env:USERPROFILE ".vscode\extensions"

    $customExtensionsDir = "E:\VSCodeExtensions"

    # ============================================
    # Header
    # ============================================

    Clear-Host

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " Pscript Extension Update" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "Source:" -ForegroundColor DarkGray
    Write-Host "  $sourceDir" -ForegroundColor White
    Write-Host ""

    # ============================================
    # Choose extension installation location
    # ============================================

    Write-Host "Choose extension installation location:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] VS Code default (C:)" -ForegroundColor White
    Write-Host "      $defaultExtensionsDir" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [2] Custom (E:)" -ForegroundColor White
    Write-Host "      $customExtensionsDir" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [3] Exit" -ForegroundColor White
    Write-Host ""

    $locationChoice = Read-Host "Select location"

    switch ($locationChoice) {

        "1" {
            $extensionsDir = $defaultExtensionsDir
            $codeArgs = @("--extensions-dir", $extensionsDir)

            Write-Host ""
            Write-Host "Installation target: C:" -ForegroundColor Cyan
        }

        "2" {

            # ------------------------------------
            # Create E: extension directory
            # ------------------------------------

            if (-not (Test-Path $customExtensionsDir)) {

                Write-Host ""
                Write-Host "Creating extension directory..." -ForegroundColor Yellow

                New-Item `
                    -ItemType Directory `
                    -Path $customExtensionsDir `
                    -Force | Out-Null
            }

            $extensionsDir = $customExtensionsDir
            $codeArgs = @("--extensions-dir", $extensionsDir)

            Write-Host ""
            Write-Host "Installation target: E:" -ForegroundColor Cyan
        }

        "3" {
            Write-Host ""
            Write-Host "Update cancelled." -ForegroundColor Yellow
            return
        }

        default {
            Write-Host ""
            Write-Host "ERROR: Invalid option." -ForegroundColor Red
            return
        }
    }

    Write-Host ""
    Write-Host "Extension directory:" -ForegroundColor DarkGray
    Write-Host "  $extensionsDir" -ForegroundColor White

    # ============================================
    # Menu
    # ============================================

    Write-Host ""
    Write-Host "Choose an action:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] Remove old .vsix files only"
    Write-Host "  [2] Uninstall extension + remove old .vsix"
    Write-Host "  [3] Exit"
    Write-Host ""

    $choice = Read-Host "Select option"

    switch ($choice) {

        # ========================================
        # OPTION 1
        # ========================================

        "1" {

            Write-Host ""
            Write-Host "[1/4] Removing old VSIX files..." -ForegroundColor Yellow

            $oldVsix = Get-ChildItem `
                -Path $sourceDir `
                -Filter "*.vsix" `
                -File

            if ($oldVsix) {

                $oldVsix | Remove-Item -Force

                Write-Host "      Removed old VSIX files." -ForegroundColor Green
            }
            else {

                Write-Host `
                    "      No old VSIX files found." `
                    -ForegroundColor DarkGray
            }
        }

        # ========================================
        # OPTION 2
        # ========================================

        "2" {

            # ------------------------------------
            # Uninstall extension if installed
            # ------------------------------------

            Write-Host ""
            Write-Host "[1/4] Checking old Pscript extension..." `
                -ForegroundColor Yellow

            $installedExtensions = & code `
                "--extensions-dir" `
                $extensionsDir `
                "--list-extensions" 2>$null

            if ($installedExtensions -contains $extensionId) {

                Write-Host `
                    "      Found: $extensionId" `
                    -ForegroundColor DarkGray

                Write-Host `
                    "      Uninstalling..." `
                    -ForegroundColor Yellow

                & code `
                    "--extensions-dir" `
                    $extensionsDir `
                    "--uninstall-extension" `
                    $extensionId

                if ($LASTEXITCODE -ne 0) {

                    Write-Host ""
                    Write-Host `
                        "ERROR: Failed to uninstall extension." `
                        -ForegroundColor Red

                    return
                }

                Write-Host `
                    "      Extension uninstalled." `
                    -ForegroundColor Green
            }
            else {

                Write-Host `
                    "      Extension is not installed in this directory." `
                    -ForegroundColor DarkGray

                Write-Host `
                    "      Continuing..." `
                    -ForegroundColor DarkGray
            }
        }

        # ========================================
        # OPTION 3
        # ========================================

        "3" {

            Write-Host ""
            Write-Host "Update cancelled." -ForegroundColor Yellow
            return
        }

        # ========================================
        # INVALID
        # ========================================

        default {

            Write-Host ""
            Write-Host "ERROR: Invalid option." -ForegroundColor Red
            return
        }
    }

    # ============================================
    # 2/4 - Package extension
    # ============================================

    Write-Host ""
    Write-Host "[2/4] Packaging extension..." -ForegroundColor Yellow

    Push-Location $sourceDir

    try {

        npx @vscode/vsce package

        if ($LASTEXITCODE -ne 0) {

            Write-Host ""
            Write-Host `
                "ERROR: vsce package failed." `
                -ForegroundColor Red

            return
        }
    }
    finally {

        Pop-Location
    }

    Write-Host `
        "      Package created successfully." `
        -ForegroundColor Green

    # ============================================
    # 3/4 - Find generated VSIX
    # ============================================

    Write-Host ""
    Write-Host "[3/4] Finding generated VSIX..." `
        -ForegroundColor Yellow

    $vsix = Get-ChildItem `
        -Path $sourceDir `
        -Filter "*.vsix" `
        -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $vsix) {

        Write-Host ""
        Write-Host `
            "ERROR: No VSIX file found." `
            -ForegroundColor Red

        return
    }

    Write-Host `
        "      VSIX: $($vsix.Name)" `
        -ForegroundColor Green

    # ============================================
    # 4/4 - Install / Update extension
    # ============================================

    Write-Host ""
    Write-Host "[4/4] Installing extension..." `
        -ForegroundColor Yellow

    Write-Host ""
    Write-Host "      VSIX:" -ForegroundColor DarkGray
    Write-Host "      $($vsix.FullName)" -ForegroundColor White

    Write-Host ""
    Write-Host "      Install directory:" -ForegroundColor DarkGray
    Write-Host "      $extensionsDir" -ForegroundColor White

    Write-Host ""

    & code `
        "--extensions-dir" `
        $extensionsDir `
        "--install-extension" `
        $vsix.FullName `
        "--force"

    if ($LASTEXITCODE -ne 0) {

        Write-Host ""
        Write-Host `
            "ERROR: VSCode extension installation failed." `
            -ForegroundColor Red

        return
    }

    # ============================================
    # Verify installation
    # ============================================

    Write-Host ""
    Write-Host "Verifying installation..." `
        -ForegroundColor Yellow

    $installedExtension = Join-Path `
        $extensionsDir `
        "$extensionId-0.0.3"

    if (Test-Path $installedExtension) {

        Write-Host ""
        Write-Host `
            "      Installed successfully." `
            -ForegroundColor Green

        Write-Host ""
        Write-Host `
            "      Location:" `
            -ForegroundColor DarkGray

        Write-Host `
            "      $installedExtension" `
            -ForegroundColor Cyan
    }
    else {

        Write-Host ""
        Write-Host `
            "WARNING: Extension installed, but exact version directory was not found." `
            -ForegroundColor Yellow
    }

    # ============================================
    # Done
    # ============================================

    Write-Host ""
    Write-Host "============================================" `
        -ForegroundColor Green

    Write-Host `
        " Pscript Extension updated successfully!" `
        -ForegroundColor Green

    Write-Host "============================================" `
        -ForegroundColor Green

    Write-Host ""

    Write-Host `
        "Installed: $($vsix.Name)" `
        -ForegroundColor Cyan

    Write-Host `
        "Extension: $extensionId" `
        -ForegroundColor Cyan

    Write-Host `
        "Location:  $extensionsDir" `
        -ForegroundColor Cyan

    Write-Host ""
}
