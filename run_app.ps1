#!/usr/bin/env pwsh
# Smart Document Chat - Application Launcher
# Enhanced PowerShell script to run the RAG chatbot with all features

param(
    [int]$Port = 8501,
    [switch]$Debug,
    [switch]$Help
)

if ($Help) {
    Write-Host "Smart Document Chat - Application Launcher" -ForegroundColor Green
    Write-Host "Usage: .\run_app.ps1 [-Port <port>] [-Debug] [-Help]" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -Port <port>    : Specify port number (default: 8501)" -ForegroundColor White
    Write-Host "  -Debug          : Run with debug logging" -ForegroundColor White
    Write-Host "  -Help           : Show this help message" -ForegroundColor White
    exit 0
}

Write-Host "🤖 Smart Document Chat Launcher" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Make sure app.py is in the current directory" -ForegroundColor Yellow
    exit 1
}

# Function to check if Ollama is running
function Test-OllamaConnection {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Function to start Ollama if not running
function Start-OllamaService {
    Write-Host "🤖 Checking Ollama service..." -ForegroundColor Yellow
    
    if (Test-OllamaConnection) {
        Write-Host "✅ Ollama is already running" -ForegroundColor Green
        return
    }
    
    Write-Host "� Starting Ollama service..." -ForegroundColor Yellow
    
    # Check if Ollama is installed
    if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Ollama is not installed!" -ForegroundColor Red
        Write-Host "📖 Please install Ollama from: https://ollama.ai" -ForegroundColor Cyan
        Write-Host "   Or run the installer script: .\install.ps1" -ForegroundColor Cyan
        exit 1
    }
    
    # Start Ollama in background
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    
    # Wait for Ollama to start
    $attempts = 0
    $maxAttempts = 30
    
    while (-not (Test-OllamaConnection) -and $attempts -lt $maxAttempts) {
        Start-Sleep -Seconds 2
        $attempts++
        Write-Host "   Waiting for Ollama to start... ($attempts/$maxAttempts)" -ForegroundColor Cyan
    }
    
    if (Test-OllamaConnection) {
        Write-Host "✅ Ollama service started successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start Ollama service" -ForegroundColor Red
        Write-Host "   Please start Ollama manually: ollama serve" -ForegroundColor Yellow
        exit 1
    }
}

# Function to check required models
function Test-RequiredModels {
    Write-Host "📋 Checking required AI models..." -ForegroundColor Yellow
    
    try {
        $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
        $modelNames = $models.models | ForEach-Object { $_.name }
        
        $requiredModels = @("gemma3:4b", "nomic-embed-text")
        $missingModels = @()
        
        foreach ($model in $requiredModels) {
            if ($modelNames -notcontains $model) {
                $missingModels += $model
            }
        }
        
        if ($missingModels.Count -eq 0) {
            Write-Host "✅ All required models are available" -ForegroundColor Green
            return
        }
        
        Write-Host "⚠️ Missing models: $($missingModels -join ', ')" -ForegroundColor Yellow
        $response = Read-Host "Would you like to download missing models now? (y/n)"
        
        if ($response -eq 'y' -or $response -eq 'Y' -or $response -eq '') {
            foreach ($model in $missingModels) {
                Write-Host "📥 Downloading $model (this may take a while)..." -ForegroundColor Cyan
                ollama pull $model
            }
            Write-Host "✅ All models downloaded!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Some features may not work without required models" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "⚠️ Could not check models (Ollama might not be ready)" -ForegroundColor Yellow
    }
}

# Function to activate Python environment
function Initialize-PythonEnvironment {
    Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
    
    # Check if virtual environment exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "   • Activating virtual environment..." -ForegroundColor Cyan
        & ".\venv\Scripts\Activate.ps1"
    } elseif (Test-Path "venv\bin\activate") {
        Write-Host "   • Activating virtual environment (Unix-style)..." -ForegroundColor Cyan
        & ".\venv\bin\activate"
    } else {
        Write-Host "⚠️ Virtual environment not found" -ForegroundColor Yellow
        Write-Host "   Using system Python installation" -ForegroundColor Cyan
    }
    
    # Check if required packages are installed
    try {
        python -c "import streamlit, langchain, chromadb" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python packages are available" -ForegroundColor Green
        } else {
            throw "Package import failed"
        }
    } catch {
        Write-Host "❌ Required Python packages are missing!" -ForegroundColor Red
        Write-Host "� Please install requirements: pip install -r requirements.txt" -ForegroundColor Cyan
        Write-Host "   Or run the installer script: .\install.ps1" -ForegroundColor Cyan
        exit 1
    }
}

# Function to check port availability
function Test-PortAvailability {
    param($Port)
    
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

# Function to create directories
function Initialize-Directories {
    $directories = @("pdfFiles", "vectorDB", "logs")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "   • Created directory: $dir" -ForegroundColor Cyan
        }
    }
}

# Function to display startup information
function Show-StartupInfo {
    Write-Host ""
    Write-Host "🚀 Starting Smart Document Chat..." -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Web Interface: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "📁 PDF Storage: pdfFiles/" -ForegroundColor Cyan
    Write-Host "🗄️ Vector Database: vectorDB/" -ForegroundColor Cyan
    Write-Host "📝 Logs: logs/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Usage Tips:" -ForegroundColor Yellow
    Write-Host "   • Upload PDFs using the sidebar" -ForegroundColor White
    Write-Host "   • Click 'Process PDFs' to analyze documents" -ForegroundColor White
    Write-Host "   • Start asking questions about your documents" -ForegroundColor White
    Write-Host "   • Your data persists between sessions!" -ForegroundColor White
    Write-Host ""
    Write-Host "🛑 To stop the application, press Ctrl+C" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
try {
    # Check port availability
    if (-not (Test-PortAvailability $Port)) {
        Write-Host "❌ Port $Port is already in use!" -ForegroundColor Red
        Write-Host "   Try using a different port: .\run_app.ps1 -Port 8502" -ForegroundColor Yellow
        exit 1
    }
    
    # Initialize directories
    Initialize-Directories
    
    # Start Ollama service
    Start-OllamaService
    
    # Check required models
    Test-RequiredModels
    
    # Set up Python environment
    Initialize-PythonEnvironment
    
    # Show startup information
    Show-StartupInfo
    
    # Set debug environment if requested
    if ($Debug) {
        $env:STREAMLIT_LOGGER_LEVEL = "debug"
        Write-Host "🐛 Debug logging enabled" -ForegroundColor Magenta
    }
    
    # Run the Streamlit application
    $streamlitArgs = @(
        "run", "app.py",
        "--server.port", $Port,
        "--server.address", "localhost",
        "--server.headless", "true",
        "--browser.serverAddress", "localhost",
        "--browser.serverPort", $Port
    )
    
    python -m streamlit @streamlitArgs
    
} catch {
    Write-Host ""
    Write-Host "❌ Error starting application: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure you ran the installer: .\install.ps1" -ForegroundColor White
    Write-Host "   2. Check that Python and required packages are installed" -ForegroundColor White
    Write-Host "   3. Ensure Ollama is installed and running" -ForegroundColor White
    Write-Host "   4. Verify port $Port is not in use" -ForegroundColor White
    Write-Host ""
    exit 1
} finally {
    Write-Host ""
    Write-Host "👋 Thank you for using Smart Document Chat!" -ForegroundColor Green
}

Write-Host "`n👋 Application stopped" -ForegroundColor Blue
