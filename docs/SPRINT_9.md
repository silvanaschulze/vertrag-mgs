# 🚀 PROMPT - Sprint 9: Relatórios e Estatísticas

## 📋 CONTEXTO DO PROJETO

Estou desenvolvendo o **Vertrag-MGS** (Sistema de Gestão de Contratos) com:
- **Backend:** FastAPI + SQLAlchemy Async + SQLite
- **Frontend:** React 18 + Vite 5 + Material-UI 5
- **Autenticação:** JWT com sistema de 7 roles e 6 access levels
- **Localização:** Projeto em /home/sschulze/projects/vertrag-mgs

---

## ✅ SPRINTS ANTERIORES COMPLETAS

### Sprint 1-8: ✅ Todas completas

---

## 🎯 SPRINT 9: RELATÓRIOS E ESTATÍSTICAS

### Objetivo

Implementar sistema completo de relatórios e análises com:
- **Dashboard de relatórios** com gráficos interativos
- **Relatórios financeiros** (valores por período, tipo, departamento)
- **Relatórios de vencimentos** (contratos expirando, vencidos)
- **Análise por departamento/time**
- **Exportação** para PDF e Excel
- **Filtros avançados** (período, tipo, departamento, status)
- **TUDO respeitando permissões por role/level**

---

## 📝 Backend Já Existente

```
✅ backend/app/routers/reports.py - Endpoints (a criar se não existe):
   - GET /api/reports/financial (relatório financeiro)
   - GET /api/reports/expirations (contratos expirando)
   - GET /api/reports/by-department (análise por departamento)
   - GET /api/reports/by-type (análise por tipo)
   - GET /api/reports/summary (resumo geral)
   - POST /api/reports/export/pdf (gerar PDF)
   - POST /api/reports/export/excel (gerar Excel)
```

**⚠️ NOTA:** Se esses endpoints não existem no backend, precisarão ser criados na Sprint 9.

---

## 🎨 Frontend Estrutura Atual

```
frontend/src/
├── components/
│   ├── reports/  (❌ CRIAR AGORA)
│   │   ├── FinancialReport.jsx
│   │   ├── ExpirationReport.jsx
│   │   ├── DepartmentAnalysis.jsx
│   │   ├── ChartContracts.jsx
│   │   ├── ChartValues.jsx
│   │   └── ReportFilters.jsx
│   └── ...
├── pages/
│   ├── reports/  (❌ CRIAR AGORA)
│   │   ├── ReportsPage.jsx
│   │   ├── FinancialReportPage.jsx
│   │   ├── ExpirationReportPage.jsx
│   │   └── DepartmentReportPage.jsx
│   └── ...
├── services/
│   ├── reportsApi.js  (❌ CRIAR AGORA)
│   └── ...
└── ...
```

---

## 📝 CHECKLIST SPRINT 9

### 1. Backend - Criar Endpoints de Relatórios (se não existem)

- [ ] Criar `backend/app/routers/reports.py` com:
  ```python
  @router.get("/financial")
  async def financial_report(
      start_date: Optional[date] = None,
      end_date: Optional[date] = None,
      contract_type: Optional[str] = None,
      department: Optional[str] = None,
      db: AsyncSession = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      # Retorna: total_value, avg_value, count, contracts_by_type, etc
      # Filtrado por permissões do usuário
  
  @router.get("/expirations")
  async def expiration_report(
      days: int = 30,  # Próximos 30 dias
      db: AsyncSession = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      # Retorna: contratos expirando, já vencidos, etc
  
  @router.get("/by-department")
  async def department_analysis(...):
      # Retorna: contratos por departamento, valores, etc
  
  @router.get("/summary")
  async def summary_report(...):
      # Retorna: resumo geral filtrado por permissões
  ```

### 2. Services/API (Backend Integration)

- [ ] Criar `frontend/src/services/reportsApi.js` com:
  - `getFinancialReport(params)` - GET /api/reports/financial
  - `getExpirationReport(params)` - GET /api/reports/expirations
  - `getDepartmentAnalysis(params)` - GET /api/reports/by-department
  - `getTypeAnalysis(params)` - GET /api/reports/by-type
  - `getSummary(params)` - GET /api/reports/summary
  - `exportPDF(reportType, params)` - POST /api/reports/export/pdf
  - `exportExcel(reportType, params)` - POST /api/reports/export/excel

### 3. Componentes de Relatórios

- [ ] `frontend/src/components/reports/FinancialReport.jsx`
  **Funcionalidades:**
  - Card com resumo financeiro:
    - Valor total de contratos ativos
    - Valor médio por contrato
    - Total de contratos
    - Maior contrato (valor)
    - Menor contrato (valor)
  - Gráfico de barras: Valores por tipo de contrato
  - Gráfico de pizza: Distribuição de valores por tipo
  - Tabela: Top 10 contratos por valor
  
  **Props:**
  ```javascript
  {
    data: {
      totalValue: 150000,
      avgValue: 5000,
      count: 30,
      contractsByType: { LEASE: 10, SERVICE: 15, OTHER: 5 },
      valuesByType: { LEASE: 80000, SERVICE: 60000, OTHER: 10000 },
      topContracts: [...]
    },
    loading: boolean
  }
  ```

- [ ] `frontend/src/components/reports/ExpirationReport.jsx`
  **Funcionalidades:**
  - Card com resumo de vencimentos:
    - Contratos expirando em 30 dias
    - Contratos expirando em 60 dias
    - Contratos expirando em 90 dias
    - Contratos já vencidos
  - Timeline de vencimentos (próximos 6 meses)
  - Tabela: Contratos expirando ordenados por data
  - Alert visual para contratos críticos (< 10 dias)
  
  **Props:**
  ```javascript
  {
    data: {
      expiring30: 5,
      expiring60: 12,
      expiring90: 20,
      expired: 3,
      timeline: [...],  // Vencimentos por mês
      contracts: [...]  // Lista de contratos expirando
    },
    loading: boolean
  }
  ```

- [ ] `frontend/src/components/reports/DepartmentAnalysis.jsx`
  **Funcionalidades:**
  - Gráfico de barras: Contratos por departamento
  - Gráfico de barras: Valores por departamento
  - Tabela: Departamentos com métricas:
    - Nome do departamento
    - Total de contratos
    - Valor total
    - Valor médio
    - Contratos ativos/inativos
  - Permite drill-down (clicar em departamento para ver detalhes)
  
  **Props:**
  ```javascript
  {
    data: {
      departments: [
        { name: 'IT', count: 20, totalValue: 50000, avgValue: 2500 },
        { name: 'HR', count: 15, totalValue: 30000, avgValue: 2000 },
        ...
      ]
    },
    loading: boolean,
    onDepartmentClick: (department) => void
  }
  ```

- [ ] `frontend/src/components/reports/ChartContracts.jsx`
  **Funcionalidades:**
  - Gráfico de linha: Contratos criados ao longo do tempo
  - Permite selecionar período (último mês, últimos 3 meses, último ano)
  - Usa Recharts
  - Responsivo
  
  **Props:**
  ```javascript
  {
    data: [
      { month: 'Jan', count: 10 },
      { month: 'Feb', count: 15 },
      ...
    ],
    title: string,
    color: string
  }
  ```

- [ ] `frontend/src/components/reports/ChartValues.jsx`
  **Funcionalidades:**
  - Gráfico de barras ou pizza: Valores por categoria
  - Animado
  - Tooltip com valores formatados (€)
  - Usa Recharts
  
  **Props:**
  ```javascript
  {
    data: [
      { name: 'LEASE', value: 80000 },
      { name: 'SERVICE', value: 60000 },
      ...
    ],
    type: 'bar' | 'pie',
    title: string
  }
  ```

- [ ] `frontend/src/components/reports/ReportFilters.jsx`
  **Funcionalidades:**
  - Filtros:
    - Período (Date Range Picker)
    - Tipo de contrato (select)
    - Departamento (text ou select)
    - Status (select)
  - Botão "Aplicar Filtros"
  - Botão "Limpar Filtros"
  - Layout responsivo
  
  **Props:**
  ```javascript
  {
    filters: { startDate, endDate, type, department, status },
    onChange: (filters) => void,
    onApply: () => void,
    onClear: () => void
  }
  ```

### 4. Páginas

- [ ] `frontend/src/pages/reports/ReportsPage.jsx`
  **Layout (Dashboard de Relatórios):**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Berichte / Reports
    </Typography>
    
    <ReportFilters 
      filters={filters}
      onChange={handleFilterChange}
      onApply={handleApplyFilters}
      onClear={handleClearFilters}
    />
    
    <Grid container spacing={3} sx={{ mt: 2 }}>
      {/* Cards de resumo */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total Contracts</Typography>
            <Typography variant="h4">{summary.totalContracts}</Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total Value</Typography>
            <Typography variant="h4">€ {summary.totalValue}</Typography>
          </CardContent>
        </Card>
      </Grid>
      
      {/* Gráficos */}
      <Grid item xs={12} md={6}>
        <ChartContracts data={contractsOverTime} />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <ChartValues data={valuesByType} type="pie" />
      </Grid>
      
      {/* Botões de exportação */}
      <Grid item xs={12}>
        <Button 
          variant="contained" 
          startIcon={<PictureAsPdfIcon />}
          onClick={handleExportPDF}
        >
          PDF exportieren / Export PDF
        </Button>
        <Button 
          variant="outlined" 
          startIcon={<TableChartIcon />}
          onClick={handleExportExcel}
          sx={{ ml: 2 }}
        >
          Excel exportieren / Export Excel
        </Button>
      </Grid>
    </Grid>
  </Container>
  ```

- [ ] `frontend/src/pages/reports/FinancialReportPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Finanzbericht / Financial Report
    </Typography>
    
    <ReportFilters {...} />
    
    <FinancialReport data={financialData} loading={loading} />
  </Container>
  ```

- [ ] `frontend/src/pages/reports/ExpirationReportPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Ablaufbericht / Expiration Report
    </Typography>
    
    <ReportFilters {...} />
    
    <ExpirationReport data={expirationData} loading={loading} />
  </Container>
  ```

- [ ] `frontend/src/pages/reports/DepartmentReportPage.jsx`
  **Layout:**
  ```jsx
  <Container>
    <Typography variant="h4" gutterBottom>
      Abteilungsanalyse / Department Analysis
    </Typography>
    
    <DepartmentAnalysis 
      data={departmentData} 
      loading={loading}
      onDepartmentClick={handleDepartmentClick}
    />
  </Container>
  ```

### 5. Routing

- [ ] Atualizar `frontend/src/App.jsx`:
  ```jsx
  <Route
    path="reports"
    element={
      <RequirePermission permission="reports:view">
        <ReportsPage />
      </RequirePermission>
    }
  />
  <Route
    path="reports/financial"
    element={
      <RequirePermission permission="reports:view">
        <FinancialReportPage />
      </RequirePermission>
    }
  />
  <Route
    path="reports/expirations"
    element={
      <RequirePermission permission="reports:view">
        <ExpirationReportPage />
      </RequirePermission>
    }
  />
  <Route
    path="reports/department"
    element={
      <RequirePermission permission="reports:view">
        <DepartmentReportPage />
      </RequirePermission>
    }
  />
  ```

### 6. Sidebar Menu

- [ ] Menu "Reports" já existe no Sidebar
- [ ] Visível para roles com permissão `reports:view`:
  - Level 5 (DIRECTOR) - vê todos relatórios
  - Level 4 (DEPARTMENT_ADM) - vê relatórios do departamento
  - Level 2 (TEAM_LEAD) - vê relatórios do time
- [ ] Submenu (opcional):
  - Reports Overview
  - Financial Report
  - Expiration Report
  - Department Analysis

---

## 🔐 REGRAS DE PERMISSÕES

### Visualização de Relatórios (reports:view)

- **Level 5 (DIRECTOR):** Vê TODOS relatórios (empresa toda)
- **Level 4 (DEPARTMENT_ADM):** Vê relatórios do departamento (COM valores)
- **Level 2 (TEAM_LEAD):** Vê relatórios do time
- **Level 3 (DEPARTMENT_USER):** Vê relatórios do departamento (SEM valores financeiros)
- **Level 1 (STAFF/READ_ONLY):** NÃO vê relatórios

### Exportação (reports:export)

- **Level 5, 4:** Podem exportar
- **Outros:** NÃO podem exportar

---

## 🎯 PRIORIDADES

### Prioridade ALTA (fazer primeiro)

1. **Backend:** Criar endpoints de relatórios (se não existem)
2. reportsApi.js (API calls)
3. ReportsPage.jsx (dashboard de relatórios)
4. ChartContracts.jsx (gráfico de contratos)
5. ChartValues.jsx (gráfico de valores)

### Prioridade MÉDIA (depois)

6. FinancialReport.jsx (relatório financeiro)
7. ExpirationReport.jsx (relatório de vencimentos)
8. DepartmentAnalysis.jsx (análise por departamento)
9. ReportFilters.jsx (filtros avançados)
10. FinancialReportPage.jsx

### Prioridade BAIXA (polimento)

11. ExpirationReportPage.jsx
12. DepartmentReportPage.jsx
13. Exportação PDF/Excel
14. Drill-down em gráficos
15. Gráficos avançados (combinados, área, etc)

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

Sprint 9 estará completa quando:

- [ ] Dashboard de relatórios funcional
- [ ] Gráficos de contratos ao longo do tempo exibidos
- [ ] Gráficos de valores por tipo exibidos
- [ ] Relatório financeiro com cards e gráficos funcionando
- [ ] Relatório de vencimentos com timeline funcionando
- [ ] Análise por departamento funcionando
- [ ] Filtros avançados (período, tipo, departamento) aplicando corretamente
- [ ] Exportação para PDF funcionando
- [ ] Exportação para Excel funcionando
- [ ] Permissões respeitadas (valores financeiros ocultos para Level 3)
- [ ] Loading states em todas operações
- [ ] Error handling em todas API calls
- [ ] Gráficos responsivos

---

## 🚀 COMO COMEÇAR

### 1. **Backend: Criar endpoints de relatórios** (se não existem)

```python
# backend/app/routers/reports.py

@router.get("/summary")
async def get_summary_report(...):
    # Filtra por permissões do usuário
    # Retorna: totalContracts, totalValue, activeContracts, etc
    
@router.get("/financial")
async def get_financial_report(...):
    # Relatório financeiro completo
    
@router.get("/expirations")
async def get_expiration_report(...):
    # Contratos expirando
```

### 2. Criar reportsApi.js:

- Implementar 7 funções (summary, financial, expirations, etc)

### 3. Implementar ReportsPage (dashboard):

- Cards de resumo
- Gráficos básicos (Recharts)
- Filtros

### 4. Implementar gráficos individuais:

- ChartContracts (linha)
- ChartValues (barras/pizza)

### 5. Implementar relatórios específicos:

- FinancialReport
- ExpirationReport
- DepartmentAnalysis

### 6. Testar com diferentes roles:

- director@test.com (Level 5) - vê tudo
- department_adm@test.com (Level 4) - vê departamento com valores
- department_user@test.com (Level 3) - vê departamento SEM valores
- staff@test.com (Level 1) - NÃO vê relatórios

---

## 📚 ARQUIVOS DE REFERÊNCIA

- Backend dashboard: `backend/app/routers/dashboard.py` (exemplo de agregação)
- Frontend Dashboard: `frontend/src/pages/Dashboard.jsx` (exemplo de gráficos)
- Recharts docs: https://recharts.org/

---

## 🎯 META

Ao final da Sprint 9, o usuário deverá conseguir:

1. **Login como DIRECTOR, DEPARTMENT_ADM ou TEAM_LEAD**
2. **Ver menu "Reports"** no sidebar
3. **Acessar dashboard de relatórios**
4. **Ver resumo** (total contratos, valores, etc)
5. **Ver gráficos** (contratos ao longo do tempo, valores por tipo)
6. **Aplicar filtros** (período, tipo, departamento)
7. **Acessar relatório financeiro** com análise detalhada
8. **Acessar relatório de vencimentos** com timeline
9. **Acessar análise por departamento** com drill-down
10. **Exportar relatórios** para PDF e Excel
11. **Ver que Level 3** NÃO vê valores financeiros nos relatórios

---

**Pronto para começar! Vamos implementar a Sprint 9 passo a passo, seguindo as prioridades definidas.**

---

## 🎉 CONCLUSÃO DO PROJETO

Ao completar a Sprint 9, o **Vertrag-MGS** estará **100% funcional** com todas as funcionalidades planejadas:

✅ Sprint 1: Setup + Autenticação  
✅ Sprint 2: Dashboard por Role  
✅ Sprint 3: CRUD de Contratos  
✅ Sprint 4: Alertas + Notificações  
✅ Sprint 5: Upload + Import de PDFs  
✅ Sprint 6: Aprovações (Workflow)  
✅ Sprint 7: Gerenciamento de Usuários  
✅ Sprint 8: Sistema Admin + Configurações  
✅ Sprint 9: Relatórios + Estatísticas  

**Projeto completo e pronto para produção!** 🚀
