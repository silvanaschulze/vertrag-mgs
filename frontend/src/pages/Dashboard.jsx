/**
 * Dashboard Page - Página do Dashboard
 * 
 * Renderiza o dashboard apropriado baseado no role do usuário.
 * Cada role tem um componente de dashboard específico com widgets adequados.
 * 
 * Rendert das entsprechende Dashboard basierend auf der Benutzerrolle.
 * Jede Rolle hat eine spezifische Dashboard-Komponente mit passenden Widgets.
 */

import { useAuthStore } from '../store/authStore';
import DashboardSystemAdmin from '../components/dashboard/DashboardSystemAdmin';
import DashboardDirector from '../components/dashboard/DashboardDirector';
import DashboardDepartmentAdm from '../components/dashboard/DashboardDepartmentAdm';
import DashboardDepartmentUser from '../components/dashboard/DashboardDepartmentUser';
import DashboardTeamLead from '../components/dashboard/DashboardTeamLead';
import DashboardStaff from '../components/dashboard/DashboardStaff';

/**
 * Mapeamento de roles para componentes de dashboard
 * Zuordnung von Rollen zu Dashboard-Komponenten
 */
const DASHBOARD_COMPONENTS = {
  SYSTEM_ADMIN: DashboardSystemAdmin,
  DIRECTOR: DashboardDirector,
  DEPARTMENT_ADM: DashboardDepartmentAdm,
  DEPARTMENT_USER: DashboardDepartmentUser,
  TEAM_LEAD: DashboardTeamLead,
  STAFF: DashboardStaff,
  READ_ONLY: DashboardStaff  // READ_ONLY usa o mesmo dashboard que STAFF
};

/**
 * Página principal do Dashboard
 * Dashboard-Hauptseite
 * 
 * @returns {JSX.Element} Componente de dashboard apropriado / Passende Dashboard-Komponente
 */
export default function Dashboard() {
  const { user } = useAuthStore();

  // Se não houver usuário, não renderiza nada (PrivateRoute já redireciona)
  if (!user || !user.role) {
    return null;
  }

  // Seleciona o componente apropriado baseado no role
  const DashboardComponent = DASHBOARD_COMPONENTS[user.role] || DashboardStaff;

  return <DashboardComponent />;
}
