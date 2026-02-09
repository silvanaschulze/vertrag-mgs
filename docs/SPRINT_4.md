# 🚀 PROMPT - Sprint 4: Alertas e Notificações

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

---

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
- Frontend: 6 componentes de dashboard (um para cada role/level)
- Todos dashboards traduzidos para inglês
- API GET /api/dashboard/stats funcionando

### Sprint 3: CRUD Completo de Contratos ✅
- ContractsList com paginação, ordenação, filtros
- ContractCreate e ContractEdit com React Hook Form + Zod
- ContractView com detalhes completos
- ContractDelete com confirmação
- Upload de PDF implementado (pendências de integração backend)
- Permissões por role implementadas

---

## 🎯 SPRINT 4: ALERTAS E NOTIFICAÇÕES

### Objetivo

Implementar sistema completo de alertas e notificações para contratos com:
- Lista de alertas com paginação e filtros
- Badge de notificações não lidas no menu
- Marcar alertas como lidos
- Visualizar detalhes do alerta e contrato relacionado
- Filtros por tipo de alerta (expirando, vencido, manual)
- **TUDO respeitando permissões por role/level**

---

## 📝 Backend Já Existente

```
✅ backend/app/models/alert.py - Modelo Alert completo
✅ backend/app/routers/alerts.py - Endpoints:
   - GET /api/alerts (list com filtros)
   - GET /api/alerts/{id}
   - PATCH /api/alerts/{id}/read (marcar como lido)
   - POST /api/alerts (criar alerta manual - admin)
   - DELETE /api/alerts/{id} (deletar alerta)
✅ backend/app/services/notification_service.py - Lógica de criação de alertas
```

### Modelo Alert (Referência)

```python
class Alert(Base):
    __tablename__ = "alerts"
    
    id: int
    contract_id: int  # FK para contracts
    alert_type: str  # 'T-60', 'T-30', 'T-10', 'T-1', 'CUSTOM'
    alert_date: date
    triggered_at: datetime
    is_read: bool
    read_at: datetime | None
    created_at: datetime
    
    # Relacionamentos
    contract: Contract
```

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── alerts/  (❌ CRIAR AGORA)
│   │   ├── AlertsList.jsx
│   │   ├── AlertBadge.jsx
│   │   └── AlertFilters.jsx
│   └── ...
├── pages/
│   ├── alerts/  (❌ CRIAR AGORA)
│   │   └── AlertsPage.jsx
│   └── ...
├── services/
│   ├── alertsApi.js  (❌ CRIAR AGORA)
│   └── ...
└── utils/
    ├── constants.js  (⏳ ADICIONAR ALERT_TYPES)
    └── ...
```

---

## 📝 CHECKLIST SPRINT 4

### 1. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/alertsApi.js` com:
  - `getAlerts(filters, page, pageSize)` - GET /api/alerts
  - `getAlert(id)` - GET /api/alerts/{id}
  - `markAsRead(id)` - PATCH /api/alerts/{id}/read
  - `createAlert(data)` - POST /api/alerts (apenas admin)
  - `deleteAlert(id)` - DELETE /api/alerts/{id}
  - `getUnreadCount()` - GET /api/alerts?is_read=false&page_size=1 (pega total)

### 2. Utils/Constants

- [ ] Atualizar `frontend/src/utils/constants.js` com:
  ```javascript
  export const ALERT_TYPES = {
    T_60: 'T-60',      // 60 dias antes do vencimento
    T_30: 'T-30',      // 30 dias antes
    T_10: 'T-10',      // 10 dias antes
    T_1: 'T-1',        // 1 dia antes
    CUSTOM: 'CUSTOM'   // Alerta manual
  };
  
  export const ALERT_TYPE_LABELS = {
    'T-60': '60 Tage / 60 Days',
    'T-30': '30 Tage / 30 Days',
    'T-10': '10 Tage / 10 Days',
    'T-1': '1 Tag / 1 Day',
    'CUSTOM': 'Benutzerdefiniert / Custom'
  };
  
  export const ALERT_TYPE_COLORS = {
    'T-60': 'info',
    'T-30': 'warning',
    'T-10': 'error',
    'T-1': 'error',
    'CUSTOM': 'default'
  };
  ```

### 3. Componentes de Alertas

- [ ] `frontend/src/components/alerts/AlertsList.jsx`
  - Tabela de alertas (pode usar MUI Table ou DataGrid)
  - Colunas:
    - ID
    - Tipo (Chip colorido)
    - Título do Contrato (link para ContractView)
    - Data do Alerta (alert_date)
    - Status (Lido/Não Lido - com ícone)
    - Actions (Marcar como lido, Ver contrato)
  - Paginação server-side
  - Clique na linha abre contrato relacionado
  - Badge/Highlight para alertas não lidos

- [ ] `frontend/src/components/alerts/AlertBadge.jsx`
  - Badge com contador de alertas não lidos
  - Usado no menu Sidebar
  - Atualiza automaticamente (polling ou WebSocket futuro)
  - Exemplo:
    ```jsx
    <Badge badgeContent={unreadCount} color="error">
      <NotificationsIcon />
    </Badge>
    ```

- [ ] `frontend/src/components/alerts/AlertFilters.jsx`
  - Filtros:
    - Tipo (All, T-60, T-30, T-10, T-1, Custom)
    - Status (All, Read, Unread)
    - Busca por título do contrato
  - Clear filters button
  - Layout responsivo Grid

### 4. Páginas

- [ ] `frontend/src/pages/alerts/AlertsPage.jsx`
  - Header "Warnungen / Alerts"
  - AlertFilters
  - AlertsList
  - Estado: alerts, loading, error, filters, page, pageSize, totalRows, unreadCount
  - Polling para atualizar unreadCount a cada 30s (opcional)
  - Botão "Mark All as Read" (apenas se houver não lidos)

### 5. Routing

- [ ] Atualizar `frontend/src/App.jsx` com rotas:
  ```jsx
  <Route path="alerts" element={<AlertsPage />} />
  ```
  (Já deve estar lá como placeholder)

### 6. Sidebar Menu

- [ ] Atualizar `frontend/src/components/layout/Sidebar.jsx`:
  - Item "Alerts" já existe
  - Adicionar AlertBadge ao lado do ícone:
    ```jsx
    <ListItemIcon>
      <AlertBadge />
    </ListItemIcon>
    ```
  - Mostrar para todos (Levels 1-6)

### 7. Integrações

- [ ] **Dashboard widgets:** Adicionar contador de alertas não lidos
  - Cada dashboard deve chamar `getUnreadCount()` e exibir um Card
  - Exemplo: "5 Warnungen / 5 Alerts"

- [ ] **ContractView:** Adicionar lista de alertas do contrato
  - Ao visualizar um contrato, mostrar todos alertas relacionados
  - Tabela simples com tipo, data, status

---

## 🎨 REFERÊNCIAS DE DESIGN

### AlertsList (Tabela)

```jsx
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>ID</TableCell>
        <TableCell>Typ / Type</TableCell>
        <TableCell>Vertrag / Contract</TableCell>
        <TableCell>Datum / Date</TableCell>
        <TableCell>Status</TableCell>
        <TableCell>Actions</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {alerts.map(alert => (
        <TableRow 
          key={alert.id}
          sx={{ 
            backgroundColor: !alert.is_read ? 'action.hover' : 'inherit',
            cursor: 'pointer'
          }}
          onClick={() => navigate(`/app/contracts/${alert.contract_id}`)}
        >
          <TableCell>{alert.id}</TableCell>
          <TableCell>
            <Chip 
              label={ALERT_TYPE_LABELS[alert.alert_type]} 
              color={ALERT_TYPE_COLORS[alert.alert_type]}
              size="small"
            />
          </TableCell>
          <TableCell>{alert.contract?.title}</TableCell>
          <TableCell>{format(new Date(alert.alert_date), 'dd.MM.yyyy')}</TableCell>
          <TableCell>
            {alert.is_read ? (
              <CheckCircleIcon color="success" />
            ) : (
              <CircleIcon color="disabled" />
            )}
          </TableCell>
          <TableCell>
            {!alert.is_read && (
              <IconButton onClick={(e) => {
                e.stopPropagation();
                handleMarkAsRead(alert.id);
              }}>
                <DoneIcon />
              </IconButton>
            )}
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>
```

### AlertBadge

```jsx
const AlertBadge = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  
  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const count = await alertsApi.getUnreadCount();
        setUnreadCount(count);
      } catch (error) {
        console.error('Error fetching unread count:', error);
      }
    };
    
    fetchUnread();
    
    // Polling a cada 30s (opcional)
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Badge badgeContent={unreadCount} color="error" max={99}>
      <NotificationsIcon />
    </Badge>
  );
};
```

---

## 🔐 REGRAS DE PERMISSÕES

### Visualização de Alertas (alerts:view)

- **Level 6 (SYSTEM_ADMIN):** Vê TODOS alertas do sistema
- **Level 5 (DIRECTOR):** Vê TODOS alertas
- **Level 4 (DEPARTMENT_ADM):** Vê alertas de contratos do departamento
- **Level 3 (DEPARTMENT_USER):** Vê alertas de contratos do departamento
- **Level 2 (TEAM_LEAD):** Vê alertas de contratos do time
- **Level 1 (STAFF/READ_ONLY):** Vê alertas de contratos onde é responsável

### Criação de Alertas Manuais (alerts:create)

- **Apenas Levels 5, 4:** Podem criar alertas manuais (CUSTOM)

### Exclusão de Alertas (alerts:delete)

- **Apenas Level 5 (DIRECTOR):** Pode deletar alertas

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. alertsApi.js (API calls)
2. AlertsPage.jsx (página principal)
3. AlertsList.jsx (tabela de alertas)
4. AlertFilters.jsx (filtros)
5. Routing em App.jsx

### Prioridade MÉDIA (depois)

6. AlertBadge.jsx (contador no menu)
7. Integração com Sidebar (badge)
8. Constants (ALERT_TYPES)
9. Mark as read functionality
10. Polling para atualização automática

### Prioridade BAIXA (polimento)

11. Integração com Dashboard (contador de alertas)
12. Integração com ContractView (lista de alertas do contrato)
13. Botão "Mark All as Read"
14. Notificações push (WebSocket - Sprint futura)

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 4 estará completa quando:

- [ ] Listagem de alertas funcional com paginação
- [ ] Filtros de Tipo e Status funcionando
- [ ] Badge de contador de não lidos no menu Alerts
- [ ] Marcar alerta como lido (individual)
- [ ] Clicar em alerta abre contrato relacionado
- [ ] Permissões respeitadas (backend filtra alertas por role)
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Toast notifications (sucesso ao marcar como lido)
- [ ] Alertas não lidos destacados visualmente (background diferente)

---

## 🚀 COMO COMEÇAR

### 1. Instalar dependências (se necessário):

```bash
cd /home/sschulze/projects/vertrag-mgs/frontend
# Já deve ter todas as dependências da Sprint 3
```

### 2. Criar alertsApi.js primeiro:

- Implementar 5 funções (CRUD + getUnreadCount)
- Usar axios instance de api.js
- Error handling com try/catch

### 3. Criar constants.js - Adicionar ALERT_TYPES:

- ALERT_TYPES enum
- ALERT_TYPE_LABELS
- ALERT_TYPE_COLORS

### 4. Implementar AlertsPage + AlertsList:

- Começar com listagem simples
- Adicionar paginação
- Adicionar filtros
- Adicionar mark as read

### 5. Implementar AlertBadge:

- Contador de não lidos
- Polling a cada 30s
- Integrar no Sidebar

### 6. Testar com diferentes roles:

- admin@test.com (Level 6) - deve ver todos alertas
- director@test.com (Level 5) - deve ver todos alertas
- staff@test.com (Level 1) - deve ver apenas alertas de contratos próprios

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend alerts: `backend/app/routers/alerts.py`
- Backend models: `backend/app/models/alert.py`
- Backend notification service: `backend/app/services/notification_service.py`
- Frontend contracts: `frontend/src/pages/contracts/ContractsList.jsx` (estrutura similar)
- Frontend API: `frontend/src/services/contractsApi.js` (exemplo de API calls)

---

## 🎯 META

Ao final da Sprint 4, o usuário deverá conseguir:

- Fazer login como qualquer role
- Ver menu "Alerts" no sidebar com badge de contador
- Clicar e ver lista de alertas (paginada)
- Filtrar alertas por tipo/status
- Marcar alertas como lidos
- Clicar em alerta e ser redirecionado para o contrato
- Ver que alertas não lidos aparecem destacados
- Ver que contador de badge atualiza após marcar como lido

---

## 📝 OBSERVAÇÕES IMPORTANTES

### Backend Integration

- Backend já está pronto e funcionando
- Endpoint GET /api/alerts retorna alertas filtrados por role automaticamente
- Não precisa implementar lógica de permissões no frontend (backend faz isso)
- Apenas precisa chamar as APIs corretamente

### Alertas Automáticos

- Alertas T-60, T-30, T-10, T-1 são criados automaticamente pelo backend
- Rodando em background scheduler (a cada 6 horas)
- Frontend apenas exibe os alertas existentes

### Alertas Manuais (CUSTOM)

- Apenas Levels 5 e 4 podem criar alertas manuais
- Formulário simples: contract_id, alert_date, mensagem
- Será implementado em Sprint futura (não é prioridade agora)

---

**Pronto para começar! Vamos implementar a Sprint 4 passo a passo, seguindo as prioridades definidas.**
