# 🚀 PROMPT PARA INICIAR IMPLEMENTAÇÃO DO FRONTEND

**COLE ESTE PROMPT NO PRÓXIMO CHAT PARA COMEÇAR A IMPLEMENTAÇÃO:**

---

## CONTEXTO DO PROJETO

Estou desenvolvendo um **sistema de gestão de contratos (Vertrag-MGS)** com backend FastAPI pronto e funcional. Agora vou implementar o frontend React.

### Backend (JÁ PRONTO)
- **Tech Stack:** FastAPI 0.119.0, SQLAlchemy 2.0+, SQLite, Alembic
- **Features implementadas:**
  - Autenticação JWT completa
  - CRUD de contratos com rent_steps
  - Upload e extração automática de PDFs
  - Sistema de alertas
  - Sistema de aprovações (ContractApproval)
  - Health checks (/health, /health/db, /health/detailed, /health/ready)
  - Sistema de backups (Linux/Windows)
  - 7 roles com 6 access levels (SYSTEM_ADMIN até READ_ONLY)

### Sistema de Roles e Permissões (CRÍTICO - COPIAR EXATAMENTE)

**Roles:**
```python
UserRole:
  SYSTEM_ADMIN    (Level 6) - Admin técnico completo
  DIRECTOR        (Level 5) - Acesso toda empresa  
  DEPARTMENT_ADM  (Level 4) - Admin do departamento
  DEPARTMENT_USER (Level 3) - Usuário do departamento
  TEAM_LEAD       (Level 2) - Líder de time
  STAFF           (Level 1-2) - Colaborador
  READ_ONLY       (Level 1) - Somente leitura
```

**Access Levels:**
```python
AccessLevel:
  SYSTEM (6) - Config, logs, backups
  COMPANY (5) - Todos contratos da empresa
  DEPARTMENT (4) - Contratos + usuários + reports do dept
  DEPARTMENT_RESTRICTED (3) - Contratos do dept, reports restritos  
  TEAM (2) - Contratos do time
  OWN (1) - Apenas próprios contratos
```

**Princípio fundamental de segurança:**
- ✅ **Backend decide TUDO** (JWT, roles, permissões, filtros por escopo)
- ✅ **Frontend apenas UX** (esconde/mostra menus e botões)
- ✅ **Dashboard específico por role** (6 widgets diferentes)
- ✅ **Roles do frontend = roles do backend** (mesmos nomes)

---

## DECISÕES TÉCNICAS TOMADAS

### Stack Frontend
```json
{
  "framework": "React 18",
  "bundler": "Vite 5",
  "router": "React Router DOM 6",
  "stateManagement": "Zustand 4",
  "httpClient": "Axios 1",
  "uiLibrary": "Material-UI 5",
  "dataGrid": "@mui/x-data-grid",
  "formHandling": "react-hook-form 7 + zod 3",
  "dataFetching": "@tanstack/react-query 5",
  "dateHandling": "date-fns 3",
  "fileUpload": "react-dropzone 14",
  "notifications": "notistack 3",
  "charts": "recharts 2"
}
```

### Estrutura de Pastas Definida
```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/              # Login, PrivateRoute, RequirePermission
│   │   ├── dashboard/         # 6 widgets (um por role)
│   │   ├── layout/            # AppLayout, Sidebar, Header
│   │   ├── contracts/         # Table, Form, Detail, Filters, RentSteps
│   │   ├── alerts/            # AlertsList, AlertBadge
│   │   ├── approvals/         # ApprovalsList, ApprovalActions
│   │   ├── ui/                # ConfirmDialog, LoadingSpinner, ErrorBoundary
│   │   └── upload/            # DropzoneUpload, PDFPreview
│   ├── pages/                 # Login, Dashboard, Contracts, Alerts, etc
│   ├── services/              # api.js, authApi.js, contractsApi.js, etc
│   ├── store/                 # authStore, uiStore, filtersStore (Zustand)
│   ├── hooks/                 # useAuth, usePermissions, useContracts
│   ├── utils/                 # permissions.js (ROLE_PERMISSIONS), dateFormat, currency
│   ├── theme/                 # theme.js (MUI light/dark)
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
└── .env.example
```

### Dashboard por Role (IMPORTANTE)
Cada role vê um dashboard diferente com widgets específicos:

**SYSTEM_ADMIN:**
- Total contratos, usuários, alertas, aprovações
- Último backup, uso de disco, sessões ativas, uptime
- Gráficos: contratos criados, erros/logs, top usuários

**DIRECTOR:**
- Total contratos ativos (empresa toda)
- Expirando em 30/90 dias
- Valor total mensal
- Gráficos: contratos por dept, valor por tipo, timeline vencimentos

**DEPARTMENT_ADM:**
- Nome do departamento
- Contratos ativos do dept, expirando, valor mensal
- Alertas, aprovações, usuários do dept
- Gráficos: contratos por time, status aprovações

**DEPARTMENT_USER:**
- Nome do departamento
- Contratos ativos do dept (view only), expirando, alertas
- Gráfico simples de status

**TEAM_LEAD:**
- Nome do time
- Contratos ativos do time, expirando, alertas, valor mensal
- Gráfico de status

**STAFF / READ_ONLY:**
- Meus contratos ativos
- Meus contratos expirando
- Meus alertas
- Apenas tabela, sem gráficos

---

## MATRIZ DE PERMISSÕES FRONTEND

```javascript
// src/utils/permissions.js - IMPLEMENTAR EXATAMENTE ASSIM

export const UserRole = {
  SYSTEM_ADMIN: 'SYSTEM_ADMIN',
  DIRECTOR: 'DIRECTOR',
  DEPARTMENT_ADM: 'DEPARTMENT_ADM',
  DEPARTMENT_USER: 'DEPARTMENT_USER',
  TEAM_LEAD: 'TEAM_LEAD',
  STAFF: 'STAFF',
  READ_ONLY: 'READ_ONLY'
};

export const ROLE_PERMISSIONS = {
  SYSTEM_ADMIN: {
    level: 6,
    permissions: ['contracts:*', 'users:*', 'alerts:*', 'system:config', 'system:logs', 'system:backups', 'approvals:*', 'reports:*'],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'system']
  },
  DIRECTOR: {
    level: 5,
    permissions: ['contracts:view_all', 'contracts:edit_all', 'contracts:delete_all', 'contracts:import', 'approvals:approve_all', 'users:view', 'alerts:view_all', 'reports:view_all'],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  DEPARTMENT_ADM: {
    level: 4,
    permissions: ['contracts:view_department', 'contracts:edit_department', 'contracts:delete_department', 'contracts:import', 'approvals:approve_department', 'users:view_department', 'users:manage_department', 'alerts:view_department', 'reports:view_department'],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  DEPARTMENT_USER: {
    level: 3,
    permissions: ['contracts:view_department', 'contracts:edit_department', 'alerts:view_department', 'reports:view_basic'],
    menu: ['dashboard', 'contracts', 'alerts', 'reports']
  },
  TEAM_LEAD: {
    level: 2,
    permissions: ['contracts:view_team', 'contracts:edit_team', 'contracts:import', 'alerts:view_team', 'reports:view_team'],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'reports']
  },
  STAFF: {
    level: 1,
    permissions: ['contracts:view_own', 'contracts:edit_own', 'alerts:view_own'],
    menu: ['dashboard', 'contracts', 'alerts']
  },
  READ_ONLY: {
    level: 1,
    permissions: ['contracts:view_own', 'alerts:view_own'],
    menu: ['dashboard', 'contracts', 'alerts']
  }
};

export const hasPermission = (userRole, permission) => {
  const roleConfig = ROLE_PERMISSIONS[userRole];
  if (!roleConfig) return false;
  if (roleConfig.permissions.includes('*')) return true;
  const [category] = permission.split(':');
  return roleConfig.permissions.includes(permission) || roleConfig.permissions.includes(`${category}:*`);
};

export const canAccessMenu = (userRole, menuItem) => {
  const roleConfig = ROLE_PERMISSIONS[userRole];
  return roleConfig?.menu.includes(menuItem) || false;
};
```

---

## ENDPOINTS DO BACKEND DISPONÍVEIS

```
Autenticação:
  POST   /api/auth/login              - Login (retorna {access_token, user})
  GET    /api/auth/me                 - Dados do usuário logado

Contratos:
  GET    /api/contracts               - Lista (filtrado por role/scope)
  POST   /api/contracts               - Criar
  GET    /api/contracts/{id}          - Detalhes
  PUT    /api/contracts/{id}          - Editar
  DELETE /api/contracts/{id}          - Deletar
  
Rent Steps:
  GET    /api/rent-steps              - Lista
  POST   /api/rent-steps              - Criar
  PUT    /api/rent-steps/{id}         - Editar
  DELETE /api/rent-steps/{id}         - Deletar

Import:
  POST   /api/contracts/import        - Upload PDF (retorna dados extraídos)

Alertas:
  GET    /api/alerts                  - Lista (filtrado por role/scope)
  PUT    /api/alerts/{id}/read        - Marcar como lido

Aprovações:
  GET    /api/approvals               - Lista pendentes (filtrado)
  POST   /api/approvals/{id}/approve  - Aprovar
  POST   /api/approvals/{id}/reject   - Rejeitar

Usuários:
  GET    /api/users                   - Lista (filtrado por role)
  POST   /api/users                   - Criar
  PUT    /api/users/{id}              - Editar
  DELETE /api/users/{id}              - Deletar

Health:
  GET    /health                      - Status básico
  GET    /health/db                   - Status do banco
  GET    /health/detailed             - Detalhado (apenas admin)
```

**NOVO endpoint a criar no backend (você vai me ajudar):**
```
Dashboard:
  GET    /api/dashboard/stats         - Estatísticas filtradas por role
```

---

## O QUE PRECISO QUE VOCÊ FAÇA

### SPRINT 1: Setup + Autenticação (COMEÇAR AGORA)

**Objetivo:** Projeto configurado, login funcional, proteção de rotas

**Tarefas:**
1. **Criar projeto Vite + React:**
   ```bash
   npm create vite@latest frontend -- --template react
   cd frontend
   ```

2. **Instalar TODAS as dependências:**
   ```bash
   npm install react-router-dom zustand axios \
     @mui/material @mui/icons-material @mui/x-data-grid \
     @emotion/react @emotion/styled \
     react-hook-form zod @tanstack/react-query \
     date-fns react-dropzone notistack recharts
   ```

3. **Criar estrutura de pastas completa** (conforme definido acima)

4. **Configurar Vite (vite.config.js):**
   - Proxy para backend em `http://localhost:8000`

5. **Criar .env.example:**
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

6. **Implementar arquivos core:**
   - `src/services/api.js` - Axios instance + interceptors (401→logout, 403→toast)
   - `src/services/authApi.js` - login(), logout(), getMe()
   - `src/store/authStore.js` - Zustand (token, user, login, logout, isAllowed, canViewMenu)
   - `src/utils/permissions.js` - ROLE_PERMISSIONS (copiar do prompt)
   - `src/theme/theme.js` - MUI light/dark theme

7. **Criar componentes de autenticação:**
   - `src/components/auth/PrivateRoute.jsx` - Verifica token, redireciona se não logado
   - `src/components/auth/RequirePermission.jsx` - Verifica permissão específica
   - `src/pages/Login.jsx` - Formulário de login (email + senha)
   - `src/pages/Unauthorized.jsx` - Página 403

8. **Criar layout básico:**
   - `src/components/layout/AppLayout.jsx` - Container com Header + Sidebar + Content
   - `src/components/layout/Header.jsx` - AppBar com nome do user, role, botão logout
   - `src/components/layout/Sidebar.jsx` - Drawer com menu items (filtrado por role)

9. **Configurar rotas (App.jsx):**
   ```javascript
   /login                    - Público
   /unauthorized            - Público
   /app/*                   - Privado (PrivateRoute)
     /app/dashboard         - Dashboard
     /app/contracts         - Lista de contratos
     /app/contracts/new     - Criar contrato (RequirePermission)
     /app/import            - Import PDF (RequirePermission)
     /app/alerts            - Alertas
     /app/approvals         - Aprovações (RequirePermission)
     /app/users             - Usuários (RequirePermission)
     /app/system            - Sistema (RequirePermission)
   ```

10. **Testar fluxo completo:**
    - Login com usuário do backend
    - Token salvo no localStorage
    - Header Authorization adicionado automaticamente
    - Redirecionar para dashboard
    - Menu lateral mostra apenas itens permitidos
    - Logout limpa token e redireciona

---

## REGRAS IMPORTANTES

### Segurança
1. ✅ **Backend valida tudo** - Frontend apenas UX
2. ✅ **Interceptor Axios** trata 401 (logout) e 403 (toast)
3. ✅ **Roles exatos do backend** - copiar nomes exatamente
4. ✅ **hasPermission antes de ações** - verificar antes de mostrar botão
5. ✅ **canAccessMenu para sidebar** - filtrar menus por role

### UX
1. ✅ **Loading states** em todas as requisições
2. ✅ **Toast notifications** para sucesso/erro (notistack)
3. ✅ **Validação de formulários** com zod
4. ✅ **Confirmação antes de deletar** (ConfirmDialog)
5. ✅ **Mensagens em PT-BR** (ou bilíngue PT/DE se preferir)

### Boas práticas
1. ✅ **Componentes pequenos e focados**
2. ✅ **Custom hooks** para lógica reutilizável
3. ✅ **ErrorBoundary** para capturar erros React
4. ✅ **Código limpo** e comentado
5. ✅ **Console.log para debug** (estou aprendendo)

---

## EXEMPLO DE CÓDIGO ESPERADO

### authStore.js (Zustand)
```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { hasPermission, canAccessMenu, getAccessLevel } from '../utils/permissions';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null, // { id, email, name, role, access_level, department_id, team_id }
      
      login: (token, user) => {
        set({ token, user });
      },
      
      logout: () => {
        set({ token: null, user: null });
      },
      
      isAllowed: (permission) => {
        const { user } = get();
        if (!user || !user.role) return false;
        return hasPermission(user.role, permission);
      },
      
      canViewMenu: (menuItem) => {
        const { user } = get();
        if (!user || !user.role) return false;
        return canAccessMenu(user.role, menuItem);
      },
      
      getUserLevel: () => {
        const { user } = get();
        return user?.access_level || 0;
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user })
    }
  )
);
```

### api.js (Axios + Interceptors)
```javascript
import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
});

// Request interceptor - adiciona token
api.interceptors.request.use(
  config => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor - trata 401/403
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    // 403 será tratado por toast no componente
    return Promise.reject(error);
  }
);

export default api;
```

### Sidebar.jsx (Menu filtrado por role)
```javascript
import { useAuthStore } from '../../store/authStore';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Chip, Box, Typography } from '@mui/material';
import { Dashboard, Description, Upload, Notifications, People, CheckCircle, Settings } from '@mui/icons-material';
import { Link } from 'react-router-dom';

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Dashboard, path: '/app/dashboard' },
  { id: 'contracts', label: 'Contratos', icon: Description, path: '/app/contracts' },
  { id: 'import', label: 'Importar', icon: Upload, path: '/app/import', permission: 'contracts:import' },
  { id: 'alerts', label: 'Alertas', icon: Notifications, path: '/app/alerts' },
  { id: 'approvals', label: 'Aprovações', icon: CheckCircle, path: '/app/approvals', permission: 'approvals:view' },
  { id: 'users', label: 'Usuários', icon: People, path: '/app/users', permission: 'users:view' },
  { id: 'system', label: 'Sistema', icon: Settings, path: '/app/system', permission: 'system:config' }
];

export const Sidebar = ({ open }) => {
  const { user, canViewMenu, isAllowed } = useAuthStore();
  
  return (
    <Drawer variant="permanent" open={open}>
      {/* User info */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle1">{user?.name}</Typography>
        <Chip label={user?.role} size="small" color="primary" />
        <Typography variant="caption" display="block">
          Level: {user?.access_level}
        </Typography>
      </Box>
      
      {/* Menu */}
      <List>
        {menuItems.map(item => {
          // Verifica se pode ver no menu E tem permissão específica
          if (!canViewMenu(item.id)) return null;
          if (item.permission && !isAllowed(item.permission)) return null;
          
          return (
            <ListItem key={item.id} button component={Link} to={item.path}>
              <ListItemIcon><item.icon /></ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          );
        })}
      </List>
    </Drawer>
  );
};
```

---

## INFORMAÇÕES DO BACKEND

**Backend rodando em:** `http://localhost:8000`  
**Documentação API:** `http://localhost:8000/docs`

**Usuário de teste (você pode criar outros):**
```
Email: admin@test.com
Password: admin123
Role: SYSTEM_ADMIN
```

---

## PRÓXIMOS PASSOS (APÓS SPRINT 1)

- Sprint 2: Dashboard com widgets por role
- Sprint 3: Lista de contratos + filtros
- Sprint 4: CRUD de contratos
- Sprint 5: Upload/Import de PDFs
- Sprint 6: Alertas + Aprovações

---

## INSTRUÇÕES FINAIS

1. **Crie TODO o boilerplate da Sprint 1** (setup + auth + layout básico)
2. **Implemente EXATAMENTE como especificado** (mesmos nomes de roles, mesma estrutura)
3. **Teste cada feature** antes de seguir para próxima
4. **Me explique o que está fazendo** (estou aprendendo)
5. **Use console.log** liberalmente para debug
6. **Commits frequentes** (a cada feature pequena)

**IMPORTANTE:**
- ✅ Foque em fazer funcionar PRIMEIRO, otimizar DEPOIS
- ✅ Código limpo e comentado
- ✅ Mensagens de erro claras
- ✅ Comece simples, adicione complexidade gradualmente

---

**PODE COMEÇAR A IMPLEMENTAÇÃO DA SPRINT 1 AGORA!**

