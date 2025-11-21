# Deploy Interno - Vertragsverwaltungssystem
# Deploy Interno - Sistema de Gerenciamento de Contratos

## Descrição / Beschreibung

**Português:** Script automatizado para deploy interno do sistema de gerenciamento de contratos em servidores da empresa.

**Deutsch:** Automatisiertes Script für den internen Deploy des Vertragsverwaltungssystems auf Firmenservern.

## Pré-requisitos / Voraussetzungen

### Sistema / System
- Ubuntu/Debian Linux
- Acesso sudo / Sudo-Zugang
- Python 3.11+
- Rede interna da empresa / Firmeninternes Netzwerk

### Dependências Instaladas Automaticamente / Automatisch Installierte Abhängigkeiten
- Apache2
- Python3-pip
- Módulos Apache necessários / Benötigte Apache-Module

## Como Usar / Verwendung

### 1. Preparar Script / Script Vorbereiten

```bash
# Tornar executável / Ausführbar machen
chmod +x deploy-internal.sh
```

### 2. Deploy Completo / Vollständiges Deployment

```bash
# Deploy básico / Basic Deployment
./deploy-internal.sh deploy

# Deploy em modo desenvolvimento / Deployment im Entwicklungsmodus  
./deploy-internal.sh deploy development

# Deploy em modo produção / Deployment im Produktionsmodus
./deploy-internal.sh deploy production
```

### 3. Gerenciar Sistema / System Verwalten

```bash
# Ver status / Status ansehen
./deploy-internal.sh status

# Ver logs / Logs ansehen
./deploy-internal.sh logs

# Ver logs específicos / Spezifische Logs ansehen
./deploy-internal.sh logs apache
./deploy-internal.sh logs fastapi

# Reiniciar serviços / Services neu starten
./deploy-internal.sh restart

# Parar serviços / Services stoppen
./deploy-internal.sh stop
```

### 4. Menu Interativo / Interaktives Menü

```bash
# Mostrar opções / Optionen anzeigen
./deploy-internal.sh
# ou / oder
./deploy-internal.sh menu
```

### 5. Ajuda / Hilfe

```bash
./deploy-internal.sh help
```

## Estrutura de Deploy / Deploy-Struktur

### Arquivos Criados / Erstellte Dateien

```
/etc/systemd/system/
└── vertrag-mgs-api.service          # Serviço FastAPI / FastAPI Service

/etc/apache2/sites-available/
└── vertrag-mgs.conf                 # Configuração Apache / Apache Konfiguration

/var/www/html/
└── vertrag-mgs/                     # Frontend files / Frontend-Dateien

/home/sschulze/projects/vertrag-mgs/
├── .venv/                           # Virtual environment / Virtuelle Umgebung
├── backend/                         # Backend FastAPI / Backend FastAPI
└── deploy/                          # Scripts de deploy / Deploy-Scripts
```

### Serviços Configurados / Konfigurierte Services

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| Apache | 80 | http://servidor/ | Frontend web / Web-Frontend |
| FastAPI | 8000 | http://servidor/api/ | API backend / Backend-API |

## URLs de Acesso / Zugangs-URLs

Após deploy bem-sucedido / Nach erfolgreichem Deployment:

```bash
# Interface principal / Hauptschnittstelle
http://IP-DO-SERVIDOR/

# API documentation / API-Dokumentation  
http://IP-DO-SERVIDOR/api/docs

# API endpoints / API-Endpunkte
http://IP-DO-SERVIDOR/api/contracts/
http://IP-DO-SERVIDOR/api/users/
http://IP-DO-SERVIDOR/api/alerts/
```

## Resolução de Problemas / Fehlerbehebung

### Problemas Comuns / Häufige Probleme

#### 1. Apache não inicia / Apache startet nicht
```bash
# Verificar configuração / Konfiguration prüfen
sudo apache2ctl configtest

# Verificar logs / Logs prüfen
sudo tail -f /var/log/apache2/error.log
```

#### 2. FastAPI não conecta / FastAPI verbindet nicht
```bash
# Verificar serviço / Service prüfen
sudo systemctl status vertrag-mgs-api

# Verificar logs / Logs prüfen
sudo journalctl -u vertrag-mgs-api -f
```

#### 3. Permissões negadas / Zugriff verweigert
```bash
# Reconfigurar permissões / Berechtigungen neu konfigurieren
./setup-permissions.sh

# Verificar propriedade Apache / Apache-Besitzer prüfen
sudo chown -R www-data:www-data /var/www/html/vertrag-mgs
```

#### 4. Banco não encontrado / Datenbank nicht gefunden
```bash
# Verificar localização / Speicherort prüfen
ls -la contracts.db

# Executar migrações / Migrationen ausführen
source .venv/bin/activate
alembic upgrade head
```

### Logs Importantes / Wichtige Logs

```bash
# Apache errors / Apache-Fehler
/var/log/apache2/vertrag-mgs-error.log

# Apache access / Apache-Zugriff
/var/log/apache2/vertrag-mgs-access.log

# FastAPI service / FastAPI-Service
sudo journalctl -u vertrag-mgs-api

# System logs / System-Logs
/var/log/syslog
```

## Firewall / Firewall-Konfiguration

### Portas Necessárias / Benötigte Ports

```bash
# Permitir HTTP / HTTP erlauben
sudo ufw allow 80/tcp

# Permitir FastAPI (opcional para debug) / FastAPI erlauben (optional für Debug)
sudo ufw allow 8000/tcp

# Ver regras / Regeln anzeigen
sudo ufw status
```

## Atualizações / Updates

### Atualizar Sistema / System Aktualisieren

```bash
# Parar serviços / Services stoppen
./deploy-internal.sh stop

# Atualizar código / Code aktualisieren
cd /home/sschulze/projects/vertrag-mgs
git pull origin main

# Reinstalar dependências / Abhängigkeiten neu installieren
source .venv/bin/activate
pip install -r backend/requirements.txt

# Executar migrações / Migrationen ausführen
alembic upgrade head

# Reiniciar serviços / Services neu starten
./deploy-internal.sh restart
```

## Backup / Backup

### Backup Essencial / Essentielles Backup

```bash
# Banco de dados / Datenbank
cp contracts.db /backup/contracts-$(date +%Y%m%d).db

# Configurações / Konfigurationen
sudo cp /etc/apache2/sites-available/vertrag-mgs.conf /backup/

# Arquivos de upload / Upload-Dateien
tar -czf /backup/uploads-$(date +%Y%m%d).tar.gz backend/uploads/
```

## Monitoramento / Überwachung

### Scripts de Monitoramento / Überwachungsskripte

```bash
# Status contínuo / Kontinuierlicher Status
watch ./deploy-internal.sh status

# Logs em tempo real / Logs in Echtzeit
sudo journalctl -u vertrag-mgs-api -f

# Monitor de recursos / Ressourcenmonitor
htop
```

## Segurança / Sicherheit

### Configurações de Segurança / Sicherheitskonfigurationen

- ✅ Banco de dados protegido (600) / Datenbank geschützt (600)
- ✅ Configurações sensíveis protegidas / Sensible Konfigurationen geschützt
- ✅ Headers de segurança no Apache / Sicherheits-Headers in Apache
- ✅ CORS configurado para rede interna / CORS für internes Netzwerk konfiguriert
- ✅ Logs de acesso monitorados / Zugriffslogs überwacht

### Recomendações / Empfehlungen

1. **Backup regular** dos dados / **Regelmäßige Backups** der Daten
2. **Monitor logs** de acesso / **Überwachung der Zugriffslogs**
3. **Atualizar sistema** regularmente / **System regelmäßig aktualisieren**
4. **Verificar permissões** periodicamente / **Berechtigungen regelmäßig prüfen**

## Suporte / Support

Para problemas técnicos / Für technische Probleme:

1. Verificar logs / Logs prüfen
2. Executar diagnósticos / Diagnosen ausführen: `./deploy-internal.sh status`
3. Consultar documentação técnica / Technische Dokumentation konsultieren
4. Contatar administrador do sistema / Systemadministrator kontaktieren
