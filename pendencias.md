# ⚠️ Pendências da Sprint 3 - CRUD de Contratos
# Sprint 3 Pending Tasks - Contract CRUD

**Data de Análise / Analysis Date:** 15 de janeiro de 2026  
**Versão / Version:** 1.0

---

## 📊 Status Geral / General Status

✅ **Sprint 3 - IMPLEMENTADA COM SUCESSO / SUCCESSFULLY IMPLEMENTED**

A Sprint 3 foi concluída com todas as funcionalidades principais implementadas. No entanto, há **pequenos ajustes e integrações** que precisam ser feitos para garantir o funcionamento completo end-to-end.

---

## ✅ O que está Funcionando / What is Working

### 1. **Frontend CRUD Completo / Complete Frontend CRUD**
- ✅ ContractsList com paginação, filtros, ordenação
- ✅ ContractCreate com formulário completo
- ✅ ContractEdit com carregamento de dados existentes
- ✅ ContractView com detalhes completos
- ✅ ContractDelete com confirmação
- ✅ Validação Zod em todos os campos
- ✅ Toast notifications (notistack)
- ✅ Loading states em todas operações
- ✅ Permissões por role (esconde/mostra botões)

### 2. **Componentes Implementados / Implemented Components**
- ✅ ContractTable (DataGrid com 310 linhas)
- ✅ ContractForm (React Hook Form + Zod - 885 linhas)
- ✅ ContractFilters (Filtros por status/tipo/busca - 90 linhas)
- ✅ ContractDetail (Visualização detalhada - 330 linhas)
- ✅ ConfirmDialog (Diálogo de confirmação - 60 linhas)

### 3. **Campos Implementados / Implemented Fields**
- ✅ title, client_name, company_name, legal_form
- ✅ contract_type, status
- ✅ start_date, end_date, renewal_date
- ✅ value, currency
- ✅ description, notes, terms_and_conditions
- ✅ client_document, client_email, client_phone, client_address
- ✅ department, team, responsible_user_id
- ✅ **payment_frequency** ✅ IMPLEMENTADO
- ✅ **payment_custom_years** ✅ IMPLEMENTADO
- ✅ **pdfFile** (upload de PDF) ✅ IMPLEMENTADO NO FRONTEND

---

## 🔧 Pendências Identificadas / Identified Pending Tasks

### 1. **Upload de PDF - Integração Backend / PDF Upload - Backend Integration**

#### Status Atual / Current Status (ATUALIZADO 19/01/2026)
- ✅ **Frontend:** Campo de upload de PDF implementado no ContractForm
- ✅ **Frontend:** Validação de tipo de arquivo (apenas PDF)
- ✅ **Frontend:** Exibição do nome e tamanho do arquivo selecionado
- ⚠️ **Backend:** Endpoints de upload EXISTEM mas NÃO estão integrados diretamente no POST/PUT de contracts
  - ✅ `/contracts/import/upload` - upload com extração (funcionando)
  - ✅ `/contracts/{id}/upload-pdf` - upload separado (funcionando)
  - ❌ `POST /contracts/` - NÃO aceita multipart/form-data (apenas JSON)
  - ❌ `PUT /contracts/{id}` - NÃO aceita multipart/form-data (apenas JSON)

#### O que precisa ser feito / What needs to be done

**Backend (`backend/app/routers/contracts.py`):**

1. **Modificar `POST /api/contracts/`** para aceitar `multipart/form-data`:
   ```python
   @router.post("/", response_model=ContractOut)
   async def create_contract(
       db: AsyncSession = Depends(get_db),
       current_user: User = Depends(get_current_user),
       title: str = Form(...),
       client_name: str = Form(...),
       contract_type: str = Form(...),
       status: str = Form(...),
       start_date: date = Form(...),
       # ... outros campos ...
       pdf_file: UploadFile = File(...)  # ⚠️ ADICIONAR
   ):
       # Salvar PDF usando contract_service.save_contract_pdf()
       # Upload PDF using contract_service.save_contract_pdf()
   ```

2. **Modificar `PUT /api/contracts/{contract_id}`** para aceitar PDF opcional:
   ```python
   @router.put("/{contract_id}", response_model=ContractOut)
   async def update_contract(
       contract_id: int,
       db: AsyncSession = Depends(get_db),
       current_user: User = Depends(get_current_user),
       # ... campos ...
       pdf_file: UploadFile = File(None)  # ⚠️ ADICIONAR (opcional)
   ):
       # Se pdf_file existe, substituir PDF antigo
       # If pdf_file exists, replace old PDF
   ```

**Frontend (`frontend/src/services/contractsApi.js`):**

3. **Modificar `createContract()` para enviar FormData**:
   ```javascript
   createContract: async (data) => {
     const formData = new FormData();
     // Adicionar todos os campos como FormData
     // Add all fields as FormData
     Object.keys(data).forEach(key => {
       if (data[key] !== null && key !== 'pdfFile') {
         formData.append(key, data[key]);
       }
     });
     
     // Adicionar PDF
     if (data.pdfFile) {
       formData.append('pdf_file', data.pdfFile);
     }
     
     const response = await api.post('/contracts/', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     });
     return response.data;
   }
   ```

4. **Modificar `updateContract()` para enviar FormData (se PDF alterado)**:
   ```javascript
   updateContract: async (id, data) => {
     // Se pdfFile existe, usar FormData, senão usar JSON
     // If pdfFile exists, use FormData, otherwise use JSON
     if (data.pdfFile) {
       const formData = new FormData();
       // ... adicionar campos ...
       formData.append('pdf_file', data.pdfFile);
       
       const response = await api.put(`/contracts/${id}`, formData, {
         headers: { 'Content-Type': 'multipart/form-data' }
       });
       return response.data;
     } else {
       // JSON normal como está atualmente
       const response = await api.put(`/contracts/${id}`, data);
       return response.data;
     }
   }
   ```

#### Testes Necessários / Required Tests

1. ✅ **Criar contrato COM upload de PDF:**
   - Selecionar arquivo PDF
   - Preencher formulário
   - Enviar
   - ❌ **PROBLEMA REPORTADO:** "Estou conseguindo fazendo o download do pdf mas não está salvando, a opção de salvar fica indisponível"
   - **VERIFICAR:** Se backend está salvando PDF em `uploads/contracts/persisted/{contract_id}/`
   - **VERIFICAR:** Se campo `pdf_path` no banco está sendo preenchido

2. ✅ **Criar contrato SEM upload de PDF (apenas se opcional):**
   - Verificar se backend aceita null
   - OU se backend rejeita com erro claro

3. ✅ **Editar contrato e SUBSTITUIR PDF:**
   - Carregar contrato existente
   - Fazer upload de novo PDF
   - Verificar se PDF antigo é substituído

4. ✅ **Download de PDF existente:**
   - Visualizar contrato com PDF
   - Clicar em botão de download
   - ❌ **PROBLEMA:** "Estou conseguindo fazendo o download do pdf mas não está salvando, a opção de salvar fica indisponível"
   - **POSSÍVEL CAUSA:** Headers incorretos no backend (Content-Disposition, Content-Type)

---

### 2. **Payment Frequency - Validação e Lógica / Validation and Logic**

#### Status Atual / Current Status (ATUALIZADO 19/01/2026)
- ✅ **Frontend:** Campo `payment_frequency` implementado (select)
- ✅ **Frontend:** Campo `payment_custom_years` implementado (number input)
- ✅ **Frontend:** Lógica condicional (mostra custom_years apenas se frequency === 'CUSTOM')
- ✅ **Backend:** Campos adicionados ao modelo Contract
- ❌ **Backend:** Validação condicional de `payment_custom_years` NÃO IMPLEMENTADA
  - ❌ Não existe `@validator` ou `@model_validator` em `schemas/contract.py`
  - ⚠️ Permite salvar `payment_custom_years = null` quando frequency = 'CUSTOM_YEARS'
  - ⚠️ Permite salvar `payment_custom_years = 5` quando frequency = 'MONTHLY'

#### O que precisa ser verificado / What needs to be verified

1. **Verificar se `payment_frequency` está sendo salvo corretamente:**
   ```bash
   # No SQLite
   sqlite3 contracts.db
   SELECT id, title, payment_frequency, payment_custom_years FROM contracts LIMIT 10;
   ```

2. **Verificar se lógica condicional está funcionando:**
   - Criar contrato com `payment_frequency = 'MONTHLY'` → `payment_custom_years` deve ser `null`
   - Criar contrato com `payment_frequency = 'CUSTOM'` e `payment_custom_years = 5` → deve salvar 5

3. **Adicionar validação backend (se não existe):**
   ```python
   # backend/app/schemas/contract.py
   @validator('payment_custom_years')
   def validate_custom_years(cls, v, values):
       if values.get('payment_frequency') == 'CUSTOM' and not v:
           raise ValueError('payment_custom_years is required when payment_frequency is CUSTOM')
       if values.get('payment_frequency') != 'CUSTOM' and v:
           raise ValueError('payment_custom_years should be null when payment_frequency is not CUSTOM')
       return v
   ```

#### Testes Necessários / Required Tests

1. ✅ **Criar contrato com frequency 'MONTHLY':**
   - `payment_frequency` = 'MONTHLY'
   - `payment_custom_years` = null
   - Verificar se salva corretamente

2. ✅ **Criar contrato com frequency 'CUSTOM':**
   - `payment_frequency` = 'CUSTOM'
   - `payment_custom_years` = 5
   - Verificar se campo custom_years aparece/desaparece no frontend
   - Verificar se ambos valores são salvos

3. ✅ **Editar contrato e alterar frequency:**
   - Mudar de 'MONTHLY' para 'CUSTOM'
   - Verificar se campo custom_years aparece
   - Salvar e verificar banco

---

### 3. **Visualização e Download de PDF / PDF View and Download**

#### Problema Reportado / Reported Issue
> "Estou conseguindo fazendo o download do pdf mas não está salvando, a opção de salvar fica indisponível"

#### Diagnóstico / Diagnosis (ATUALIZADO 19/01/2026)

**Status dos Headers no Código Atual:**

✅ **Download (endpoint `/contracts/{id}/original`):**
- ✅ Headers corretos implementados:
  ```python
  headers = {
      "Content-Disposition": f'attachment; filename="{safe_filename}"',
      "Content-Type": "application/pdf"
  }
  ```
- ⚠️ Sanitização de filename simples: `re.sub(r'[^\w\s.-]', '_', filename)`
  - Pode não ser suficiente para caracteres UTF-8 (ä, ö, ü, ß)

✅ **Visualização inline (endpoint `/contracts/{id}/view`):**
- ✅ Headers corretos implementados:
  ```python
  headers = {
      "Content-Disposition": f'inline; filename="{safe_filename}"',
      "Content-Type": "application/pdf",
      "Cache-Control": "no-cache, no-store, must-revalidate",
      "Pragma": "no-cache",
      "Expires": "0"
  }
  ```

**Possíveis Causas do Problema (ainda existentes):**

1. ⚠️ **Nome do arquivo com caracteres especiais não UTF-8:**
   - Sanitização atual pode quebrar nomes alemães (Vertrag_für_Büro.pdf)
   - Solução: usar `urllib.parse.quote()` para encoding adequado

2. ⚠️ **Browser esperando `Content-Length` header:**
   - StreamingResponse pode não enviar Content-Length automaticamente
   - Solução: adicionar header manualmente

3. ⚠️ **Frontend não usando `responseType: 'blob'`:**
   - Se frontend não especifica blob, axios pode corromper binário

#### Solução / Solution

**Backend (`backend/app/routers/contracts.py`):**

Verificar endpoint `GET /api/contracts/{id}/pdf`:

```python
@router.get("/{contract_id}/pdf")
async def download_contract_pdf(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = await contract_service.get_contract(db, contract_id)
    
    if not contract.pdf_path or not os.path.exists(contract.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # IMPORTANTE: Headers corretos / IMPORTANT: Correct headers
    filename = f"contract_{contract_id}_{contract.title}.pdf"
    # Sanitizar filename / Sanitize filename
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    
    return FileResponse(
        path=contract.pdf_path,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',  # ⚠️ CRÍTICO
            'Content-Type': 'application/pdf',
            'Cache-Control': 'no-cache'
        }
    )
```

**Frontend (verificar se está correto):**

```javascript
// Exemplo de download
const downloadPdf = async (contractId) => {
  try {
    const response = await api.get(`/contracts/${contractId}/pdf`, {
      responseType: 'blob'  // ⚠️ IMPORTANTE
    });
    
    // Criar blob URL
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    
    // Criar link temporário e clicar
    const link = document.createElement('a');
    link.href = url;
    link.download = `contract_${contractId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Liberar memória
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
  }
};
```

#### Testes Necessários / Required Tests

1. ✅ **Download via botão no ContractView:**
   - Abrir contrato com PDF
   - Clicar em "Download PDF"
   - Verificar se download inicia
   - Verificar se arquivo abre corretamente

2. ✅ **Preview inline (opcional):**
   - Usar `<iframe>` ou `<object>` para exibir PDF
   - Testar em diferentes browsers

---

### 4. **Verificação de Contratos Acessíveis / Accessible Contracts Verification**

#### Problema Reportado / Reported Issue
> "Verifique se todos os 252 contratos estão acessíveis"

#### O que verificar / What to verify

1. **Paginação funcionando:**
   - Testar com page_size = 10, 25, 50, 100
   - Navegar por todas as páginas
   - Verificar se total = 252

2. **Filtros não removendo contratos:**
   - Filtro "All" deve retornar 252 contratos (em múltiplas páginas)
   - Filtros por status devem retornar subsets corretos

3. **Permissões corretas:**
   - Director (Level 5) deve ver todos 252
   - Department_Adm (Level 4) deve ver apenas do departamento
   - Staff (Level 1) deve ver apenas próprios contratos

#### Testes Necessários / Required Tests

1. ✅ **Login como Director:**
   ```javascript
   // Email: director@test.com
   // Verificar se vê 252 contratos (total em todas páginas)
   ```

2. ✅ **Login como Department_Adm:**
   ```javascript
   // Verificar se vê apenas contratos do departamento
   // Total deve ser < 252
   ```

3. ✅ **Login como Staff:**
   ```javascript
   // Verificar se vê apenas contratos onde é responsável
   // Total deve ser pequeno
   ```

4. ✅ **Testar paginação:**
   ```javascript
   // Navegar todas páginas
   // Verificar se não há duplicatas
   // Verificar se não faltam contratos
   ```

---

## 🎯 Prioridade de Resolução / Resolution Priority

### **Prior (ATUALIZADO 19/01/2026)

- [ ] **CRÍTICO:** Modificar `POST /contracts/` para aceitar `multipart/form-data` com PDF direto
  - Arquivo: `backend/app/routers/contracts.py` linha 146
  - Adicionar parâmetro `pdf_file: UploadFile = File(None)`
- [ ] **CRÍTICO:** Modificar `PUT /contracts/{id}` para aceitar `multipart/form-data` (opcional)
  - Arquivo: `backend/app/routers/contracts.py` linha 365
  - Adicionar parâmetro `pdf_file: UploadFile = File(None)`
- [ ] **ALTA:** Adicionar validação de `payment_custom_years` condicional
  - Arquivo: `backend/app/schemas/contract.py`
  - Adicionar `@model_validator(mode='after')` em `ContractBase`
  - Regra: `frequency == 'CUSTOM_YEARS'` → `payment_custom_years` obrigatório
  - Regra: `frequency != 'CUSTOM_YEARS'` → `payment_custom_years` deve ser `null`
- [x] ~~Corrigir headers de download de PDF~~ **JÁ IMPLEMENTADO** ✅
  - Headers corretos já existem em `/contracts/{id}/original` e `/contracts/{id}/view`
- [ ] **MÉDIA:** Melhorar sanitização de filename para UTF-8 (caracteres alemães)
  - Arquivo: `backend/app/routers/contracts.py` linha 471
  - Usar `urllib.parse.quote()` ao invés de `re.sub()`
- [ ] **BAIXA:** Adicionar `Content-Length` header em StreamingResponse
- [ ] Testar endpoint de upload com Postman/Thunder Client

### Frontend (ATUALIZADO 19/01/2026)

- [ ] **CRÍTICO:** Modificar `contractsApi.createContract()` para enviar `FormData` quando tem PDF
  - Arquivo: `frontend/src/services/contractsApi.js` linha 89
  - Atualmente: faz upload separado + create JSON (workaround funcional mas indireto)
  - Objetivo: enviar FormData diretamente para `POST /contracts/`
- [ ] **CRÍTICO:** Modificar `contractsApi.updateContract()` para enviar `FormData` se PDF alterado
  - Arquivo: `frontend/src/services/contractsApi.js` linha 132
  - Atualmente: faz 2 requisições separadas (upload-pdf + put JSON)
  - Objetivo: enviar FormData diretamente para `PUT /contracts/{id}`
- [ ] **ALTA:** Verificar se download usa `responseType: 'blob'`
  - Arquivo: verificar componente que faz download de PDF
  - Garantir: `api.get('/contracts/{id}/original', { responseType: 'blob' })`
- [ ] Testar criação de contrato com PDF
- [ ] Testar edição de contrato com novo PDF
- [ ] Testar download de PDF em diferentes browsers
- [ ] Verificar se todos 252 contratos são acessíveis (paginação)

### Testes End-to-End (ATUALIZADO 19/01/2026)

- [ ] **T1:** Criar contrato SEM PDF → Verificar se cria normalmente
- [ ] **T2:** Criar contrato COM PDF (via FormData direto) → Verificar se salva no banco e em `uploads/contracts/persisted/contract_{id}/original.pdf`
- [ ] **T3:** Criar contrato COM PDF (via workaround atual) → Confirmar se continua funcionando (retrocompatibilidade)
- [ ] **T4:** Editar contrato e substituir PDF → Verificar se PDF antigo é deletado/sobrescrito
- [ ] **T5:** Download de PDF → Verificar se arquivo abre corretamente em Chrome/Firefox/Edge
- [ ] **T6:** Download de PDF com nome alemão (ä,ö,ü,ß) → Verificar encoding correto
- [ ] **T7:** Payment Frequency 'CUSTOM_YEARS' COM `payment_custom_years = null` → Backend deve rejeitar
- [ ] **T8:** Payment Frequency 'CUSTOM_YEARS' COM `payment_custom_years = 5` → Backend deve aceitar
- [ ] **T9:** Payment Frequency 'MONTHLY' COM `payment_custom_years = 5` → Backend deve rejeitar
- [ ] **T10:** Payment Frequency 'MONTHLY' COM `payment_custom_years = null` → Backend deve aceitar
- [ ] **T11:** Navegar todas páginas de contratos (252 total) → Verificar duplicatas/faltantes
---

## ⚠️ PROBLEMAS CRÍTICOS SEM SOLUÇÃO IMPLEMENTADA (19/01/2026)

> **ATENÇÃO:** Os problemas abaixo foram identificados pelo usuário e **NÃO tiveram êxito na implementação anterior**. Requerem análise detalhada do código e implementação cuidadosa para não quebrar funcionalidades existentes.

### PROBLEMA 1: Upload/Salvamento de PDF não persiste corretamente

#### Relato do Usuário
> "Consigo fazer o download do PDF, mas o documento não está sendo salvo"

#### Análise Técnica (19/01/2026)
**Status:** ❌ **NÃO RESOLVIDO**

**Causa Raiz Confirmada:**
- ✅ Backend TEM endpoints de upload: `/contracts/import/upload` e `/contracts/{id}/upload-pdf`
- ❌ `POST /contracts/` **NÃO** aceita multipart/form-data diretamente
- ❌ `PUT /contracts/{id}` **NÃO** aceita multipart/form-data diretamente
- ⚠️ Frontend usa **workaround indireto**: upload separado + create JSON
- ⚠️ Metadados são passados via `extraction_metadata` mas o fluxo é confuso

**Comportamento Atual:**
```javascript
// Frontend (contractsApi.js linha 89-126)
createContract: async (data) => {
  if (data.pdfFile) {
    // 1. Upload para extrair dados
    const uploadResponse = await api.post('/contracts/import/upload', formData);
    // 2. Create com JSON (não FormData!)
    const contractData = { ...extractedData, ...data };
    const response = await api.post('/contracts', contractData);
  }
}
```

**Por que falha:**
1. PDF é salvo em `temp/` durante `/import/upload`
2. Create recebe `extraction_metadata.temp_file_path`
3. Backend TENTA mover `temp/` → `persisted/` mas pode falhar silenciosamente
4. Se falhar, PDF fica em `temp/` e DB aponta para caminho errado

**Solução Necessária:**
- [ ] Modificar `POST /contracts/` para aceitar FormData:
  ```python
  @router.post("/", response_model=ContractResponse)
  async def create_contract(
      title: str = Form(...),
      client_name: str = Form(...),
      # ... todos os campos como Form(...)
      pdf_file: UploadFile = File(None),  # Opcional
      db: AsyncSession = Depends(get_db)
  ):
  ```
- [ ] Modificar `PUT /contracts/{id}` para aceitar FormData opcional
- [ ] Adicionar logs detalhados na movimentação de arquivos
- [ ] Adicionar tratamento de erro se arquivo não pode ser movido

---

### PROBLEMA 2: Download de PDF - Headers e Compatibilidade

#### Relato do Usuário
> "Download não funciona corretamente" (botão de salvar indisponível)

#### Análise Técnica (19/01/2026)
**Status:** ⚠️ **PARCIALMENTE RESOLVIDO**

**O que está CORRETO:**
- ✅ Headers `Content-Disposition` e `Content-Type` estão implementados
- ✅ Endpoint `/contracts/{id}/original` existe e funciona
- ✅ Endpoint `/contracts/{id}/view` existe para visualização inline

**O que está INCORRETO/INCOMPLETO:**
- ⚠️ Sanitização de filename inadequada para caracteres UTF-8:
  ```python
  # Atual (contracts.py linha 471)
  safe_filename = re.sub(r'[^\w\s.-]', '_', filename)
  ```
  - Problema: Remove caracteres alemães (ä → _, ö → _, ü → _, ß → _)
  - Resultado: "Vertrag_für_Büro.pdf" vira "Vertrag_f_r_B_ro.pdf"

- ❌ Frontend pode NÃO estar usando `responseType: 'blob'`
  - Se axios não recebe blob, pode corromper binário

**Solução Necessária:**
- [ ] Melhorar sanitização de filename:
  ```python
  from urllib.parse import quote
  # Encoding adequado para RFC 5987
  safe_filename = quote(filename.encode('utf-8'))
  headers = {
      "Content-Disposition": f'attachment; filename*=UTF-8\'\'{safe_filename}'
  }
  ```
- [ ] Garantir que frontend usa `responseType: 'blob'`
- [ ] Adicionar `Content-Length` header
- [ ] Testar em Chrome, Firefox, Edge, Safari

---

### PROBLEMA 3: Validação de payment_custom_years (Lógica Condicional)

#### Relato do Usuário
> Validar payment_custom_years de forma condicional baseado em frequency

#### Análise Técnica (19/01/2026)
**Status:** ❌ **NÃO IMPLEMENTADO**

**Regra de Negócio:**
- Se `payment_frequency == 'CUSTOM_YEARS'` → `payment_custom_years` **OBRIGATÓRIO** (≥ 1)
- Se `payment_frequency != 'CUSTOM_YEARS'` → `payment_custom_years` **DEVE SER NULL**

**Problema Atual:**
- ❌ Nenhum `@validator` ou `@model_validator` implementado em `schemas/contract.py`
- ⚠️ Sistema aceita dados inconsistentes:
  - Aceita: `frequency='MONTHLY'` com `custom_years=5` ❌
  - Aceita: `frequency='CUSTOM_YEARS'` com `custom_years=null` ❌

**Código Atual (schemas/contract.py linha 93):**
```python
payment_frequency: Optional[PaymentFrequency] = Field(None, ...)
payment_custom_years: Optional[int] = Field(None, ge=1, le=100, ...)
# ❌ Sem validação condicional!
```

**Solução Necessária:**
- [ ] Adicionar validador em `ContractBase`:
  ```python
  @model_validator(mode='after')
  def validate_payment_frequency_logic(self) -> 'ContractBase':
      if self.payment_frequency == PaymentFrequency.CUSTOM_YEARS:
          if not self.payment_custom_years:
              raise ValueError(
                  'payment_custom_years é obrigatório quando '
                  'payment_frequency é CUSTOM_YEARS'
              )
      else:
          if self.payment_custom_years is not None:
              raise ValueError(
                  'payment_custom_years deve ser null quando '
                  'payment_frequency não é CUSTOM_YEARS'
              )
      return self
  ```
- [ ] Adicionar mesmo validador em `ContractUpdate`
- [ ] Adicionar testes unitários para todos os cenários
- [ ] Atualizar frontend para limpar `payment_custom_years` ao mudar frequency

---

### PROBLEMA 4: Frontend envia JSON ao invés de FormData

#### Relato do Usuário
> create/update ainda envia JSON ao invés de FormData, então o backend nunca recebe o arquivo corretamente

#### Análise Técnica (19/01/2026)
**Status:** ❌ **NÃO RESOLVIDO**

**Comportamento Atual Confirmado:**

**CreateContract (contractsApi.js linha 89-126):**
```javascript
createContract: async (data) => {
  if (data.pdfFile) {
    // 1. Upload separado (FormData) ✅
    const formData = new FormData();
    formData.append('file', data.pdfFile);
    const uploadResponse = await api.post('/contracts/import/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    // 2. Create com JSON (não FormData!) ❌
    const contractData = { ...extractedData, ...data, pdfFile: undefined };
    const response = await api.post('/contracts', contractData);  // ❌ JSON
    return response.data;
  }
}
```

**UpdateContract (contractsApi.js linha 132-158):**
```javascript
updateContract: async (id, data) => {
  if (data.pdfFile) {
    // 1. Upload separado ✅
    await api.post(`/contracts/${id}/upload-pdf`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
  
  // 2. Update com JSON (não FormData!) ❌
  const { pdfFile, ...contractData } = data;
  const response = await api.put(`/contracts/${id}`, contractData);  // ❌ JSON
  return response.data;
}
```

**Por que isso é um problema:**
- ⚠️ 2 requisições ao invés de 1 (ineficiente)
- ⚠️ Se primeira requisição sucede mas segunda falha, fica inconsistente
- ⚠️ Backend nunca recebe PDF diretamente no create/update
- ⚠️ Complexidade desnecessária (gerenciamento de `extraction_metadata`)

**Solução Necessária:**
1. **Backend:** Implementar suporte FormData (ver PROBLEMA 1)
2. **Frontend:** Refatorar para enviar FormData unificado:
   ```javascript
   createContract: async (data) => {
     const formData = new FormData();
     
     // Adicionar todos os campos
     Object.keys(data).forEach(key => {
       if (key !== 'pdfFile' && data[key] !== null && data[key] !== undefined) {
         formData.append(key, data[key]);
       }
     });
     
     // Adicionar PDF se existe
     if (data.pdfFile) {
       formData.append('pdf_file', data.pdfFile);
     }
     
     // Uma única requisição!
     const response = await api.post('/contracts/', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     });
     return response.data;
   }
   ```

---

### PROBLEMA 5: Paginação e Acesso aos 252 Contratos

#### Relato do Usuário
> Verificar se todos os 252 contratos são acessíveis via paginação, sem duplicatas/faltantes

#### Análise Técnica (19/01/2026)
**Status:** ⚠️ **PRECISA VERIFICAÇÃO**

**Código de Paginação (contracts.py linha 117-145):**
```python
async def list_contracts(
    page: int = Query(1, ge=1, ...),
    per_page: int = Query(10, ge=1, le=100, ...),
    # ... filtros ...
):
    return await contract_service.list_contracts(
        skip=(page - 1) * per_page,
        limit=per_page,
        # ...
    )
```

**Implementação no Service (contract_service.py linha 214-281):**
- ✅ Usa `offset()` e `limit()` corretamente
- ✅ Calcula `total` com `count()` separado
- ✅ Retorna `page`, `per_page`, `total` na resposta
- ⚠️ Validação de `skip`/`limit` pode permitir valores negativos/excessivos

**Possíveis Problemas:**
1. **Filtros removendo contratos:**
   - Verificar se filtro "All" realmente não filtra nada
   - Verificar se permissões não escondem contratos indevidamente

2. **Ordenação causando duplicatas:**
   - Se `sort_by` tem valores duplicados, pode repetir registros entre páginas
   - Solução: adicionar `id` como critério secundário de ordenação

3. **Concorrência:**
   - Se contratos são criados/deletados durante paginação, pode desalinhar

**Testes Necessários:**
- [ ] Login como Director (Level 5) → Verificar `total = 252`
- [ ] Navegar TODAS as páginas (page_size=25 → 11 páginas)
- [ ] Guardar IDs de cada página, verificar se:
  - Não há duplicatas (mesmo ID em 2 páginas)
  - Não faltam IDs (todos os 252 IDs únicos aparecem)
- [ ] Testar com diferentes `sort_by` (title, start_date, created_at)
- [ ] Testar com filtros + paginação
- [ ] Testar permissões (Department_Adm, Staff) + paginação

**Solução Preventiva:**
```python
# contract_service.py - adicionar ordenação secundária por ID
query = query.order_by(
    asc(sort_column) if sort_order == "asc" else desc(sort_column),
    asc(Contract.id)  # ← Ordenação secundária para consistência
)
```

---

## 🆕 Problemas Adicionais Identificados (19/01/2026)

### 4. **Estrutura de Armazenamento de PDFs**

#### Status Atual
- ✅ **Estrutura organizada implementada:**
  ```
  uploads/contracts/
  ├── temp/                          # PDFs temporários durante upload
  └── persisted/                     # PDFs permanentes
      └── contract_{id}/             # Um diretório por contrato
          └── original.pdf           # Nome fixo
  ```
- ✅ Função `move_temp_to_persisted_contract()` implementada
- ✅ Função `get_contract_pdf_path()` implementada com fallback para estrutura antiga

#### Observações
- ✅ Sistema suporta migração de estrutura antiga (PDFs com nomes variados)
- ✅ Duplikat-Prüfung (detecção de duplicatas) via SHA256 implementada em `/contracts/import/upload`

---

### 5. **Fluxo Indireto de Upload (Workaround Atual)**

#### Problema
O fluxo atual de criação com PDF é indireto:

```javascript
// Frontend (contractsApi.js)
createContract: async (data) => {
  if (data.pdfFile) {
    // 1. Upload separado para extrair dados
    const uploadResponse = await api.post('/contracts/import/upload', formData);
    
    // 2. Criar contrato com dados extraídos (JSON)
    const contractData = { ...extractedData, ...data };
    const response = await api.post('/contracts', contractData);
  }
}
```

#### Impacto
- ✅ Funciona tecnicamente (workaround eficaz)
- ⚠️ Complexidade desnecessária (2 requisições)
- ⚠️ Dificulta manutenção e debug
- ⚠️ Frontend precisa gerenciar `extraction_metadata` manualmente

#### Solução Proposta
Implementar endpoint unificado que aceita FormData diretamente:
```python
@router.post("/", response_model=ContractResponse)
async def create_contract(
    title: str = Form(...),
    client_name: str = Form(...),
    # ... outros campos ...
    pdf_file: UploadFile = File(None),  # Opcional
    db: AsyncSession = Depends(get_db)
):
    # Processar PDF se existe
    # Criar contrato
    # Retornar ContractResponse
```

---

### 6. **Ausência de Testes Automatizados para Upload/Download**

#### Status Atual
- ✅ Testes existem em `backend/test/`:
  - `test_contract.py` - testes de CRUD
  - `test_pdf_unit.py` - testes de extração de PDF
  - `test_integration_e2e.py` - testes end-to-end
- ❌ Não há testes específicos para:
  - Upload de PDF via `POST /contracts/` com FormData
  - Download de PDF com headers corretos
  - Substituição de PDF em `PUT /contracts/{id}`
  - Validação de `payment_custom_years` condicional

#### Recomendação
Adicionar testes em `test_contract.py`:
```python
async def test_create_contract_with_pdf_multipart():
    """Testa criação de contrato com PDF via FormData"""
    # Implementar teste

async def test_download_pdf_headers():
    """Testa headers de download de PDF"""
    # Implementar teste
```

---

## ✅ Conclusão / Conclusion (ATUALIZADO 19/01/2026)

A **Sprint 3 foi implementada com sucesso** em termos de componentes frontend e estrutura de código. 

### Resumo do Status Atual:

✅ **Funcionando:**
- CRUD completo de contratos (sem PDF)
- Upload de PDF via endpoints separados (`/import/upload`, `/{id}/upload-pdf`)
- Download de PDF com headers corretos
- Estrutura de armazenamento organizada
- Workaround frontend para upload funcional

❌ **Pendente (Prioridade ALTA):**
1. Validação condicional de `payment_custom_years` no backend
2. Endpoint `POST /contracts/` aceitar multipart/form-data direto
3. Endpoint `PUT /contracts/{id}` aceitar multipart/form-data direto

⚠️ **Pendente (Prioridade MÉDIA):**
1. Melhorar sanitização de filename para UTF-8
2. Refatorar frontend para usar FormData direto
3. Adicionar testes automatizados para upload/download

📊 **Métricas:**
- 252 contratos no banco de dados
- Paginação implementada e funcionando
- Sistema de permissões implementado

**Próximos passos:**
1. **Prioridade 1:** Implementar validação de `payment_custom_years` (baixo risco)
2. **Prioridade 2:** Melhorar headers de download para UTF-8 (baixo risco)
3. **Prioridade 3:** Adicionar suporte multipart/form-data em POST/PUT (médio risco)
4. Testar todos os 252 contratos (paginação, permissões)
5. Iniciar Sprint 4 (Alertas + Notificações)

---

**Fim do Documento / End of Document**  
**Última Atualização / Last Update:** 19
- [ ] Testar edição de contrato com novo PDF
- [ ] Testar download de PDF
- [ ] Verificar se todos 252 contratos são acessíveis (paginação)

### Testes End-to-End

- [ ] Criar contrato com PDF → Verificar se salva no banco e em `uploads/contracts/persisted/`
- [ ] Editar contrato e substituir PDF → Verificar se PDF antigo é deletado
- [ ] Download de PDF → Verificar se arquivo abre corretamente
- [ ] Payment Frequency 'CUSTOM' → Verificar se `payment_custom_years` é obrigatório
- [ ] Payment Frequency 'MONTHLY' → Verificar se `payment_custom_years` é null
- [ ] Navegar todas páginas de contratos (252 total) → Verificar duplicatas/faltantes

---

## ✅ Conclusão / Conclusion

A **Sprint 3 foi implementada com sucesso** em termos de componentes frontend e estrutura de código. As pendências identificadas são **pequenos ajustes de integração** entre frontend e backend, principalmente relacionados ao upload de PDF.

**Próximos passos:**
1. Resolver pendências da Sprint 3 (upload PDF, download PDF)
2. Iniciar Sprint 4 (Alertas + Notificações)
3. Continuar com Sprints 5-9 conforme planejado

---
## 📋 PLANO DE IMPLEMENTAÇÃO RECOMENDADO (19/01/2026)

> **Estratégia:** Resolver problemas em ordem crescente de risco e complexidade, garantindo que cada etapa seja testada antes de prosseguir. Priorizar correções que não quebram funcionalidades existentes.

---

### 🎯 FASE 1: CORREÇÕES DE BAIXO RISCO (Estimativa: 4-6 horas)

**Objetivo:** Resolver problemas isolados que não afetam o fluxo principal

#### **TAREFA 1.1: Validação Condicional de payment_custom_years** ⭐ PRIORIDADE MÁXIMA
**Arquivo:** `backend/app/schemas/contract.py`  
**Tempo:** 1 hora  
**Risco:** 🟢 BAIXO (apenas adiciona validação)

**Implementação:**
```python
# Adicionar após a classe ContractBase (linha ~108)
from pydantic import model_validator

class ContractBase(BaseModel):
    # ... campos existentes ...
    
    @model_validator(mode='after')
    def validate_payment_frequency_logic(self) -> 'ContractBase':
        """Valida lógica condicional de payment_custom_years"""
        if self.payment_frequency == PaymentFrequency.CUSTOM_YEARS:
            if not self.payment_custom_years or self.payment_custom_years < 1:
                raise ValueError(
                    'payment_custom_years ist erforderlich und muss >= 1 sein, '
                    'wenn payment_frequency CUSTOM_YEARS ist. / '
                    'payment_custom_years é obrigatório e deve ser >= 1 quando '
                    'payment_frequency é CUSTOM_YEARS.'
                )
        else:
            # Se frequency não é CUSTOM_YEARS, custom_years deve ser null
            if self.payment_custom_years is not None:
                # Limpar automaticamente ao invés de dar erro
                self.payment_custom_years = None
        return self
```

**Aplicar também em:**
- `ContractUpdate` (mesma lógica)

**Testes:**
```python
# backend/test/test_contract.py - adicionar
def test_payment_custom_years_validation():
    # T1: CUSTOM_YEARS sem custom_years → deve rejeitar
    # T2: CUSTOM_YEARS com custom_years=5 → deve aceitar
    # T3: MONTHLY com custom_years=5 → deve limpar para null
    # T4: MONTHLY sem custom_years → deve aceitar
```

**Rollback:** Remover `@model_validator` (reversível)

---

#### **TAREFA 1.2: Melhorar Sanitização de Filename para UTF-8** ⭐ ALTA
**Arquivo:** `backend/app/routers/contracts.py`  
**Tempo:** 30 minutos  
**Risco:** 🟢 BAIXO (apenas melhora headers)

**Implementação:**
```python
# Linha ~471 (função download_original_pdf)
from urllib.parse import quote

# ANTES:
# safe_filename = re.sub(r'[^\w\s.-]', '_', filename)

# DEPOIS:
# Preservar caracteres UTF-8 (ä, ö, ü, ß)
safe_filename_display = filename  # Para display
safe_filename_encoded = quote(filename.encode('utf-8'))

headers = {
    # RFC 5987: suporte a UTF-8 em headers
    "Content-Disposition": (
        f'attachment; '
        f'filename="{safe_filename_display}"; '
        f'filename*=UTF-8\'\'{safe_filename_encoded}'
    ),
    "Content-Type": "application/pdf"
}
```

**Aplicar em:**
- `/contracts/{id}/original` (download)
- `/contracts/{id}/view` (visualização inline)

**Testes:**
- Download de PDF com nome "Vertrag_für_Büro_Köln.pdf"
- Verificar se nome preserva caracteres alemães
- Testar em Chrome, Firefox, Edge

**Rollback:** Reverter para regex anterior (reversível)

---

#### **TAREFA 1.3: Adicionar Ordenação Secundária por ID na Paginação** ⭐ MÉDIA
**Arquivo:** `backend/app/services/contract_service.py`  
**Tempo:** 30 minutos  
**Risco:** 🟢 BAIXO (melhora consistência)

**Implementação:**
```python
# Linha ~269 (função list_contracts)
# ANTES:
if sort_order.lower() == "asc":
    query = query.order_by(asc(sort_column))
else:
    query = query.order_by(desc(sort_column))

# DEPOIS:
if sort_order.lower() == "asc":
    query = query.order_by(asc(sort_column), asc(Contract.id))
else:
    query = query.order_by(desc(sort_column), asc(Contract.id))
```

**Benefício:** Evita duplicatas/faltantes quando registros têm mesmo valor no campo de ordenação

**Testes:**
- Criar 10 contratos com mesmo `created_at`
- Navegar paginação com `sort_by=created_at`
- Verificar se não há duplicatas

**Rollback:** Remover ordenação secundária (reversível)

---

#### **TAREFA 1.4: Validação de skip/limit em list_contracts** ⭐ BAIXA
**Arquivo:** `backend/app/services/contract_service.py`  
**Tempo:** 15 minutos  
**Risco:** 🟢 BAIXO (apenas adiciona validação)

**Implementação:**
```python
# Linha ~214 (início de list_contracts)
async def list_contracts(self, skip: int = 0, limit: int = 10, ...):
    # Normalize and cap skip/limit (JÁ EXISTE mas pode melhorar)
    skip = max(0, int(skip))  # Não permitir negativos
    limit = max(1, min(100, int(limit)))  # Entre 1 e 100
    
    # ... resto do código ...
```

**Testes:**
- Testar com `skip=-10` → deve usar 0
- Testar com `limit=1000` → deve usar 100
- Testar com `limit=0` → deve usar 1

**Rollback:** Remover validação (reversível)

---

### 🎯 FASE 2: INTEGRAÇÃO DE UPLOAD UNIFICADO (Estimativa: 6-8 horas)

**Objetivo:** Implementar suporte a multipart/form-data nos endpoints principais

#### **TAREFA 2.1: Adicionar Suporte FormData em POST /contracts/** ⭐ CRÍTICA
**Arquivo:** `backend/app/routers/contracts.py`  
**Tempo:** 3-4 horas  
**Risco:** 🟡 MÉDIO (altera endpoint principal)

**Estratégia:** Criar NOVO endpoint e manter compatibilidade com JSON

**Implementação:**

**OPÇÃO A: Endpoint Duplo (RECOMENDADO - menor risco)**
```python
# Manter endpoint JSON atual (linha 146)
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(    
    contract: ContractCreate,
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service)
):
    # Código atual mantido sem alteração
    # ...

# NOVO endpoint para FormData
@router.post("/with-upload", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract_with_upload(
    # Campos obrigatórios
    title: str = Form(..., min_length=2, max_length=200),
    client_name: str = Form(..., min_length=2, max_length=200),
    contract_type: str = Form(...),
    status: str = Form(default="DRAFT"),
    start_date: date = Form(...),
    
    # Campos opcionais
    description: Optional[str] = Form(None),
    end_date: Optional[date] = Form(None),
    renewal_date: Optional[date] = Form(None),
    value: Optional[Decimal] = Form(None),
    currency: str = Form(default="EUR"),
    payment_frequency: Optional[str] = Form(None),
    payment_custom_years: Optional[int] = Form(None),
    
    company_name: Optional[str] = Form(None),
    legal_form: Optional[str] = Form(None),
    client_document: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    client_phone: Optional[str] = Form(None),
    client_address: Optional[str] = Form(None),
    
    department: Optional[str] = Form(None),
    team: Optional[str] = Form(None),
    responsible_user_id: Optional[int] = Form(None),
    
    terms_and_conditions: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    
    # PDF (opcional)
    pdf_file: Optional[UploadFile] = File(None),
    
    # Dependencies
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria contrato com upload de PDF em uma única requisição.
    Creates contract with PDF upload in a single request.
    """
    # 1. Validar PDF se existe
    if pdf_file and pdf_file.filename:
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, detail="Apenas arquivos PDF / Only PDF files")
        
        content = await pdf_file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(413, detail="Arquivo muito grande / File too large (max 10MB)")
        await pdf_file.seek(0)  # Reset para reler
    
    # 2. Criar objeto ContractCreate para usar validações existentes
    contract_data = ContractCreate(
        title=title,
        client_name=client_name,
        contract_type=contract_type,
        status=status,
        start_date=start_date,
        description=description,
        end_date=end_date,
        renewal_date=renewal_date,
        value=value,
        currency=currency,
        payment_frequency=payment_frequency,
        payment_custom_years=payment_custom_years,
        company_name=company_name,
        legal_form=legal_form,
        client_document=client_document,
        client_email=client_email,
        client_phone=client_phone,
        client_address=client_address,
        department=department,
        team=team,
        responsible_user_id=responsible_user_id,
        terms_and_conditions=terms_and_conditions,
        notes=notes
    )
    
    # 3. Criar contrato (reutilizar lógica existente)
    created = await contract_service.create_contract(contract_data, current_user.id)
    
    # 4. Se tem PDF, salvar e anexar
    if pdf_file and pdf_file.filename:
        # Criar diretório
        contract_dir = os.path.join(settings.UPLOAD_DIR, "contracts", "persisted", f"contract_{created.id}")
        os.makedirs(contract_dir, exist_ok=True)
        
        # Salvar PDF
        file_path = os.path.join(contract_dir, "original.pdf")
        content = await pdf_file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Calcular hash
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Anexar ao contrato
        await contract_service.attach_original_pdf(
            created.id, 
            file_path, 
            pdf_file.filename, 
            file_hash, 
            "",  # ocr_text vazio
            ""   # ocr_sha256 vazio
        )
        
        # Refresh para pegar metadados do PDF
        updated = await contract_service.get_contract(created.id)
        return updated
    
    return created
```

**OPÇÃO B: Detectar Content-Type automaticamente (mais arriscado)**
```python
# Modificar endpoint existente para aceitar ambos
# Requer lógica para detectar se é JSON ou FormData
# NÃO RECOMENDADO - maior chance de quebrar código existente
```

**Vantagens da Opção A:**
- ✅ Mantém compatibilidade total com código existente
- ✅ Frontend pode migrar gradualmente
- ✅ Fácil rollback (apenas remover novo endpoint)
- ✅ Permite testar novo fluxo sem afetar produção

**Testes:**
```bash
# Postman/Thunder Client
POST http://localhost:8000/api/contracts/with-upload
Content-Type: multipart/form-data

title: Test Contract
client_name: Test Client
contract_type: SERVICE
status: DRAFT
start_date: 2026-01-20
pdf_file: [arquivo.pdf]
```

**Rollback:** Remover endpoint `/with-upload` (reversível, não afeta código existente)

---

#### **TAREFA 2.2: Adicionar Suporte FormData em PUT /contracts/{id}** ⭐ CRÍTICA
**Arquivo:** `backend/app/routers/contracts.py`  
**Tempo:** 2-3 horas  
**Risco:** 🟡 MÉDIO

**Implementação:** Mesma estratégia (endpoint duplo)

```python
# Novo endpoint
@router.put("/{contract_id}/with-upload", response_model=ContractResponse)
async def update_contract_with_upload(
    contract_id: int,
    # Todos os campos como Optional[...] = Form(None)
    title: Optional[str] = Form(None),
    # ... todos os campos ...
    pdf_file: Optional[UploadFile] = File(None),
    # ...
):
    """Atualiza contrato com possibilidade de substituir PDF"""
    # 1. Buscar contrato existente
    # 2. Atualizar campos fornecidos
    # 3. Se pdf_file existe, substituir PDF antigo
    # 4. Retornar ContractResponse atualizado
```

**Lógica de substituição de PDF:**
```python
if pdf_file and pdf_file.filename:
    # Remover PDF antigo se existe
    old_pdf_path = get_contract_pdf_path(contract_id)
    if old_pdf_path and os.path.exists(old_pdf_path):
        os.remove(old_pdf_path)
    
    # Salvar novo PDF
    # ... mesma lógica do POST
```

**Testes:**
- Atualizar contrato SEM PDF → deve manter PDF existente
- Atualizar contrato COM PDF → deve substituir PDF antigo
- Verificar se PDF antigo foi deletado do filesystem

**Rollback:** Remover endpoint `/with-upload` (reversível)

---

#### **TAREFA 2.3: Refatorar Frontend para usar Endpoints Unificados** ⭐ CRÍTICA
**Arquivo:** `frontend/src/services/contractsApi.js`  
**Tempo:** 1-2 horas  
**Risco:** 🟡 MÉDIO (altera chamadas de API)

**Implementação:**

```javascript
// NOVO createContract (linha 89)
createContract: async (data) => {
  try {
    // Decidir qual endpoint usar
    const useFormData = !!data.pdfFile;
    
    if (useFormData) {
      // Usar novo endpoint com FormData
      const formData = new FormData();
      
      // Adicionar todos os campos
      Object.keys(data).forEach(key => {
        if (key === 'pdfFile') {
          // Adicionar arquivo
          formData.append('pdf_file', data.pdfFile);
        } else if (data[key] !== null && data[key] !== undefined) {
          // Adicionar campo (converter para string se necessário)
          const value = data[key];
          if (value instanceof Date) {
            formData.append(key, value.toISOString().split('T')[0]);
          } else {
            formData.append(key, value.toString());
          }
        }
      });
      
      const response = await api.post('/contracts/with-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } else {
      // Usar endpoint JSON tradicional (sem PDF)
      const { pdfFile, ...contractData } = data;
      const response = await api.post('/contracts', contractData);
      return response.data;
    }
  } catch (error) {
    console.error('Error creating contract:', error);
    throw error;
  }
}
```

**Implementação para updateContract:**
```javascript
updateContract: async (id, data) => {
  try {
    const useFormData = !!data.pdfFile;
    
    if (useFormData) {
      // Usar novo endpoint com FormData
      const formData = new FormData();
      // ... mesma lógica do create ...
      
      const response = await api.put(`/contracts/${id}/with-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } else {
      // Usar endpoint JSON tradicional
      const { pdfFile, ...contractData } = data;
      const response = await api.put(`/contracts/${id}`, contractData);
      return response.data;
    }
  } catch (error) {
    console.error(`Error updating contract ${id}:`, error);
    throw error;
  }
}
```

**Testes:**
- Criar contrato SEM PDF → deve usar `/contracts` (JSON)
- Criar contrato COM PDF → deve usar `/contracts/with-upload` (FormData)
- Atualizar contrato SEM PDF → deve usar `/contracts/{id}` (JSON)
- Atualizar contrato COM PDF → deve usar `/contracts/{id}/with-upload` (FormData)

**Rollback:** Reverter para código anterior (commit anterior do git)

---

### 🎯 FASE 3: VERIFICAÇÃO E TESTES (Estimativa: 3-4 horas)

**Objetivo:** Garantir que todas as correções funcionam corretamente

#### **TAREFA 3.1: Testes Manuais E2E** ⭐ CRÍTICA
**Tempo:** 2 horas  
**Responsável:** QA / Desenvolvedor

**Cenários:**

**T1: Criar contrato SEM PDF**
- [ ] Preencher formulário sem selecionar PDF
- [ ] Salvar
- [ ] Verificar se criado no banco
- [ ] Verificar se `original_pdf_path = null`

**T2: Criar contrato COM PDF**
- [ ] Preencher formulário + selecionar PDF
- [ ] Salvar
- [ ] Verificar se criado no banco
- [ ] Verificar se PDF salvo em `uploads/contracts/persisted/contract_{id}/original.pdf`
- [ ] Verificar se `original_pdf_path` aponta para arquivo correto
- [ ] Download do PDF → deve abrir corretamente

**T3: Editar contrato e SUBSTITUIR PDF**
- [ ] Abrir contrato existente com PDF
- [ ] Fazer upload de novo PDF
- [ ] Salvar
- [ ] Verificar se PDF antigo foi deletado
- [ ] Verificar se novo PDF foi salvo
- [ ] Download → deve baixar novo PDF

**T4: Editar contrato SEM alterar PDF**
- [ ] Abrir contrato com PDF
- [ ] Alterar apenas title
- [ ] Salvar
- [ ] Verificar se PDF não foi alterado

**T5: Payment Frequency - Validações**
- [ ] Criar com `frequency=CUSTOM_YEARS` sem `custom_years` → deve REJEITAR
- [ ] Criar com `frequency=CUSTOM_YEARS` + `custom_years=5` → deve ACEITAR
- [ ] Criar com `frequency=MONTHLY` + `custom_years=5` → deve LIMPAR para null
- [ ] Editar e mudar frequency → verificar lógica

**T6: Download com Nome Alemão**
- [ ] Criar contrato com PDF "Bürovertrag_für_München.pdf"
- [ ] Download
- [ ] Verificar se nome preserva ä, ö, ü, ß
- [ ] Testar em Chrome, Firefox, Edge

**T7: Paginação (252 contratos)**
- [ ] Login como Director
- [ ] Verificar `total = 252`
- [ ] Navegar TODAS as páginas (page_size=25 → 11 páginas)
- [ ] Exportar IDs de cada página
- [ ] Verificar duplicatas/faltantes
- [ ] Testar com diferentes `sort_by`

**T8: Permissões**
- [ ] Login como Director → ver todos 252
- [ ] Login como Department_Adm → ver só departamento
- [ ] Login como Staff → ver só próprios

---

#### **TAREFA 3.2: Testes Automatizados** ⭐ ALTA
**Arquivo:** `backend/test/test_contract.py`  
**Tempo:** 1-2 horas

**Adicionar:**
```python
async def test_create_contract_with_pdf_formdata():
    """Testa criação com PDF via FormData"""
    # Simular upload de PDF
    # Verificar persistência
    
async def test_payment_custom_years_validation():
    """Testa validação condicional"""
    # 4 cenários (ver Tarefa 1.1)

async def test_download_pdf_utf8_filename():
    """Testa download com caracteres alemães"""
    # Criar contrato com PDF
    # Download
    # Verificar headers
```

---

### 🎯 FASE 4: LIMPEZA E OTIMIZAÇÃO (Estimativa: 2-3 horas)

**Objetivo:** Remover código redundante e documentar mudanças

#### **TAREFA 4.1: Remover/Deprecar Endpoints Antigos (OPCIONAL)** ⭐ BAIXA
**Arquivo:** Vários  
**Tempo:** 1 hora

**APÓS confirmar que novo fluxo funciona 100%:**

- [ ] Marcar endpoints antigos como `deprecated` (mas manter funcionando)
- [ ] Adicionar warnings em logs quando usados
- [ ] Planejar remoção para versão futura

```python
@router.post("/", deprecated=True, response_model=ContractResponse)
async def create_contract(...):
    """DEPRECATED: Use /contracts/with-upload para upload de PDF"""
    # ...
```

---

#### **TAREFA 4.2: Documentação** ⭐ MÉDIA
**Arquivos:** README, CHANGELOG, OpenAPI docs  
**Tempo:** 1 hora

- [ ] Atualizar README com novo fluxo de upload
- [ ] Adicionar entry no CHANGELOG
- [ ] Verificar se OpenAPI docs estão corretos
- [ ] Adicionar comentários no código

---

#### **TAREFA 4.3: Monitoramento** ⭐ BAIXA
**Tempo:** 30 minutos

- [ ] Adicionar logs detalhados em upload/download
- [ ] Adicionar métricas (quantos PDFs salvos, tamanho médio, etc)
- [ ] Alertas se muitos uploads falharem

---

## 📊 RESUMO DO PLANO

### Cronograma Estimado

| Fase | Duração | Risco | Pode Quebrar? |
|------|---------|-------|---------------|
| **Fase 1** | 4-6h | 🟢 Baixo | ❌ Não |
| **Fase 2** | 6-8h | 🟡 Médio | ⚠️ Sim (se mal implementado) |
| **Fase 3** | 3-4h | 🟢 Baixo | ❌ Não (apenas testa) |
| **Fase 4** | 2-3h | 🟢 Baixo | ❌ Não |
| **TOTAL** | **15-21h** | - | - |

### Ordem de Implementação Recomendada

1. ✅ **DIA 1 (4-6h):** Fase 1 completa → Deploy e testar
2. ✅ **DIA 2 (6-8h):** Fase 2 (backend) → Testar com Postman
3. ✅ **DIA 3 (4-6h):** Fase 2 (frontend) + Fase 3 → Testes E2E
4. ✅ **DIA 4 (2-3h):** Fase 4 (limpeza) → Deploy final

### Estratégia de Rollback

Cada fase tem rollback independente:

- **Fase 1:** Reverter commits (validações não quebram código)
- **Fase 2:** Manter endpoints antigos funcionando (novos são opcionais)
- **Fase 3:** Apenas testes, sem código de produção
- **Fase 4:** Documentação e logs, sem impacto funcional

### Critérios de Sucesso

- ✅ Todos os 12 testes E2E passam
- ✅ 252 contratos acessíveis sem duplicatas
- ✅ Upload de PDF funciona em 1 requisição
- ✅ Download funciona com nomes alemães
- ✅ Validação de payment_custom_years ativa
- ✅ Zero regressões (funcionalidades existentes intactas)

---
**Fim do Documento / End of Document**  
**Última Atualização / Last Update:** 15 de janeiro de 2026
