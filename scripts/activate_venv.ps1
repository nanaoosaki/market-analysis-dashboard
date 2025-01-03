# Check and set PowerShell execution policy
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($currentPolicy -eq "Restricted") {
    Write-Host "Current execution policy is Restricted. Setting to RemoteSigned..."
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "Execution policy updated to RemoteSigned"
    }
    catch {
        Write-Host "Error: Failed to set execution policy. Please run as administrator or set manually."
        Write-Host "You can set it manually by running:"
        Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        exit 1
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "py310")) {
    Write-Host "Creating virtual environment..."
    try {
        python -m venv py310
        Write-Host "Virtual environment created successfully"
    }
    catch {
        Write-Host "Error: Failed to create virtual environment"
        Write-Host $_.Exception.Message
        exit 1
    }
}

# Activate virtual environment
if (-not ($env:VIRTUAL_ENV)) {
    try {
        Write-Host "Activating virtual environment..."
        .\py310\Scripts\Activate.ps1
        
        # Verify activation
        if ($env:VIRTUAL_ENV) {
            Write-Host "Virtual environment activated successfully"
            Write-Host "Using Python from: $(where.exe python)"
        } else {
            throw "Virtual environment activation failed"
        }
    }
    catch {
        Write-Host "Error: Failed to activate virtual environment"
        Write-Host $_.Exception.Message
        exit 1
    }
}

# Check if requirements are installed
$pip_list = pip freeze
if (-not ($pip_list -match "yfinance")) {
    Write-Host "Installing requirements..."
    try {
        pip install -r requirements.txt
        Write-Host "Requirements installed successfully"
    }
    catch {
        Write-Host "Error: Failed to install requirements"
        Write-Host $_.Exception.Message
        exit 1
    }
}

# Display environment information
Write-Host "`nEnvironment Information:"
Write-Host "----------------------"
Write-Host "Python Version: $(python --version)"
Write-Host "Pip Version: $(pip --version)"
Write-Host "Virtual Environment: $env:VIRTUAL_ENV"
Write-Host "Execution Policy: $(Get-ExecutionPolicy -Scope CurrentUser)" 