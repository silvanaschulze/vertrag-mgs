/**
 * Zustand Store - Autenticação / Authentifizierung
 * 
 * Armazena: token, user, funções de verificação de permissões
 * Persistência: localStorage (sobrevive refresh)
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { hasPermission, canAccessMenu, getAccessLevel } from '../utils/permissions';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // Estado / Zustand
      token: null,
      user: null, // { id, email, name, role, access_level, department_id, team_id }
      
      /**
       * Faz login / Login durchführen
       * @param {string} token - JWT token
       * @param {object} user - Dados do usuário
       */
      login: (token, user) => {
        set({ token, user });
      },
      
      /**
       * Faz logout / Logout durchführen
       */
      logout: () => {
        set({ token: null, user: null });
      },
      
      /**
       * Verifica se tem permissão específica
       * Prüft spezifische Berechtigung
       * 
       * @param {string} permission - Ex: 'contracts:edit_all'
       * @returns {boolean}
       */
      isAllowed: (permission) => {
        const { user } = get();
        if (!user || !user.role) return false;
        return hasPermission(user.role, permission);
      },
      
      /**
       * Verifica se pode ver item do menu
       * Prüft Menüpunkt-Sichtbarkeit
       * 
       * @param {string} menuItem - Ex: 'contracts'
       * @returns {boolean}
       */
      canViewMenu: (menuItem) => {
        const { user } = get();
        if (!user || !user.role) return false;
        return canAccessMenu(user.role, menuItem);
      },
      
      /**
       * Retorna access level do usuário
       * Gibt Zugriffsebene zurück
       * 
       * @returns {number} 1-6
       */
      getUserLevel: () => {
        const { user } = get();
        return user?.access_level || 0;
      },
      
      /**
       * Verifica se está autenticado
       * Prüft Authentifizierung
       * 
       * @returns {boolean}
       */
      isAuthenticated: () => {
        const { token, user } = get();
        return !!(token && user);
      }
    }),
    {
      name: 'auth-storage', // Nome no localStorage
      partialize: (state) => ({ 
        token: state.token, 
        user: state.user 
      })
    }
  )
);
