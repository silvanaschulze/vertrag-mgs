# 🚀 PROMPT - Sprint 5: Upload e Import de PDFs

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

---

## 🎯 SPRINT 5: UPLOAD E IMPORT DE PDFs

### Objetivo

Implementar sistema completo de upload e import de PDFs de contratos com:
- **Drag & Drop** para upload de PDF
- **Preview do PDF** (visualização inline ou em modal)
- **Extração inteligente de dados** do PDF (usando backend)
- **Formulário pré-preenchido** com dados extraídos
- **Edição dos dados** antes de salvar
- **Upload direto** em create/edit de contratos
- **Página de Import** dedicada para upload em massa
- **TUDO respeitando permissões por role/level**

---

## 📝 Backend Já Existente

```
✅ backend/app/routers/contracts_import.py - Endpoints:
   - POST /api/contracts/import/upload (upload + extração)
   - POST /api/contracts/import/confirm (salvar após edição)
   - GET /api/contracts/{id}/pdf (download PDF)
   - GET /api/contracts/{id}/pdf/preview (preview inline)

✅ backend/app/services/pdf_reader.py - Extração inteligente:
   - Extração de texto com pdfplumber
   - OCR com Tesseract (para PDFs escaneados)
   - Análise de datas, valores, parceiros
   - Confidence scoring (0-100%)
   - Suporte para alemão e português

✅ backend/app/services/contract_service.py - Gerenciamento de PDFs:
   - save_contract_pdf() - Salva PDF em uploads/contracts/persisted/{contract_id}/
   - move_temp_to_persisted() - Move de temp/ para persisted/
   - delete_contract_pdf() - Deleta PDF ao deletar contrato
```

### Schema de Extração (Referência)

```python
class ExtractedContract(BaseModel):
    title: Optional[str]
    client_name: Optional[str]
    company_name: Optional[str]
    contract_type: Optional[str]  # 'LEASE', 'SERVICE', etc
    start_date: Optional[date]
    end_date: Optional[date]
    value: Optional[float]
    description: Optional[str]
    
    # Metadata
    confidence: float  # 0-100%
    extracted_text: str
    warnings: List[str]  # Avisos durante extração
```

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── upload/  (❌ CRIAR AGORA)
│   │   ├── DropzoneUpload.jsx
│   │   ├── PDFPreview.jsx
│   │   └── ExtractedDataForm.jsx
│   └── ...
├── pages/
│   ├── import/  (❌ CRIAR AGORA)
│   │   └── ImportPage.jsx
│   └── ...
├── services/
│   ├── importApi.js  (❌ CRIAR AGORA)
│   └── ...
└── ...
```

---

## 📝 CHECKLIST SPRINT 5

### 1. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/importApi.js` com:
  - `uploadPDF(file)` - POST /api/contracts/import/upload (retorna dados extraídos)
  - `confirmImport(data)` - POST /api/contracts/import/confirm (salva contrato)
  - `downloadPDF(contractId)` - GET /api/contracts/{id}/pdf (download)
  - `previewPDF(contractId)` - GET /api/contracts/{id}/pdf/preview (blob para iframe)

### 2. Componentes de Upload

- [ ] `frontend/src/components/upload/DropzoneUpload.jsx`
  **Funcionalidades:**
  - Drag & Drop área com `react-dropzone`
  - Aceita apenas arquivos PDF
  - Validação de tamanho (max 10MB)
  - Preview do nome do arquivo
  - Loading state durante upload
  - Progress bar (opcional)
  - Error handling (tamanho, tipo, etc)
  
  **Props:**
  ```javascript
  {
    onUpload: (file) => void,       // Callback quando arquivo é selecionado
    loading: boolean,                // Estado de loading
    error: string | null,            // Mensagem de erro
    acceptedFileTypes: string,       // 'application/pdf'
    maxSize: number                  // 10 * 1024 * 1024 (10MB)
  }
  ```

- [ ] `frontend/src/components/upload/PDFPreview.jsx`
  **Funcionalidades:**
  - Preview do PDF em iframe ou objeto
  - Opção de full-screen
  - Botão de download
  - Paginação (se PDF tem múltiplas páginas)
  - Loading skeleton
  
  **Props:**
  ```javascript
  {
    pdfUrl: string,                  // URL do PDF (blob ou http)
    title: string,                   // Título do PDF
    onDownload: () => void,          // Callback para download
    height: number                   // Altura do preview (default: 600px)
  }
  ```

- [ ] `frontend/src/components/upload/ExtractedDataForm.jsx`
  **Funcionalidades:**
  - Formulário pré-preenchido com dados extraídos
  - React Hook Form + Zod validation
  - Mesmos campos do ContractForm
  - Highlight de campos com confidence baixa (<70%)
  - Indicador de confidence ao lado de cada campo
  - Permite editar todos os campos
  - Botão "Salvar Contrato"
  
  **Props:**
  ```javascript
  {
    extractedData: ExtractedContract, // Dados extraídos do PDF
    onSubmit: (data) => void,         // Callback ao salvar
    loading: boolean                  // Estado de salvamento
  }
  ```

### 3. Páginas

- [ ] `frontend/src/pages/import/ImportPage.jsx`
  **Fluxo:**
  1. Exibe DropzoneUpload
  2. Usuário faz upload de PDF
  3. Backend extrai dados (loading...)
  4. Exibe PDFPreview (lado esquerdo) + ExtractedDataForm (lado direito)
  5. Usuário edita dados se necessário
  6. Clica em "Salvar Contrato"
  7. Redireciona para ContractView do contrato criado
  
  **Layout:**
  ```jsx
  <Grid container spacing={2}>
    <Grid item xs={12}>
      <Typography variant="h4">PDF Import / PDF-Import</Typography>
    </Grid>
    
    {/* Passo 1: Upload */}
    {!pdfUploaded && (
      <Grid item xs={12}>
        <DropzoneUpload onUpload={handleUpload} />
      </Grid>
    )}
    
    {/* Passo 2: Preview + Form */}
    {pdfUploaded && (
      <>
        <Grid item xs={12} md={6}>
          <PDFPreview pdfUrl={pdfUrl} />
        </Grid>
        <Grid item xs={12} md={6}>
          <ExtractedDataForm 
            extractedData={extractedData}
            onSubmit={handleConfirm}
          />
        </Grid>
      </>
    )}
  </Grid>
  ```

### 4. Integração com ContractForm

- [ ] **Atualizar `frontend/src/components/contracts/ContractForm.jsx`:**
  - Adicionar campo de upload de PDF (já existe)
  - ⚠️ **PENDÊNCIA DA SPRINT 3:** Integrar upload com backend
  - Usar DropzoneUpload ou input file simples
  - Exibir nome do arquivo selecionado
  - Validar que PDF é obrigatório em create (opcional em edit)

- [ ] **Atualizar `frontend/src/services/contractsApi.js`:**
  - Modificar `createContract()` para enviar FormData com PDF
  - Modificar `updateContract()` para enviar FormData se PDF alterado
  - Exemplo:
    ```javascript
    createContract: async (data) => {
      const formData = new FormData();
      
      // Adicionar campos
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

### 5. Integração com ContractView

- [ ] **Atualizar `frontend/src/pages/contracts/ContractView.jsx`:**
  - Adicionar botão "Download PDF" se contrato tem PDF
  - Adicionar PDFPreview inline (opcional, pode ser modal)
  - Exemplo:
    ```jsx
    {contract.pdf_path && (
      <Box sx={{ mt: 2 }}>
        <Button 
          variant="outlined" 
          startIcon={<PictureAsPdfIcon />}
          onClick={handleDownloadPDF}
        >
          PDF herunterladen / Download PDF
        </Button>
        
        <Button 
          variant="outlined" 
          startIcon={<VisibilityIcon />}
          onClick={() => setShowPreview(true)}
          sx={{ ml: 1 }}
        >
          PDF anzeigen / View PDF
        </Button>
      </Box>
    )}
    
    {showPreview && (
      <PDFPreview 
        pdfUrl={`/api/contracts/${contract.id}/pdf/preview`}
        title={contract.title}
        onClose={() => setShowPreview(false)}
      />
    )}
    ```

### 6. Routing

- [ ] Atualizar `frontend/src/App.jsx` com rotas:
  ```jsx
  <Route
    path="import"
    element={
      <RequirePermission permission="contracts:import">
        <ImportPage />
      </RequirePermission>
    }
  />
  ```
  (Já deve estar lá como placeholder)

### 7. Sidebar Menu

- [ ] Menu "Import" já existe no Sidebar
- [ ] Visível apenas para roles com permissão `contracts:import`:
  - Level 5 (DIRECTOR)
  - Level 4 (DEPARTMENT_ADM)
  - Level 2 (TEAM_LEAD)

---

## 🎨 REFERÊNCIAS DE DESIGN

### DropzoneUpload

```jsx
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const DropzoneUpload = ({ onUpload, loading }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    }
  });

  return (
    <Paper
      {...getRootProps()}
      sx={{
        p: 4,
        textAlign: 'center',
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'grey.400',
        backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
        cursor: 'pointer',
        '&:hover': { borderColor: 'primary.main' }
      }}
    >
      <input {...getInputProps()} disabled={loading} />
      <CloudUploadIcon sx={{ fontSize: 60, color: 'grey.500', mb: 2 }} />
      <Typography variant="h6">
        {isDragActive
          ? 'PDF hier ablegen / Drop PDF here'
          : 'PDF hierher ziehen oder klicken / Drag PDF here or click'}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Max 10MB
      </Typography>
    </Paper>
  );
};
```

### PDFPreview (com iframe)

```jsx
const PDFPreview = ({ pdfUrl, title, onDownload }) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">{title}</Typography>
        <Button 
          variant="outlined" 
          startIcon={<DownloadIcon />}
          onClick={onDownload}
        >
          Herunterladen / Download
        </Button>
      </Box>
      
      <Box 
        component="iframe"
        src={pdfUrl}
        sx={{
          width: '100%',
          height: 600,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1
        }}
      />
    </Paper>
  );
};
```

### ExtractedDataForm (com confidence indicators)

```jsx
const ExtractedDataForm = ({ extractedData, onSubmit }) => {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 50) return 'warning';
    return 'error';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Extrahierte Daten / Extracted Data
      </Typography>
      
      <Box mb={2}>
        <Chip 
          label={`Confidence: ${extractedData.confidence.toFixed(0)}%`}
          color={getConfidenceColor(extractedData.confidence)}
        />
      </Box>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Campos do formulário */}
        {/* Cada campo com indicador de confidence */}
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              label="Titel / Title"
              fullWidth
              {...register('title')}
              InputProps={{
                endAdornment: (
                  <Chip 
                    label={`${extractedData.titleConfidence}%`}
                    size="small"
                    color={getConfidenceColor(extractedData.titleConfidence)}
                  />
                )
              }}
            />
          </Grid>
          {/* ... outros campos ... */}
        </Grid>
        
        <Button type="submit" variant="contained" sx={{ mt: 2 }}>
          Vertrag speichern / Save Contract
        </Button>
      </form>
    </Paper>
  );
};
```

---

## 🔐 REGRAS DE PERMISSÕES

### Permissão para Import (contracts:import)

- **Level 5 (DIRECTOR):** Pode importar
- **Level 4 (DEPARTMENT_ADM):** Pode importar
- **Level 2 (TEAM_LEAD):** Pode importar
- **Outros:** NÃO podem importar

### Upload de PDF em Create/Edit

- **Todos com permissão de criar/editar contratos** podem fazer upload de PDF
- PDF é **obrigatório** em create
- PDF é **opcional** em edit (apenas se quiser substituir)

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. **Resolver pendências da Sprint 3:**
   - Integrar upload de PDF no ContractForm
   - Modificar contractsApi.createContract() para FormData
   - Testar criação de contrato com PDF

2. **Implementar Download de PDF:**
   - Corrigir headers no backend (Content-Disposition)
   - Adicionar botão "Download PDF" no ContractView
   - Testar download

3. **importApi.js** (API calls)

### Prioridade MÉDIA (depois)

4. DropzoneUpload.jsx (componente drag & drop)
5. PDFPreview.jsx (visualização)
6. ImportPage.jsx (fluxo completo)
7. ExtractedDataForm.jsx (formulário com dados extraídos)

### Prioridade BAIXA (polimento)

8. Upload em massa (múltiplos PDFs)
9. Preview inline no ContractView
10. Progress bar durante upload
11. Validação de OCR para PDFs escaneados

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 5 estará completa quando:

- [ ] Upload de PDF funciona em ContractCreate (FormData)
- [ ] Download de PDF funciona em ContractView (headers corretos)
- [ ] Página de Import com drag & drop funcional
- [ ] Extração de dados do PDF funcionando
- [ ] Formulário pré-preenchido com dados extraídos
- [ ] Usuário pode editar dados antes de salvar
- [ ] Confidence score exibido
- [ ] Preview do PDF visível
- [ ] Permissões respeitadas (apenas roles autorizadas veem Import)
- [ ] Loading states em todas operações
- [ ] Error handling (arquivo muito grande, tipo inválido, extração falhou)
- [ ] Toast notifications (sucesso/erro)

---

## 🚀 COMO COMEÇAR

### 1. **RESOLVER PENDÊNCIAS DA SPRINT 3 PRIMEIRO:**

#### Backend: Modificar POST /api/contracts/ para aceitar FormData

```python
# backend/app/routers/contracts.py

from fastapi import File, UploadFile, Form

@router.post("/", response_model=ContractOut)
async def create_contract(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    title: str = Form(...),
    client_name: str = Form(...),
    contract_type: str = Form(...),
    status: str = Form(...),
    start_date: date = Form(...),
    end_date: Optional[date] = Form(None),
    value: Optional[float] = Form(None),
    # ... outros campos ...
    pdf_file: UploadFile = File(...)  # OBRIGATÓRIO
):
    # 1. Criar contrato no banco
    contract_data = ContractCreate(
        title=title,
        client_name=client_name,
        # ... outros campos ...
    )
    contract = await contract_service.create_contract(db, contract_data, current_user)
    
    # 2. Salvar PDF
    pdf_path = await contract_service.save_contract_pdf(contract.id, pdf_file)
    contract.pdf_path = pdf_path
    await db.commit()
    
    return contract
```

#### Frontend: Modificar contractsApi.createContract()

```javascript
// frontend/src/services/contractsApi.js

createContract: async (data) => {
  const formData = new FormData();
  
  // Adicionar todos os campos
  Object.keys(data).forEach(key => {
    if (data[key] !== null && key !== 'pdfFile') {
      formData.append(key, data[key]);
    }
  });
  
  // Adicionar PDF (obrigatório)
  if (!data.pdfFile) {
    throw new Error('PDF file is required');
  }
  formData.append('pdf_file', data.pdfFile);
  
  const response = await api.post('/contracts/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
}
```

### 2. Testar Upload:

```bash
# Criar contrato com PDF pelo frontend
# Verificar se:
# - PDF é salvo em uploads/contracts/persisted/{contract_id}/
# - Campo pdf_path no banco está preenchido
# - Não há erros no console
```

### 3. Implementar Download:

```python
# backend/app/routers/contracts.py

@router.get("/{contract_id}/pdf")
async def download_contract_pdf(...):
    filename = f"contract_{contract_id}.pdf"
    return FileResponse(
        path=contract.pdf_path,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf'
        }
    )
```

```jsx
// frontend - ContractView.jsx

const handleDownloadPDF = async () => {
  try {
    const response = await api.get(`/contracts/${contract.id}/pdf`, {
      responseType: 'blob'
    });
    
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `contract_${contract.id}.pdf`;
    link.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
  }
};
```

### 4. Após resolver pendências, continuar com:

- importApi.js
- DropzoneUpload.jsx
- ImportPage.jsx

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend import: `backend/app/routers/contracts_import.py`
- Backend PDF reader: `backend/app/services/pdf_reader.py`
- Backend contract service: `backend/app/services/contract_service.py`
- Frontend ContractForm: `frontend/src/components/contracts/ContractForm.jsx`
- react-dropzone docs: https://react-dropzone.js.org/

---

## 🎯 META

Ao final da Sprint 5, o usuário deverá conseguir:

1. **Criar contrato com upload de PDF** (Sprint 3 pendência resolvida)
2. **Fazer download de PDF** de contrato existente
3. **Acessar página de Import**
4. **Fazer drag & drop de PDF**
5. **Ver preview do PDF** e **dados extraídos** lado a lado
6. **Editar dados** extraídos se necessário
7. **Salvar contrato** com um clique
8. **Ver confidence score** de cada campo
9. **Receber feedback** de sucesso/erro

---

**Pronto para começar! Vamos implementar a Sprint 5 passo a passo, resolvendo primeiro as pendências da Sprint 3.**
