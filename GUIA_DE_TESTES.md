# 🧪 GUIA DE TESTES - Funcionalidades Implementadas

## ⚠️ CONCEITOS IMPORTANTES - LEIA PRIMEIRO!

### 📌 ALERTAS vs APROVAÇÕES - Diferença Crucial!

**1. ALERTAS (Alerts) 🔔**
- **O que são?** Notificações sobre **VENCIMENTOS de contratos**
- **Quando são criados?** Automaticamente pelo sistema em datas específicas:
  - T-60: 60 dias antes do vencimento
  - T-30: 30 dias antes
  - T-10: 10 dias antes
  - T-1: 1 dia antes
  - BENUTZERDEFINIERT: Alertas customizados que você cria manualmente
- **Onde ver?** 
  - Página `/app/alerts` → lista TODOS os alertas de TODOS os contratos
  - Dentro de cada contrato → alertas daquele contrato específico
- **Podem ser criados ao criar contrato?** **NÃO!** Porque o contrato precisa ter um ID (precisa estar salvo primeiro)

**2. APROVAÇÕES (Approvals) ✅**
- **O que são?** Pedidos de aprovação para **CRIAR/EDITAR contratos**
- **Quando são criados?** Quando alguém cria ou edita um contrato
- **São formulários?** **NÃO!** São registros gerados automaticamente pelo sistema
- **Onde ver?** 
  - Página `/app/approvals` → lista TODAS as aprovações pendentes
  - Dentro de cada contrato → histórico de aprovações daquele contrato
- **Precisa preencher campos ao criar contrato?** **NÃO!** O sistema gera automaticamente

### 🔑 Resumo da Confusão

| Item | Alertas 🔔 | Aprovações ✅ |
|------|---------|------------|
| **Propósito** | Avisar vencimento | Aprovar criação/edição |
| **Página Global** | `/app/alerts` | `/app/approvals` |
| **Página Individual** | Dentro do contrato | Dentro do contrato |
| **Criação Manual?** | Sim (custom alerts) | Não (automático) |
| **Requer contrato salvo?** | Sim (precisa ID) | Sim (gera após salvar) |
| **São formulários?** | Sim (custom alert form) | NÃO (workflow) |

---

## 📋 Índice
1. [Preparação do Ambiente](#preparação-do-ambiente)
2. [Sistema de Alertas](#sistema-de-alertas)
3. [Rent Steps (Mietstaffelungen)](#rent-steps)
4. [Sistema de Aprovações](#sistema-de-aprovações)
5. [Checklist Final](#checklist-final)

---

## 🚀 Preparação do Ambiente

### 1. Iniciar Backend
```bash
cd /home/sschulze/projects/vertrag-mgs/backend
source ../.venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verificar:**
- ✅ Backend rodando em http://localhost:8000
- ✅ Docs disponível em http://localhost:8000/docs
- ✅ Health check: http://localhost:8000/health

### 2. Iniciar Frontend
```bash
cd /home/sschulze/projects/vertrag-mgs/frontend
npm run dev
```

**Verificar:**
- ✅ Frontend rodando em http://localhost:5173
- ✅ Console sem erros
- ✅ Página de login carregando

### 3. Login no Sistema
```
Email: director@test.com
Password: director123
Role: DIRECTOR (Nível 5)
```

**Usuários alternativos disponíveis:**
- `admin@test.com` / `admin123` - SYSTEM_ADMIN (Nível 6)
- `director@test.com` / `director123` - DIRECTOR (Nível 5) ✅ **USANDO ESTE**

**Após login verificar:**
- ✅ Token armazenado no localStorage
- ✅ Redirecionamento para /app/dashboard
- ✅ Header mostrando nome do usuário: "Director Test"
- ✅ Sidebar com menus visíveis para DIRECTOR:
  - Dashboard
  - Contratos
  - Importar
  - Alertas
  - Usuários
  - Aprovações
  - Relatórios

---

## 🔔 Sistema de Alertas

### Funcionalidade 1: Visualizar Alertas

**Navegação:** Sidebar → "Alertas" → AlertsPage

**Verificar:**
1. ✅ Página carrega lista de alertas
2. ✅ Badge no menu mostra contagem de pendentes
3. ✅ Filtros disponíveis:
   - Status: Todos / Pendente / Enviado / Falhou
   - Tipo: T-60 / T-30 / T-10 / T-1 / Customizado

**Dados na tabela:**
- ID do alerta
- Tipo (chip colorido)
- Nome do contrato
- Data agendada
- Status (chip colorido)
- Botões de ação

### Funcionalidade 2: Processar Alertas Manualmente

**Passo a passo:**
1. Na página de alertas, clicar em **"Warnungen verarbeiten"**
2. Aguardar processamento
3. Ver toast de sucesso
4. Lista de alertas atualiza automaticamente

**Verificar:**
- ✅ Botão funciona
- ✅ Loading durante processamento
- ✅ Toast "Alertas processados"
- ✅ Contadores atualizados

### Funcionalidade 3: Marcar Alerta como Lido

**Passo a passo:**
1. Na lista, encontrar alerta com status **"Pendente"**
2. Clicar no ícone de ✓ (check)
3. Aguardar confirmação

**Verificar:**
- ✅ Ícone de loading aparece
- ✅ Toast "Alerta marcado como lido"
- ✅ Alerta some da lista de pendentes

### Funcionalidade 4: Reprocessar Alerta Falhado

**Pré-requisito:** Ter alerta com status "Falhou"

**Passo a passo:**
1. Filtrar por Status = "Falhou"
2. Clicar no ícone 🔄 (Replay)
3. Aguardar reprocessamento

**Verificar:**
- ✅ Botão só aparece para alertas falhados
- ✅ Loading durante reprocessamento
- ✅ Toast de sucesso/erro
- ✅ Status atualizado

### Funcionalidade 5: Alertas no Badge do Menu

**Verificar:**
1. Badge no menu "Alertas" mostra número
2. Número corresponde a alertas pendentes
3. Badge atualiza a cada 30 segundos
4. Ao marcar como lido, número diminui




---

## 📈 Rent Steps (Mietstaffelungen)

### Funcionalidade 6: Visualizar Rent Steps de um Contrato

**Navegação:** Contratos → Selecionar contrato → Visualizar

**Localização:** Após "Alertas do Contrato", seção "Mietstaffelungen"

**Verificar:**
1. ✅ Tabela com rent steps ordenados por data
2. ✅ Colunas:
   - Data de vigência
   - Valor (formatado com símbolo de moeda)
   - Aumento % (chip colorido)
   - Status (Ativo/Planejado/Hoje)
   - Observações
   - Ações (editar/excluir)
3. ✅ Alert destacando próximo aumento (se houver)

### Funcionalidade 7: Criar Rent Step

**Pré-requisito:** Estar na página de visualização ou edição do contrato

**Passo a passo:**
1. Na seção "Mietstaffelungen", clicar **"Hinzufügen"**
2. Preencher formulário:
   - **Data de vigência:** Escolher data futura
   - **Valor:** Ex: 1200.00
   - **Moeda:** EUR
   - **Observações:** (opcional) "Aumento anual contratual"
3. Clicar **"Erstellen"**

**Verificar:**
- ✅ Dialog abre corretamente
- ✅ DatePicker em alemão
- ✅ Validação: data e valor obrigatórios
- ✅ Toast "Mietstaffelung erstellt"
- ✅ Novo step aparece na tabela
- ✅ Percentual de aumento calculado automaticamente

### Funcionalidade 8: Editar Rent Step

**Passo a passo:**
1. Clicar no ícone ✏️ (edit) ao lado do rent step
2. Modificar valor ou data
3. Clicar **"Aktualisieren"**

**Verificar:**
- ✅ Dialog pré-preenchido com dados atuais
- ✅ Alterações salvas
- ✅ Toast de sucesso
- ✅ Tabela atualizada

### Funcionalidade 9: Excluir Rent Step

**Passo a passo:**
1. Clicar no ícone 🗑️ (delete)
2. Confirmar exclusão no dialog

**Verificar:**
- ✅ Dialog de confirmação aparece
- ✅ Após confirmar, step removido
- ✅ Toast de sucesso

### Funcionalidade 10: Rent Steps na Edição de Contrato

**Navegação:** Contratos → Selecionar → Editar

**Verificar:**
- ✅ Seção "Mietstaffelungen" aparece APÓS o formulário
- ✅ Mesma funcionalidade CRUD disponível
- ✅ Alterações refletem na visualização

---

## ✅ Sistema de Aprovações

### Funcionalidade 11: Visualizar Histórico de Aprovações

**Navegação:** Contratos → Selecionar contrato com status "PENDING_APPROVAL"

**Localização:** Após "Rent Steps", seção "Genehmigungen"

**Verificar:**
1. ✅ Tabela de aprovações
2. ✅ Colunas:
   - Aprovador (nome + nível)
   - Status (chip colorido)
   - Data de aprovação/rejeição
   - Comentários
   - Motivo da rejeição
3. ✅ Se pendente, aparece alert amarelo

### Funcionalidade 12: Aprovar Contrato

**Pré-requisito:** 
- Contrato com status "PENDING_APPROVAL"
- Usuário com permissão (Manager ou Admin)

**Passo a passo:**
1. No alert amarelo, clicar **"Genehmigen"**
2. (Opcional) Adicionar comentários
3. Clicar **"Genehmigen"** no dialog

**Verificar:**
- ✅ Dialog de confirmação abre
- ✅ Mostra título do contrato
- ✅ Campo de comentários opcional
- ✅ Após aprovar:
  - Toast "Vertrag genehmigt"
  - Status do contrato muda para "ACTIVE"
  - Aprovação registrada na tabela
  - Alert amarelo desaparece

### Funcionalidade 13: Rejeitar Contrato

**Passo a passo:**
1. Clicar **"Ablehnen"** (botão vermelho)
2. **Obrigatório:** Informar motivo da rejeição
3. (Opcional) Adicionar comentários adicionais
4. Clicar **"Ablehnen"**

**Verificar:**
- ✅ Dialog de rejeição abre
- ✅ Campo "Motivo" obrigatório
- ✅ Botão desabilitado se motivo vazio
- ✅ Após rejeitar:
  - Toast "Vertrag abgelehnt"
  - Status do contrato muda para "DRAFT"
  - Rejeição registrada com motivo
  - Motivo aparece na coluna correspondente

### Funcionalidade 14: Permissões de Aprovação

**Testar com diferentes usuários:**

**SYSTEM_ADMIN / DIRECTOR:**
- ✅ Vê botões de aprovar/rejeitar em todos os contratos

**DEPARTMENT_ADM:**
- ✅ Vê botões apenas para contratos do seu departamento

**DEPARTMENT_USER / TEAM_LEAD:**
- ✅ Vê botões se tiver access_level >= 3

**STAFF / READ_ONLY:**
- ❌ NÃO vê botões (apenas visualiza histórico)

---

## 🎯 Funcionalidades Extras Implementadas

### Funcionalidade 15: Criar Alerta Customizado

**Navegação:** Contrato → Visualizar → Seção "Warnungen"

**Passo a passo:**
1. Clicar botão **"Benutzerdefiniert"**
2. Preencher formulário:
   - **Data de envio:** Data/hora futura
   - **E-mail destinatário:** email@valido.com
   - **Assunto:** "Lembrete importante"
   - **Mensagem customizada:** (opcional)
3. Clicar **"Erstellen"**

**Verificar:**
- ✅ Dialog abre com DateTimePicker
- ✅ Validação de e-mail
- ✅ Assunto obrigatório
- ✅ Após criar:
  - Toast de sucesso
  - Alerta aparece na lista com tipo "BENUTZERDEFINIERT"
  - Scheduled_for = data escolhida
  - Recipient = e-mail informado

### Funcionalidade 16: Alertas na Visualização de Contrato

**Navegação:** Contrato → Visualizar → Seção "Warnungen / Alertas"

**Verificar:**
1. ✅ Tabela compacta com alertas do contrato
2. ✅ Mostra: Tipo, Data, Status, Criado em
3. ✅ Contador: "(X alertas)"
4. ✅ Botão "Benutzerdefiniert" disponível

---

## 📝 Checklist Final de Testes

### Backend Endpoints (via /docs)

**Alertas:**
- [ ] GET /api/alerts - Lista alertas
- [ ] POST /api/alerts - Cria alerta
- [ ] POST /api/alerts/process-all - Processa alertas
- [ ] POST /api/alerts/{id}/reprocess - Reprocessa alerta falhado
- [ ] PUT /api/alerts/{id}/read - Marca como lido

**Rent Steps:**
- [ ] GET /api/contracts/{id}/rent-steps - Lista rent steps
- [ ] POST /api/contracts/{id}/rent-steps - Cria rent step
- [ ] PUT /api/contracts/{id}/rent-steps/{step_id} - Edita
- [ ] DELETE /api/contracts/{id}/rent-steps/{step_id} - Deleta

**Aprovações:**
- [ ] GET /api/contracts/{id}/approvals - Lista aprovações
- [ ] POST /api/contracts/{id}/approve - Aprova contrato
- [ ] POST /api/contracts/{id}/reject - Rejeita contrato

### Frontend Components

**Alertas:**
- [ ] AlertsPage renderiza corretamente
- [ ] AlertFilters funciona
- [ ] AlertsList exibe dados
- [ ] AlertBadge mostra contagem e atualiza
- [ ] ContractAlerts integrado na visualização
- [ ] CustomAlertForm cria alertas

**Rent Steps:**
- [ ] RentStepsList exibe tabela
- [ ] RentStepForm cria/edita
- [ ] Cálculo de % de aumento correto
- [ ] Próximo aumento destacado
- [ ] Status (Ativo/Planejado) correto
- [ ] Integração em ContractView e ContractEdit

**Aprovações:**
- [ ] ContractApprovals exibe histórico
- [ ] ApprovalActions com botões
- [ ] Dialog de aprovação funciona
- [ ] Dialog de rejeição valida motivo
- [ ] Permissões respeitadas
- [ ] Status do contrato atualiza

### Integrações

- [ ] ContractView mostra 3 seções: Alertas + Rent Steps + Aprovações
- [ ] ContractEdit mostra Rent Steps
- [ ] Alertas badge no menu atualiza em tempo real
- [ ] Todas as notificações (toasts) aparecem corretamente
- [ ] Sem erros no console do navegador
- [ ] Sem erros no terminal do backend

---

## 🐛 Troubleshooting

### Problema: "Alertas não aparecem"
**Solução:**
1. Verificar se backend tem contratos com end_date
2. Executar processamento manual
3. Verificar logs do backend

### Problema: "Botão de aprovar não aparece"
**Solução:**
1. Verificar role do usuário logado
2. Confirmar que contrato está PENDING_APPROVAL
3. Verificar permissões no backend

### Problema: "Rent steps não salvam"
**Solução:**
1. Verificar se usuário é Manager ou Admin
2. Verificar validação: data e valor obrigatórios
3. Checar console para erros de API

### Problema: "Badge não atualiza"
**Solução:**
1. Aguardar 30 segundos (intervalo de polling)
2. Verificar endpoint /api/alerts retorna dados
3. Checar console para erros

---

## ✅ Critérios de Sucesso

**Alertas:**
- ✅ Visualização, criação, processamento manual
- ✅ Reprocessar falhados
- ✅ Badge atualiza automaticamente
- ✅ Alertas customizados com destinatário

**Rent Steps:**
- ✅ CRUD completo
- ✅ Cálculo automático de aumento
- ✅ Status visual (Ativo/Planejado)
- ✅ Próximo aumento destacado
- ✅ Moedas suportadas: EUR, USD, GBP, CHF, BRL

**Aprovações:**
- ✅ Histórico completo
- ✅ Aprovar com comentários
- ✅ Rejeitar com motivo obrigatório
- ✅ Permissões por role
- ✅ Status do contrato atualiza

**Qualidade:**
- ✅ Sem erros no console
- ✅ Validações funcionando
- ✅ Mensagens em PT/DE
- ✅ Loading states visíveis
- ✅ Toast notifications claras

---

## 📊 Estatísticas da Implementação

**Arquivos Criados:** 11
- rentStepsApi.js
- RentStepForm.jsx
- RentStepsList.jsx
- approvalsApi.js
- ApprovalActions.jsx
- ContractApprovals.jsx
- CustomAlertForm.jsx
- (4 arquivos do Sprint 4 de alertas)

**Arquivos Atualizados:** 8
- constants.js
- alertsApi.js
- AlertsList.jsx
- ContractAlerts.jsx
- ContractView.jsx
- ContractEdit.jsx
- (2 arquivos da Sprint 4)

**Total de Linhas:** ~2.500+

**Funcionalidades:** 16

**Sem erros TypeScript/ESLint:** ✅

---

## 🎓 Próximos Passos

Após validar todas essas funcionalidades, você pode:

1. **Criar contratos de teste** com diferentes end_dates
2. **Testar permissões** com diferentes roles de usuários
3. **Simular alertas falhados** (desativar SMTP) para testar reprocessamento
4. **Criar rent steps complexos** para testar cálculos
5. **Workflow de aprovação completo** do início ao fim

**Dúvidas ou problemas?** Verifique logs do backend e console do navegador!
