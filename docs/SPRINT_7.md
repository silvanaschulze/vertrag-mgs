# 🚀 PROMPT - Sprint 7: Gerenciamento de Usuários

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

---

## ✅ SPRINTS ANTERIORES COMPLETAS

### Sprint 1-6: ✅ Todas completas

---

## 🎯 SPRINT 7: GERENCIAMENTO DE USUÁRIOS

### Objetivo

Implementar sistema completo de gerenciamento de usuários com:
- **Lista de usuários** com paginação, filtros, ordenação
- **Criar novo usuário** com role e access level
- **Editar usuário existente** (nome, email, role, departamento, time)
- **Resetar senha** de usuário
- **Ativar/Desativar** usuário (sem deletar)
- **Filtros por role, departamento, status** (ativo/inativo)
- **TUDO respeitando permissões por role/level**

---

## 📝 Backend Já Existente

```
✅ backend/app/models/user.py - Modelo User completo
✅ backend/app/routers/users.py - Endpoints:
   - GET /api/users (lista com filtros)
   - GET /api/users/{id}
   - POST /api/users (criar novo)
   - PUT /api/users/{id} (atualizar)
   - POST /api/users/{id}/reset-password (resetar senha)
   - PATCH /api/users/{id}/activate (ativar)
   - PATCH /api/users/{id}/deactivate (desativar)
   - DELETE /api/users/{id} (deletar - apenas admin)
```

### Modelo User (Referência)

```python
class User(Base):
    __tablename__ = "users"
    
    id: int
    email: str  # Unique
    name: str
    password_hash: str
    role: str  # SYSTEM_ADMIN, DIRECTOR, DEPARTMENT_ADM, DEPARTMENT_USER, TEAM_LEAD, STAFF, READ_ONLY
    access_level: int  # 1-6
    department_id: Optional[int]
    team_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── users/  (❌ CRIAR AGORA)
│   │   ├── UserTable.jsx
│   │   ├── UserForm.jsx
│   │   ├── UserFilters.jsx
│   │   └── ResetPasswordDialog.jsx
│   └── ...
├── pages/
│   ├── users/  (❌ CRIAR AGORA)
│   │   ├── UsersPage.jsx
│   │   └── UserManage.jsx (create/edit)
│   └── ...
├── services/
│   ├── usersApi.js  (❌ CRIAR AGORA)
│   └── ...
└── ...
```

---

## 📝 CHECKLIST SPRINT 7

### 1. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/usersApi.js` com:
  - `getUsers(params)` - GET /api/users?page=1&page_size=25&role=STAFF
  - `getUser(id)` - GET /api/users/{id}
  - `createUser(data)` - POST /api/users
  - `updateUser(id, data)` - PUT /api/users/{id}
  - `resetPassword(id, newPassword)` - POST /api/users/{id}/reset-password
  - `activateUser(id)` - PATCH /api/users/{id}/activate
  - `deactivateUser(id)` - PATCH /api/users/{id}/deactivate
  - `deleteUser(id)` - DELETE /api/users/{id} (apenas SYSTEM_ADMIN)

### 2. Utils/Constants

- [ ] Atualizar `frontend/src/utils/constants.js` com:
  ```javascript
  export const USER_ROLES = {
    SYSTEM_ADMIN: 'SYSTEM_ADMIN',
    DIRECTOR: 'DIRECTOR',
    DEPARTMENT_ADM: 'DEPARTMENT_ADM',
    DEPARTMENT_USER: 'DEPARTMENT_USER',
    TEAM_LEAD: 'TEAM_LEAD',
    STAFF: 'STAFF',
    READ_ONLY: 'READ_ONLY'
  };
  
  export const USER_ROLE_LABELS = {
    SYSTEM_ADMIN: 'Systemadministrator / System Admin',
    DIRECTOR: 'Direktor / Director',
    DEPARTMENT_ADM: 'Abteilungsleiter / Department Admin',
    DEPARTMENT_USER: 'Abteilungsbenutzer / Department User',
    TEAM_LEAD: 'Teamleiter / Team Lead',
    STAFF: 'Mitarbeiter / Staff',
    READ_ONLY: 'Nur Lesen / Read Only'
  };
  
  export const ACCESS_LEVELS = {
    SYSTEM: 6,
    COMPANY: 5,
    DEPARTMENT: 4,
    DEPARTMENT_RESTRICTED: 3,
    TEAM: 2,
    OWN: 1
  };
  
  export const ACCESS_LEVEL_LABELS = {
    6: 'System (6)',
    5: 'Company (5)',
    4: 'Department (4)',
    3: 'Department Restricted (3)',
    2: 'Team (2)',
    1: 'Own (1)'
  };
  ```

### 3. Componentes de Usuários

- [ ] `frontend/src/components/users/UserTable.jsx`
  **Funcionalidades:**
  - DataGrid do MUI com paginação server-side
  - Colunas:
    - ID
    - Name
    - Email
    - Role (Chip colorido)
    - Access Level
    - Department (se tiver)
    - Team (se tiver)
    - Status (Ativo/Inativo - Switch ou Badge)
    - Actions (Edit, Reset Password, Activate/Deactivate)
  - Ordenação server-side
  - Highlight para usuários inativos (cinza)
  
  **Props:**
  ```javascript
  {
    users: Array<User>,
    loading: boolean,
    page: number,
    pageSize: number,
    totalRows: number,
    onPageChange: (page) => void,
    onPageSizeChange: (pageSize) => void,
    onSortChange: (sortBy) => void,
    onEdit: (userId) => void,
    onResetPassword: (userId) => void,
    onToggleActive: (userId, isActive) => void
  }
  ```

- [ ] `frontend/src/components/users/UserForm.jsx`
  **Funcionalidades:**
  - Formulário reutilizável para create/edit
  - React Hook Form + Zod validation
  - Campos:
    - name (required)
    - email (required, unique, validation email)
    - password (required apenas em create)
    - role (select - required)
    - access_level (número, baseado em role - readonly ou auto-calculado)
    - department (text, opcional)
    - team (text, opcional)
    - is_active (checkbox, default true)
  - Validação de email único (backend valida)
  - Labels bilíngues (DE/PT)
  
  **Props:**
  ```javascript
  {
    initialData: User | null,  // null = create, objeto = edit
    onSubmit: (data) => void,
    onCancel: () => void,
    loading: boolean
  }
  ```

- [ ] `frontend/src/components/users/UserFilters.jsx`
  **Funcionalidades:**
  - Filtros:
    - Role (All, SYSTEM_ADMIN, DIRECTOR, etc)
    - Status (All, Active, Inactive)
    - Department (text search)
    - Search (nome ou email)
  - Clear filters button
  - Layout responsivo Grid
  
  **Props:**
  ```javascript
  {
    filters: { role, status, department, search },
    onChange: (filters) => void,
    onClear: () => void
  }
  ```

- [ ] `frontend/src/components/users/ResetPasswordDialog.jsx`
  **Funcionalidades:**
  - Modal para resetar senha de usuário
  - Formulário com:
    - Nova senha (input password)
    - Confirmar senha (input password)
  - Validação: senhas devem ser iguais
  - Validação: senha deve ter pelo menos 8 caracteres
  - Loading state
  
  **Props:**
  ```javascript
  {
    open: boolean,
    userId: number,
    userName: string,
    onClose: () => void,
    onSubmit: (newPassword) => void,
    loading: boolean
  }
  ```

### 4. Páginas

- [ ] `frontend/src/pages/users/UsersPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Typography variant="h4">
        Benutzer / Users
      </Typography>
      
      {/* Botão criar apenas se permitido */}
      {canCreateUser && (
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => navigate('/app/users/new')}
        >
          Neuer Benutzer / New User
        </Button>
      )}
    </Box>
    
    <UserFilters 
      filters={filters}
      onChange={handleFilterChange}
      onClear={handleClearFilters}
    />
    
    <UserTable 
      users={users}
      loading={loading}
      page={page}
      pageSize={pageSize}
      totalRows={totalRows}
      onEdit={handleEdit}
      onResetPassword={handleResetPassword}
      onToggleActive={handleToggleActive}
      {...}
    />
    
    {/* Dialog de Reset Password */}
    <ResetPasswordDialog 
      open={resetPasswordOpen}
      userId={selectedUserId}
      userName={selectedUserName}
      onClose={() => setResetPasswordOpen(false)}
      onSubmit={handleResetPasswordSubmit}
    />
  </Container>
  ```

- [ ] `frontend/src/pages/users/UserManage.jsx`
  **Funcionalidades:**
  - Página para criar ou editar usuário
  - Se `id` na URL → modo edit, carrega usuário existente
  - Se sem `id` → modo create
  - Usa UserForm component
  - Breadcrumb: Users > New User (ou Edit User)
  - Redirect para /app/users após salvar
  
  **Layout:**
  ```jsx
  <Container>
    <Breadcrumbs sx={{ mb: 2 }}>
      <Link to="/app/users">Users</Link>
      <Typography>{id ? 'Edit User' : 'New User'}</Typography>
    </Breadcrumbs>
    
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {id ? 'Benutzer bearbeiten / Edit User' : 'Neuer Benutzer / New User'}
      </Typography>
      
      {loading && <CircularProgress />}
      
      {!loading && (
        <UserForm 
          initialData={user}
          onSubmit={handleSubmit}
          onCancel={() => navigate('/app/users')}
          loading={submitting}
        />
      )}
    </Paper>
  </Container>
  ```

### 5. Routing

- [ ] Atualizar `frontend/src/App.jsx`:
  ```jsx
  <Route
    path="users"
    element={
      <RequirePermission permission="users:view">
        <UsersPage />
      </RequirePermission>
    }
  />
  <Route
    path="users/new"
    element={
      <RequirePermission permission="users:create">
        <UserManage />
      </RequirePermission>
    }
  />
  <Route
    path="users/:id/edit"
    element={
      <RequirePermission permission="users:edit">
        <UserManage />
      </RequirePermission>
    }
  />
  ```

### 6. Sidebar Menu

- [ ] Menu "Users" já existe no Sidebar
- [ ] Visível apenas para roles com permissão `users:view`:
  - Level 6 (SYSTEM_ADMIN)
  - Level 5 (DIRECTOR)
  - Level 4 (DEPARTMENT_ADM) - vê apenas usuários do departamento

---

## 🔐 REGRAS DE PERMISSÕES

### Visualização de Usuários (users:view)

- **Level 6 (SYSTEM_ADMIN):** Vê TODOS usuários
- **Level 5 (DIRECTOR):** Vê TODOS usuários
- **Level 4 (DEPARTMENT_ADM):** Vê usuários do departamento
- **Outros:** NÃO veem página de usuários

### Criação de Usuários (users:create)

- **Level 6 (SYSTEM_ADMIN):** Pode criar usuários com qualquer role
- **Level 5 (DIRECTOR):** Pode criar usuários (exceto SYSTEM_ADMIN)
- **Level 4 (DEPARTMENT_ADM):** Pode criar usuários do departamento (DEPARTMENT_USER, STAFF, READ_ONLY)

### Edição de Usuários (users:edit)

- **Level 6:** Pode editar TODOS
- **Level 5:** Pode editar TODOS (exceto SYSTEM_ADMIN)
- **Level 4:** Pode editar usuários do departamento

### Deletar Usuários (users:delete)

- **Apenas Level 6 (SYSTEM_ADMIN):** Pode deletar

### Reset de Senha (users:reset-password)

- Mesmas regras de `users:edit`

### Ativar/Desativar (users:toggle-active)

- Mesmas regras de `users:edit`

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. usersApi.js (API calls)
2. UsersPage.jsx (página principal)
3. UserTable.jsx (DataGrid)
4. UserFilters.jsx (filtros)
5. Routing em App.jsx

### Prioridade MÉDIA (depois)

6. UserForm.jsx (create/edit)
7. UserManage.jsx (página create/edit)
8. ResetPasswordDialog.jsx (modal de reset)
9. Constants (USER_ROLES, ACCESS_LEVELS)
10. Integração com Sidebar

### Prioridade BAIXA (polimento)

11. Activate/Deactivate em massa (múltiplos usuários)
12. Exportação de lista de usuários (CSV)
13. Avatar/Foto de usuário
14. Histórico de ações do usuário

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 7 estará completa quando:

- [ ] Listagem de usuários funcional com paginação e ordenação
- [ ] Filtros de Role e Status funcionando
- [ ] Criar novo usuário (formulário completo)
- [ ] Editar usuário existente
- [ ] Resetar senha de usuário (com confirmação)
- [ ] Ativar/Desativar usuário (toggle)
- [ ] Permissões respeitadas (backend filtra usuários por role/department)
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Toast notifications (sucesso/erro)
- [ ] Menu "Users" no Sidebar (apenas para Levels 6, 5, 4)

---

## 🚀 COMO COMEÇAR

### 1. Criar usersApi.js primeiro:

- Implementar 8 funções (CRUD + reset, activate, deactivate)
- Error handling com try/catch

### 2. Criar constants.js - Adicionar USER_ROLES:

- USER_ROLES enum
- USER_ROLE_LABELS
- ACCESS_LEVELS
- ACCESS_LEVEL_LABELS

### 3. Implementar UsersPage + UserTable:

- Listagem simples
- Paginação
- Filtros
- Ordenação

### 4. Implementar UserForm + UserManage:

- Formulário create/edit
- Validação Zod
- Modo create vs edit

### 5. Implementar ResetPasswordDialog:

- Modal de reset
- Validação de senha

### 6. Testar com diferentes roles:

- admin@test.com (Level 6) - deve ver todos usuários
- director@test.com (Level 5) - deve ver todos usuários
- department_adm@test.com (Level 4) - deve ver apenas usuários do departamento

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend users: `backend/app/routers/users.py`
- Backend models: `backend/app/models/user.py`
- Frontend contracts: `frontend/src/pages/contracts/ContractsList.jsx` (estrutura similar)

---

## 🎯 META

Ao final da Sprint 7, o usuário deverá conseguir:

1. **Login como SYSTEM_ADMIN, DIRECTOR ou DEPARTMENT_ADM**
2. **Ver menu "Users"** no sidebar
3. **Acessar página de Users**
4. **Ver lista de usuários** (filtrada por permissão)
5. **Filtrar usuários** por role/status
6. **Clicar em "New User"** e criar novo usuário
7. **Editar usuário** existente
8. **Resetar senha** de usuário (com modal)
9. **Ativar/Desativar** usuário (toggle direto na tabela)
10. **Ver que DEPARTMENT_ADM** vê apenas usuários do departamento

---

**Pronto para começar! Vamos implementar a Sprint 7 passo a passo, seguindo as prioridades definidas.**
