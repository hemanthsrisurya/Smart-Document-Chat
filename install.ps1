# Smart Document Chat - Windows Auto Installer
# This script will automatically set up everything you need!

param(
    [switch]$SkipOllama,
    [switch]$QuickStart
)

Write-Host "🚀 Smart Document Chat Auto-Installer" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# Function to check if running as administrator
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Chocolatey if not present
function Install-Chocolatey {
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Chocolatey package manager..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        Write-Host "✅ Chocolatey installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
    }
}

# Function to check and install Python
function Install-Python {
    Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [version]$matches[1]
            if ($version -ge [version]"3.8") {
                Write-Host "✅ Python $($matches[1]) is installed and compatible" -ForegroundColor Green
                return
            }
        }
    } catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
    }
    
    Write-Host "📦 Installing Python 3.11..." -ForegroundColor Yellow
    choco install python311 -y
    
    # Refresh environment variables
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    
    Write-Host "✅ Python installed successfully!" -ForegroundColor Green
}

# Function to check and install Git
function Install-Git {
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Git..." -ForegroundColor Yellow
        choco install git -y
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        Write-Host "✅ Git installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "✅ Git already installed" -ForegroundColor Green
    }
}

# Function to install Ollama
function Install-Ollama {
    if ($SkipOllama) {
        Write-Host "⏭️ Skipping Ollama installation (--SkipOllama flag used)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🤖 Checking Ollama installation..." -ForegroundColor Yellow
    
    if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Ollama..." -ForegroundColor Yellow
        
        # Download and install Ollama
        $ollamaUrl = "https://ollama.ai/download/windows"
        $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
        
        try {
            Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller -UseBasicParsing
            Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait
            Write-Host "✅ Ollama installed successfully!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to install Ollama automatically" -ForegroundColor Red
            Write-Host "📖 Please download and install Ollama manually from: https://ollama.ai" -ForegroundColor Yellow
            return
        }
    } else {
        Write-Host "✅ Ollama already installed" -ForegroundColor Green
    }
    
    # Start Ollama service
    Write-Host "🚀 Starting Ollama service..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    
    # Pull required models
    Write-Host "📥 Downloading AI models (this may take a while)..." -ForegroundColor Yellow
    Write-Host "   • Downloading Gemma3:4B model..." -ForegroundColor Cyan
    ollama pull gemma3:4b
    Write-Host "   • Downloading embedding model..." -ForegroundColor Cyan
    ollama pull nomic-embed-text
    
    Write-Host "✅ Ollama setup complete!" -ForegroundColor Green
}

# Function to set up Python environment
function Setup-PythonEnvironment {
    Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
    
    # Create virtual environment if it doesn't exist
    if (!(Test-Path "venv")) {
        Write-Host "   • Creating virtual environment..." -ForegroundColor Cyan
        python -m venv venv
    }
    
    # Activate virtual environment
    Write-Host "   • Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Host "   • Upgrading pip..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    
    # Install requirements
    Write-Host "   • Installing Python packages..." -ForegroundColor Cyan
    pip install -r requirements.txt
    
    Write-Host "✅ Python environment setup complete!" -ForegroundColor Green
}

# Function to create necessary directories
function Create-Directories {
    Write-Host "📁 Creating project directories..." -ForegroundColor Yellow
    
    $directories = @("pdfFiles", "vectorDB", "logs")
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "   • Created: $dir" -ForegroundColor Cyan
        }
    }
    
    # Create .gitkeep files to preserve empty directories
    foreach ($dir in $directories) {
        $gitkeep = Join-Path $dir ".gitkeep"
        if (!(Test-Path $gitkeep)) {
            New-Item -ItemType File -Path $gitkeep -Force | Out-Null
        }
    }
    
    Write-Host "✅ Directories created successfully!" -ForegroundColor Green
}

# Function to test the installation
function Test-Installation {
    Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
    
    # Test Python imports
    $testScript = @"
try:
    import streamlit
    import langchain
    import chromadb
    import pypdf
    print("✅ All Python packages imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
"@
    
    $testResult = python -c $testScript
    Write-Host "   $testResult" -ForegroundColor Cyan
    
    # Test Ollama connection
    try {
        $ollamaTest = curl -s http://localhost:11434/api/tags 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Ollama service is running!" -ForegroundColor Cyan
        } else {
            Write-Host "   ⚠️ Ollama might not be running (this is OK for now)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️ Could not test Ollama connection" -ForegroundColor Yellow
    }
    
    Write-Host "✅ Installation test complete!" -ForegroundColor Green
}

# Function to start the application
function Start-Application {
    Write-Host "🚀 Starting Smart Document Chat..." -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 The application will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "📖 Upload some PDFs and start chatting with your documents!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop the application, press Ctrl+C in this window." -ForegroundColor Yellow
    Write-Host ""
    
    # Activate virtual environment and start the app
    & ".\venv\Scripts\Activate.ps1"
    streamlit run app.py
}

# Main installation process
try {
    # Check if we're in the right directory
    if (!(Test-Path "app.py")) {
        Write-Host "❌ Please run this script from the Smart Document Chat project directory" -ForegroundColor Red
        Write-Host "   Make sure app.py is in the current directory" -ForegroundColor Yellow
        exit 1
    }
    
    # Check admin rights for system installations
    if (!(Test-Admin)) {
        Write-Host "⚠️ For best results, run as Administrator (Right-click → 'Run as Administrator')" -ForegroundColor Yellow
        Write-Host "   Continuing with user-level installation..." -ForegroundColor Cyan
        Write-Host ""
    }
    
    Write-Host "Starting automated installation..." -ForegroundColor Cyan
    Write-Host ""
    
    # Install system dependencies
    if (!(Test-Admin)) {
        Write-Host "⏭️ Skipping system package installation (not running as admin)" -ForegroundColor Yellow
    } else {
        Install-Chocolatey
        Install-Python
        Install-Git
    }
    
    # Create project structure
    Create-Directories
    
    # Set up Python environment
    Setup-PythonEnvironment
    
    # Install and configure Ollama
    Install-Ollama
    
    # Test everything
    Test-Installation
    
    Write-Host ""
    Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    
    if (!$QuickStart) {
        $response = Read-Host "Would you like to start the application now? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y' -or $response -eq '') {
            Start-Application
        } else {
            Write-Host ""
            Write-Host "🚀 To start the application later, run:" -ForegroundColor Cyan
            Write-Host "   .\run_app.ps1" -ForegroundColor White
            Write-Host ""
        }
    } else {
        Start-Application
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "📖 Manual installation steps:" -ForegroundColor Yellow
    Write-Host "1. Install Python 3.8+ from https://python.org" -ForegroundColor White
    Write-Host "2. Install Ollama from https://ollama.ai" -ForegroundColor White
    Write-Host "3. Run: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "4. Run: ollama serve && ollama pull gemma2:9b" -ForegroundColor White
    Write-Host "5. Run: streamlit run app.py" -ForegroundColor White
    exit 1
}
