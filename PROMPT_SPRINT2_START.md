# 🚀 PROMPT PARA CONTINUAR - SPRINT 2 (Dashboard)

**COLE ESTE PROMPT NO PRÓXIMO CHAT PARA CONTINUAR A IMPLEMENTAÇÃO:**

---

## ✅ O QUE JÁ ESTÁ PRONTO (SPRINT 1 COMPLETA)

### Backend
- **FastAPI** rodando em `http://localhost:8000`
- **SQLite** database: `backend/contracts.db`
- **Autenticação JWT** funcionando perfeitamente
- **7 roles** + **6 access levels** implementados
- **CORS** configurado para desenvolvimento (`allow_origins=["*"]`)
- **Prefixo /api** em todas as rotas
- **Admin user criado:** `admin@test.com` / `admin123`

### Frontend
- **React 18.3.1 + Vite 5.4.10** configurado
- **Estrutura completa de pastas** criada
- **Login funcional** com validação Zod + react-hook-form
- **Proteção de rotas** (PrivateRoute, RequirePermission)
- **Layout completo** (AppLayout, Sidebar, Header)
- **Zustand store** com persist (authStore)
- **Axios interceptors** (401→logout, JWT auto-inject)
- **MUI customizado** com cores Christburg
- **Menu lateral** filtrado por role (240px fixo)

### Git
- ✅ 3 commits realizados e push para GitHub:
  - `feat(frontend): implement authentication system`
  - `fix(backend): improve authentication and API routes`
  - `feat(scripts): add database initialization and admin utilities`

---

## 📁 ESTRUTURA DE ARQUIVOS CRIADOS

### Frontend Completo
```
frontend/src/
├── components/
│   ├── auth/
│   │   ├── PrivateRoute.jsx          ✅ PRONTO (Sprint 1)
│   │   └── RequirePermission.jsx     ✅ PRONTO (Sprint 1)
│   ├── layout/
│   │   ├── AppLayout.jsx             ✅ PRONTO (Sprint 1) - Layout principal
│   │   ├── Header.jsx                ✅ PRONTO (Sprint 1) - AppBar + user menu + logout
│   │   └── Sidebar.jsx               ✅ PRONTO (Sprint 1) - Menu 240px + filtro por role
│   └── dashboard/                    ⏳ SPRINT 2 - CRIAR AGORA
│       ├── DashboardStaff.jsx        ⏳ MAIS SIMPLES - Começar aqui
│       ├── DashboardTeamLead.jsx     ⏳
│       ├── DashboardDepartmentUser.jsx ⏳
│       ├── DashboardDepartmentAdm.jsx  ⏳
│       ├── DashboardDirector.jsx     ⏳
│       └── DashboardSystemAdmin.jsx  ⏳ MAIS COMPLEXO - Fazer por último
├── pages/
│   ├── Login.jsx                     ✅ PRONTO (Sprint 1)
│   ├── Unauthorized.jsx              ✅ PRONTO (Sprint 1)
│   └── Dashboard.jsx                 ⏳ SPRINT 2 - Renderiza dashboard por role
├── services/
│   ├── api.js                        ✅ PRONTO (Sprint 1)
│   ├── authApi.js                    ✅ PRONTO (Sprint 1)
│   └── dashboardApi.js               ⏳ SPRINT 2 - getStats()
├── store/
│   ├── authStore.js                  ✅ PRONTO (Sprint 1)
│   └── uiStore.js                    ⏳ OPCIONAL - Tema, sidebar toggle
├── utils/
│   └── permissions.js                ✅ PRONTO (Sprint 1)
├── theme/
│   └── theme.js                      ✅ PRONTO (Sprint 1)
├── App.jsx                           ✅ PRONTO (Sprint 1)
└── main.jsx                          ✅ PRONTO (Vite default)
```

### Backend Modificado
```
backend/
├── main.py                           ✅ Prefixo /api + CORS
├── app/routers/
│   ├── auth.py                       ✅ Login retorna user object
│   └── dashboard.py                  ⏳ CRIAR NA SPRINT 2
├── app/schemas/
│   ├── token.py                      ✅ User object adicionado
│   └── dashboard.py                  ⏳ CRIAR NA SPRINT 2
├── app/services/
│   ├── user_service.py               ✅ Email/username login
│   └── dashboard_service.py          ⏳ CRIAR NA SPRINT 2
```

### Scripts Utilitários
```
create_admin.py                       ✅ Cria admin@test.com
check_db.py                           ✅ Verifica tabelas
add_missing_tables.py                 ✅ Adiciona tabelas faltantes
init_db.py                            ✅ Inicializa DB completo
```

---

## 🎯 SPRINT 2: DASHBOARD POR ROLE

### Objetivo
Criar **6 dashboards diferentes**, um para cada role, com widgets específicos e estatísticas filtradas pelo backend.

### ⚠️ IMPORTANTE: Layout Já Está Pronto!
**Sprint 1 foi ALÉM do planejado** e já incluiu:
- ✅ Sidebar completa com navegação e filtro por role
- ✅ Header com user info e logout
- ✅ AppLayout funcionando perfeitamente
- ✅ Menu items já usando `canAccessMenu()`

**Isso significa que a Sprint 2 é mais curta (2-3 dias):**
- Focar apenas em: Dashboard widgets + Backend stats endpoint + uiStore (opcional)
- Pular tarefas 1, 2, 3 do plano original (já feitas!)

### O QUE VOCÊ VAI FAZER

#### 1. Backend: Endpoint de Estatísticas

**Criar arquivo:** `backend/app/schemas/dashboard.py`
```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DashboardStats(BaseModel):
    # Contratos
    total_contracts: int
    active_contracts: int
    expiring_30_days: int
    expiring_90_days: int
    monthly_value: float
    
    # Alertas e Aprovações
    total_alerts: int
    unread_alerts: int
    pending_approvals: int
    
    # Admin/Director extras
    total_users: Optional[int] = None
    contracts_by_department: Optional[Dict[str, int]] = None
    contracts_by_status: Optional[Dict[str, int]] = None
    
    # System Admin extras
    last_backup: Optional[str] = None
    disk_usage: Optional[float] = None
    active_sessions: Optional[int] = None
    uptime_days: Optional[int] = None
    
    # Department/Team specific
    department_name: Optional[str] = None
    team_name: Optional[str] = None
    team_contracts: Optional[int] = None
```

**Criar arquivo:** `backend/app/services/dashboard_service.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.schemas.dashboard import DashboardStats
from datetime import datetime, timedelta
# Implementar lógica de filtro por role/access_level
```

**Criar arquivo:** `backend/app/routers/dashboard.py`
```python
from fastapi import APIRouter, Depends
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_stats_by_role(current_user)
```

**Modificar:** `backend/main.py`
```python
from app.routers import dashboard

app.include_router(dashboard.router, prefix="/api")
```

#### 2. Frontend: Dashboard Components

**Criar arquivo:** `frontend/src/services/dashboardApi.js`
```javascript
import api from './api';

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  }
};
```

**Criar arquivo:** `frontend/src/pages/Dashboard.jsx`
```javascript
import { useAuthStore } from '../store/authStore';
import DashboardSystemAdmin from '../components/dashboard/DashboardSystemAdmin';
import DashboardDirector from '../components/dashboard/DashboardDirector';
import DashboardDepartmentAdm from '../components/dashboard/DashboardDepartmentAdm';
import DashboardDepartmentUser from '../components/dashboard/DashboardDepartmentUser';
import DashboardTeamLead from '../components/dashboard/DashboardTeamLead';
import DashboardStaff from '../components/dashboard/DashboardStaff';

const DASHBOARD_COMPONENTS = {
  SYSTEM_ADMIN: DashboardSystemAdmin,
  DIRECTOR: DashboardDirector,
  DEPARTMENT_ADM: DashboardDepartmentAdm,
  DEPARTMENT_USER: DashboardDepartmentUser,
  TEAM_LEAD: DashboardTeamLead,
  STAFF: DashboardStaff,
  READ_ONLY: DashboardStaff  // Mesmo que STAFF
};

export default function Dashboard() {
  const { user } = useAuthStore();
  const DashboardComponent = DASHBOARD_COMPONENTS[user?.role] || DashboardStaff;
  
  return <DashboardComponent />;
}
```

#### 3. Widgets por Role

**SYSTEM_ADMIN** (`DashboardSystemAdmin.jsx`):
- Grid 4 colunas com Cards:
  - Total contratos, Total usuários, Alertas, Aprovações pendentes
- Grid 2 colunas:
  - Último backup, Uso de disco, Sessões ativas, Uptime
- Gráficos (Recharts):
  - Contratos criados (últimos 30 dias) - LineChart
  - Top 5 usuários mais ativos - BarChart
  - Status de contratos - PieChart

**DIRECTOR** (`DashboardDirector.jsx`):
- Grid 4 colunas:
  - Contratos ativos (empresa), Expirando 30d, Expirando 90d, Valor mensal total
- Gráficos:
  - Contratos por departamento - BarChart
  - Valor por tipo de contrato - PieChart
  - Timeline de vencimentos (próximos 6 meses) - LineChart

**DEPARTMENT_ADM** (`DashboardDepartmentAdm.jsx`):
- Título: Nome do departamento
- Grid 3 colunas:
  - Contratos ativos dept, Alertas, Aprovações pendentes
  - Expirando 30d, Valor mensal, Usuários do dept
- Gráficos:
  - Contratos por time - BarChart
  - Status de aprovações - PieChart

**DEPARTMENT_USER** (`DashboardDepartmentUser.jsx`):
- Título: Nome do departamento
- Grid 3 colunas:
  - Contratos ativos (view only), Expirando 30d, Alertas
- Gráfico simples:
  - Status de contratos - PieChart

**TEAM_LEAD** (`DashboardTeamLead.jsx`):
- Título: Nome do time
- Grid 4 colunas:
  - Contratos ativos time, Expirando 30d, Alertas, Valor mensal
- Gráfico:
  - Status de contratos do time - PieChart

**STAFF / READ_ONLY** (`DashboardStaff.jsx`):
- Grid 3 colunas (cards apenas):
  - Meus contratos ativos
  - Meus contratos expirando
  - Meus alertas
- Tabela simples de últimos contratos (sem gráficos)

---

## 📐 DESIGN SYSTEM ESTABELECIDO

### Cores (MUI Theme)
```javascript
primary: '#2563EB'      // Azul Christburg
secondary: '#6B7280'    // Cinza
success: '#10B981'      // Verde
error: '#EF4444'        // Vermelho
warning: '#F59E0B'      // Amarelo
info: '#3B82F6'         // Azul info
```

### Typography
```javascript
fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif'
h4: { fontWeight: 600, fontSize: '1.75rem' }
h5: { fontWeight: 600, fontSize: '1.5rem' }
h6: { fontWeight: 600, fontSize: '1.25rem' }
```

### Layout
- **Sidebar:** 240px fixo à esquerda
- **Header:** 64px altura
- **Content area:** calc(100vh - 64px) com padding 24px
- **Cards:** elevation={3}, sx={{ p: 3 }}
- **Grid spacing:** spacing={3}

### Componentes MUI a usar
```javascript
import {
  Grid, Card, CardContent, Typography, Box,
  Paper, Divider, Chip, Avatar
} from '@mui/material';

import {
  BarChart, Bar, LineChart, Line, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';
```

---

## 🔑 REGRAS DE SEGURANÇA E PERMISSÕES

### Sistema de Roles (7 roles)
```javascript
UserRole.SYSTEM_ADMIN    // Level 6 - Admin completo
UserRole.DIRECTOR        // Level 5 - Toda empresa
UserRole.DEPARTMENT_ADM  // Level 4 - Departamento
UserRole.DEPARTMENT_USER // Level 3 - Dept (restrito)
UserRole.TEAM_LEAD       // Level 2 - Time
UserRole.STAFF           // Level 1-2 - Próprios
UserRole.READ_ONLY       // Level 1 - Somente leitura
```

### Matriz de Permissões (`src/utils/permissions.js`)
**JÁ IMPLEMENTADO** - copiar do arquivo existente se necessário.

### Funções Utilitárias
```javascript
hasPermission(userRole, permission)     // Verifica permissão
canAccessMenu(userRole, menuItem)       // Verifica menu
getAccessLevel(userRole)                // Retorna level numérico
```

### Menu Items (Sidebar)
```javascript
SYSTEM_ADMIN:    dashboard, contracts, import, alerts, users, approvals, system
DIRECTOR:        dashboard, contracts, import, alerts, users, approvals, reports
DEPARTMENT_ADM:  dashboard, contracts, import, alerts, users, approvals, reports
DEPARTMENT_USER: dashboard, contracts, alerts, reports
TEAM_LEAD:       dashboard, contracts, import, alerts, reports
STAFF:           dashboard, contracts, alerts
READ_ONLY:       dashboard, contracts, alerts
```

---

## 🛠️ COMANDOS ÚTEIS

### Iniciar Backend
```bash
cd /home/sschulze/projects/vertrag-mgs/backend
source ../.venv/bin/activate  # ou: ../.venv/bin/python
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Iniciar Frontend
```bash
cd /home/sschulze/projects/vertrag-mgs/frontend
npm run dev
# Abre em http://localhost:5173
```

### Criar Admin (se necessário)
```bash
cd /home/sschulze/projects/vertrag-mgs
../.venv/bin/python create_admin.py
```

### Verificar DB
```bash
../.venv/bin/python check_db.py
```

### Git
```bash
git status --short
git add .
git commit -m "feat(dashboard): implement role-based dashboard widgets"
git push origin main
```

---

## 🔐 CREDENCIAIS DE TESTE

```
Email: admin@test.com
Senha: admin123
Role: SYSTEM_ADMIN
Access Level: 6
```

---

## 📋 ENDPOINTS BACKEND DISPONÍVEIS

### Autenticação
```
POST /api/auth/login              - Login (form-urlencoded)
GET  /api/auth/me                 - User info
```

### Contratos (filtrados por role/scope)
```
GET    /api/contracts             - Lista
POST   /api/contracts             - Criar
GET    /api/contracts/{id}        - Detalhes
PUT    /api/contracts/{id}        - Editar
DELETE /api/contracts/{id}        - Deletar
```

### Rent Steps
```
GET    /api/rent-steps            - Lista
POST   /api/rent-steps            - Criar
PUT    /api/rent-steps/{id}       - Editar
DELETE /api/rent-steps/{id}       - Deletar
```

### Import PDF
```
POST /api/contracts/import        - Upload PDF + extração
```

### Alertas
```
GET /api/alerts                   - Lista (filtrado)
PUT /api/alerts/{id}/read         - Marcar lido
```

### Aprovações
```
GET  /api/approvals               - Pendentes (filtrado)
POST /api/approvals/{id}/approve  - Aprovar
POST /api/approvals/{id}/reject   - Rejeitar
```

### Usuários
```
GET    /api/users                 - Lista (filtrado)
POST   /api/users                 - Criar
PUT    /api/users/{id}            - Editar
DELETE /api/users/{id}            - Deletar
```

### Dashboard (⏳ A CRIAR)
```
GET /api/dashboard/stats          - Estatísticas por role
```

---

## 🎨 EXEMPLO DE WIDGET CARD

```javascript
import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary' }) {
  return (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
          <Icon sx={{ color: `${color}.main`, fontSize: 32 }} />
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
    ⚡ ORDEM RECOMENDADA DE EXECUÇÃO

**FASE 1: Backend primeiro (1 dia)**
1. ⏳ Criar `backend/app/schemas/dashboard.py` - DashboardStats model
2. ⏳ Criar `backend/app/services/dashboard_service.py` - Lógica de filtro por role
3. ⏳ Criar `backend/app/routers/dashboard.py` - GET /api/dashboard/stats
4. ⏳ Modificar `backend/main.py` - Incluir dashboard router
5. ✅ Testar endpoint com curl: `curl http://localhost:8000/api/dashboard/stats -H "Authorization: Bearer <token>"`

**FASE 2: Frontend básico (0.5 dia)**
1. ⏳ Criar `frontend/src/services/dashboardApi.js` - getStats()
2. ⏳ Criar `frontend/src/pages/Dashboard.jsx` - Switch por role
3. ⏳ (OPCIONAL) Criar `frontend/src/store/uiStore.js` - Tema, sidebar state

**FASE 3: Dashboards por role (1-1.5 dias)**
1. ⏳ Criar `frontend/src/components/dashboard/DashboardStaff.jsx` - **COMEÇAR AQUI** (mais simples)
2. ⏳ Criar `frontend/src/components/dashboard/DashboardTeamLead.jsx`
3. ⏳ Criar `frontend/src/components/dashboard/DashboardDepartmentUser.jsx`
4. ⏳ Criar `frontend/src/components/dashboard/DashboardDepartmentAdm.jsx`
5. ⏳ Criar `frontend/src/components/dashboard/DashboardDirector.jsx`
6. ⏳ Criar `frontend/src/components/dashboard/DashboardSystemAdmin.jsx` - **MAIS COMPLEXO** (fazer por último)

**FASE 4: Testes e ajustes (0.5 dia)**
1. ✅ Login com admin@test.com - Dashboard SYSTEM_ADMIN renderiza
2. ⏳ Criar usuários de teste para outros roles (DIRECTOR, DEPARTMENT_ADM, STAFF)
3. ⏳ Testar cada dashboard individualmente
4. ⏳ Verificar se widgets mostram dados corretos
5. ⏳ Testar gráficos (Recharts) renderizam sem erros
6. ⏳ Verificar responsividade em mobile

### 📋 CHECKLIST DETALHADO

**Backend:**
- [ ] DashboardStats schema com todos os campos
- [ ] DashboardService filtra por role (SYSTEM_ADMIN vê tudo, STAFF vê só próprios)
- [ ] Endpoint /api/dashboard/stats protegido com get_current_user
- [ ] Router incluído em main.py
- [ ] Testado com curl/Postman

**Frontend:**
- [ ] dashboardApi.js com função getStats()
- [ ] Dashboard.jsx renderiza componente correto por user.role
- [ ] 6 componentes de dashboard criados
- [ ] Cada dashboard usa dados do backend (não mock)
- [ ] Cards MUI com elevation e padding
- [ ] Gráficos Recharts (BarChart, PieChart, LineChart)
- [ ] Loading state enquanto carrega stats
- [ ] Error handling se API falhar

**Testes:**
- [ ] SYSTEM_ADMIN: vê todos dados + gráficos técnicos
- [ ] DIRECTOR: vê dados empresa + gráficos executivos
- [ ] DEPARTMENT_ADM: vê apenas seu departamento
- [ ] DEPARTMENT_USER: vê departamento sem valores financeiros
- [ ] TEAM_LEAD: vê apenas seu time
- [ ] STAFF: vê apenas próprios contratos (sem gráficos)shboard/DashboardDirector.jsx`
5. ✅ Criar `frontend/src/components/dashboard/DashboardDepartmentAdm.jsx`
6. ✅ Criar `frontend/src/components/dashboard/DashboardDepartmentUser.jsx`
7. ✅ Criar `frontend/src/components/dashboard/DashboardTeamLead.jsx`
8. ✅ Criar `frontend/src/components/dashboard/DashboardStaff.jsx`

### Testes
1. ✅ Login com admin@test.com
2. ✅ Dashboard SYSTEM_ADMIN renderiza
3. ✅ Widgets mostram dados corretos
4. ✅ Gráficos renderizam sem erros
5. ✅ Responsivo em diferentes tamanhos

---

## 🚨 REGRAS IMPORTANTES

### Segurança
1. ✅ **Backend decide tudo** - Frontend apenas UX
2. ✅ SEMPRE começar pelo backend** - Criar endpoint /api/dashboard/stats primeiro
2. **Testar endpoint com curl** antes de tocar no frontend:
   ```bash
   curl http://localhost:8000/api/dashboard/stats \
     -H "Authorization: Bearer <token_do_admin>"
   ```
3. **Dashboard mais SIMPLES primeiro** - DashboardStaff (só 3 cards, sem gráficos)
4. **Copiar e adaptar** - DashboardStaff serve de template para outros
5. **NÃO usar dados mock** - Backend já tem contracts, users, alerts
6. **Commit incremental** - Separar backend, frontend básico, e dashboards
7. **Criar usuários de teste** para cada role usando create_admin.py como base
8. **Gráficos por último** - Primeiro fazer cards funcionarem, depois Recharts
2. ✅ **Error boundary** para capturar erros
3. ✅ **Toast de erro** se API falhar
4. ✅ **Refresh automático** a cada 30s (opcional)
5. ✅ **Números formatados** (1.234,56 para valores)

### Código
1. ✅ **Componentes pequenos** (max 200 linhas)
2. ✅ **Custom hook useStats()** para lógica de fetch
3. ✅ **Comentários em GE-ALEMAO e PT-BR** (bilíngue)
4. ✅ **Console.log para debug** (remover antes de commit)
5. ✅ **Commits de github em inglês** para GitHub

---

## 📚 PRÓXIMAS SPRINTS (ROADMAP)

- **Sprint 3:** Contratos CRUD (lista, criar, editar, deletar)
- **Sprint 4:** Upload e Import de PDF
- **Sprint 5:** Alertas e Notificações
- **Sprint 6:** Sistema de Aprovações
- **Sprint 7:** Gestão de Usuários (apenas admin/director)
- **Sprint 8:** Relatórios e Exports
- **Sprint 9:** Sistema de Configurações (apenas SYSTEM_ADMIN)
- **Sprint 10:** Testes e Deploy

---

## 💡 DICAS PARA O PRÓXIMO CHAT

1. **Começar pelo backend** - Criar endpoint /api/dashboard/stats primeiro
2. **Testar com curl/Postman** antes do frontend
3. **Criar um widget simples primeiro** (DashboardStaff)
4. **Copiar e adaptar** para outros roles
5. **Usar dados mock** se backend não estiver pronto
6. **Commit incremental** - Um commit por componente grande

---

## 📞 CONTEXTO ADICIONAL

- **Usuário:** sschulze (Linux)
- **Workspace:** `/home/sschulze/projects/vertrag-mgs`
- **Python env:** `.venv` na raiz do projeto
- **Node version:** 18.20.8
- **Python version:** 3.12.3
- **Database:** SQLite em `backend/contracts.db`
- **Frontend dev server:** http://localhost:5173
- **Backend dev server:** http://localhost:8000
- **Modo:** Development (CORS permissivo)

---

**BOA SORTE NA SPRINT 2! 🚀**

Cole este prompt completo no início do próximo chat e diga: "Vamos começar a Sprint 2 do Dashboard".
