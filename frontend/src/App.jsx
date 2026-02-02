import UsersPage from './pages/users/UsersPage';
import UserManage from './pages/users/UserManage';
// ...existing code...
import AlertsPage from './pages/alerts/AlertsPage';
import RequirePermission from './components/auth/RequirePermission';
import PrivateRoute from './components/auth/PrivateRoute';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import ContractsList from './pages/contracts/ContractsList';
import ContractCreate from './pages/contracts/ContractCreate';
import ContractView from './pages/contracts/ContractView';
import ContractEdit from './pages/contracts/ContractEdit';
import Unauthorized from './pages/Unauthorized';
import Login from './pages/Login';
/**
 * App - Configuração de Rotas / Routenkonfiguration
 * 
 * Define todas as rotas da aplicação com proteção
 * Definiert alle Anwendungsrouten mit Schutz
 */

import ContractImport from './pages/contracts/ContractImport';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import theme from './theme/theme';
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
                      <Route path="dashboard" element={<Dashboard />} />

                      {/* Contratos - Todos podem acessar / Verträge - Alle können zugreifen */}
                      <Route path="contracts" element={<ContractsList />} />
                      <Route path="contracts/new" element={<ContractCreate />} />
                      <Route path="contracts/:id" element={<ContractView />} />
                      <Route path="contracts/:id/edit" element={<ContractEdit />} />

                      {/* Import - Requer permissão / Import - Berechtigung erforderlich */}
                      <Route
                        path="import"
                        element={
                          <RequirePermission permission="contracts:import">
                            <ContractImport />
                          </RequirePermission>
                        }
                      />

                      {/* Alertas - Todos podem acessar / Warnungen - Alle können zugreifen */}
                      <Route path="alerts" element={<AlertsPage />} />


                      {/* Usuários - CRUD completo */}
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
                          <RequirePermission permission="users:manage_all">
                            <UserManage />
                          </RequirePermission>
                        }
                      />
                      <Route
                        path="users/:id/edit"
                        element={
                          <RequirePermission permission="users:manage_all">
                            <UserManage />
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
