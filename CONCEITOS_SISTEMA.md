# 📚 CONCEITOS DO SISTEMA - Esclarecimento

## ⚠️ LEIA ISTO PARA ENTENDER O SISTEMA!

---

## 1️⃣ ALERTAS vs APROVAÇÕES - A Grande Confusão

### 🔔 ALERTAS (Alerts/Warnungen)

**O que são?**
- São **notificações sobre vencimentos de contratos**
- São **lembretes automáticos** enviados em datas específicas

**Quando são criados?**
O sistema cria automaticamente 4 tipos de alertas:
- **T-60**: 60 dias antes do vencimento
- **T-30**: 30 dias antes do vencimento
- **T-10**: 10 dias antes do vencimento
- **T-1**: 1 dia antes do vencimento
- **BENUTZERDEFINIERT**: Alertas customizados que VOCÊ cria manualmente

**Onde visualizar?**
- **Página Global:** `/app/alerts` → Mostra TODOS os alertas de TODOS os contratos
- **Página Individual:** Dentro de cada contrato → Mostra apenas alertas daquele contrato

**Por que NÃO aparecem ao criar novo contrato?**
- Porque alertas precisam do `contract_id` (ID do contrato)
- O contrato precisa estar **SALVO** no banco de dados primeiro
- Por isso há um aviso azul na criação: _"Alertas e Rent Steps só podem ser adicionados após salvar o contrato"_

**Posso criar alertas manualmente?**
- Sim! Os **alertas customizados** (BENUTZERDEFINIERT)
- Mas **APENAS** depois de salvar o contrato
- Vá em: Contrato → Ver → Seção "Warnungen" → Botão "Benutzerdefiniert"

---

### ✅ APROVAÇÕES (Approvals/Genehmigungen)

**O que são?**
- São **pedidos de aprovação** para criar ou editar contratos
- São parte do **workflow de aprovação**

**Quando são criados?**
- Automaticamente pelo sistema quando:
  - Alguém cria um novo contrato
  - Alguém edita um contrato existente
- Depende das regras de aprovação configuradas no sistema

**São formulários para preencher?**
- **NÃO!** 
- Aprovações **não são campos** em formulários
- São **registros gerados automaticamente** pelo sistema
- Você **não preenche** aprovações, você **aprova ou rejeita** elas

**Onde visualizar?**
- **Página Global:** `/app/approvals` → Lista TODAS as aprovações pendentes de TODOS os contratos
- **Página Individual:** Dentro de cada contrato → Histórico de aprovações daquele contrato específico

**Como funciona o fluxo?**
1. Usuário cria/edita um contrato
2. Sistema **gera automaticamente** um registro de aprovação
3. Status do contrato fica "PENDING_APPROVAL"
4. Manager/Admin vê na página `/app/approvals`
5. Manager/Admin clica em "Aprovar" ou "Rejeitar"
6. Se aprovado: contrato fica "ACTIVE"
7. Se rejeitado: contrato volta para "DRAFT"

**Por que NÃO aparecem campos de aprovação ao criar contrato?**
- Porque aprovações **não são campos de formulário**
- Elas são **ações posteriores** à criação
- O fluxo é: Criar → Sistema gera aprovação → Manager aprova/rejeita

---

## 2️⃣ COMPARAÇÃO LADO A LADO

| Aspecto | 🔔 ALERTAS | ✅ APROVAÇÕES |
|---------|-----------|---------------|
| **Finalidade** | Lembrar vencimentos | Aprovar criação/edição |
| **Quando surgem?** | Automaticamente em T-60, T-30, T-10, T-1 | Quando alguém cria/edita contrato |
| **São criados manualmente?** | Sim (alertas customizados) | Não (sempre automático) |
| **Página global** | `/app/alerts` | `/app/approvals` |
| **Aparecem no contrato?** | Sim (seção "Warnungen") | Sim (seção "Genehmigungen") |
| **Podem existir antes de salvar?** | NÃO (precisam de contract_id) | NÃO (precisam de contrato salvo) |
| **São formulários?** | Sim (custom alert form) | NÃO (workflow) |
| **Usuário preenche?** | Sim (data, email, mensagem) | NÃO (sistema gera) |
| **Usuário aprova/rejeita?** | NÃO | SIM |

---

## 3️⃣ PERGUNTAS E RESPOSTAS

### ❓ "Por que não consigo adicionar alertas ao criar novo contrato?"

**Resposta:** Porque o contrato ainda não foi salvo e não tem um ID. Alertas precisam do `contract_id` para saber a qual contrato pertencem.

**Solução:**
1. Crie e **salve** o contrato primeiro
2. Depois vá em "Ver contrato"
3. Encontre a seção "Warnungen / Alertas"
4. Lá você pode criar alertas customizados

---

### ❓ "Cadê os campos de aprovação ao criar contrato?"

**Resposta:** Aprovações **não são campos de formulário**! Elas são geradas automaticamente pelo sistema depois que você salva o contrato.

**Como funciona:**
- Você cria o contrato normalmente
- Ao salvar, o sistema **gera automaticamente** um pedido de aprovação
- Um manager/admin vê esse pedido em `/app/approvals`
- Ele aprova ou rejeita

---

### ❓ "Entrei em /app/alerts mas não vejo aprovações pendentes!"

**Resposta:** Porque `/app/alerts` mostra **ALERTAS** (vencimentos), não **APROVAÇÕES**!

**Páginas corretas:**
- **Alertas:** `/app/alerts`
- **Aprovações:** `/app/approvals` ← Aqui ficam as aprovações!

---

### ❓ "Como faço para aprovar um contrato então?"

**Resposta:** Tem 3 formas:

**Forma 1 - Página Global:**
1. Vá em `/app/approvals`
2. Veja a lista de todas as aprovações pendentes
3. Clique em "Aprovar" (verde) ou "Rejeitar" (vermelho)

**Forma 2 - Dentro do Contrato:**
1. Abra o contrato específico
2. Se ele estiver "PENDING_APPROVAL", verá um alerta amarelo no topo
3. Clique em "Genehmigen" ou "Ablehnen" nesse alerta

**Forma 3 - Histórico do Contrato:**
1. Dentro do contrato, vá até a seção "Genehmigungen / Aprovações"
2. Veja o histórico completo
3. Aprove/rejeite pendentes

---

### ❓ "Qual a diferença entre a seção de alertas dentro do contrato e a página /app/alerts?"

**Resposta:**

**Seção dentro do contrato:**
- Mostra APENAS os alertas **daquele contrato específico**
- Use quando quiser ver/gerenciar alertas de um contrato que você já abriu

**Página /app/alerts:**
- Mostra **TODOS os alertas de TODOS os contratos**
- Use quando quiser uma visão geral de todos os vencimentos próximos

**Analogia:**
- Seção no contrato = Ver emails de uma pessoa específica
- Página global = Ver TODOS os emails da caixa de entrada

---

## 4️⃣ FLUXOS COMPLETOS

### 🔄 Fluxo de Criação de Contrato com Aprovações

```
1. Usuário cria contrato
   ↓
2. Preenche formulário (título, valor, datas, etc)
   ↓
3. Clica "Salvar"
   ↓
4. Sistema salva contrato no banco
   ↓
5. Sistema GERA AUTOMATICAMENTE registro de aprovação
   ↓
6. Contrato fica com status "PENDING_APPROVAL"
   ↓
7. Manager entra em /app/approvals
   ↓
8. Vê o contrato pendente na lista
   ↓
9. Clica "Aprovar" ou "Rejeitar"
   ↓
10. Se aprovado: Status → ACTIVE
    Se rejeitado: Status → DRAFT
```

### 🔄 Fluxo de Alertas de Vencimento

```
1. Contrato salvo com end_date = 01/06/2025
   ↓
2. Sistema agenda automaticamente:
   - Alerta T-60: 01/04/2025
   - Alerta T-30: 01/05/2025
   - Alerta T-10: 21/05/2025
   - Alerta T-1: 31/05/2025
   ↓
3. Quando chega a data, sistema envia email
   ↓
4. Alerta muda de PENDING → SENT ou FAILED
   ↓
5. Você vê em /app/alerts ou dentro do contrato
```

### 🔄 Fluxo de Alerta Customizado

```
1. Contrato JÁ SALVO (tem contract_id)
   ↓
2. Abre visualização do contrato
   ↓
3. Vai na seção "Warnungen / Alertas"
   ↓
4. Clica "Benutzerdefiniert"
   ↓
5. Preenche:
   - Data/hora de envio
   - Email destinatário
   - Assunto
   - Mensagem (opcional)
   ↓
6. Clica "Erstellen"
   ↓
7. Sistema salva alerta customizado
   ↓
8. Na data escolhida, envia o email
```

---

## 5️⃣ ESTRUTURA DAS PÁGINAS

```
/app
├── /dashboard          → Visão geral, estatísticas
├── /alerts            → TODOS os alertas de vencimento
├── /approvals         → TODAS as aprovações pendentes ⭐
├── /contracts
│   ├── /new           → Criar novo contrato
│   ├── /:id           → Ver contrato específico
│   │   ├── Seção "Warnungen"      → Alertas daquele contrato
│   │   ├── Seção "Genehmigungen"  → Aprovações daquele contrato
│   │   └── Seção "Rent Steps"     → Aumentos daquele contrato
│   └── /:id/edit      → Editar contrato
└── /users             → Gerenciar usuários
```

---

## 6️⃣ RESUMO PARA NUNCA MAIS ESQUECER

### 🎯 Sobre ALERTAS
- ✅ São lembretes de vencimento
- ✅ Alguns automáticos (T-60, T-30, T-10, T-1)
- ✅ Alguns manuais (customizados)
- ❌ NÃO podem ser criados antes de salvar contrato
- 📍 Ver em: `/app/alerts` (todos) ou dentro do contrato (específicos)

### 🎯 Sobre APROVAÇÕES
- ✅ São pedidos de aprovação para criar/editar
- ✅ Sempre geradas automaticamente
- ❌ NÃO são formulários para preencher
- ❌ NÃO podem ser criadas manualmente
- 📍 Ver em: `/app/approvals` (todos) ou dentro do contrato (histórico)

### 🎯 Sobre RENT STEPS
- ✅ São aumentos progressivos do aluguel
- ✅ Podem ser manuais ou com percentual
- ✅ Precisam de contrato salvo (têm contract_id)
- 📍 Ver em: Dentro do contrato, seção "Rent Steps"

---

## ✅ Checklist de Compreensão

Marque ✅ quando entender completamente:

- [ ] Sei a diferença entre Alertas e Aprovações
- [ ] Entendi que aprovações não são formulários
- [ ] Sei que alertas precisam de contrato salvo
- [ ] Sei onde encontrar aprovações pendentes (/app/approvals)
- [ ] Sei que /app/alerts mostra vencimentos, não aprovações
- [ ] Entendi o fluxo de aprovação (criar → sistema gera → aprovar)
- [ ] Sei criar alertas customizados (depois de salvar contrato)
- [ ] Entendi que o sistema gera T-60, T-30, T-10, T-1 automaticamente

---

**🎓 Se chegou até aqui e marcou todos os itens, você está pronto para usar o sistema!**
