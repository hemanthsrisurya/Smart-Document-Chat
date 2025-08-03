"""
Smart Document Chat - System Validation Script
Run this to check if your system is ready for the application
"""

import sys
import subprocess
import os
import platform
import requests
from pathlib import Path
import importlib.util

def print_header(text):
    print(f"\n{'='*50}")
    print(f" {text}")
    print(f"{'='*50}")

def print_status(message, status):
    if status:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_python_version():
    print_header("Python Environment Check")
    
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}.{version.micro}"
    print_info(f"Python version: {python_version}")
    
    if version >= (3, 8):
        print_status("Python version is compatible (3.8+)", True)
        return True
    else:
        print_status("Python version is too old (requires 3.8+)", False)
        return False

def check_required_packages():
    print_header("Required Python Packages")
    
    required_packages = [
        'streamlit',
        'langchain', 
        'langchain_core',
        'langchain_community',
        'langchain_chroma',
        'langchain_ollama',
        'chromadb',
        'pypdf',
        'pydantic',
        'termcolor',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'langchain_core':
                import langchain_core
            elif package == 'langchain_community':
                import langchain_community
            elif package == 'langchain_chroma':
                import langchain_chroma
            elif package == 'langchain_ollama':
                import langchain_ollama
            else:
                __import__(package)
            print_status(f"{package} is installed", True)
        except ImportError:
            print_status(f"{package} is missing", False)
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    else:
        print_status("All required packages are installed", True)
        return True

def check_ollama_installation():
    print_header("Ollama Service Check")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status("Ollama is installed", True)
            print_info(f"Version: {result.stdout.strip()}")
        else:
            print_status("Ollama command failed", False)
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_status("Ollama is not installed or not in PATH", False)
        print_info("Install from: https://ollama.ai")
        return False
    
    # Check if Ollama service is running
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print_status("Ollama service is running", True)
            
            # Check available models
            models_data = response.json()
            model_names = [model['name'] for model in models_data.get('models', [])]
            
            required_models = ['gemma3:4b', 'nomic-embed-text']
            missing_models = [model for model in required_models if not any(model in name for name in model_names)]
            
            if not missing_models:
                print_status("All required models are available", True)
            else:
                print_warning(f"Missing models: {', '.join(missing_models)}")
                print_info("Download with: ollama pull <model_name>")
                
            return True
        else:
            print_status("Ollama service returned error", False)
            return False
            
    except requests.RequestException:
        print_status("Ollama service is not running", False)
        print_info("Start with: ollama serve")
        return False

def check_directories():
    print_header("Project Structure Check")
    
    required_files = ['app.py', 'chatbot.py', 'config.py', 'requirements.txt']
    required_dirs = ['pdfFiles', 'vectorDB', 'logs']
    
    all_good = True
    
    for file in required_files:
        if Path(file).exists():
            print_status(f"{file} exists", True)
        else:
            print_status(f"{file} is missing", False)
            all_good = False
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_status(f"{dir_name}/ directory exists", True)
        else:
            print_status(f"{dir_name}/ directory missing", False)
            dir_path.mkdir(exist_ok=True)
            print_info(f"Created {dir_name}/ directory")
    
    return all_good

def check_system_resources():
    print_header("System Resources Check")
    
    # Check available disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (1024**3)
    
    print_info(f"Free disk space: {free_gb} GB")
    if free_gb >= 10:
        print_status("Sufficient disk space available", True)
    else:
        print_warning("Low disk space (need at least 10GB for models)")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Running in virtual environment", True)
    else:
        print_warning("Not running in virtual environment (recommended)")
    
    return True

def provide_setup_instructions():
    print_header("Setup Instructions")
    
    print_info("If any checks failed, follow these steps:")
    print("")
    
    print("🔧 Quick Fix Options:")
    print("  1. Run the auto-installer:")
    print("     • Right-click install.ps1 → 'Run with PowerShell'")
    print("     • Or double-click start_app.bat")
    
    print("\n  2. Manual installation:")
    print("     • Install Python 3.8+: https://python.org")
    print("     • Install Ollama: https://ollama.ai")
    print("     • pip install -r requirements.txt")
    print("     • ollama serve")
    print("     • ollama pull gemma3:4b")
    print("     • ollama pull nomic-embed-text")
    
    print("\n  3. Run the application:")
    print("     • .\\run_app.ps1")
    print("     • streamlit run app.py")

def main():
    print("🔍 Smart Document Chat - System Validation")
    print(f"Running on: {platform.system()} {platform.release()}")
    print(f"Python executable: {sys.executable}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages), 
        ("Ollama Service", check_ollama_installation),
        ("Project Structure", check_directories),
        ("System Resources", check_system_resources)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_status(f"{name} check failed with error: {str(e)}", False)
            results.append((name, False))
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        print_status(f"{name}", result)
    
    print(f"\n📊 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System is ready! You can start the application.")
        print("   Run: .\\run_app.ps1")
        print("   Or:  streamlit run app.py")
    else:
        print("⚠️  Some issues need to be resolved before starting.")
        provide_setup_instructions()

if __name__ == "__main__":
    main()
