# PowerShell setup script for Orchestratex

# Function to install Python packages
function Install-PythonDependencies {
    Write-Host "Installing Python dependencies..."
    pip install -r ../requirements.txt
}

# Function to create environment file
function Create-EnvironmentFile {
    Write-Host "Creating environment file..."
    $envPath = "../.env"
    
    if (Test-Path $envPath) {
        Write-Host ".env file already exists. Skipping creation."
        return
    }
    
    $envData = @{
        PROJECT_NAME = "Orchestratex"
        VERSION = "0.1.0"
        SECRET_KEY = [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes(32) | Format-Hex | ForEach-Object { $_.ToString("X2") } | Join-String -Separator ""
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = "30"
        DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/orchestratex"
        MONGO_URI = "mongodb://localhost:27017/orchestratex"
        REDIS_URL = "redis://localhost:6379"
        PINECONE_API_KEY = "YOUR_PINECONE_KEY"
        HUGGINGFACE_TOKEN = "YOUR_HF_TOKEN"
        OPENAI_API_KEY = "YOUR_OPENAI_KEY"
        ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_KEY"
        IBM_QUANTUM_TOKEN = "YOUR_IBM_QUANTUM_TOKEN"
        AZURE_QUANTUM_TOKEN = "YOUR_AZURE_QUANTUM_TOKEN"
        AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY"
        AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_KEY"
        AWS_REGION = "us-east-1"
    }
    
    foreach ($key in $envData.Keys) {
        Add-Content -Path $envPath -Value "$key=$($envData[$key])"
    }
    
    Write-Host "Environment file created. Please update the API keys with your actual credentials."
}

# Function to check and install PostgreSQL
function Install-PostgreSQL {
    Write-Host "Checking PostgreSQL installation..."
    if (-not (Test-Path "C:\Program Files\PostgreSQL")) {
        Write-Host "PostgreSQL not found. Please download and install from: https://www.postgresql.org/download/windows/"
    }
}

# Function to check and install MongoDB
function Install-MongoDB {
    Write-Host "Checking MongoDB installation..."
    if (-not (Test-Path "C:\Program Files\MongoDB")) {
        Write-Host "MongoDB not found. Please download and install from: https://www.mongodb.com/try/download/community"
    }
}

# Function to check and install Redis
function Install-Redis {
    Write-Host "Checking Redis installation..."
    if (-not (Test-Path "C:\Program Files\Redis")) {
        Write-Host "Redis not found. Please download and install from: https://github.com/tporadowski/redis/releases"
    }
}

# Function to check CUDA installation
function Check-CUDA {
    Write-Host "Checking CUDA installation..."
    if (Test-Path "C:\Program Files\NVIDIA Corporation") {
        Write-Host "CUDA detected. Please download CUDA from: https://developer.nvidia.com/cuda-downloads"
    }
}

# Main setup function
function Setup-Orchestratex {
    Write-Host "Starting Orchestratex setup..."
    
    # Install system dependencies
    Install-PostgreSQL
    Install-MongoDB
    Install-Redis
    Check-CUDA
    
    # Create environment file
    Create-EnvironmentFile
    
    # Install Python dependencies
    Install-PythonDependencies
    
    Write-Host "`nSetup complete!"
    Write-Host "Please update the following in the .env file:"
    Write-Host "- API keys for OpenAI, Anthropic, Pinecone"
    Write-Host "- IBM Quantum token"
    Write-Host "- Azure Quantum token"
    Write-Host "- AWS credentials"
}

# Run setup
Setup-Orchestratex
