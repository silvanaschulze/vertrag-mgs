# 🚀 Production Deployment Guide - Vertrag MGS

**Guia de Implantação em Produção**  
**Produktionsbereitstellungsanleitung**

---

## 📋 Pré-requisitos / Voraussetzungen

### Sistema Operacional / Betriebssystem
- Ubuntu 20.04+ / Debian 11+
- Python 3.11+
- Apache 2.4+ ou Nginx
- systemd

### Pacotes Necessários / Erforderliche Pakete
```bash
sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    apache2 \
    libapache2-mod-proxy-html \
    sqlite3 \
    curl \
    logrotate
```

---

## 🔧 Instalação Passo a Passo / Schritt-für-Schritt-Installation

### 1. Preparar Diretórios / Verzeichnisse vorbereiten

```bash
# Criar estrutura / Verzeichnisstruktur erstellen
sudo mkdir -p /var/www/vertrag-mgs
sudo mkdir -p /var/log/vertrag-mgs
sudo mkdir -p /var/backups/vertrag-mgs

# Permissões / Berechtigungen
sudo chown -R www-data:www-data /var/www/vertrag-mgs
sudo chown -R www-data:www-data /var/log/vertrag-mgs
sudo chmod -R 755 /var/www/vertrag-mgs
```

### 2. Clonar Repositório / Repository klonen

```bash
cd /var/www/vertrag-mgs
sudo -u www-data git clone https://seu-repo/vertrag-mgs.git .
```

### 3. Configurar Ambiente Python / Python-Umgebung einrichten

```bash
cd /var/www/vertrag-mgs/backend

# Criar virtualenv / Virtualenv erstellen
sudo -u www-data python3.11 -m venv .venv

# Ativar / Aktivieren
source .venv/bin/activate

# Instalar dependências / Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements-compatible.txt
```

### 4. Configurar Variáveis de Ambiente / Umgebungsvariablen konfigurieren

```bash
# Copiar template / Template kopieren
cp .env.production.template .env

# Editar com valores reais / Mit echten Werten bearbeiten
nano .env

# IMPORTANTE / WICHTIG: Gerar SECRET_KEY aleatória
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copiar output para SECRET_KEY no .env
```

**Configurações críticas / Kritische Konfigurationen:**
- `SECRET_KEY` - Chave única de 64 caracteres
- `SMTP_*` - Credenciais de e-mail
- `FIRST_SUPERUSER_*` - Admin inicial

### 5. Executar Migrações / Migrationen ausführen

```bash
cd /var/www/vertrag-mgs

# Aplicar migrações do Alembic / Alembic-Migrationen anwenden
alembic upgrade head
```

### 6. Configurar Systemd Service

```bash
# Copiar arquivo de serviço / Service-Datei kopieren
sudo cp deploy/vertrag-mgs-api.service /etc/systemd/system/

# Recarregar systemd / systemd neu laden
sudo systemctl daemon-reload

# Habilitar serviço / Dienst aktivieren
sudo systemctl enable vertrag-mgs-api.service

# Iniciar serviço / Dienst starten
sudo systemctl start vertrag-mgs-api.service

# Verificar status / Status prüfen
sudo systemctl status vertrag-mgs-api.service
```

### 7. Configurar Apache Reverse Proxy

```bash
# Habilitar módulos / Module aktivieren
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod rewrite

# Copiar configuração / Konfiguration kopieren
sudo cp deploy/apache-internal.conf /etc/apache2/sites-available/vertrag-mgs.conf

# Habilitar site / Site aktivieren
sudo a2ensite vertrag-mgs.conf

# Testar configuração / Konfiguration testen
sudo apache2ctl configtest

# Reiniciar Apache / Apache neu starten
sudo systemctl restart apache2
```

### 8. Configurar Logrotate

```bash
# Copiar configuração / Konfiguration kopieren
sudo cp deploy/logrotate-vertrag-mgs /etc/logrotate.d/vertrag-mgs

# Testar / Testen
sudo logrotate -d /etc/logrotate.d/vertrag-mgs
```

### 9. Configurar Backups Automáticos / Automatische Backups einrichten

```bash
# Copiar scripts / Skripte kopieren
sudo cp scripts/backup-system.sh /usr/local/bin/
sudo cp scripts/restore-system.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup-system.sh
sudo chmod +x /usr/local/bin/restore-system.sh

# Configurar cron / Cron konfigurieren
cd /var/www/vertrag-mgs
sudo bash scripts/setup-backup-cron.sh

# Testar backup manualmente / Backup manuell testen
sudo /usr/local/bin/backup-system.sh
```

---

## ✅ Verificação de Instalação / Installationsüberprüfung

### Health Checks

```bash
# 1. Verificar serviço systemd / systemd-Dienst prüfen
systemctl status vertrag-mgs-api.service

# 2. Verificar porta / Port prüfen
curl http://localhost:8000/health

# 3. Verificar banco de dados / Datenbank prüfen
curl http://localhost:8000/health/db

# 4. Verificar armazenamento / Speicher prüfen
curl http://localhost:8000/health/storage

# 5. Health check completo / Vollständiger Health Check
curl http://localhost:8000/health/detailed
```

### Logs

```bash
# Logs da aplicação / Anwendungsprotokolle
sudo tail -f /var/log/vertrag-mgs/api.log

# Logs de erro / Fehlerprotokolle
sudo tail -f /var/log/vertrag-mgs/api-error.log

# Journalctl (systemd)
sudo journalctl -u vertrag-mgs-api.service -f
```

---

## 🐳 Deployment com Docker (Alternativa)

### Build e Execução / Build und Ausführung

```bash
# Build da imagem / Image bauen
bash deploy/docker-build.sh

# Executar com docker-compose / Mit docker-compose ausführen
docker-compose up -d

# Verificar containers / Container prüfen
docker-compose ps

# Logs / Protokolle
docker-compose logs -f backend
```

---

## 🔄 Atualizações / Updates

### Atualizar aplicação / Anwendung aktualisieren

```bash
cd /var/www/vertrag-mgs

# 1. Fazer backup / Backup erstellen
sudo /usr/local/bin/backup-system.sh

# 2. Parar serviço / Dienst stoppen
sudo systemctl stop vertrag-mgs-api.service

# 3. Atualizar código / Code aktualisieren
sudo -u www-data git pull

# 4. Atualizar dependências (se necessário)
source backend/.venv/bin/activate
pip install -r backend/requirements-compatible.txt

# 5. Executar migrações / Migrationen ausführen
alembic upgrade head

# 6. Reiniciar serviço / Dienst neu starten
sudo systemctl start vertrag-mgs-api.service

# 7. Verificar / Überprüfen
curl http://localhost:8000/health
```

---

## 🛡️ Segurança / Sicherheit

### Firewall (UFW)

```bash
# Permitir Apache / Apache erlauben
sudo ufw allow 'Apache Full'

# Permitir SSH / SSH erlauben
sudo ufw allow OpenSSH

# Habilitar firewall / Firewall aktivieren
sudo ufw enable
```

### Permissões de Arquivos / Dateiberechtigungen

```bash
# Uploads
sudo chown -R www-data:www-data /var/www/vertrag-mgs/backend/uploads
sudo chmod -R 755 /var/www/vertrag-mgs/backend/uploads

# Banco de dados
sudo chown www-data:www-data /var/www/vertrag-mgs/backend/contracts.db
sudo chmod 644 /var/www/vertrag-mgs/backend/contracts.db
```

---

## 📊 Monitoramento / Überwachung

### Healthcheck Endpoints

| Endpoint | Propósito / Zweck |
|----------|-------------------|
| `/health` | Status básico / Grundstatus |
| `/health/db` | Conexão com banco / Datenbankverbindung |
| `/health/storage` | Espaço em disco / Speicherplatz |
| `/health/detailed` | Completo / Vollständig |

### Prometheus Metrics (Futuro)

```bash
# TODO: Implementar metrics endpoint
# /metrics - Prometheus format
```

---

## 🆘 Troubleshooting

### Serviço não inicia / Dienst startet nicht

```bash
# Verificar logs / Protokolle prüfen
sudo journalctl -u vertrag-mgs-api.service -n 50

# Verificar permissões / Berechtigungen prüfen
ls -la /var/www/vertrag-mgs/backend/

# Testar comando manualmente / Befehl manuell testen
cd /var/www/vertrag-mgs/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Erro 502 Bad Gateway

```bash
# Verificar se serviço está rodando / Prüfen ob Dienst läuft
systemctl status vertrag-mgs-api.service

# Verificar porta / Port prüfen
netstat -tlnp | grep 8000

# Verificar configuração Apache / Apache-Konfiguration prüfen
sudo apache2ctl configtest
```

### Banco de dados corrompido / Datenbank beschädigt

```bash
# Restaurar do backup / Aus Backup wiederherstellen
sudo /usr/local/bin/restore-system.sh
# Selecionar backup mais recente / Neuestes Backup auswählen
```

---

## 📞 Suporte / Support

- **Documentação**: `/docs/` (Swagger UI)
- **Logs**: `/var/log/vertrag-mgs/`
- **Backups**: `/var/backups/vertrag-mgs/`

---

**Versão / Version:** 1.0.0  
**Última atualização / Letzte Aktualisierung:** 2024
