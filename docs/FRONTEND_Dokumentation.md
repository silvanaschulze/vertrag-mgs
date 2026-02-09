# Frontend Technische Dokumentation - Vertrag-MGS
# Documentação Técnica Frontend - Vertrag-MGS

**Erstellt:** 15. Januar 2026  
**Criado:** 15 de janeiro de 2026  
**Version:** 1.0  

---

## 📑 Inhaltsverzeichnis / Índice

1. [Projektübersicht / Visão Geral do Projeto](#projektübersicht--visão-geral-do-projeto)
2. [Systemarchitektur / Arquitetura do Sistema](#systemarchitektur--arquitetura-do-sistema)
3. [Verzeichnisstruktur / Estrutura de Diretórios](#verzeichnisstruktur--estrutura-de-diretórios)
4. [Technologie-Stack / Stack Tecnológico](#technologie-stack--stack-tecnológico)
5. [Hauptkomponenten / Componentes Principais](#hauptkomponenten--componentes-principais)
6. [Services und API Integration / Serviços e Integração de API](#services-und-api-integration--serviços-e-integração-de-api)
7. [Authentifizierung und Autorisierung / Autenticação e Autorização](#authentifizierung-und-autorisierung--autenticação-e-autorização)
8. [Routing und Navigation / Roteamento e Navegação](#routing-und-navigation--roteamento-e-navegação)
9. [State Management / Gerenciamento de Estado](#state-management--gerenciamento-de-estado)
10. [Entwicklung / Desenvolvimento](#entwicklung--desenvolvimento)
11. [Tests / Testes](#tests--testes)

---

## 📋 Projektübersicht / Visão Geral do Projeto

### Beschreibung / Descrição

**Deutsch:** React-basiertes Frontend für das Vertragsverwaltungssystem Vertrag-MGS. Bietet eine moderne, benutzerfreundliche Oberfläche für die Verwaltung von Verträgen mit rollenbasierter Zugriffskontrolle (RBAC), Dashboard-Widgets, CRUD-Operationen und PDF-Upload.

**Português:** Frontend baseado em React para o sistema de gerenciamento de contratos Vertrag-MGS. Fornece uma interface moderna e amigável para gerenciar contratos com controle de acesso baseado em funções (RBAC), widgets de dashboard, operações CRUD e upload de PDF.

### Hauptfunktionen / Funcionalidades Principais

- ✅ **JWT-Authentifizierung / Autenticação JWT** - Login seguro com tokens persistentes
- ✅ **Rollenbasierte Zugriffskontrolle / Controle de Acesso por Funções** (7 roles, 6 access levels)
- ✅ **Dashboard-Widgets por Role** - Painéis específicos para cada função
- ✅ **Vertrags-CRUD / CRUD de Contratos** - Criar, visualizar, editar, deletar contratos
- ✅ **Erweiterte Filter / Filtros Avançados** - Status, tipo, busca, paginação, ordenação
- ✅ **PDF-Upload / Upload de PDF** - Gerenciamento de documentos
- ✅ **Responsive Design / Design Responsivo** - Material-UI com tema customizado
- ✅ **Zweisprachige Labels / Labels Bilíngues** - Alemão/Português
- ✅ **Toast-Benachrichtigungen / Notificações Toast** - Feedback visual para ações

### Projektstandort / Localização do Projeto

```
/home/sschulze/projects/vertrag-mgs/frontend
```

### Entwicklungsserver / Servidor de Desenvolvimento

```bash
# Frontend starten / Iniciar frontend
cd /home/sschulze/projects/vertrag-mgs/frontend
npm run dev

# Läuft auf / Roda em: http://localhost:5173
```

---

## 🏗️ Systemarchitektur / Arquitetura do Sistema

### Architekturmuster / Padrão Arquitetural

Das Frontend folgt einer **modularen komponentenbasierten Architektur** mit klarer Trennung von Verantwortlichkeiten:

O frontend segue uma **arquitetura modular baseada em componentes** com clara separação de responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                      React Application                      │
│                  (React 18 + Vite 5)                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   UI Layer   │    │ Service Layer│    │  Store Layer │
│ (Components) │◄──►│   (APIs)     │◄──►│   (Zustand)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Pages     │    │    Axios     │    │ localStorage │
│  (Routing)   │    │ (HTTP Client)│    │ (Persist)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Architekturschichten / Camadas da Arquitetura

#### 1. **Präsentationsschicht / Camada de Apresentação**
- **Components:** Wiederverwendbare UI-Komponenten / Componentes reutilizáveis
- **Pages:** Seiten-Level-Komponenten mit Routing / Componentes de nível de página com roteamento
- **Theme:** Material-UI Theming und Styling / Temas e estilos do Material-UI

#### 2. **Geschäftslogik-Schicht / Camada de Lógica de Negócio**
- **Services:** API-Integration mit Backend / Integração de API com backend
- **Utils:** Hilfsfunktionen und Konstanten / Funções auxiliares e constantes
- **Hooks:** Custom React Hooks (zukünftig) / Hooks customizados do React (futuro)

#### 3. **Datenschicht / Camada de Dados**
- **Store:** Zustand State Management / Gerenciamento de estado com Zustand
- **localStorage:** Token- und User-Persistierung / Persistência de token e usuário

---

## 📁 Verzeichnisstruktur / Estrutura de Diretórios

### Vollständige Struktur / Estrutura Completa

```
frontend/
├── public/                          # Statische Assets / Assets estáticos
│   └── vite.svg                    # Vite Logo
│
├── src/                            # Quellcode / Código fonte
│   ├── assets/                     # Bilder, Icons / Imagens, ícones
│   │   └── react.svg
│   │
│   ├── components/                 # Wiederverwendbare Komponenten / Componentes reutilizáveis
│   │   ├── auth/                  # Authentifizierung / Autenticação
│   │   │   ├── PrivateRoute.jsx   # Route Guard für authentifizierte Routen / Guard para rotas autenticadas
│   │   │   └── RequirePermission.jsx # Permission Guard / Guard de permissões
│   │   │
│   │   ├── contracts/             # Vertrags-Komponenten / Componentes de contratos
│   │   │   ├── ContractTable.jsx  # DataGrid mit Paginierung / DataGrid com paginação
│   │   │   ├── ContractForm.jsx   # Formular (Create/Edit) / Formulário (Criar/Editar)
│   │   │   ├── ContractDetail.jsx # Detailansicht / Visualização detalhada
│   │   │   └── ContractFilters.jsx # Filter-Komponente / Componente de filtros
│   │   │
│   │   ├── dashboard/             # Dashboard-Widgets / Widgets de dashboard
│   │   │   ├── DashboardSystemAdmin.jsx  # Level 6 (Technisch / Técnico)
│   │   │   ├── DashboardDirector.jsx     # Level 5 (Gesamtunternehmen / Empresa toda)
│   │   │   ├── DashboardDepartmentAdm.jsx # Level 4 (Abteilung / Departamento)
│   │   │   ├── DashboardDepartmentUser.jsx # Level 3 (Abteilungsbenutzer / Usuário dept)
│   │   │   ├── DashboardTeamLead.jsx     # Level 2 (Teamleitung / Líder de time)
│   │   │   └── DashboardStaff.jsx        # Level 1 (Mitarbeiter / Colaborador)
│   │   │
│   │   ├── layout/                # Layout-Komponenten / Componentes de layout
│   │   │   ├── AppLayout.jsx      # Hauptlayout mit Sidebar / Layout principal com sidebar
│   │   │   ├── Sidebar.jsx        # Seitenmenü mit Rollenfilterung / Menu lateral com filtro de role
│   │   │   └── Header.jsx         # Obere Navigationsleiste / Barra de navegação superior
│   │   │
│   │   ├── ui/                    # Generische UI-Komponenten / Componentes genéricos
│   │   │   └── ConfirmDialog.jsx  # Bestätigungsdialog / Diálogo de confirmação
│   │   │
│   │   ├── alerts/                # Alert-Komponenten (Zukunft) / Componentes de alertas (futuro)
│   │   ├── approvals/             # Genehmigungs-Komponenten (Zukunft) / Componentes de aprovações (futuro)
│   │   └── upload/                # Upload-Komponenten (Zukunft) / Componentes de upload (futuro)
│   │
│   ├── pages/                     # Seiten (Routen) / Páginas (rotas)
│   │   ├── Login.jsx              # Login-Seite / Página de login
│   │   ├── Dashboard.jsx          # Dashboard (rendert nach Role) / Dashboard (renderiza por role)
│   │   ├── Unauthorized.jsx       # 403 Seite / Página 403
│   │   │
│   │   └── contracts/             # Vertragsseiten / Páginas de contratos
│   │       ├── ContractsList.jsx  # Listenseite mit Filtern / Página de listagem com filtros
│   │       ├── ContractCreate.jsx # Erstellungsseite / Página de criação
│   │       ├── ContractEdit.jsx   # Bearbeitungsseite / Página de edição
│   │       └── ContractView.jsx   # Detailansicht / Visualização detalhada
│   │
│   ├── services/                  # API-Services / Serviços de API
│   │   ├── api.js                 # Axios-Konfiguration + Interceptors / Configuração Axios + Interceptors
│   │   ├── authApi.js             # Auth-Endpunkte (login, logout) / Endpoints de autenticação
│   │   ├── contractsApi.js        # Vertrags-CRUD-Endpunkte / Endpoints CRUD de contratos
│   │   └── dashboardApi.js        # Dashboard-Statistiken / Estatísticas do dashboard
│   │
│   ├── store/                     # Zustand Stores / Stores Zustand
│   │   └── authStore.js           # Authentifizierungszustand (Token, User, Permissions) / Estado de autenticação
│   │
│   ├── utils/                     # Hilfsfunktionen / Funções auxiliares
│   │   ├── constants.js           # Konstanten (Status, Types, etc) / Constantes
│   │   └── permissions.js         # RBAC-Logik (Roles, Permissions) / Lógica RBAC
│   │
│   ├── theme/                     # Material-UI Theme / Tema Material-UI
│   │   └── theme.js               # Theme-Konfiguration / Configuração de tema
│   │
│   ├── hooks/                     # Custom Hooks (Zukunft) / Hooks customizados (futuro)
│   │
│   ├── App.jsx                    # Hauptkomponente mit Routing / Componente principal com rotas
│   ├── main.jsx                   # Einstiegspunkt (ReactDOM.render) / Ponto de entrada
│   ├── App.css                    # Globale Stile / Estilos globais
│   └── index.css                  # CSS-Reset / Reset CSS
│
├── .env                           # Umgebungsvariablen (NICHT committen) / Variáveis de ambiente (NÃO commitar)
├── .env.example                   # Beispiel-Umgebungsvariablen / Exemplo de variáveis de ambiente
├── .gitignore                     # Git-Ignore-Datei / Arquivo Git ignore
├── eslint.config.js               # ESLint-Konfiguration / Configuração ESLint
├── index.html                     # HTML-Vorlage / Template HTML
├── package.json                   # Node-Abhängigkeiten / Dependências Node
├── package-lock.json              # Locked Dependencies / Dependências travadas
├── vite.config.js                 # Vite-Konfiguration / Configuração Vite
└── README.md                      # Projekt-README / README do projeto
```

---

## 🚀 Technologie-Stack / Stack Tecnológico

### Core Framework / Framework Principal

```json
{
  "framework": "React 18.3.1",
  "buildTool": "Vite 5.4.10",
  "language": "JavaScript ES6+",
  "moduleSystem": "ES Modules"
}
```

### UI-Bibliothek / Biblioteca de UI

```json
{
  "uiFramework": "Material-UI (MUI) 7.3.6",
  "icons": "@mui/icons-material 7.3.6",
  "dataGrid": "@mui/x-data-grid 8.23.0",
  "styling": "@emotion/react + @emotion/styled 11.14.x"
}
```

**Justificativa / Justificativa:**
- ✅ Komponenten professionell und sofort einsatzbereit / Componentes profissionais prontos
- ✅ DataGrid exzellent für Vertragstabellen / DataGrid excelente para tabelas de contratos
- ✅ Vollständige Dokumentation / Documentação completa
- ✅ Anpassbares Theme (Light/Dark) / Tema customizável

### State Management / Gerenciamento de Estado

```json
{
  "stateManager": "Zustand 5.0.9",
  "persistence": "zustand/middleware (persist)",
  "storage": "localStorage"
}
```

**Justificativa / Justificativa:**
- ✅ Einfacher als Redux / Mais simples que Redux
- ✅ Keine Boilerplate / Sem boilerplate
- ✅ TypeScript-freundlich / Amigável ao TypeScript
- ✅ Eingebaute Persistenz / Persistência integrada

### Routing

```json
{
  "router": "React Router DOM 6.30.2",
  "routeGuards": "Custom (PrivateRoute, RequirePermission)"
}
```

### HTTP Client / Cliente HTTP

```json
{
  "httpClient": "Axios 1.13.2",
  "features": ["Interceptors", "Auto JWT Injection", "Error Handling"]
}
```

**Justificativa / Justificativa:**
- ✅ Request/Response Interceptors für JWT / para JWT
- ✅ Bessere Fehlerbehandlung als fetch / Melhor tratamento de erros que fetch
- ✅ Timeout-Unterstützung / Suporte a timeout

### Formular-Handling / Manipulação de Formulários

```json
{
  "formLibrary": "React Hook Form 7.69.0",
  "validation": "Zod 4.2.1",
  "resolver": "@hookform/resolvers 5.2.2"
}
```

**Justificativa / Justificativa:**
- ✅ Leistungsstarke formularvalidierung / Validação performática
- ✅ Weniger Re-Renders / Menos re-renders
- ✅ Zod für TypeScript-ähnliche Validierung / para validação tipo TypeScript

### Weitere Bibliotheken / Outras Bibliotecas

```json
{
  "notifications": "notistack 3.0.2",
  "dateUtils": "date-fns 4.1.0",
  "charts": "recharts 3.6.0",
  "dataFetching": "@tanstack/react-query 5.90.15",
  "fileUpload": "react-dropzone 14.3.8"
}
```

### Dev Dependencies / Dependências de Desenvolvimento

```json
{
  "linting": "eslint 9.13.0",
  "plugins": [
    "eslint-plugin-react 7.37.2",
    "eslint-plugin-react-hooks 5.0.0",
    "eslint-plugin-react-refresh 0.4.14"
  ],
  "globals": "globals 15.11.0",
  "buildPlugin": "@vitejs/plugin-react 4.3.3"
}
```

---

## 🧩 Hauptkomponenten / Componentes Principais

### 1. **Authentifizierung / Autenticação**

#### `PrivateRoute.jsx`
**Funktionalität / Funcionalidade:**
- Route Guard für authentifizierte Routen / Guard para rotas autenticadas
- Prüft ob Token und User vorhanden / Verifica se token e usuário existem
- Redirect zu /login wenn nicht authentifiziert / Redireciona para /login se não autenticado

**Verwendung / Uso:**
```jsx
<PrivateRoute>
  <AppLayout>
    <Dashboard />
  </AppLayout>
</PrivateRoute>
```

#### `RequirePermission.jsx`
**Funktionalität / Funcionalidade:**
- Permission Guard für bestimmte Aktionen / Guard de permissões para ações específicas
- Prüft ob User die erforderliche Berechtigung hat / Verifica se usuário tem permissão necessária
- Zeigt Unauthorized-Seite wenn keine Berechtigung / Mostra página não autorizada se sem permissão

**Verwendung / Uso:**
```jsx
<RequirePermission permission="contracts:delete_all">
  <DeleteButton />
</RequirePermission>
```

---

### 2. **Layout-Komponenten / Componentes de Layout**

#### `AppLayout.jsx`
**Funktionalität / Funcionalidade:**
- Hauptlayout mit Sidebar und Header / Layout principal com sidebar e header
- Container für alle geschützten Seiten / Container para todas páginas protegidas
- Responsive Design (Sidebar klappt auf mobil) / Design responsivo

**Struktur / Estrutura:**
```jsx
<Box sx={{ display: 'flex' }}>
  <Header />
  <Sidebar />
  <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
    {children} {/* Dashboard, Contracts, etc */}
  </Box>
</Box>
```

#### `Sidebar.jsx`
**Funktionalität / Funcionalidade:**
- Seitenmenü mit Navigation / Menu lateral com navegação
- Filtert Menüitems basierend auf Role / Filtra itens de menu por role
- Highlight aktiver Route / Destaca rota ativa
- Breite: 240px

**Menüitems und Berechtigungen / Itens de Menu e Permissões:**
```javascript
const menuItems = [
  { icon: DashboardIcon, label: 'Dashboard', path: '/app/dashboard', roles: 'all' },
  { icon: DescriptionIcon, label: 'Contracts', path: '/app/contracts', roles: 'contracts' },
  { icon: UploadFileIcon, label: 'Import', path: '/app/import', roles: 'import' },
  { icon: NotificationsIcon, label: 'Alerts', path: '/app/alerts', roles: 'alerts' },
  { icon: CheckCircleIcon, label: 'Approvals', path: '/app/approvals', roles: 'approvals' },
  { icon: PeopleIcon, label: 'Users', path: '/app/users', roles: 'users' },
  { icon: AssessmentIcon, label: 'Reports', path: '/app/reports', roles: 'reports' },
  { icon: SettingsIcon, label: 'System', path: '/app/system', roles: 'system' }
];
```

#### `Header.jsx`
**Funktionalität / Funcionalidade:**
- AppBar oben mit Logo und User-Info / Barra superior com logo e info do usuário
- User-Menü: Name, Role, Access Level, Logout
- Responsive / Responsivo

---

### 3. **Dashboard-Komponenten / Componentes de Dashboard**

Sechs separate Dashboard-Komponenten, eine für jede Role:  
Seis componentes de dashboard separados, um para cada função:

#### `DashboardSystemAdmin.jsx` (Level 6)
**Daten / Dados:**
- Technische Metriken / Métricas técnicas
- Gesamtzahl Verträge / Total de contratos
- Gesamtzahl Benutzer / Total de usuários
- Systemmetriken / Métricas de sistema

**Komponenten / Componentes:**
- Cards com KPIs técnicos
- Gráficos simples

#### `DashboardDirector.jsx` (Level 5)
**Daten / Dados:**
- Alle Verträge des Unternehmens / Todos contratos da empresa
- Finanzielle Gesamtwerte / Valores financeiros totais
- Verträge nach Abteilung / Contratos por departamento
- Kritische Warnungen / Alertas críticos

**Komponenten / Componentes:**
- Cards executivos
- Gráficos Pizza e Barras
- Timeline de vencimentos

#### `DashboardDepartmentAdm.jsx` (Level 4)
**Daten / Dados:**
- Verträge der Abteilung / Contratos do departamento
- Finanzwerte der Abteilung / Valores do departamento
- Benutzer der Abteilung / Usuários do departamento
- Genehmigungs-Pending / Aprovações pendentes

#### `DashboardDepartmentUser.jsx` (Level 3)
**Daten / Dados:**
- Verträge der Abteilung (nur Ansicht) / Contratos do departamento (só visualização)
- KEINE Finanzwerte / SEM valores financeiros
- Warnungen der Abteilung / Alertas do departamento

#### `DashboardTeamLead.jsx` (Level 2)
**Daten / Dados:**
- Verträge des Teams / Contratos do time
- Finanzwerte des Teams / Valores do time
- Team-Warnungen / Alertas do time

#### `DashboardStaff.jsx` (Level 1)
**Daten / Dados:**
- Nur eigene Verträge / Apenas próprios contratos
- Eigene Warnungen / Próprios alertas
- KEINE Diagramme / SEM gráficos

---

### 4. **Vertrags-Komponenten / Componentes de Contratos**

#### `ContractTable.jsx`
**Funktionalität / Funcionalidade:**
- MUI DataGrid mit Server-Side Paginierung / com paginação server-side
- Server-Side Sortierung / Ordenação server-side
- Dynamische Spalten (versteckt Finanzwerte für Levels 1,2,3,6) / Colunas dinâmicas
- Actions: View, Edit (wenn erlaubt), Delete (wenn erlaubt) / se permitido

**Props:**
```javascript
{
  contracts: Array,      // Liste der Verträge / Lista de contratos
  loading: boolean,      // Ladezustand / Estado de carregamento
  page: number,          // Aktuelle Seite / Página atual
  pageSize: number,      // Anzahl pro Seite / Itens por página
  totalRows: number,     // Gesamtzahl / Total
  onPageChange: func,    // Seite ändern / Mudar página
  onPageSizeChange: func,// Seitengröße ändern / Mudar tamanho
  onSortChange: func,    // Sortierung ändern / Mudar ordenação
  onView: func,          // Ansicht öffnen / Abrir visualização
  onEdit: func,          // Bearbeiten öffnen / Abrir edição
  onDelete: func         // Löschen / Deletar
}
```

**Spalten / Colunas:**
1. ID
2. Title / Título
3. Partner / Parceiro
4. Type / Tipo (Chip)
5. Status (Chip colorido)
6. Start Date / Data Início
7. End Date / Data Fim
8. Value / Valor (€) - **CONDICIONAL (Levels 4, 5 only)**
9. Actions / Ações

#### `ContractForm.jsx`
**Funktionalität / Funcionalidade:**
- Wiederverwendbares Formular für Create & Edit / Formulário reutilizável
- React Hook Form + Zod Validierung / validação
- Zweisprachige Labels (DE/PT) / Labels bilíngues

**Felder / Campos:**
- title (erforderlich / obrigatório)
- client_name (parceiro / Partner)
- contract_type (select)
- status (select)
- start_date (date picker)
- end_date (date picker)
- value (number)
- description (textarea)
- contact_person (opcional)
- contact_email (opcional)
- contact_phone (opcional)
- notes (opcional)

**Validierung / Validação:**
```javascript
const schema = z.object({
  title: z.string().min(3, 'Mindestens 3 Zeichen / Mínimo 3 caracteres'),
  client_name: z.string().min(1),
  contract_type: z.string(),
  status: z.string(),
  start_date: z.string(),
  end_date: z.string(),
  value: z.number().positive().optional()
});
```

#### `ContractDetail.jsx`
**Funktionalität / Funcionalidade:**
- Zeigt alle Vertragsdetails / Exibe todos detalhes do contrato
- Cards organisiert (Basic Info, Partner, Rent Steps, Notes, Audit)
- Finanzwerte konditional (nur Levels 4, 5) / Valores condicionais
- Rent Steps Tabelle

#### `ContractFilters.jsx`
**Funktionalität / Funcionalidade:**
- Filter für Status, Type, Suche / Filtros para status, tipo, busca
- Clear Filters Button
- Grid Layout responsivo

---

### 5. **UI-Komponenten / Componentes de UI**

#### `ConfirmDialog.jsx`
**Funktionalität / Funcionalidade:**
- Wiederverwendbarer Bestätigungsdialog / Diálogo de confirmação reutilizável
- Verwendet für Löschen von Verträgen / Usado para deletar contratos

**Props:**
```javascript
{
  open: boolean,
  title: string,
  message: string,
  confirmText: string,
  cancelText: string,
  severity: 'warning' | 'error' | 'info',
  onConfirm: func,
  onCancel: func
}
```

---

## 🔌 Services und API Integration / Serviços e Integração de API

### Axios-Konfiguration / Configuração Axios

#### `api.js`
**Funktionalität / Funcionalidade:**
- Axios-Instanz mit Base URL / Instância com URL base
- Request Interceptor (JWT-Token-Injektion) / Injeção automática de token JWT
- Response Interceptor (Fehlerbehandlung) / Tratamento de erros

**Code:**
```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
});

// REQUEST INTERCEPTOR
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

### API Services / Serviços de API

#### `authApi.js`
**Endpunkte / Endpoints:**
```javascript
{
  login: (email, password) => POST /auth/login,
  logout: () => POST /auth/logout,
  getCurrentUser: () => GET /auth/me
}
```

#### `contractsApi.js`
**Endpunkte / Endpoints:**
```javascript
{
  getContracts: (params) => GET /contracts/?page=1&page_size=25&status=aktiv,
  getContract: (id) => GET /contracts/{id},
  createContract: (data) => POST /contracts/,
  updateContract: (id, data) => PUT /contracts/{id},
  deleteContract: (id) => DELETE /contracts/{id}
}
```

**Paginierung / Paginação:**
```javascript
const result = await contractsApi.getContracts({
  page: 1,
  page_size: 25,
  status: 'ACTIVE',
  contract_type: 'LEASE',
  search: 'office',
  sort_by: '-start_date' // Descending
});

// Returns / Retorna:
{
  items: Contract[],
  total: number,
  page: number,
  page_size: number
}
```

#### `dashboardApi.js`
**Endpunkte / Endpoints:**
```javascript
{
  getStats: () => GET /dashboard/stats
}
```

**Rückgabe automatisch gefiltert nach Role:**  
**Retorno automaticamente filtrado por role:**
- Level 6: Technische Stats / Estatísticas técnicas
- Level 5: Gesamtunternehmen / Empresa toda
- Level 4: Abteilung / Departamento
- Level 3: Abteilung (ohne Finanzwerte) / sem valores
- Level 2: Team
- Level 1: Eigene Verträge / Próprios contratos

---

## 🔐 Authentifizierung und Autorisierung / Autenticação e Autorização

### Rollenbasierte Zugriffskontrolle / Controle de Acesso por Funções

#### 7 Rollen / 7 Funções

```javascript
export const UserRole = {
  SYSTEM_ADMIN: 'SYSTEM_ADMIN',        // Level 6
  DIRECTOR: 'DIRECTOR',                // Level 5
  DEPARTMENT_ADM: 'DEPARTMENT_ADM',    // Level 4
  DEPARTMENT_USER: 'DEPARTMENT_USER',  // Level 3
  TEAM_LEAD: 'TEAM_LEAD',              // Level 2
  STAFF: 'STAFF',                      // Level 1-2
  READ_ONLY: 'READ_ONLY'               // Level 1
};
```

#### 6 Access Levels / 6 Níveis de Acesso

```javascript
export const AccessLevel = {
  SYSTEM: 6,              // Config, Logs, Backups
  COMPANY: 5,             // Gesamtunternehmen / Empresa toda
  DEPARTMENT: 4,          // Abteilung + Finanzwerte / Departamento + valores
  DEPARTMENT_RESTRICTED: 3, // Abteilung ohne Finanzwerte / Sem valores
  TEAM: 2,                // Team
  OWN: 1                  // Nur eigene Verträge / Próprios contratos
};
```

---

### Berechtigungsmatrix / Matriz de Permissões

**Definiert in:** `src/utils/permissions.js`  
**Definido em:** `src/utils/permissions.js`

```javascript
export const ROLE_PERMISSIONS = {
  SYSTEM_ADMIN: {
    level: 6,
    permissions: ['users:*', 'alerts:*', 'system:config', 'system:logs', 'system:backups'],
    menu: ['dashboard', 'alerts', 'users', 'system']
  },
  DIRECTOR: {
    level: 5,
    permissions: [
      'contracts:view_all', 'contracts:edit_all', 'contracts:delete_all',
      'contracts:import', 'approvals:approve_all', 'users:view',
      'alerts:view_all', 'reports:view_all'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  DEPARTMENT_ADM: {
    level: 4,
    permissions: [
      'contracts:view_department', 'contracts:edit_department', 'contracts:delete_department',
      'contracts:import', 'approvals:approve_department',
      'users:view_department', 'users:manage_department',
      'alerts:view_department', 'reports:view_department'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  DEPARTMENT_USER: {
    level: 3,
    permissions: [
      'contracts:view_department', 'contracts:edit_department',
      'alerts:view_department', 'reports:view_basic'
    ],
    menu: ['dashboard', 'contracts', 'alerts', 'reports']
  },
  TEAM_LEAD: {
    level: 2,
    permissions: [
      'contracts:view_team', 'contracts:edit_team', 'contracts:import',
      'alerts:view_team', 'reports:view_team'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'reports']
  },
  STAFF: {
    level: 1,
    permissions: ['contracts:view_own', 'contracts:edit_own', 'alerts:view_own'],
    menu: ['dashboard', 'contracts', 'alerts']
  },
  READ_ONLY: {
    level: 1,
    permissions: ['contracts:view_own', 'alerts:view_own'],
    menu: ['dashboard', 'contracts', 'alerts']
  }
};
```

---

### Hilfsfunktionen / Funções Auxiliares

#### `hasPermission(userRole, permission)`
**Beschreibung / Descrição:**  
Prüft ob eine Role eine bestimmte Berechtigung hat.  
Verifica se uma função tem uma permissão específica.

**Beispiel / Exemplo:**
```javascript
hasPermission('DIRECTOR', 'contracts:delete_all') // true
hasPermission('STAFF', 'contracts:delete_all')    // false
```

#### `canAccessMenu(userRole, menuItem)`
**Beschreibung / Descrição:**  
Prüft ob eine Role einen Menüpunkt sehen darf.  
Verifica se uma função pode ver um item de menu.

**Beispiel / Exemplo:**
```javascript
canAccessMenu('SYSTEM_ADMIN', 'system')   // true
canAccessMenu('SYSTEM_ADMIN', 'contracts') // false (Level 6 vê apenas técnico)
canAccessMenu('DIRECTOR', 'contracts')    // true
```

#### `getAccessLevel(userRole)`
**Beschreibung / Descrição:**  
Gibt Access Level einer Role zurück.  
Retorna o nível de acesso de uma função.

**Beispiel / Exemplo:**
```javascript
getAccessLevel('DIRECTOR')       // 5
getAccessLevel('STAFF')          // 1
```

---

### Auth Store / Store de Autenticação

**Datei / Arquivo:** `src/store/authStore.js`

#### State / Estado

```javascript
{
  token: string | null,
  user: {
    id: number,
    email: string,
    name: string,
    role: UserRole,
    access_level: number,
    department_id: number | null,
    team_id: number | null
  } | null
}
```

#### Actions / Ações

```javascript
{
  login: (token, user) => void,
  logout: () => void,
  isAllowed: (permission) => boolean,
  canViewMenu: (menuItem) => boolean,
  getUserLevel: () => number,
  isAuthenticated: () => boolean
}
```

#### Persistierung / Persistência

- **Storage:** localStorage
- **Key:** `auth-storage`
- **Überleben:** Browser-Refresh / Refresh do navegador

---

## 🛤️ Routing und Navigation / Roteamento e Navegação

### Route-Konfiguration / Configuração de Rotas

**Datei / Arquivo:** `src/App.jsx`

#### Öffentliche Routen / Rotas Públicas

```javascript
/login          → Login.jsx
/unauthorized   → Unauthorized.jsx
```

#### Geschützte Routen / Rotas Protegidas

```javascript
/app/dashboard         → Dashboard.jsx (renderiza por role)
/app/contracts         → ContractsList.jsx
/app/contracts/new     → ContractCreate.jsx
/app/contracts/:id     → ContractView.jsx
/app/contracts/:id/edit → ContractEdit.jsx

/app/import           → ImportPage (Requer contracts:import)
/app/alerts           → AlertsPage
/app/approvals        → ApprovalsPage (Requer approvals:view)
/app/users            → UsersPage (Requer users:view)
/app/system           → SystemPage (Requer system:config)
```

---

### Route Guards / Guards de Rota

#### `PrivateRoute`
**Verwendung / Uso:**
```jsx
<Route path="/app/*" element={
  <PrivateRoute>
    <AppLayout>
      <Routes>...</Routes>
    </AppLayout>
  </PrivateRoute>
}>
```

**Logik / Lógica:**
1. Prüft `isAuthenticated()`
2. Wenn false → redirect `/login`
3. Wenn true → renderiza children

#### `RequirePermission`
**Verwendung / Uso:**
```jsx
<RequirePermission permission="contracts:import">
  <ImportPage />
</RequirePermission>
```

**Logik / Lógica:**
1. Prüft `isAllowed(permission)`
2. Wenn false → redirect `/unauthorized`
3. Wenn true → renderiza children

---

## 🗄️ State Management / Gerenciamento de Estado

### Zustand Store

#### Auth Store
**Datei / Arquivo:** `src/store/authStore.js`

**Funktionen / Funções:**
- Token-Persistierung / Persistência de token
- User-Daten / Dados do usuário
- Permission Checks / Verificações de permissões
- localStorage Sync

**Hooks-Verwendung / Uso de Hooks:**
```javascript
import { useAuthStore } from '../store/authStore';

function MyComponent() {
  const { user, logout, isAllowed, canViewMenu } = useAuthStore();
  
  const canDeleteAll = isAllowed('contracts:delete_all');
  const canSeeContracts = canViewMenu('contracts');
  
  return <div>Welcome {user?.name}</div>;
}
```

---

## 💻 Entwicklung / Desenvolvimento

### Installation / Instalação

```bash
cd /home/sschulze/projects/vertrag-mgs/frontend
npm install
```

### Entwicklungsserver / Servidor de Desenvolvimento

```bash
npm run dev
# Läuft auf / Roda em: http://localhost:5173
```

### Build für Produktion / Build para Produção

```bash
npm run build
# Output: dist/
```

### Linting

```bash
npm run lint
```

### Preview Production Build / Visualizar Build de Produção

```bash
npm run preview
```

---

### Umgebungsvariablen / Variáveis de Ambiente

**Datei / Arquivo:** `.env`

```dotenv
VITE_API_URL=http://localhost:8000/api
```

**WICHTIG / IMPORTANTE:**  
`.env` ist in `.gitignore` - NIEMALS committen!  
`.env` está no `.gitignore` - NUNCA fazer commit!

---

### Entwicklungs-Workflow / Fluxo de Desenvolvimento

1. **Backend starten / Iniciar backend:**
   ```bash
   cd /home/sschulze/projects/vertrag-mgs
   source .venv/bin/activate
   cd backend
   uvicorn main:app --reload
   ```

2. **Frontend starten / Iniciar frontend:**
   ```bash
   cd /home/sschulze/projects/vertrag-mgs/frontend
   npm run dev
   ```

3. **Testen / Testar:**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

---

## 🧪 Tests / Testes

### Aktueller Stand / Estado Atual

**Frontend-Tests:** Noch nicht implementiert / Ainda não implementados

### Geplante Test-Strategie / Estratégia de Testes Planejada

```json
{
  "unitTests": "Vitest",
  "componentTests": "@testing-library/react",
  "e2eTests": "Playwright",
  "coverage": "vitest coverage"
}
```

---

## 📊 Metriken / Métricas

### Codebase-Statistiken / Estatísticas da Codebase

```
Komponenten: 20+
Services: 4
Store: 1
Utils: 2
Pages: 8
Zeilen Code: ~3.000 (JavaScript/JSX)
Linhas de código: ~3.000 (JavaScript/JSX)
```

---

## 🚀 Nächste Schritte / Próximos Passos

### Sprint 4: Alertas + Notificações
- AlertsList.jsx
- AlertBadge.jsx
- Echtzeit-Updates / Atualizações em tempo real

### Sprint 5: Upload + Import de PDFs
- DropzoneUpload.jsx
- PDFPreview.jsx
- Import-Workflow

### Sprint 6: Aprovações
- ApprovalsList.jsx
- ApprovalActions.jsx
- Workflow multi-step

### Sprint 7: Usuários
- UsersList.jsx
- UserManage.jsx
- CRUD de usuários

### Sprint 8: Sistema Admin
- SystemConfig.jsx
- SystemLogs.jsx
- Backups.jsx

### Sprint 9: Relatórios
- ReportsDashboard.jsx
- Charts avançados
- Export para PDF/Excel

---

## 📚 Dokumentations-Referenzen / Referências de Documentação

- **React:** https://react.dev/
- **Material-UI:** https://mui.com/
- **Zustand:** https://zustand-demo.pmnd.rs/
- **React Router:** https://reactrouter.com/
- **React Hook Form:** https://react-hook-form.com/
- **Zod:** https://zod.dev/
- **Axios:** https://axios-http.com/
- **Vite:** https://vitejs.dev/

---

**Ende der Dokumentation / Fim da Documentação**  
**Letzte Aktualisierung / Última Atualização:** 15. Januar 2026 / 15 de janeiro de 2026
