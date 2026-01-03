/**
 * PrivateRoute - Proteção de Rotas / Routenschutz
 * 
 * Protege rotas que exigem autenticação
 * Schützt Routen, die Authentifizierung erfordern
 * 
 * Uso / Verwendung:
 * <PrivateRoute>
 *   <Dashboard />
 * </PrivateRoute>
 */
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const PrivateRoute = ({ children }) => {
  const { token, user } = useAuthStore();

  // Verifica se está autenticado / Prüft Authentifizierung
  const isAuthenticated = token && user;

  // Se não estiver autenticado, redireciona para login
  // Wenn nicht authentifiziert, zu Login umleiten
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Se autenticado, mostra a página / Wenn authentifiziert, Seite anzeigen
  return children;
};

export default PrivateRoute;
