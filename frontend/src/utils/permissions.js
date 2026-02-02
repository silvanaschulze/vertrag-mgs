/**
 * Sistema de Roles e Permissões / Rollen- und Berechtigungssystem
 * 
 * Define todas as roles, access levels e permissões do sistema
 * DEVE SER IGUAL AO BACKEND (backend/app/models/user.py)
 */

// Roles do sistema / Systemrollen
export const UserRole = {
  SYSTEM_ADMIN: 'SYSTEM_ADMIN',        // Level 6 - Admin técnico
  DIRECTOR: 'DIRECTOR',                // Level 5 - Acesso toda empresa
  DEPARTMENT_ADM: 'DEPARTMENT_ADM',    // Level 4 - Admin departamento
  DEPARTMENT_USER: 'DEPARTMENT_USER',  // Level 3 - Usuário departamento
  TEAM_LEAD: 'TEAM_LEAD',              // Level 2 - Líder de time
  STAFF: 'STAFF',                      // Level 1-2 - Colaborador
  READ_ONLY: 'READ_ONLY'               // Level 1 - Somente leitura
};

// Access Levels / Zugriffsebenen
export const AccessLevel = {
  SYSTEM: 6,              // Config, logs, backups
  COMPANY: 5,             // Todos contratos da empresa
  DEPARTMENT: 4,          // Contratos + usuários + reports do dept
  DEPARTMENT_RESTRICTED: 3, // Contratos do dept, reports restritos
  TEAM: 2,                // Contratos do time
  OWN: 1                  // Apenas próprios contratos
};

// Matriz de permissões por role / Berechtigungsmatrix nach Rolle
export const ROLE_PERMISSIONS = {
  SYSTEM_ADMIN: {
    level: 6,
    permissions: [
      'users:*',
      'alerts:*',
      'system:config',
      'system:logs',
      'system:backups'
    ],
    menu: ['dashboard', 'alerts', 'users', 'system']
  },
  
  DIRECTOR: {
    level: 5,
    permissions: [
      'contracts:view_all',
      'contracts:edit_all',
      'contracts:delete_all',
      'contracts:import',
      'approvals:approve_all',
      'users:view',
      'users:manage_all',
      'alerts:view_all',
      'reports:view_all'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  
  DEPARTMENT_ADM: {
    level: 4,
    permissions: [
      'contracts:view_department',
      'contracts:edit_department',
      'contracts:delete_department',
      'contracts:import',
      'approvals:approve_department',
      'users:view_department',
      'users:manage_department',
      'alerts:view_department',
      'reports:view_department'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'users', 'approvals', 'reports']
  },
  
  DEPARTMENT_USER: {
    level: 3,
    permissions: [
      'contracts:view_department',
      'contracts:edit_department',
      'alerts:view_department',
      'reports:view_basic'
    ],
    menu: ['dashboard', 'contracts', 'alerts', 'reports']
  },
  
  TEAM_LEAD: {
    level: 2,
    permissions: [
      'contracts:view_team',
      'contracts:edit_team',
      'contracts:import',
      'alerts:view_team',
      'reports:view_team'
    ],
    menu: ['dashboard', 'contracts', 'import', 'alerts', 'reports']
  },
  
  STAFF: {
    level: 1,
    permissions: [
      'contracts:view_own',
      'contracts:edit_own',
      'alerts:view_own'
    ],
    menu: ['dashboard', 'contracts', 'alerts']
  },
  
  READ_ONLY: {
    level: 1,
    permissions: [
      'contracts:view_own',
      'alerts:view_own'
    ],
    menu: ['dashboard', 'contracts', 'alerts']
  }
};

/**
 * Normaliza role para uppercase (backend retorna lowercase)
 * Normalisiert Rolle zu Großbuchstaben (Backend gibt Kleinbuchstaben zurück)
 */
const normalizeRole = (role) => {
  if (!role) return null;
  return role.toUpperCase();
};

/**
 * Verifica se usuário tem permissão específica
 * Prüft, ob Benutzer eine bestimmte Berechtigung hat
 * 
 * @param {string} userRole - Role do usuário (ex: 'SYSTEM_ADMIN' ou 'system_admin')
 * @param {string} permission - Permissão a verificar (ex: 'contracts:edit_all')
 * @returns {boolean} True se tem permissão
 */
export const hasPermission = (userRole, permission) => {
  const roleConfig = ROLE_PERMISSIONS[normalizeRole(userRole)];
  if (!roleConfig) return false;
  
  // Wildcard: se tem '*', pode tudo
  if (roleConfig.permissions.includes('*')) return true;
  
  // Verifica permissão exata
  if (roleConfig.permissions.includes(permission)) return true;
  
  // Verifica wildcard de categoria (ex: 'contracts:*')
  const [category] = permission.split(':');
  return roleConfig.permissions.includes(`${category}:*`);
};

/**
 * Verifica se usuário pode ver item do menu
 * Prüft, ob Benutzer Menüpunkt sehen kann
 * 
 * @param {string} userRole - Role do usuário
 * @param {string} menuItem - Item do menu (ex: 'contracts')
 * @returns {boolean} True se pode ver
 */
export const canAccessMenu = (userRole, menuItem) => {
  const roleConfig = ROLE_PERMISSIONS[normalizeRole(userRole)];
  return roleConfig?.menu.includes(menuItem) || false;
};

/**
 * Retorna access level numérico do usuário
 * Gibt numerische Zugriffsebene des Benutzers zurück
 * 
 * @param {string} userRole - Role do usuário
 * @returns {number} Access level (1-6)
 */
export const getAccessLevel = (userRole) => {
  const roleConfig = ROLE_PERMISSIONS[normalizeRole(userRole)];
  return roleConfig?.level || 0;
};
