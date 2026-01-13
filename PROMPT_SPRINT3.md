# 🚀 PROMPT - Sprint 3: CRUD Completo de Contratos

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

## ✅ SPRINTS ANTERIORES COMPLETAS

### Sprint 1: Setup e Autenticação ✅
- Backend FastAPI configurado e rodando em http://localhost:8000
- Frontend React+Vite configurado e rodando em http://localhost:5173
- Sistema de autenticação JWT funcional
- Login page com centralização
- Rotas protegidas por role
- authStore (Zustand) implementado

### Sprint 2: Dashboard com Widgets por Role ✅
- Backend: schemas/dashboard.py, services/dashboard_service.py, routers/dashboard.py
- Frontend: 6 componentes de dashboard (um para cada role/level):
  - DashboardSystemAdmin.jsx (Level 6 - apenas dados técnicos)
  - DashboardDirector.jsx (Level 5 - visão completa empresa)
  - DashboardDepartmentAdm.jsx (Level 4 - departamento com valores)
  - DashboardDepartmentUser.jsx (Level 3 - departamento sem valores)
  - DashboardTeamLead.jsx (Level 2 - contratos do time)
  - DashboardStaff.jsx (Level 1 - apenas próprios contratos)
- Correções críticas em permissions.py (Level 6 = técnico apenas, SEM contratos)
- Todos dashboards traduzidos para inglês
- API GET /api/dashboard/stats funcionando
- Testado com admin@test.com (Level 6) e director@test.com (Level 5)

## 🎯 SPRINT 3: CRUD COMPLETO DE CONTRATOS

### Objetivo
Implementar interface completa para gestão de contratos com:
- Listagem com DataGrid (paginação, sorting, filtros)
- Criação de novos contratos
- Edição de contratos existentes
- Visualização detalhada
- Delete com confirmação
- Gestão de Rent Steps (passos de aluguel)
- **TUDO respeitando permissões por role/level**

### Backend Já Existente
```
✅ backend/app/models/contract.py - Modelo Contract completo
✅ backend/app/models/rent_step.py - Modelo RentStep
✅ backend/app/routers/contracts.py - Endpoints CRUD:
   - GET /api/contracts (list com filtros)
   - POST /api/contracts (create)
   - GET /api/contracts/{id} (get one)
   - PUT /api/contracts/{id} (update)
   - DELETE /api/contracts/{id} (delete)
✅ backend/app/routers/rent_steps.py - CRUD de rent steps
✅ backend/app/core/permissions.py - Funções de autorização:
   - can_view_contract(user, contract)
   - can_edit_contract(user, contract)
   - can_delete_contract(user, contract)
   - can_access_reports(user)
```

### Frontend Estrutura Atual
```
frontend/src/
├── components/
│   ├── auth/ (✅ completo)
│   ├── dashboard/ (✅ 6 dashboards completos)
│   ├── layout/ (✅ AppLayout, Sidebar, Header)
│   ├── contracts/ (❌ CRIAR AGORA)
│   ├── ui/ (⏳ criar conforme necessário)
│   └── upload/ (⏳ Sprint 5)
├── pages/
│   ├── Dashboard.jsx (✅)
│   ├── Login.jsx (✅)
│   ├── contracts/ (❌ CRIAR AGORA)
│   └── ...
├── services/
│   ├── api.js (✅)
│   ├── authApi.js (✅)
│   ├── dashboardApi.js (✅)
│   └── contractsApi.js (❌ CRIAR AGORA)
├── store/
│   ├── authStore.js (✅)
│   └── uiStore.js (⏳ criar se necessário)
└── utils/
    ├── permissions.js (⏳ criar se necessário)
    └── constants.js (⏳ criar se necessário)
```

## 📝 CHECKLIST SPRINT 3

### 1. Services/API (Backend Integration)
- [ ] Criar `frontend/src/services/contractsApi.js` com:
  - `getContracts(filters, page, pageSize, sortBy)` - GET /api/contracts
  - `getContract(id)` - GET /api/contracts/{id}
  - `createContract(data)` - POST /api/contracts
  - `updateContract(id, data)` - PUT /api/contracts/{id}
  - `deleteContract(id)` - DELETE /api/contracts/{id}

### 2. Utils/Constants
- [ ] Criar `frontend/src/utils/constants.js` com:
  - CONTRACT_STATUS: ['ACTIVE', 'INACTIVE', 'EXPIRING', 'EXPIRED']
  - CONTRACT_TYPES: ['MIETE', 'PACHT', 'LIZENZ', 'SERVICE']
  - DEFAULT_PAGE_SIZE: 25
  - PAGE_SIZE_OPTIONS: [10, 25, 50, 100]

- [ ] Criar `frontend/src/utils/permissions.js` com:
  - `hasPermission(user, permission)` - verifica se user pode executar ação
  - `canViewContract(user, contract)` - wrapper do backend
  - `canEditContract(user, contract)` - wrapper do backend
  - `canDeleteContract(user, contract)` - wrapper do backend

### 3. Componentes de Contratos
- [ ] `frontend/src/components/contracts/ContractTable.jsx`
  - DataGrid do MUI (@mui/x-data-grid)
  - Colunas: ID, Title, Partner, Type, Status, Start Date, End Date, Monthly Value, Actions
  - Paginação server-side
  - Sorting server-side
  - Filtros: Status (All/Active/Expiring), Type, Search
  - Actions (Edit/View/Delete) conforme permissões
  - Loading state
  - Empty state

- [ ] `frontend/src/components/contracts/ContractForm.jsx`
  - React Hook Form + Zod validation
  - Campos: title, partner_name, contract_type, status, start_date, end_date, monthly_value, description, department_id, team_id, responsible_user_id
  - Autocomplete para departments/teams/users
  - Date pickers (date-fns)
  - Currency input (monthly_value)
  - Submit/Cancel buttons
  - Error handling

- [ ] `frontend/src/components/contracts/ContractDetail.jsx`
  - Card com todas informações do contrato
  - Rent Steps table (se existirem)
  - Botões: Edit, Delete, Back (conforme permissões)
  - Info adicional: created_at, updated_at, created_by

- [ ] `frontend/src/components/contracts/ContractFilters.jsx`
  - Select Status (All, Active, Expiring, Inactive, Expired)
  - Select Type (All, Miete, Pacht, Lizenz, Service)
  - TextField Search (title, partner)
  - Button Clear Filters
  - Date range filters (opcional)

- [ ] `frontend/src/components/ui/ConfirmDialog.jsx`
  - Dialog genérico de confirmação
  - Props: open, title, message, onConfirm, onCancel
  - Usado para delete de contratos

### 4. Páginas
- [ ] `frontend/src/pages/contracts/ContractsList.jsx`
  - Header com título "Contracts" + botão "New Contract" (se permitido)
  - ContractFilters
  - ContractTable
  - useEffect para carregar contratos
  - Estado: contracts, loading, error, filters, page, pageSize, totalRows

- [ ] `frontend/src/pages/contracts/ContractCreate.jsx`
  - Header "New Contract"
  - ContractForm em modo create
  - onSubmit → contractsApi.createContract()
  - Redirect para /contracts após sucesso
  - Toast de sucesso/erro (notistack)

- [ ] `frontend/src/pages/contracts/ContractEdit.jsx`
  - useParams() para pegar ID
  - Carregar contrato existente
  - ContractForm em modo edit (preenchido)
  - onSubmit → contractsApi.updateContract()
  - Redirect para /contracts após sucesso

- [ ] `frontend/src/pages/contracts/ContractView.jsx`
  - useParams() para pegar ID
  - ContractDetail component
  - Breadcrumb: Contracts > {contract.title}

### 5. Routing
- [ ] Atualizar `frontend/src/App.jsx` com rotas:
  ```jsx
  <Route path="/contracts" element={<ContractsList />} />
  <Route path="/contracts/new" element={<ContractCreate />} />
  <Route path="/contracts/:id" element={<ContractView />} />
  <Route path="/contracts/:id/edit" element={<ContractEdit />} />
  ```

### 6. Sidebar Menu
- [ ] Atualizar `frontend/src/components/layout/Sidebar.jsx`:
  - Adicionar item "Contracts" no menu (ícone: DescriptionIcon)
  - Mostrar apenas para roles que podem ver contratos (Levels 1-5, NÃO 6)

## 🎨 REFERÊNCIAS DE DESIGN

### ContractTable (DataGrid)
```jsx
<DataGrid
  rows={contracts}
  columns={columns}
  pageSize={pageSize}
  rowCount={totalRows}
  paginationMode="server"
  sortingMode="server"
  onPageChange={handlePageChange}
  onPageSizeChange={handlePageSizeChange}
  onSortModelChange={handleSortChange}
  loading={loading}
  disableSelectionOnClick
  autoHeight
/>
```

### Colunas Exemplo
```jsx
const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'title', headerName: 'Title', flex: 1, minWidth: 200 },
  { field: 'partner_name', headerName: 'Partner', flex: 1, minWidth: 150 },
  { field: 'contract_type', headerName: 'Type', width: 120 },
  { field: 'status', headerName: 'Status', width: 120, renderCell: (params) => <Chip label={params.value} color={statusColor(params.value)} /> },
  { field: 'monthly_value', headerName: 'Monthly Value', width: 150, valueFormatter: (params) => formatCurrency(params.value) },
  { field: 'actions', headerName: 'Actions', width: 150, renderCell: (params) => <ActionsMenu contract={params.row} /> }
];
```

## 🔐 REGRAS DE PERMISSÕES

### Visualização (can_view_contract)
- Level 6 (SYSTEM_ADMIN): Apenas contratos do time (technical only)
- Level 5 (DIRECTOR): Todos contratos
- Level 4 (DEPARTMENT_ADM): Contratos do departamento
- Level 3 (DEPARTMENT_USER): Contratos do departamento
- Level 2 (TEAM_LEAD): Contratos do time
- Level 1 (STAFF/READ_ONLY): Apenas onde é responsável ou criou

### Edição (can_edit_contract)
- Level 6: Apenas contratos do time
- Level 5: Todos contratos
- Level 4: Contratos do departamento
- Level 3: Contratos do departamento
- Level 2: Contratos do time
- Level 1 STAFF: Onde é responsável
- Level 1 READ_ONLY: NENHUM

### Exclusão (can_delete_contract)
- Level 6: NÃO pode deletar
- Level 5: Todos contratos
- Level 4: Contratos do departamento
- Level 3: NÃO pode deletar
- Level 2: NÃO pode deletar
- Level 1: NÃO pode deletar

### Valores Financeiros (can_access_reports)
- Level 6: NÃO vê valores
- Level 5: Vê tudo
- Level 4: Vê valores
- Level 3: NÃO vê valores (hidden)
- Level 2: NÃO vê valores
- Level 1: NÃO vê valores

## ⚙️ CONFIGURAÇÕES TÉCNICAS

### Dependências a Instalar
```bash
cd frontend
npm install @mui/x-data-grid react-hook-form zod @hookform/resolvers date-fns notistack
```

### Variáveis de Ambiente (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)
1. contractsApi.js (API calls)
2. ContractsList page (listagem básica)
3. ContractTable (DataGrid simples)
4. ContractFilters (filtros básicos)
5. Routing em App.jsx

### Prioridade MÉDIA (depois)
6. ContractForm (create/edit)
7. ContractCreate page
8. ContractEdit page
9. ConfirmDialog (delete)
10. Permissions utils

### Prioridade BAIXA (polimento)
11. ContractView page (detalhes)
12. ContractDetail component
13. Rent Steps integration
14. Advanced filters (date range)

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 3 estará completa quando:
- [ ] Listagem de contratos funcional com paginação e sorting
- [ ] Filtros de Status e Type funcionando
- [ ] Criar novo contrato (formulário completo)
- [ ] Editar contrato existente
- [ ] Deletar contrato com confirmação
- [ ] Permissões respeitadas (frontend esconde/mostra conforme role)
- [ ] Backend valida permissões (403 se sem acesso)
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Toast notifications (sucesso/erro)
- [ ] Menu "Contracts" no Sidebar (apenas para Levels 1-5)

## 🚀 COMO COMEÇAR

1. **Instalar dependências:**
   ```bash
   cd /home/sschulze/projects/vertrag-mgs/frontend
   npm install @mui/x-data-grid react-hook-form zod @hookform/resolvers date-fns notistack
   ```

2. **Criar contractsApi.js primeiro:**
   - Implementar 5 funções básicas (CRUD)
   - Usar axios instance de api.js
   - Error handling com try/catch

3. **Criar constants.js:**
   - STATUS, TYPES, etc
   - Será usado em filtros e forms

4. **Implementar ContractsList + ContractTable:**
   - Começar com listagem simples
   - Adicionar paginação
   - Adicionar sorting
   - Adicionar filtros

5. **Implementar Create/Edit:**
   - ContractForm reutilizável
   - Validação com Zod
   - Toast notifications

6. **Testar com diferentes roles:**
   - admin@test.com (Level 6) - não deve ver menu Contracts
   - director@test.com (Level 5) - deve ver tudo

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend permissions: `backend/app/core/permissions.py`
- Backend models: `backend/app/models/contract.py`
- Backend routers: `backend/app/routers/contracts.py`
- Frontend auth: `frontend/src/store/authStore.js`
- Frontend dashboard: `frontend/src/pages/Dashboard.jsx` (exemplo de estrutura)
- Frontend API: `frontend/src/services/dashboardApi.js` (exemplo de API calls)

## 🎯 META

Ao final da Sprint 3, o usuário deverá conseguir:
- Fazer login como director@test.com
- Ver menu "Contracts" no sidebar
- Clicar e ver lista de contratos (se existirem no DB)
- Filtrar por status/tipo
- Clicar em "New Contract" e criar um novo
- Editar contrato existente
- Deletar contrato (com confirmação)
- Ver que Level 6 (admin@test.com) NÃO vê menu Contracts

---

**Pronto para começar! Vamos implementar a Sprint 3 passo a passo, seguindo as prioridades definidas.**
