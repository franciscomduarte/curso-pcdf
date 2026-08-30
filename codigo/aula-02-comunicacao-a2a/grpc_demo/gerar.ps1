# Gera os stubs Python do classificador.proto (Windows/PowerShell).
# Requer: pip install -r ..\requirements-opcionais.txt
Set-Location $PSScriptRoot
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. classificador.proto
Write-Host "stubs gerados em $PSScriptRoot"
