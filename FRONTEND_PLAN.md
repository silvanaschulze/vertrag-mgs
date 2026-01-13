# 🎯 Plano Completo de Implementação - Frontend Vertrag-MGS

**Data:** 28 de dezembro de 2025  
**Autor:** Planejamento baseado em discussão com GitHub Copilot  
**Objetivo:** Implementar frontend React para sistema de gestão de contratos com roles e permissões granulares

---

## 📚 1. DECISÕES TÉCNICAS - STACK FRONTEND

### 1.1 Core Stack
```json
{
  "framework": "React 18.x",
  "bundler": "Vite 5.x",
  "language": "JavaScript (ES6+)",
  "router": "React Router DOM 6.x",
  "stateManagement": "Zustand 4.x",
  "httpClient": "Axios 1.x"
}
```

**Justificativa:**
- ✅ **Vite:** Mais rápido que Create React App, HMR instantâneo
- ✅ **Zustand:** Mais simples que Redux, ideal para primeiro projeto
- ✅ **Axios:** Interceptors para JWT, melhor tratamento de erros

### 1.2 UI Library
```json
{
  "library": "Material-UI (MUI) 5.x",
  "dataGrid": "@mui/x-data-grid 6.x (free version)",
  "icons": "@mui/icons-material 5.x",
  "styling": "@emotion/react + @emotion/styled"
}
```

**Justificativa:**
- ✅ Componentes prontos e profissionais
- ✅ DataGrid excelente para tabelas de contratos
- ✅ Documentação completa em PT-BR
- ✅ Tema customizável (light/dark mode)

### 1.3 Bibliotecas Essenciais
```json
{
  "formHandling": "react-hook-form 7.x",
  "validation": "zod 3.x",
  "dataFetching": "@tanstack/react-query 5.x",
  "dateHandling": "date-fns 3.x",
  "fileUpload": "react-dropzone 14.x",
  "notifications": "notistack 3.x",
  "charts": "recharts 2.x",
  "statePersistence": "zustand/middleware (persist)"
}
```

### 1.4 Dev Dependencies
```json
{
  "linting": "eslint + eslint-plugin-react",
  "formatting": "prettier",
  "vite": "@vitejs/plugin-react"
}
```

---

## 🏗️ 2. ESTRUTURA DE PASTAS

```
frontend/
├── public/
│   └── logo.svg
├── src/
│   ├── assets/              # Imagens, logos estáticos
│   │   └── images/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── auth/           # Login, PrivateRoute, RequirePermission
│   │   ├── dashboard/      # Widgets por role
│   │   │   ├── SystemAdminDashboard.jsx
│   │   │   ├── DirectorDashboard.jsx
│   │   │   ├── DepartmentAdminDashboard.jsx
│   │   │   ├── DepartmentUserDashboard.jsx
│   │   │   ├── TeamLeadDashboard.jsx
│   │   │   └── StaffDashboard.jsx
│   │   ├── layout/         # Header, Sidebar, Footer
│   │   │   ├── AppLayout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Footer.jsx
│   │   ├── contracts/      # Componentes de contratos
│   │   │   ├── ContractTable.jsx
│   │   │   ├── ContractForm.jsx
│   │   │   ├── ContractDetail.jsx
│   │   │   ├── ContractFilters.jsx
│   │   │   └── RentStepsTable.jsx
│   │   ├── alerts/         # Componentes de alertas
│   │   │   ├── AlertsList.jsx
│   │   │   └── AlertBadge.jsx
│   │   ├── approvals/      # Componentes de aprovações
│   │   │   ├── ApprovalsList.jsx
│   │   │   └── ApprovalActions.jsx
│   │   ├── ui/             # Componentes genéricos
│   │   │   ├── ConfirmDialog.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── PermissionGuard.jsx
│   │   └── upload/         # Upload de PDFs
│   │       ├── DropzoneUpload.jsx
│   │       └── PDFPreview.jsx
│   ├── pages/              # Páginas/Rotas
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Unauthorized.jsx
│   │   ├── NotFound.jsx
│   │   ├── contracts/
│   │   │   ├── ContractsList.jsx
│   │   │   ├── ContractCreate.jsx
│   │   │   ├── ContractEdit.jsx
│   │   │   └── ContractView.jsx
│   │   ├── import/
│   │   │   └── ImportContracts.jsx
│   │   ├── alerts/
│   │   │   └── AlertsPage.jsx
│   │   ├── approvals/
│   │   │   └── ApprovalsPage.jsx
│   │   ├── users/
│   │   │   ├── UsersList.jsx
│   │   │   └── UserManage.jsx
│   │   └── system/
│   │       ├── SystemConfig.jsx
│   │       ├── SystemLogs.jsx
│   │       └── Backups.jsx
│   ├── services/           # API calls
│   │   ├── api.js         # Axios instance + interceptors
│   │   ├── authApi.js     # /auth endpoints
│   │   ├── contractsApi.js # /contracts endpoints
│   │   ├── alertsApi.js   # /alerts endpoints
│   │   ├── approvalsApi.js # /approvals endpoints
│   │   ├── usersApi.js    # /users endpoints
│   │   └── dashboardApi.js # /dashboard endpoints
│   ├── store/              # Zustand stores
│   │   ├── authStore.js   # Token, user, roles, permissions
│   │   ├── uiStore.js     # Sidebar, theme, toasts
│   │   └── filtersStore.js # Filtros de tabelas
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.js
│   │   ├── usePermissions.js
│   │   ├── useContracts.js
│   │   └── useNotifications.js
│   ├── utils/              # Helpers
│   │   ├── permissions.js  # ROLE_PERMISSIONS, hasPermission()
│   │   ├── dateFormat.js   # Formatação PT/DE
│   │   ├── currency.js     # Formatação de valores
│   │   └── constants.js    # Roles, status, etc
│   ├── theme/              # MUI Theme
│   │   └── theme.js
│   ├── App.jsx             # Routes + Layout
│   ├── main.jsx            # Entry point
│   └── index.css           # Estilos globais mínimos
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── index.html
├── package.json
├── vite.config.js
└── README-FRONTEND.md
```

---

## 🔐 3. SISTEMA DE ROLES E PERMISSÕES

### 3.1 Roles do Backend (Copiar Exatamente)
```javascript
export const UserRole = {
  SYSTEM_ADMIN: 'SYSTEM_ADMIN',      // Level 6
  DIRECTOR: 'DIRECTOR',              // Level 5
  DEPARTMENT_ADM: 'DEPARTMENT_ADM',  // Level 4
  DEPARTMENT_USER: 'DEPARTMENT_USER',// Level 3
  TEAM_LEAD: 'TEAM_LEAD',            // Level 2
  STAFF: 'STAFF',                    // Level 1-2
  READ_ONLY: 'READ_ONLY'             // Level 1
};

export const AccessLevel = {
  SYSTEM: 6,              // Config, logs, backups
  COMPANY: 5,             // Todos contratos da empresa
  DEPARTMENT: 4,          // Contratos + usuários + reports
  DEPARTMENT_RESTRICTED: 3, // Contratos do dept, reports restritos
  TEAM: 2,                // Contratos do time
  OWN: 1                  // Apenas próprios contratos
};
```

### 3.2 Matriz de Permissões (permissions.js)
```javascript
export const ROLE_PERMISSIONS = {
  SYSTEM_ADMIN: {
    level: 6,
    permissions: [
      'contracts:*',
      'users:*',
      'alerts:*',
      'system:config',
      'system:logs',
      'system:backups',
      'approvals:*',
      'reports:*'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'system']
  },
  
  DIRECTOR: {
    level: 5,
    permissions: [
      'contracts:view_all',
      'contracts:edit_all',
      'contracts:delete_all',
      'contracts:import',
      'approvals:approve_all',
      'users:view',
      'alerts:view_all',
      'reports:view_all'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  
  DEPARTMENT_ADM: {
    level: 4,
    permissions: [
      'contracts:view_department',
      'contracts:edit_department',
      'contracts:delete_department',
      'contracts:import',
      'approvals:approve_department',
      'users:view_department',
      'users:manage_department',
      'alerts:view_department',
      'reports:view_department'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  
  DEPARTMENT_USER: {
    level: 3,
    permissions: [
      'contracts:view_department',
      'contracts:edit_department',
      'alerts:view_department',
      'reports:view_basic'
    ],
    menu: ['dashboard', 'contracts', 'alerts', 'reports']
  },
  
  TEAM_LEAD: {
    level: 2,
    permissions: [
      'contracts:view_team',
      'contracts:edit_team',
      'contracts:import',
      'alerts:view_team',
      'reports:view_team'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'reports']
  },
  
  STAFF: {
    level: 1,
    permissions: [
      'contracts:view_own',
      'contracts:edit_own',
      'alerts:view_own'
    ],
    menu: ['dashboard', 'contracts', 'alerts']
  },
  
  READ_ONLY: {
    level: 1,
    permissions: [
      'contracts:view_own',
      'alerts:view_own'
    ],
    menu: ['dashboard', 'contracts', 'alerts']
  }
};
```

### 3.3 Helper Functions
```javascript
export const hasPermission = (userRole, permission) => {
  const roleConfig = ROLE_PERMISSIONS[userRole];
  if (!roleConfig) return false;
  
  if (roleConfig.permissions.includes('*')) return true;
  
  const [category] = permission.split(':');
  return roleConfig.permissions.includes(permission) || 
         roleConfig.permissions.includes(`${category}:*`);
};

export const canAccessMenu = (userRole, menuItem) => {
  const roleConfig = ROLE_PERMISSIONS[userRole];
  return roleConfig?.menu.includes(menuItem) || false;
};

export const getAccessLevel = (userRole) => {
  return ROLE_PERMISSIONS[userRole]?.level || 1;
};
```

---

## 📊 4. DASHBOARD POR ROLE - WIDGETS ESPECÍFICOS

### 4.1 SYSTEM_ADMIN Dashboard
**Dados visíveis:**
- Total de contratos no sistema
- Total de usuários
- Alertas ativos (todos)
- Aprovações pendentes (todas)
- Último backup
- Uso de disco
- Sessões ativas
- System uptime
- Logs de erros recentes

**Componentes:**
- Cards com métricas técnicas
- Gráfico: Contratos criados (últimos 30 dias)
- Gráfico: Erros/Logs (últimas 24h)
- Tabela: Top 5 usuários mais ativos

### 4.2 DIRECTOR Dashboard
**Dados visíveis:**
- Total de contratos ativos (empresa toda)
- Contratos expirando em 30/90 dias
- Valor total mensal (€)
- Alertas críticos
- Aprovações aguardando diretoria

**Componentes:**
- Cards com KPIs executivos
- Gráfico Pizza: Contratos por departamento
- Gráfico Barras: Valor por tipo de contrato
- Timeline: Vencimentos próximos 6 meses
- Tabela: Top 10 contratos por valor

### 4.3 DEPARTMENT_ADM Dashboard
**Dados visíveis:**
- Nome do departamento
- Contratos ativos do departamento
- Contratos expirando em 30 dias
- Valor total mensal do departamento
- Alertas do departamento
- Aprovações pendentes
- Usuários no departamento

**Componentes:**
- Header com nome do departamento
- Cards com métricas do departamento
- Gráfico: Contratos por time (dentro do dept)
- Gráfico: Status de aprovações
- Tabela: Contratos do departamento

### 4.4 DEPARTMENT_USER Dashboard
**Dados visíveis:**
- Nome do departamento
- Contratos ativos do departamento (somente visualização)
- Contratos expirando em 30 dias
- Alertas do departamento

**Componentes:**
- Cards básicos (sem valores financeiros)
- Tabela simples: Contratos do departamento
- Gráfico simples: Status dos contratos

### 4.5 TEAM_LEAD Dashboard
**Dados visíveis:**
- Nome do time
- Contratos ativos do time
- Contratos expirando em 30 dias
- Alertas do time
- Valor total mensal do time

**Componentes:**
- Header com nome do time
- Cards com métricas do time
- Tabela: Contratos do time
- Gráfico: Status dos contratos

### 4.6 STAFF / READ_ONLY Dashboard
**Dados visíveis:**
- Meus contratos ativos
- Meus contratos expirando em 30 dias
- Meus alertas

**Componentes:**
- Cards minimalistas
- Tabela: Meus contratos
- (Sem gráficos)

---

## 🚀 5. ORDEM DE IMPLEMENTAÇÃO (SPRINTS)

### **SPRINT 1: Setup + Autenticação (3-4 dias)**

**Objetivo:** Configurar projeto, login funcional, proteção de rotas

**Tarefas:**
1. Criar projeto Vite + React
2. Instalar todas as dependências (MUI, Zustand, Axios, etc)
    #npm create vite@5 frontend -- --template react
          Pasta frontend/ com estrutura básica React package.json, vite.config.js, etc.
    #cd frontend
    #npm install -> Instala React, ReactDOM, Vite e dependências básicas
    #npm run dev -> testa se funcionou
3. Configurar estrutura de pastas
4. Criar tema MUI (theme.js)
5. Configurar Axios com interceptors
6. Implementar authStore (Zustand)
7. Criar tela de login
8. Implementar /auth/login no frontend
9. Armazenar token + user no localStorage
10. Criar componente PrivateRoute
11. Criar componente RequirePermission
12. Implementar logout
13. Criar layout básico (AppLayout, Header, Sidebar vazio)
14. Testar fluxo: login → dashboard → logout

**Arquivos principais:**
- `src/services/api.js` (Axios + interceptors)
- `src/services/authApi.js` (login, logout)
- `src/store/authStore.js` (Zustand)
- `src/utils/permissions.js` (ROLE_PERMISSIONS)
- `src/components/auth/PrivateRoute.jsx`
- `src/components/auth/RequirePermission.jsx`
- `src/pages/Login.jsx`
- `src/components/layout/AppLayout.jsx`
- `src/App.jsx` (rotas)

**Critério de sucesso:**
✅ Login funcional com JWT
✅ Token armazenado no localStorage
✅ Interceptor adiciona Authorization header
✅ 401 redireciona para login
✅ 403 mostra mensagem de erro
✅ Logout limpa token e redireciona

---

### **SPRINT 2: Dashboard por Role (2-3 dias)** ⚡ LAYOUT JÁ PRONTO!

**Objetivo:** Dashboards específicos por role com widgets e estatísticas do backend

**⚠️ MUDANÇA: Sprint 1 foi ALÉM do planejado!**
Já temos pronto (não precisa fazer):
- ✅ Sidebar com navegação completa (240px, filtro por role)
- ✅ Menu items usando canAccessMenu()
- ✅ AppBar com user info + logout
- ✅ AppLayout funcionando

**Tarefas REAIS da Sprint 2:**
1. ~~Implementar Sidebar com navegação~~ ✅ **JÁ FEITO NA SPRINT 1**
2. ~~Criar menu items baseados em roles (canAccessMenu)~~ ✅ **JÁ FEITO NA SPRINT 1**
3. ~~Adicionar AppBar com user info + logout~~ ✅ **JÁ FEITO NA SPRINT 1**
4. Implementar uiStore (sidebar aberta/fechada, tema) - **OPCIONAL**
5. Criar /api/dashboard/stats endpoint (backend) - **OBRIGATÓRIO**
6. Implementar dashboardApi.js (frontend) - **OBRIGATÓRIO**
7. Criar componentes de dashboard por role:
   - DashboardStaff.jsx - **COMEÇAR AQUI** (mais simples)
   - DashboardTeamLead.jsx
   - DashboardDepartmentUser.jsx
   - DashboardDepartmentAdm.jsx
   - DashboardDirector.jsx
   - DashboardSystemAdmin.jsx - **MAIS COMPLEXO** (fazer por último)
8. Criar Dashboard.jsx (renderiza componente correto por role)
9. Adicionar Cards de métricas (MUI Card) + Gráficos (Recharts)
10. Criar usuários de teste para cada role
11. Testar cada dashboard individualmente

**Arquivos principais:**
- ~~`src/components/layout/Sidebar.jsx`~~ ✅ **PRONTO**
- ~~`src/components/layout/Header.jsx`~~ ✅ **PRONTO**
- `src/store/uiStore.js` (opcional)
- `src/services/dashboardApi.js` ⏳
- `src/components/dashboard/*Dashboard.jsx` (6 componentes) ⏳
- `src/pages/Dashboard.jsx` ⏳
- `backend/app/schemas/dashboard.py` (novo) ⏳
- `backend/app/services/dashboard_service.py` (novo) ⏳
- `backend/app/routers/dashboard.py` (novo) ⏳

**Critério de sucesso:**
✅ Menu lateral mostra apenas itens permitidos por role - **JÁ FUNCIONA**
✅ Dashboard renderiza widgets corretos por role
✅ SYSTEM_ADMIN vê dados técnicos (total contratos, usuários, backups, logs)
✅ DIRECTOR vê dados de toda empresa (todos contratos, valores, gráficos executivos)
✅ DEPARTMENT_ADM vê apenas seu departamento
✅ STAFF vê apenas próprios contratos (sem gráficos)
✅ Sidebar abre/fecha corretamente - **JÁ FUNCIONA**
✅ Backend filtra stats por role automaticamente

---

### **SPRINT 3: Lista de Contratos + Filtros (4-5 dias)**

**Objetivo:** Tabela de contratos com sorting, paginação, filtros

**Tarefas:**
1. Criar contractsApi.js (getContracts, getContractById)
2. Criar ContractTable.jsx (MUI DataGrid)
3. Implementar paginação (backend retorna total + page)
4. Implementar sorting (colunas: nome, valor, data_inicio, etc)
5. Criar ContractFilters.jsx:
   - All (todos)
   - Aktiv (ativos)
   - Auslaufend (expirando em X dias)
   - Abgelaufen (expirados)
6. Implementar filtersStore (Zustand) - salvar filtros aplicados
7. Criar busca por texto (nome do contrato, fornecedor)
8. Adicionar badge de status (ativo/inativo)
9. Adicionar ações na tabela:
   - Visualizar (todos)
   - Editar (se tiver permissão)
   - Deletar (se tiver permissão)
10. Criar ContractView.jsx (modal ou página) - detalhes do contrato
11. Testar filtros por role (STAFF vê apenas próprios, etc)

**Arquivos principais:**
- `src/services/contractsApi.js`
- `src/components/contracts/ContractTable.jsx`
- `src/components/contracts/ContractFilters.jsx`
- `src/store/filtersStore.js`
- `src/pages/contracts/ContractsList.jsx`
- `src/pages/contracts/ContractView.jsx`

**Critério de sucesso:**
✅ Tabela carrega contratos do backend
✅ Paginação funciona (10/25/50 por página)
✅ Sorting funciona em todas as colunas
✅ Filtros aplicam corretamente
✅ Busca retorna resultados corretos
✅ Ações respeitam permissões (botão Edit apenas se allowed)
✅ STAFF vê apenas próprios contratos
✅ DIRECTOR vê todos os contratos

---

### **SPRINT 4: CRUD de Contratos (4-5 dias)**

**Objetivo:** Criar, editar, deletar contratos

**Tarefas:**
1. Criar ContractForm.jsx (react-hook-form + zod)
2. Criar schema de validação (zod):
   - nome_contrato (required, min 3)
   - tipo (Miete/Pacht)
   - fornecedor (required)
   - valor_mensal (number, min 0)
   - data_inicio, data_fim (dates, fim > inicio)
3. Implementar createContract, updateContract, deleteContract (API)
4. Criar ContractCreate.jsx (rota /contracts/new)
5. Criar ContractEdit.jsx (rota /contracts/:id/edit)
6. Adicionar ConfirmDialog.jsx (confirmação de delete)
7. Implementar RentStepsTable.jsx (tabela inline de rent_steps)
8. Adicionar/editar/deletar rent_steps dentro do formulário
9. Tratamento de erros (mostrar mensagens do backend)
10. Toast de sucesso (notistack)
11. Validar permissões antes de salvar
12. Testar criação/edição/deleção por role

**Arquivos principais:**
- `src/components/contracts/ContractForm.jsx`
- `src/components/contracts/RentStepsTable.jsx`
- `src/components/ui/ConfirmDialog.jsx`
- `src/pages/contracts/ContractCreate.jsx`
- `src/pages/contracts/ContractEdit.jsx`
- `src/services/contractsApi.js` (create, update, delete)

**Critério de sucesso:**
✅ Formulário valida campos corretamente
✅ Criação de contrato funciona
✅ Edição atualiza contrato existente
✅ Deleção remove contrato (com confirmação)
✅ Rent steps podem ser adicionados/removidos
✅ Erros do backend são exibidos
✅ Toast de sucesso aparece
✅ READ_ONLY não vê botão "Criar"
✅ STAFF não pode editar contratos de outros

---

### **SPRINT 5: Upload + Import de PDFs (3-4 dias)**

**Objetivo:** Upload drag & drop, preview PDF, import com dados extraídos

**Tarefas:**
1. Criar DropzoneUpload.jsx (react-dropzone)
2. Criar PDFPreview.jsx (iframe ou react-pdf)
3. Implementar importApi.js (uploadPDF, extractData)
4. Criar ImportContracts.jsx:
   - Drag & drop área
   - Upload do arquivo
   - Preview do PDF
   - Exibir dados extraídos (JSON do backend)
   - Formulário de confirmação/edição
   - Botão "Confirmar Import"
5. Tratar erros de upload (tamanho, tipo de arquivo)
6. Mostrar loading durante extração
7. Permitir editar dados antes de salvar
8. Salvar contrato após confirmação
9. Adicionar à lista de contratos
10. Testar com PDFs reais

**Arquivos principais:**
- `src/components/upload/DropzoneUpload.jsx`
- `src/components/upload/PDFPreview.jsx`
- `src/pages/import/ImportContracts.jsx`
- `src/services/importApi.js`

**Critério de sucesso:**
✅ Drag & drop funciona
✅ Preview do PDF é exibido
✅ Dados extraídos aparecem no formulário
✅ Usuário pode editar antes de salvar
✅ Import cria contrato no banco
✅ Apenas roles com permissão veem a página
✅ Erros de upload são tratados

---

### **SPRINT 6: Alertas + Aprovações (3-4 dias)**

**Objetivo:** Lista de alertas, badge de notificações, aprovações

**Tarefas:**
1. Criar alertsApi.js (getAlerts, markAsRead)
2. Criar AlertsList.jsx (tabela de alertas)
3. Criar AlertBadge.jsx (badge no menu com contador)
4. Implementar ApprovalsPage.jsx:
   - Lista de contratos pendentes de aprovação
   - Ações: Aprovar / Rejeitar
   - Modal com comentário/razão de rejeição
5. Criar approvalsApi.js (approve, reject)
6. Adicionar filtro de alertas:
   - Não lidos
   - Críticos
   - Por tipo (vencimento, renovação, etc)
7. Atualizar badge ao marcar como lido
8. Testar por role (cada um vê apenas seus alertas/aprovações)

**Arquivos principais:**
- `src/services/alertsApi.js`
- `src/services/approvalsApi.js`
- `src/components/alerts/AlertsList.jsx`
- `src/components/alerts/AlertBadge.jsx`
- `src/components/approvals/ApprovalsList.jsx`
- `src/components/approvals/ApprovalActions.jsx`
- `src/pages/alerts/AlertsPage.jsx`
- `src/pages/approvals/ApprovalsPage.jsx`

**Critério de sucesso:**
✅ Lista de alertas carrega corretamente
✅ Badge mostra número de alertas não lidos
✅ Marcar como lido atualiza badge
✅ Lista de aprovações mostra apenas pendentes
✅ Aprovar/Rejeitar funciona
✅ Comentários são salvos
✅ Apenas roles com permissão veem aprovações

---

### **SPRINT 7: Gestão de Usuários (3 dias) - OPCIONAL**

**Objetivo:** CRUD de usuários (apenas ADMIN roles)

**Tarefas:**
1. Criar usersApi.js (getUsers, createUser, updateUser, deleteUser)
2. Criar UsersList.jsx (tabela de usuários)
3. Criar UserManage.jsx (formulário)
4. Selecionar role, access_level, department, team
5. Proteger rota com RequirePermission('users:manage')
6. Testar criação de usuários

**Arquivos principais:**
- `src/services/usersApi.js`
- `src/pages/users/UsersList.jsx`
- `src/pages/users/UserManage.jsx`

**Critério de sucesso:**
✅ Apenas SYSTEM_ADMIN e DEPARTMENT_ADM veem página
✅ Criação de usuário funciona
✅ Edição atualiza usuário
✅ Deleção remove usuário

---

### **SPRINT 8: Sistema (2-3 dias) - OPCIONAL**

**Objetivo:** Configurações, logs, backups (apenas SYSTEM_ADMIN)

**Tarefas:**
1. Criar SystemConfig.jsx (configurações do sistema)
2. Criar SystemLogs.jsx (logs de erros/acessos)
3. Criar Backups.jsx (listar backups, fazer novo backup)
4. Proteger com RequirePermission('system:config')

**Arquivos principais:**
- `src/pages/system/SystemConfig.jsx`
- `src/pages/system/SystemLogs.jsx`
- `src/pages/system/Backups.jsx`

**Critério de sucesso:**
✅ Apenas SYSTEM_ADMIN vê a página
✅ Logs são exibidos corretamente
✅ Backup pode ser criado manualmente

---

### **SPRINT 9: Polimento + Responsividade (2-3 dias)**

**Objetivo:** Loading states, error handling, mobile, testes

**Tarefas:**
1. Adicionar LoadingSpinner em todas as páginas
2. Criar ErrorBoundary.jsx (captura erros React)
3. Tratar 403/401 globalmente (interceptor)
4. Toast para erros de API (notistack)
5. Tornar responsivo (mobile-friendly):
   - Sidebar vira drawer no mobile
   - Tabelas scrollam horizontalmente
   - Cards empilham verticalmente
6. Adicionar modo escuro (dark theme)
7. Testar todos os fluxos em diferentes roles
8. Criar testes básicos (opcional):
   - Login flow
   - Permissions check
   - Contract CRUD

**Arquivos principais:**
- `src/components/ui/LoadingSpinner.jsx`
- `src/components/ui/ErrorBoundary.jsx`
- `src/theme/theme.js` (dark mode)
- `src/services/api.js` (global error handling)

**Critério de sucesso:**
✅ Loading states em todas as operações
✅ Erros são capturados e exibidos
✅ Layout funciona em mobile
✅ Dark mode funciona
✅ Todas as features testadas por role

---

## 📦 6. PACKAGE.JSON COMPLETO

```json
{
  "name": "vertrag-mgs-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext js,jsx",
    "format": "prettier --write \"src/**/*.{js,jsx,json,css}\""
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "zustand": "^4.5.0",
    "axios": "^1.7.0",
    "@mui/material": "^5.16.0",
    "@mui/icons-material": "^5.16.0",
    "@mui/x-data-grid": "^6.20.0",
    "@emotion/react": "^11.13.0",
    "@emotion/styled": "^11.13.0",
    "react-hook-form": "^7.52.0",
    "zod": "^3.23.0",
    "@tanstack/react-query": "^5.51.0",
    "date-fns": "^3.6.0",
    "react-dropzone": "^14.2.0",
    "notistack": "^3.0.0",
    "recharts": "^2.12.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0",
    "eslint": "^8.57.0",
    "eslint-plugin-react": "^7.35.0",
    "prettier": "^3.3.0"
  }
}
```

---

## ⚙️ 7. CONFIGURAÇÕES IMPORTANTES

### 7.1 vite.config.js
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### 7.2 .env.example
```env
# DESENVOLVIMENTO LOCAL
VITE_API_URL=http://localhost:8000/api

# SERVIDOR DE PRODUÇÃO/TESTE (si-server)
# VITE_API_URL=http://si-server.mshome.net:8000/api

# Configuração da Aplicação
VITE_APP_NAME=Vertrag-MGS
VITE_APP_VERSION=1.0.0
```

**⚙️ Configuração do Servidor Backend:**
- **Host:** `si-server.mshome.net`
- **Usuário:** `sschulze`
- **Backend API:** `http://si-server.mshome.net:8000/api`
- **Porta Backend:** `8000`

**📝 Nota:** Para conectar ao servidor real, descomente a linha do servidor de produção e comente a linha de desenvolvimento local no arquivo `.env`

### 7.3 .eslintrc.json
```json
{
  "extends": ["eslint:recommended", "plugin:react/recommended"],
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "ecmaFeatures": { "jsx": true }
  },
  "env": { "browser": true, "es2022": true },
  "settings": { "react": { "version": "detect" } },
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off"
  }
}
```

### 7.4 .prettierrc
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 🎨 8. TEMA MUI (theme.js)

```javascript
import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    success: { main: '#4caf50' },
    warning: { main: '#ff9800' },
    error: { main: '#f44336' }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600 },
    h5: { fontWeight: 500 }
  }
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' },
    secondary: { main: '#f48fb1' }
  }
});
```

---

## 🔒 9. PRINCÍPIOS DE SEGURANÇA

### Backend decide TUDO
- ✅ JWT válido e não expirado
- ✅ Role e access_level corretos
- ✅ Filtros por department_id, team_id, user_id
- ✅ Retorna 403 se sem permissão
- ✅ Retorna 401 se token inválido

### Frontend apenas melhora UX
- ✅ Esconde menus não permitidos
- ✅ Desabilita botões sem permissão
- ✅ Redireciona em 401/403
- ✅ Mostra mensagens amigáveis
- ❌ NUNCA assume segurança no frontend

### Regras de ouro
1. **Backend valida, Frontend exibe**
2. **Roles do backend = Roles do frontend (mesmos nomes)**
3. **Permissões granulares (contracts:view_department, não apenas "view")**
4. **Scoping automático (backend filtra por escopo, não frontend)**
5. **Tratamento de 403/401 global (interceptor)**

---

## 📝 10. CHECKLIST DE IMPLEMENTAÇÃO

### Setup Inicial
- [ ] Criar projeto Vite
- [ ] Instalar dependências
- [ ] Configurar estrutura de pastas
- [ ] Criar .env
- [ ] Configurar tema MUI

### Autenticação
- [ ] Axios + interceptors
- [ ] authStore (Zustand)
- [ ] Login page
- [ ] PrivateRoute
- [ ] RequirePermission
- [ ] Logout

### Layout
- [ ] AppLayout
- [ ] Sidebar com menus por role
- [ ] Header com user info
- [ ] uiStore (sidebar, theme)

### Dashboard ✅ SPRINT 2 CONCLUÍDA
- [x] Endpoint backend /api/dashboard/stats
- [x] dashboardApi.js
- [x] 6 componentes de dashboard (um por role)
  - [x] DashboardSystemAdmin.jsx (Level 6 - Technical only)
  - [x] DashboardDirector.jsx (Level 5 - Company wide)
  - [x] DashboardDepartmentAdm.jsx (Level 4 - Department with finance)
  - [x] DashboardDepartmentUser.jsx (Level 3 - Department without finance)
  - [x] DashboardTeamLead.jsx (Level 2 - Team contracts)
  - [x] DashboardStaff.jsx (Level 1 - Own contracts only)
- [x] Dashboard.jsx (renderiza correto)
- [x] Correções de permissões (Level 6 = technical only, NO contracts)
- [x] Backend schemas (DashboardStats with Optional fields)
- [x] Backend services (6 role-specific methods)
- [x] Backend routers (GET /api/dashboard/stats)
- [x] Frontend API integration (dashboardApi.js)
- [x] Teste com usuários Level 5 e 6 (director@test.com, admin@test.com)
- [x] Tradução de todos dashboards para inglês (standardização)
- **Data de conclusão:** Janeiro 2025

### Contratos
- [ ] ContractTable (DataGrid)
- [ ] Filtros (All/Aktiv/Auslaufend)
- [ ] Paginação + sorting
- [ ] Busca
- [ ] ContractForm (create/edit)
- [ ] ContractView (detalhes)
- [ ] Delete com confirmação
- [ ] RentStepsTable

### Upload/Import
- [ ] DropzoneUpload
- [ ] PDFPreview
- [ ] ImportContracts page
- [ ] extractData + confirm

### Alertas/Aprovações
- [ ] AlertsList
- [ ] AlertBadge (contador)
- [ ] ApprovalsList
- [ ] Approve/Reject actions

### Usuários (opcional)
- [ ] UsersList
- [ ] UserManage

### Sistema (opcional)
- [ ] SystemConfig
- [ ] SystemLogs
- [ ] Backups

### Polimento
- [ ] Loading states
- [ ] Error handling global
- [ ] Responsividade mobile
- [ ] Dark mode
- [ ] Testes por role

---

## 🎯 PONTOS CRÍTICOS DE ATENÇÃO

### 1. Sempre validar roles no backend
```python
# ✅ CORRETO
if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.DIRECTOR]:
    raise HTTPException(403, "Sem permissão")

# ❌ ERRADO (confiar no frontend)
# Frontend envia role e backend aceita
```

### 2. Filtrar queries por escopo
```python
# ✅ CORRETO
if current_user.role == UserRole.DEPARTMENT_ADM:
    query = query.filter(Contract.department_id == current_user.department_id)

# ❌ ERRADO (retornar tudo e filtrar no frontend)
```

### 3. Frontend: hasPermission antes de ações
```javascript
// ✅ CORRETO
{isAllowed('contracts:edit') && (
  <Button onClick={handleEdit}>Editar</Button>
)}

// ❌ ERRADO (mostrar sempre e bloquear no backend)
<Button onClick={handleEdit}>Editar</Button>
```

### 4. Dashboard: dados do backend, não calcular no frontend
```javascript
// ✅ CORRETO
const stats = await dashboardApi.getStats(); // Backend já filtra

// ❌ ERRADO
const allContracts = await contractsApi.getAll();
const myContracts = allContracts.filter(...); // Filtrar no frontend
```

### 5. Interceptor trata 401/403 globalmente
```javascript
// ✅ CORRETO (interceptor)
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      authStore.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ❌ ERRADO (tratar em cada componente)
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL

### Links úteis
- **Vite:** https://vitejs.dev/
- **React Router:** https://reactrouter.com/
- **Zustand:** https://github.com/pmndrs/zustand
- **Material-UI:** https://mui.com/
- **React Hook Form:** https://react-hook-form.com/
- **Zod:** https://zod.dev/
- **date-fns:** https://date-fns.org/

### Comandos úteis
```bash
# Criar projeto
npm create vite@latest frontend -- --template react

# Instalar dependências
cd frontend && npm install

# Dev server
npm run dev

# Build produção
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Format
npm run format
```

---

## ✅ RESUMO EXECUTIVO

### O que vai ser implementado
1. **Frontend React + Vite** com MUI
2. **Sistema de autenticação** com JWT
3. **Sistema de permissões granulares** (7 roles, 6 levels)
4. **Dashboard específico por role** (6 widgets diferentes)
5. **CRUD completo de contratos** (lista, create, edit, delete)
6. **Upload/import de PDFs** com extração de dados
7. **Alertas e aprovações** com notificações
8. **Gestão de usuários** (admin)
9. **Configurações do sistema** (admin)

### Stack final
- React 18 + Vite 5
- Material-UI 5 + DataGrid
- Zustand 4 (state)
- Axios 1 (HTTP)
- React Router 6
- React Hook Form + Zod
- date-fns + recharts + notistack

### Segurança
- ✅ Backend valida TUDO (JWT, roles, permissões)
- ✅ Frontend apenas UX (esconde/mostra)
- ✅ Scoping automático (dept, team, own)
- ✅ Tratamento global de 401/403
- ✅ Roles exatos do backend

### Timeline estimado
- **Sprint 1-2:** 6-8 dias (setup + auth + dashboard)
- **Sprint 3-4:** 8-10 dias (contratos CRUD)
- **Sprint 5-6:** 6-8 dias (upload + alertas)
- **Sprint 7-9:** 7-9 dias (usuários + sistema + polish)
- **TOTAL:** ~27-35 dias (~5-7 semanas)

---

**FIM DO PLANO - PRONTO PARA IMPLEMENTAÇÃO**

