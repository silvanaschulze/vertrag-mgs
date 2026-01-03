/**
 * RequirePermission - Proteção por Permissão / Berechtigungsschutz
 * 
 * Protege componentes que exigem permissão específica
 * Schützt Komponenten, die spezifische Berechtigung erfordern
 * 
 * Uso / Verwendung:
 * <RequirePermission permission="users:view">
 *   <UsersPage />
 * </RequirePermission>
 */
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const RequirePermission = ({ permission, children, fallback = null }) => {
  const { isAllowed } = useAuthStore();

  // Verifica se tem a permissão necessária
  // Prüft, ob erforderliche Berechtigung vorhanden ist
  const hasPermission = isAllowed(permission);

  // Se não tiver permissão
  // Wenn keine Berechtigung vorhanden
  if (!hasPermission) {
    // Se forneceu fallback, mostra ele / Wenn Fallback bereitgestellt, anzeigen
    if (fallback) {
      return fallback;
    }
    
    // Senão, redireciona para página 403 / Sonst zu 403-Seite umleiten
    return <Navigate to="/unauthorized" replace />;
  }

  // Se tem permissão, mostra o conteúdo / Wenn Berechtigung, Inhalt anzeigen
  return children;
};

export default RequirePermission;
