# 🚀 PROMPT - Sprint 6: Aprovações de Contratos (Workflow)

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

---

## ✅ SPRINTS ANTERIORES COMPLETAS

### Sprint 1: Setup e Autenticação ✅
### Sprint 2: Dashboard com Widgets por Role ✅
### Sprint 3: CRUD Completo de Contratos ✅
### Sprint 4: Alertas e Notificações ✅
### Sprint 5: Upload e Import de PDFs ✅

---

## 🎯 SPRINT 6: APROVAÇÕES DE CONTRATOS (WORKFLOW)

### Objetivo

Implementar sistema completo de workflow de aprovação de contratos com:
- **Lista de contratos pendentes de aprovação**
- **Detalhes do contrato** com PDF preview
- **Ações de aprovação:** Aprovar, Rejeitar, Solicitar Revisão
- **Comentários** para rejeição/revisão
- **Histórico de aprovações** de cada contrato
- **Badge de contador** de aprovações pendentes no menu
- **Notificações** ao criador quando contrato é aprovado/rejeitado
- **TUDO respeitando permissões por role/level**

---

## 📝 Backend Já Existente

```
✅ backend/app/models/contract_approval.py - Modelo ContractApproval
✅ backend/app/routers/approvals.py - Endpoints:
   - GET /api/approvals (lista de contratos pendentes)
   - POST /api/approvals/{contract_id}/approve (aprovar)
   - POST /api/approvals/{contract_id}/reject (rejeitar)
   - POST /api/approvals/{contract_id}/request-revision (solicitar revisão)
   - GET /api/approvals/{contract_id}/history (histórico de aprovações)
```

### Modelo ContractApproval (Referência)

```python
class ContractApproval(Base):
    __tablename__ = "contract_approvals"
    
    id: int
    contract_id: int  # FK para contracts
    approver_id: int  # FK para users (quem aprovou/rejeitou)
    action: str  # 'APPROVED', 'REJECTED', 'REVISION_REQUESTED'
    comments: Optional[str]
    created_at: datetime
    
    # Relacionamentos
    contract: Contract
    approver: User
```

### Status de Aprovação (em Contract)

```python
# backend/app/models/contract.py
class Contract:
    approval_status: str  # 'PENDING', 'APPROVED', 'REJECTED', 'REVISION_REQUESTED'
```

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── approvals/  (❌ CRIAR AGORA)
│   │   ├── ApprovalsList.jsx
│   │   ├── ApprovalCard.jsx
│   │   ├── ApprovalActions.jsx
│   │   └── ApprovalHistory.jsx
│   └── ...
├── pages/
│   ├── approvals/  (❌ CRIAR AGORA)
│   │   └── ApprovalsPage.jsx
│   └── ...
├── services/
│   ├── approvalsApi.js  (❌ CRIAR AGORA)
│   └── ...
└── ...
```

---

## 📝 CHECKLIST SPRINT 6

### 1. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/approvalsApi.js` com:
  - `getPendingApprovals(params)` - GET /api/approvals?status=PENDING
  - `approveContract(contractId, comments)` - POST /api/approvals/{id}/approve
  - `rejectContract(contractId, reason)` - POST /api/approvals/{id}/reject
  - `requestRevision(contractId, comments)` - POST /api/approvals/{id}/request-revision
  - `getApprovalHistory(contractId)` - GET /api/approvals/{id}/history
  - `getPendingCount()` - GET /api/approvals?status=PENDING&page_size=1 (retorna total)

### 2. Utils/Constants

- [ ] Atualizar `frontend/src/utils/constants.js` com:
  ```javascript
  export const APPROVAL_STATUS = {
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED',
    REVISION_REQUESTED: 'REVISION_REQUESTED'
  };
  
  export const APPROVAL_STATUS_LABELS = {
    PENDING: 'Wartet / Pending',
    APPROVED: 'Genehmigt / Approved',
    REJECTED: 'Abgelehnt / Rejected',
    REVISION_REQUESTED: 'Überarbeitung angefordert / Revision Requested'
  };
  
  export const APPROVAL_STATUS_COLORS = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'error',
    REVISION_REQUESTED: 'info'
  };
  
  export const APPROVAL_ACTIONS = {
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED',
    REVISION_REQUESTED: 'REVISION_REQUESTED'
  };
  ```

### 3. Componentes de Aprovações

- [ ] `frontend/src/components/approvals/ApprovalsList.jsx`
  **Funcionalidades:**
  - Lista de contratos pendentes de aprovação
  - Grid/Cards com:
    - Título do contrato
    - Cliente/Parceiro
    - Valor (se permitido)
    - Data de criação
    - Criado por (nome do usuário)
    - Botões de ação (Aprovar, Rejeitar, Ver Detalhes)
  - Paginação
  - Loading states
  - Empty state se nenhuma aprovação pendente
  
  **Props:**
  ```javascript
  {
    approvals: Array<Contract>,
    loading: boolean,
    onApprove: (contractId) => void,
    onReject: (contractId) => void,
    onViewDetails: (contractId) => void
  }
  ```

- [ ] `frontend/src/components/approvals/ApprovalCard.jsx`
  **Funcionalidades:**
  - Card individual de aprovação
  - Exibe informações resumidas do contrato
  - Botões de ação
  - Status badge
  
  **Props:**
  ```javascript
  {
    contract: Contract,
    onApprove: () => void,
    onReject: () => void,
    onViewDetails: () => void,
    showFinancialValues: boolean  // Baseado em access_level
  }
  ```

- [ ] `frontend/src/components/approvals/ApprovalActions.jsx`
  **Funcionalidades:**
  - Modal/Dialog para ações de aprovação
  - Formulário com:
    - Ação (Aprovar, Rejeitar, Solicitar Revisão)
    - Comentários (obrigatório para Rejeitar e Revisão)
  - Validação
  - Loading state durante envio
  
  **Props:**
  ```javascript
  {
    open: boolean,
    contractId: number,
    contractTitle: string,
    onClose: () => void,
    onSubmit: (action, comments) => void,
    loading: boolean
  }
  ```

- [ ] `frontend/src/components/approvals/ApprovalHistory.jsx`
  **Funcionalidades:**
  - Timeline de aprovações/rejeições
  - Exibe:
    - Data/Hora
    - Ação (Aprovado/Rejeitado/Revisão)
    - Aprovador (nome + role)
    - Comentários (se houver)
  - Ordenado por data (mais recente primeiro)
  
  **Props:**
  ```javascript
  {
    contractId: number,
    history: Array<ContractApproval>
  }
  ```

### 4. Páginas

- [ ] `frontend/src/pages/approvals/ApprovalsPage.jsx`
  **Fluxo:**
  1. Carrega lista de contratos pendentes
  2. Exibe ApprovalsList
  3. Ao clicar em "Ver Detalhes" → Abre modal com:
     - PDFPreview (se tiver PDF)
     - ContractDetail
     - ApprovalHistory
     - ApprovalActions
  4. Ao aprovar/rejeitar → Atualiza lista
  
  **Layout:**
  ```jsx
  <Container>
    <Box sx={{ mb: 3 }}>
      <Typography variant="h4">
        Genehmigungen / Approvals
      </Typography>
      <Chip 
        label={`${pendingCount} Pending`}
        color="warning"
        sx={{ mt: 1 }}
      />
    </Box>
    
    {loading ? (
      <CircularProgress />
    ) : approvals.length === 0 ? (
      <EmptyState message="Keine Genehmigungen erforderlich / No approvals required" />
    ) : (
      <ApprovalsList 
        approvals={approvals}
        onApprove={handleApprove}
        onReject={handleReject}
        onViewDetails={handleViewDetails}
      />
    )}
    
    {/* Modal de detalhes */}
    <Dialog open={detailsOpen} onClose={handleCloseDetails} maxWidth="lg" fullWidth>
      <DialogTitle>{selectedContract?.title}</DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            {selectedContract?.pdf_path && (
              <PDFPreview pdfUrl={`/api/contracts/${selectedContract.id}/pdf/preview`} />
            )}
          </Grid>
          <Grid item xs={12} md={6}>
            <ContractDetail contract={selectedContract} />
            <ApprovalHistory contractId={selectedContract?.id} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <ApprovalActions 
          contractId={selectedContract?.id}
          contractTitle={selectedContract?.title}
          onSubmit={handleApprovalAction}
        />
      </DialogActions>
    </Dialog>
  </Container>
  ```

### 5. Integração com ContractView

- [ ] **Atualizar `frontend/src/pages/contracts/ContractView.jsx`:**
  - Adicionar seção "Approval History" se contrato foi submetido para aprovação
  - Exibir ApprovalHistory component
  - Mostrar status atual de aprovação (PENDING, APPROVED, REJECTED)

### 6. Integração com ContractCreate

- [ ] **Opção "Submeter para Aprovação":**
  - Ao criar contrato, checkbox "Submeter para aprovação"
  - Se marcado, status inicial = 'PENDING_APPROVAL'
  - Se não marcado, status inicial = 'DRAFT'

### 7. Routing

- [ ] Atualizar `frontend/src/App.jsx`:
  ```jsx
  <Route
    path="approvals"
    element={
      <RequirePermission permission="approvals:view">
        <ApprovalsPage />
      </RequirePermission>
    }
  />
  ```

### 8. Sidebar Menu - Badge de Contador

- [ ] Atualizar `frontend/src/components/layout/Sidebar.jsx`:
  - Item "Approvals" já existe
  - Adicionar badge com contador de pendências:
    ```jsx
    <ListItemIcon>
      <Badge badgeContent={pendingApprovalsCount} color="warning">
        <CheckCircleIcon />
      </Badge>
    </ListItemIcon>
    ```

---

## 🔐 REGRAS DE PERMISSÕES

### Visualização de Aprovações (approvals:view)

- **Level 5 (DIRECTOR):** Vê TODAS aprovações pendentes
- **Level 4 (DEPARTMENT_ADM):** Vê aprovações do departamento
- **Outros:** NÃO veem página de aprovações

### Aprovar Contratos (approvals:approve)

- **Level 5 (DIRECTOR):** Pode aprovar QUALQUER contrato
- **Level 4 (DEPARTMENT_ADM):** Pode aprovar contratos do departamento
- **Outros:** NÃO podem aprovar

### Rejeitar Contratos (approvals:reject)

- Mesmas regras de `approvals:approve`

### Solicitar Revisão (approvals:request-revision)

- Mesmas regras de `approvals:approve`

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. approvalsApi.js (API calls)
2. ApprovalsPage.jsx (página principal)
3. ApprovalsList.jsx (lista de pendências)
4. ApprovalCard.jsx (card individual)
5. ApprovalActions.jsx (modal de ações)

### Prioridade MÉDIA (depois)

6. ApprovalHistory.jsx (timeline de histórico)
7. Integração com Sidebar (badge de contador)
8. Constants (APPROVAL_STATUS)
9. Integração com ContractView (histórico)
10. Polling para atualizar contador

### Prioridade BAIXA (polimento)

11. Integração com ContractCreate (checkbox "submeter para aprovação")
12. Notificações push quando aprovado/rejeitado
13. Filtros (por departamento, por criador, etc)
14. Exportação de relatório de aprovações

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 6 estará completa quando:

- [ ] Listagem de aprovações pendentes funcional
- [ ] Badge de contador de pendências no menu Approvals
- [ ] Modal de detalhes com PDF preview + informações do contrato
- [ ] Ações de aprovar/rejeitar/solicitar revisão funcionando
- [ ] Comentários obrigatórios em rejeição/revisão
- [ ] Histórico de aprovações exibido
- [ ] Permissões respeitadas (apenas Levels 5 e 4 veem aprovações)
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Toast notifications (sucesso ao aprovar/rejeitar)
- [ ] Lista atualiza após ação de aprovação

---

## 🚀 COMO COMEÇAR

### 1. Criar approvalsApi.js primeiro:

- Implementar 5 funções (get, approve, reject, request-revision, history)
- Error handling com try/catch

### 2. Criar constants.js - Adicionar APPROVAL_STATUS:

- APPROVAL_STATUS enum
- APPROVAL_STATUS_LABELS
- APPROVAL_STATUS_COLORS

### 3. Implementar ApprovalsPage + ApprovalsList:

- Listagem simples
- Paginação
- Empty state

### 4. Implementar ApprovalActions (modal):

- Formulário com ação + comentários
- Validação (comentários obrigatórios para rejeitar/revisão)

### 5. Implementar ApprovalHistory:

- Timeline de ações
- Exibir no modal de detalhes

### 6. Testar com diferentes roles:

- director@test.com (Level 5) - deve ver todas aprovações
- department_adm@test.com (Level 4) - deve ver aprovações do departamento

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend approvals: `backend/app/routers/approvals.py`
- Backend models: `backend/app/models/contract_approval.py`, `backend/app/models/contract.py`
- Frontend ContractView: `frontend/src/pages/contracts/ContractView.jsx`

---

## 🎯 META

Ao final da Sprint 6, o usuário deverá conseguir:

1. **Login como DIRECTOR ou DEPARTMENT_ADM**
2. **Ver badge de contador** de aprovações pendentes no menu
3. **Acessar página de Approvals**
4. **Ver lista de contratos** pendentes de aprovação
5. **Clicar em "Ver Detalhes"** e visualizar:
   - PDF do contrato
   - Informações completas
   - Histórico de aprovações
6. **Aprovar contrato** com comentários opcionais
7. **Rejeitar contrato** com motivo obrigatório
8. **Solicitar revisão** com comentários obrigatórios
9. **Ver lista atualizada** após ação
10. **Receber toast** de confirmação

---

**Pronto para começar! Vamos implementar a Sprint 6 passo a passo, seguindo as prioridades definidas.**
