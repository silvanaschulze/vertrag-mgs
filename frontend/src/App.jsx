/**
 * App - Configuração de Rotas / Routenkonfiguration
 * 
 * Define todas as rotas da aplicação com proteção
 * Definiert alle Anwendungsrouten mit Schutz
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import theme from './theme/theme';
import PrivateRoute from './components/auth/PrivateRoute';
import RequirePermission from './components/auth/RequirePermission';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';

// Páginas temporárias (vamos criar depois)
// Temporäre Seiten (werden später erstellt)
const DashboardPage = () => <div><h1>Dashboard</h1><p>Em construção / In Arbeit</p></div>;
const ContractsPage = () => <div><h1>Verträge / Contracts</h1><p>Em construção / In Arbeit</p></div>;
const ImportPage = () => <div><h1>Import</h1><p>Em construção / In Arbeit</p></div>;
const AlertsPage = () => <div><h1>Warnungen / Alerts</h1><p>Em construção / In Arbeit</p></div>;
const ApprovalsPage = () => <div><h1>Genehmigungen / Approvals</h1><p>Em construção / In Arbeit</p></div>;
const UsersPage = () => <div><h1>Benutzer / Users</h1><p>Em construção / In Arbeit</p></div>;
const SystemPage = () => <div><h1>System</h1><p>Em construção / In Arbeit</p></div>;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider 
        maxSnack={3} 
        anchorOrigin={{ 
          vertical: 'top', 
          horizontal: 'right' 
        }}
      >
        <BrowserRouter>
          <Routes>
            {/* Rota Raiz - Redireciona para Dashboard / Wurzelroute - Umleitung zu Dashboard */}
            <Route path="/" element={<Navigate to="/app/dashboard" replace />} />

            {/* Login - Rota Pública / Login - Öffentliche Route */}
            <Route path="/login" element={<Login />} />

            {/* Unauthorized - Rota Pública / Unauthorized - Öffentliche Route */}
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Rotas Privadas com Layout / Private Routen mit Layout */}
            <Route
              path="/app/*"
              element={
                <PrivateRoute>
                  <AppLayout>
                    <Routes>
                      {/* Dashboard - Todos podem acessar / Dashboard - Alle können zugreifen */}
                      <Route path="dashboard" element={<DashboardPage />} />

                      {/* Contratos - Todos podem acessar / Verträge - Alle können zugreifen */}
                      <Route path="contracts" element={<ContractsPage />} />

                      {/* Import - Requer permissão / Import - Berechtigung erforderlich */}
                      <Route
                        path="import"
                        element={
                          <RequirePermission permission="contracts:import">
                            <ImportPage />
                          </RequirePermission>
                        }
                      />

                      {/* Alertas - Todos podem acessar / Warnungen - Alle können zugreifen */}
                      <Route path="alerts" element={<AlertsPage />} />

                      {/* Aprovações - Requer permissão / Genehmigungen - Berechtigung erforderlich */}
                      <Route
                        path="approvals"
                        element={
                          <RequirePermission permission="approvals:view">
                            <ApprovalsPage />
                          </RequirePermission>
                        }
                      />

                      {/* Usuários - Requer permissão / Benutzer - Berechtigung erforderlich */}
                      <Route
                        path="users"
                        element={
                          <RequirePermission permission="users:view">
                            <UsersPage />
                          </RequirePermission>
                        }
                      />

                      {/* Sistema - Requer permissão / System - Berechtigung erforderlich */}
                      <Route
                        path="system"
                        element={
                          <RequirePermission permission="system:config">
                            <SystemPage />
                          </RequirePermission>
                        }
                      />

                      {/* 404 - Redireciona para Dashboard / 404 - Umleitung zu Dashboard */}
                      <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
                    </Routes>
                  </AppLayout>
                </PrivateRoute>
              }
            />

            {/* 404 Global - Redireciona para Login / Globale 404 - Umleitung zu Login */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
