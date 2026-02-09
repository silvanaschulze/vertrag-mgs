# 🚀 PROMPT - Sprint 8: Sistema Admin e Configurações

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

---

## ✅ SPRINTS ANTERIORES COMPLETAS

### Sprint 1-7: ✅ Todas completas

---

## 🎯 SPRINT 8: SISTEMA ADMIN E CONFIGURAÇÕES

### Objetivo

Implementar painel de administração do sistema com:
- **Configurações gerais** (e-mail, notificações, etc)
- **Logs do sistema** (erros, ações, acessos)
- **Backups** (criar, restaurar, agendar)
- **Health Checks** (banco de dados, disco, API)
- **Monitoramento** (estatísticas de uso, performance)
- **Apenas para SYSTEM_ADMIN (Level 6)**

---

## 📝 Backend Já Existente

```
✅ backend/app/routers/health.py - Endpoints:
   - GET /api/health (health check geral)
   - GET /api/health/db (status do banco)
   - GET /api/health/storage (uso de disco)
   - GET /api/system/stats (estatísticas de uso)
   - GET /api/system/logs (logs do sistema)
   - POST /api/system/backup (criar backup)
   - GET /api/system/backups (lista de backups)
   - POST /api/system/restore (restaurar backup)

✅ Scripts de backup: backup-system.sh, restore-system.sh
```

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── system/  (❌ CRIAR AGORA)
│   │   ├── HealthStatus.jsx
│   │   ├── SystemLogs.jsx
│   │   ├── BackupManager.jsx
│   │   ├── SystemStats.jsx
│   │   └── ConfigForm.jsx
│   └── ...
├── pages/
│   ├── system/  (❌ CRIAR AGORA)
│   │   ├── SystemPage.jsx
│   │   ├── ConfigPage.jsx
│   │   ├── LogsPage.jsx
│   │   └── BackupsPage.jsx
│   └── ...
├── services/
│   ├── systemApi.js  (❌ CRIAR AGORA)
│   └── ...
└── ...
```

---

## 📝 CHECKLIST SPRINT 8

### 1. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/systemApi.js` com:
  - `getHealth()` - GET /api/health
  - `getDBHealth()` - GET /api/health/db
  - `getStorageHealth()` - GET /api/health/storage
  - `getSystemStats()` - GET /api/system/stats
  - `getLogs(params)` - GET /api/system/logs?level=ERROR&page=1
  - `createBackup()` - POST /api/system/backup
  - `getBackups()` - GET /api/system/backups
  - `restoreBackup(backupId)` - POST /api/system/restore
  - `getConfig()` - GET /api/system/config
  - `updateConfig(data)` - PUT /api/system/config

### 2. Componentes de Sistema

- [ ] `frontend/src/components/system/HealthStatus.jsx`
  **Funcionalidades:**
  - Exibe status de saúde do sistema em cards
  - Cards:
    - Database (conectado, tempo de resposta)
    - Storage (espaço livre, espaço usado)
    - API (uptime, versão)
  - Cores: Verde (OK), Amarelo (Warning), Vermelho (Error)
  - Auto-atualiza a cada 30s (polling)
  
  **Props:**
  ```javascript
  {
    health: {
      database: { status: 'OK', response_time: 15 },
      storage: { free: '50GB', used: '30GB', percent: 60 },
      api: { uptime: '5 days', version: '1.0.0' }
    }
  }
  ```

- [ ] `frontend/src/components/system/SystemLogs.jsx`
  **Funcionalidades:**
  - Tabela de logs do sistema
  - Colunas:
    - Timestamp
    - Level (ERROR, WARNING, INFO) - Chip colorido
    - Message
    - Source (módulo/arquivo)
  - Filtros por level
  - Paginação
  - Auto-scroll para logs novos
  
  **Props:**
  ```javascript
  {
    logs: Array<Log>,
    loading: boolean,
    filters: { level: 'ERROR' },
    onFilterChange: (filters) => void
  }
  ```

- [ ] `frontend/src/components/system/BackupManager.jsx`
  **Funcionalidades:**
  - Lista de backups disponíveis
  - Informações:
    - Data/Hora do backup
    - Tamanho do arquivo
    - Tipo (manual, automático)
    - Status (completo, falhou)
  - Ações:
    - Criar Backup (botão)
    - Restaurar (botão com confirmação)
    - Download backup
    - Deletar backup (com confirmação)
  - Loading states
  
  **Props:**
  ```javascript
  {
    backups: Array<Backup>,
    onCreateBackup: () => void,
    onRestoreBackup: (backupId) => void,
    onDeleteBackup: (backupId) => void,
    loading: boolean
  }
  ```

- [ ] `frontend/src/components/system/SystemStats.jsx`
  **Funcionalidades:**
  - Cards com estatísticas de uso do sistema
  - Métricas:
    - Total de contratos
    - Total de usuários
    - Total de alertas
    - Total de aprovações
    - Espaço em disco usado
    - Sessões ativas
    - Requests por hora (média)
  - Gráficos (Recharts):
    - Contratos criados (últimos 30 dias)
    - Usuários ativos (última semana)
  
  **Props:**
  ```javascript
  {
    stats: {
      totalContracts: 252,
      totalUsers: 7,
      totalAlerts: 45,
      diskUsage: 60,
      activeSessions: 3,
      requestsPerHour: 120
    }
  }
  ```

- [ ] `frontend/src/components/system/ConfigForm.jsx`
  **Funcionalidades:**
  - Formulário de configurações do sistema
  - Campos:
    - SMTP Host (email)
    - SMTP Port (email)
    - SMTP User (email)
    - SMTP Password (email)
    - Default Language (DE/PT)
    - Session Timeout (minutos)
    - Backup Frequency (diário, semanal)
    - Max Upload Size (MB)
  - Validação
  - Botão Salvar
  
  **Props:**
  ```javascript
  {
    config: Object,
    onSubmit: (data) => void,
    loading: boolean
  }
  ```

### 3. Páginas

- [ ] `frontend/src/pages/system/SystemPage.jsx`
  **Layout (Dashboard de Admin):**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Systemadministration / System Administration
    </Typography>
    
    <Grid container spacing={3}>
      {/* Health Status */}
      <Grid item xs={12}>
        <HealthStatus health={healthData} />
      </Grid>
      
      {/* System Stats */}
      <Grid item xs={12}>
        <SystemStats stats={statsData} />
      </Grid>
      
      {/* Quick Actions */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Schnellaktionen / Quick Actions
          </Typography>
          <Button onClick={() => navigate('/app/system/backups')}>
            Backups verwalten / Manage Backups
          </Button>
          <Button onClick={() => navigate('/app/system/logs')}>
            Logs anzeigen / View Logs
          </Button>
          <Button onClick={() => navigate('/app/system/config')}>
            Einstellungen / Settings
          </Button>
        </Paper>
      </Grid>
    </Grid>
  </Container>
  ```

- [ ] `frontend/src/pages/system/ConfigPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Systemeinstellungen / System Settings
    </Typography>
    
    <Paper sx={{ p: 3 }}>
      <ConfigForm 
        config={config}
        onSubmit={handleSaveConfig}
        loading={loading}
      />
    </Paper>
  </Container>
  ```

- [ ] `frontend/src/pages/system/LogsPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Systemprotokolle / System Logs
    </Typography>
    
    <SystemLogs 
      logs={logs}
      filters={filters}
      onFilterChange={handleFilterChange}
      loading={loading}
    />
  </Container>
  ```

- [ ] `frontend/src/pages/system/BackupsPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between' }}>
      <Typography variant="h4">
        Backups
      </Typography>
      <Button 
        variant="contained" 
        startIcon={<BackupIcon />}
        onClick={handleCreateBackup}
        disabled={creatingBackup}
      >
        Backup erstellen / Create Backup
      </Button>
    </Box>
    
    <BackupManager 
      backups={backups}
      onCreateBackup={handleCreateBackup}
      onRestoreBackup={handleRestoreBackup}
      onDeleteBackup={handleDeleteBackup}
      loading={loading}
    />
  </Container>
  ```

### 4. Routing

- [ ] Atualizar `frontend/src/App.jsx`:
  ```jsx
  <Route
    path="system"
    element={
      <RequirePermission permission="system:config">
        <SystemPage />
      </RequirePermission>
    }
  />
  <Route
    path="system/config"
    element={
      <RequirePermission permission="system:config">
        <ConfigPage />
      </RequirePermission>
    }
  />
  <Route
    path="system/logs"
    element={
      <RequirePermission permission="system:logs">
        <LogsPage />
      </RequirePermission>
    }
  />
  <Route
    path="system/backups"
    element={
      <RequirePermission permission="system:backups">
        <BackupsPage />
      </RequirePermission>
    }
  />
  ```

### 5. Sidebar Menu

- [ ] Menu "System" já existe no Sidebar
- [ ] Visível APENAS para SYSTEM_ADMIN (Level 6)
- [ ] Submenu (opcional):
  - System Overview
  - Settings
  - Logs
  - Backups

---

## 🔐 REGRAS DE PERMISSÕES

### Acesso ao Sistema Admin (system:config, system:logs, system:backups)

- **APENAS Level 6 (SYSTEM_ADMIN):** Tem acesso total
- **Outros:** NÃO veem menu System

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. systemApi.js (API calls)
2. SystemPage.jsx (dashboard admin)
3. HealthStatus.jsx (status de saúde)
4. SystemStats.jsx (estatísticas)

### Prioridade MÉDIA (depois)

5. BackupManager.jsx (gerenciamento de backups)
6. BackupsPage.jsx (página de backups)
7. SystemLogs.jsx (tabela de logs)
8. LogsPage.jsx (página de logs)

### Prioridade BAIXA (polimento)

9. ConfigForm.jsx (formulário de configurações)
10. ConfigPage.jsx (página de configurações)
11. Auto-refresh (polling para health status e logs)
12. Gráficos avançados (Recharts)

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 8 estará completa quando:

- [ ] Dashboard de System Admin funcional
- [ ] Health checks exibidos (DB, Storage, API)
- [ ] System stats exibidos (contratos, usuários, etc)
- [ ] Lista de logs com filtros funcionando
- [ ] Criação de backup manual funcionando
- [ ] Restauração de backup funcionando (com confirmação)
- [ ] Configurações do sistema podem ser editadas
- [ ] Apenas SYSTEM_ADMIN (Level 6) vê menu System
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Toast notifications (sucesso/erro)

---

## 🚀 COMO COMEÇAR

### 1. Criar systemApi.js primeiro:

- Implementar 10 funções (health, stats, logs, backups, config)

### 2. Implementar SystemPage (dashboard):

- Health Status
- System Stats
- Quick Actions

### 3. Implementar BackupsPage:

- Lista de backups
- Criar backup
- Restaurar backup (com confirmação)

### 4. Implementar LogsPage:

- Tabela de logs
- Filtros por level

### 5. Testar:

- Login como admin@test.com (Level 6)
- Verificar acesso ao menu System
- Testar todas funcionalidades

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend health: `backend/app/routers/health.py`
- Backend scripts: `backup-system.sh`, `restore-system.sh`

---

## 🎯 META

Ao final da Sprint 8, o SYSTEM_ADMIN deverá conseguir:

1. **Ver menu "System"** no sidebar (apenas Level 6)
2. **Acessar dashboard de admin**
3. **Ver health checks** (DB, Storage, API)
4. **Ver estatísticas de uso** (contratos, usuários, etc)
5. **Criar backup manual** do sistema
6. **Ver lista de backups** disponíveis
7. **Restaurar backup** (com confirmação)
8. **Ver logs do sistema** (filtrados por level)
9. **Editar configurações** do sistema
10. **Receber feedback** visual de sucesso/erro

---

**Pronto para começar! Vamos implementar a Sprint 8 passo a passo, seguindo as prioridades definidas.**
