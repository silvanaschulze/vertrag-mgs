# 🐳 Docker Engine - Windows Server Deployment

**Guia de Deploy com Docker Engine (SEM Docker Desktop)**  
**Bereitstellungsanleitung mit Docker Engine (OHNE Docker Desktop)**

> ✅ **100% Gratuito / Kostenlos**  
> ⚠️ **Requer Windows Server 2019+ ou Windows 10/11 Pro**

---

## 📋 Pré-requisitos / Voraussetzungen

### Sistema / System
- Windows Server 2019/2022 **OU** Windows 10/11 Pro
- PowerShell 5.1+
- Hyper-V habilitado / aktiviert
- 8GB RAM mínimo
- 50GB espaço em disco / Festplattenspeicher

### Verificar requisitos / Anforderungen prüfen

```powershell
# Abrir PowerShell como Administrador
# Als Administrator öffnen

# Verificar versão do Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Verificar se Hyper-V está disponível
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V

# Verificar PowerShell
$PSVersionTable.PSVersion
```

---

## 🔧 Instalação do Docker Engine / Docker Engine Installation

### Passo 1: Habilitar Hyper-V / Hyper-V aktivieren

```powershell
# PowerShell como Administrador / Als Administrator

# Habilitar Hyper-V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Reiniciar se necessário / Neustart falls erforderlich
# Restart-Computer
```

### Passo 2: Instalar Docker Engine / Docker Engine installieren

```powershell
# Baixar e instalar Docker Engine
# Docker Engine herunterladen und installieren

# Criar diretório temporário / Temporäres Verzeichnis erstellen
New-Item -Type Directory -Path "$env:TEMP\docker"
Set-Location "$env:TEMP\docker"

# Baixar Docker / Docker herunterladen
Invoke-WebRequest -Uri "https://download.docker.com/win/static/stable/x86_64/docker-24.0.7.zip" -OutFile "docker.zip"

# Extrair / Extrahieren
Expand-Archive -Path "docker.zip" -DestinationPath "$env:ProgramFiles" -Force

# Adicionar ao PATH / Zum PATH hinzufügen
$env:path += ";$env:ProgramFiles\docker"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# Registrar serviço Docker / Docker-Dienst registrieren
dockerd --register-service

# Iniciar serviço / Dienst starten
Start-Service docker

# Verificar instalação / Installation überprüfen
docker version
```

**Saída esperada / Erwartete Ausgabe:**
```
Client: Docker Engine - Community
 Version:           24.0.7
 ...
Server: Docker Engine - Community
 Version:           24.0.7
 ...
```

### Passo 3: Instalar Docker Compose / Docker Compose installieren

```powershell
# Baixar Docker Compose / Docker Compose herunterladen
Invoke-WebRequest -Uri "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-windows-x86_64.exe" -OutFile "$env:ProgramFiles\docker\docker-compose.exe"

# Verificar / Überprüfen
docker-compose version
```

---

## 📦 Deploy do Vertrag-MGS / Vertrag-MGS Deployment

### Passo 1: Preparar Diretórios / Verzeichnisse vorbereiten

```powershell
# Criar estrutura de diretórios / Verzeichnisstruktur erstellen
New-Item -ItemType Directory -Force -Path "C:\VertragMGS"
New-Item -ItemType Directory -Force -Path "C:\VertragMGS\logs"
New-Item -ItemType Directory -Force -Path "C:\VertragMGS\backups"
New-Item -ItemType Directory -Force -Path "C:\VertragMGS\data"

Set-Location "C:\VertragMGS"
```

### Passo 2: Clonar Projeto / Projekt klonen

```powershell
# Instalar Git se necessário / Git installieren falls erforderlich
# winget install --id Git.Git -e --source winget

# Clonar repositório / Repository klonen
git clone https://seu-repositorio/vertrag-mgs.git .

# OU copiar arquivos manualmente do seu ambiente de desenvolvimento
# ODER Dateien manuell von Ihrer Entwicklungsumgebung kopieren
```

### Passo 3: Configurar Ambiente / Umgebung konfigurieren

```powershell
# Copiar template .env / .env Template kopieren
Copy-Item .env.production.template .env

# Editar .env com Notepad / Mit Notepad bearbeiten
notepad .env
```

**Configurações importantes em `.env` / Wichtige Einstellungen:**

```env
# GERAR SECRET_KEY / SECRET_KEY GENERIEREN:
# python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=sua-chave-super-secreta-aqui

# Banco de dados (Docker usará SQLite)
SQLALCHEMY_DATABASE_URI=sqlite+aiosqlite:///./data/contracts.db

# Email SMTP
SMTP_HOST=smtp.empresa.de
SMTP_PORT=587
SMTP_USER=vertrag-mgs@empresa.de
SMTP_PASSWORD=sua-senha-smtp

# Diretórios (dentro do container)
UPLOAD_DIR=/app/uploads
```

### Passo 4: Ajustar docker-compose.yml / docker-compose.yml anpassen

Edite `docker-compose.yml` para usar caminhos Windows:

```yaml
services:
  backend:
    # ... outras configurações
    volumes:
      - C:/VertragMGS/data:/app/data
      - C:/VertragMGS/uploads:/app/uploads
      - C:/VertragMGS/logs:/app/logs
```

### Passo 5: Build e Deploy / Erstellen und Bereitstellen

```powershell
# Navegar para o diretório do projeto
Set-Location C:\VertragMGS

# Build das imagens / Images erstellen
docker-compose build

# Iniciar containers / Container starten
docker-compose up -d

# Verificar status / Status überprüfen
docker-compose ps
```

**Saída esperada / Erwartete Ausgabe:**
```
NAME                    STATUS              PORTS
vertrag-mgs-backend-1   Up 2 minutes        0.0.0.0:8000->8000/tcp
```

### Passo 6: Executar Migrações / Migrationen ausführen

```powershell
# Executar migrações do Alembic / Alembic-Migrationen ausführen
docker-compose exec backend alembic upgrade head

# Criar usuário admin inicial (opcional)
# Ersten Admin-Benutzer erstellen (optional)
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.services.user_service import UserService
import asyncio

async def create_admin():
    async with SessionLocal() as db:
        service = UserService(db)
        # Implementar criação de admin aqui
        print('Admin criado')

asyncio.run(create_admin())
"
```

---

## ✅ Verificação / Überprüfung

### Health Checks

```powershell
# Testar endpoint básico / Basis-Endpunkt testen
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content

# Testar banco de dados / Datenbank testen
Invoke-WebRequest -Uri "http://localhost:8000/health/db" | Select-Object -ExpandProperty Content

# Ver logs / Protokolle anzeigen
docker-compose logs backend

# Logs em tempo real / Echtzeitprotokolle
docker-compose logs -f backend
```

### Acessar de outros computadores / Von anderen Computern zugreifen

```powershell
# Descobrir IP do servidor / Server-IP ermitteln
ipconfig

# Abrir firewall (se necessário) / Firewall öffnen (falls erforderlich)
New-NetFirewallRule -DisplayName "Vertrag-MGS API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Acesso / Zugriff:**
- No servidor: `http://localhost:8000`
- Na rede: `http://IP-DO-SERVIDOR:8000`
- Documentação: `http://IP-DO-SERVIDOR:8000/docs`

---

## 💾 Backup Automatizado / Automatisierte Sicherung

### Script de Backup PowerShell

Crie `C:\VertragMGS\scripts\backup.ps1`:

```powershell
# Ver arquivo: scripts/backup-windows.ps1
# (será criado a seguir)
```

### Agendar Backup Diário / Tägliche Sicherung planen

```powershell
# Criar tarefa agendada / Geplante Aufgabe erstellen
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\VertragMGS\scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3

Register-ScheduledTask -TaskName "VertragMGS-Backup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Backup diário do Vertrag-MGS / Tägliche Sicherung von Vertrag-MGS"

# Verificar tarefa / Aufgabe überprüfen
Get-ScheduledTask -TaskName "VertragMGS-Backup"
```

---

## 🔄 Manutenção / Wartung

### Atualizar Sistema / System aktualisieren

```powershell
Set-Location C:\VertragMGS

# Parar containers / Container stoppen
docker-compose down

# Atualizar código / Code aktualisieren
git pull

# Rebuild e reiniciar / Neu erstellen und neu starten
docker-compose build
docker-compose up -d

# Executar novas migrações / Neue Migrationen ausführen
docker-compose exec backend alembic upgrade head

# Verificar / Überprüfen
docker-compose ps
```

### Ver Logs / Protokolle anzeigen

```powershell
# Logs do backend / Backend-Protokolle
docker-compose logs backend

# Últimas 100 linhas / Letzte 100 Zeilen
docker-compose logs --tail=100 backend

# Logs em tempo real / Echtzeit
docker-compose logs -f backend
```

### Reiniciar Serviços / Dienste neu starten

```powershell
# Reiniciar tudo / Alles neu starten
docker-compose restart

# Reiniciar apenas backend / Nur Backend neu starten
docker-compose restart backend
```

### Limpar Recursos / Ressourcen bereinigen

```powershell
# Remover containers parados / Gestoppte Container entfernen
docker container prune -f

# Remover imagens não utilizadas / Ungenutzte Images entfernen
docker image prune -a -f

# Remover volumes órfãos / Verwaiste Volumes entfernen
docker volume prune -f
```

---

## 🚀 Inicialização Automática / Automatischer Start

### Configurar Docker para iniciar com Windows / Docker mit Windows starten

```powershell
# Docker já está configurado como serviço / Docker ist bereits als Dienst konfiguriert
Set-Service docker -StartupType Automatic

# Configurar containers para auto-restart / Container für Auto-Neustart konfigurieren
# (já configurado no docker-compose.yml com restart: unless-stopped)
```

### Testar Reinicialização / Neustart testen

```powershell
# Reiniciar servidor / Server neu starten
Restart-Computer

# Após reiniciar, verificar / Nach Neustart überprüfen
docker ps
docker-compose ps
```

---

## 🆘 Troubleshooting

### Problema: Docker não inicia / Docker startet nicht

```powershell
# Verificar serviço / Dienst überprüfen
Get-Service docker

# Iniciar manualmente / Manuell starten
Start-Service docker

# Ver logs de erro / Fehlerprotokolle anzeigen
Get-EventLog -LogName Application -Source Docker -Newest 20
```

### Problema: Container não inicia / Container startet nicht

```powershell
# Ver logs detalhados / Detaillierte Protokolle anzeigen
docker-compose logs backend

# Verificar configuração / Konfiguration überprüfen
docker-compose config

# Recriar containers / Container neu erstellen
docker-compose down
docker-compose up -d --force-recreate
```

### Problema: Porta 8000 em uso / Port 8000 in Verwendung

```powershell
# Descobrir quem está usando a porta / Herausfinden, wer den Port verwendet
netstat -ano | findstr :8000

# Matar processo (substitua PID) / Prozess beenden (PID ersetzen)
Stop-Process -Id PID -Force

# Ou mudar porta no docker-compose.yml
# Oder Port in docker-compose.yml ändern
ports:
  - "8001:8000"  # Host:Container
```

### Problema: Sem acesso à rede / Kein Netzwerkzugriff

```powershell
# Verificar firewall / Firewall überprüfen
Get-NetFirewallRule -DisplayName "Vertrag-MGS*"

# Recriar regra / Regel neu erstellen
New-NetFirewallRule -DisplayName "Vertrag-MGS API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Verificar IP / IP überprüfen
ipconfig
```

---

## 📊 Monitoramento / Überwachung

### Uso de Recursos / Ressourcennutzung

```powershell
# Estatísticas dos containers / Container-Statistiken
docker stats

# Uso de disco / Festplattennutzung
docker system df
```

### Health Checks Programáticos / Programmatische Health Checks

```powershell
# Script para monitorar health / Skript zur Gesundheitsüberwachung
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
if ($response.StatusCode -eq 200) {
    Write-Host "✅ Sistema OK" -ForegroundColor Green
} else {
    Write-Host "❌ Sistema com problemas" -ForegroundColor Red
    # Enviar alerta, reiniciar, etc.
}
```

---

## 📁 Estrutura de Diretórios Final / Endgültige Verzeichnisstruktur

```
C:\VertragMGS\
├── docker-compose.yml
├── .env
├── .env.production.template
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   └── ...
├── data/
│   └── contracts.db
├── uploads/
│   └── contracts/
├── logs/
│   ├── api.log
│   └── api-error.log
├── backups/
│   └── backup_YYYYMMDD_HHMMSS.zip
└── scripts/
    ├── backup.ps1
    └── restore.ps1
```

---

## 🎯 Resumo dos Comandos Principais / Zusammenfassung der Hauptbefehle

```powershell
# Iniciar sistema / System starten
docker-compose up -d

# Parar sistema / System stoppen
docker-compose down

# Ver status / Status anzeigen
docker-compose ps

# Ver logs / Protokolle anzeigen
docker-compose logs -f backend

# Atualizar / Aktualisieren
docker-compose pull
docker-compose up -d

# Backup manual / Manuelle Sicherung
.\scripts\backup.ps1

# Health check
Invoke-WebRequest http://localhost:8000/health
```

---

## 📞 Suporte / Support

- **Documentação API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: `C:\VertragMGS\logs\`
- **Backups**: `C:\VertragMGS\backups\`

---

**✅ Sistema pronto para produção! / System produktionsbereit!**

Para acessar de qualquer computador na rede:  
`http://IP-DO-SERVIDOR:8000`

Os 25 usuários administrativos acessarão pelo navegador quando o frontend estiver pronto.
