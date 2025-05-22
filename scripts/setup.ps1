# Create virtual environment
python -m venv venv

# Install dependencies
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\pip install -e .

# Set execute permissions
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

Write-Host "✅ Setup completed" -ForegroundColor Green
Write-Host "To run: .\venv\Scripts\activate`nadobackup"