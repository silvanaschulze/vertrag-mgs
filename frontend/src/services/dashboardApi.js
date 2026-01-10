/**
 * Dashboard API Service
 * Serviço de API do Dashboard
 * 
 * Este módulo contém funções para buscar estatísticas do dashboard
 * do backend, que retorna dados filtrados pelo role do usuário.
 * 
 * Dieses Modul enthält Funktionen zum Abrufen von Dashboard-Statistiken
 * vom Backend, das nach Benutzerrolle gefilterte Daten zurückgibt.
 */

import api from './api';

/**
 * Dashboard API endpoints
 * Endpoints da API do Dashboard
 */
const dashboardApi = {
  /**
   * Obter estatísticas do dashboard filtradas por role do usuário
   * Dashboard-Statistiken gefiltert nach Benutzerrolle abrufen
   * 
   * Retorna dados diferentes baseado no access_level:
   * - Level 6 (SYSTEM_ADMIN): Apenas dados técnicos (usuários, backup, disco)
   * - Level 5 (DIRECTOR): Todas estatísticas da empresa
   * - Level 4 (DEPARTMENT_ADM): Estatísticas completas do departamento
   * - Level 3 (DEPARTMENT_USER): Estatísticas do departamento sem valores
   * - Level 2 (TEAM): Estatísticas do time
   * - Level 1 (STAFF): Apenas contratos próprios
   * 
   * @returns {Promise<Object>} Estatísticas do dashboard / Dashboard-Statistiken
   * @throws {Error} Se falhar a requisição / Bei fehlgeschlagener Anfrage
   * 
   * @example
   * const stats = await dashboardApi.getStats();
   * console.log(stats.total_contracts);
   * console.log(stats.active_contracts);
   */
  getStats: async () => {
    try {
      const response = await api.get('/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar estatísticas do dashboard:', error);
      throw error;
    }
  },

  /**
   * Refresh das estatísticas (mesmo que getStats, mas semântico)
   * Aktualisierung der Statistiken (gleich wie getStats, aber semantisch)
   * 
   * @returns {Promise<Object>} Estatísticas atualizadas / Aktualisierte Statistiken
   */
  refreshStats: async () => {
    return dashboardApi.getStats();
  }
};

export default dashboardApi;
