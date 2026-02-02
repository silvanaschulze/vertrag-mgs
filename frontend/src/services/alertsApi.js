/**
 * Alerts API Service
 * Serviço de API de Alertas
 * 
 * Este módulo contém funções para gerenciar alertas de contratos.
 * Dieses Modul enthält Funktionen zur Verwaltung von Vertragswarnungen.
 */

import api from './api';

/**
 * Alerts API endpoints
 * Endpoints da API de Alertas
 */
const alertsApi = {
  /**
   * Listar alertas com filtros e paginação
   * Warnungen mit Filtern und Paginierung auflisten
   * 
   * @param {Object} filters - Filtros de busca
   * @param {string} filters.alert_type - Tipo de alerta (T-60, T-30, T-10, T-1, CUSTOM)
   * @param {boolean} filters.is_read - Status de leitura (true/false)
   * @param {string} filters.search - Busca por título do contrato
   * @param {number} page - Página atual (1-based)
   * @param {number} pageSize - Itens por página
   * @returns {Promise<Object>} { items: Alert[], total: number, page: number, page_size: number }
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * const result = await alertsApi.getAlerts({ is_read: false }, 1, 25);
   * console.log(result.items, result.total);
   */
  getAlerts: async (filters = {}, page = 1, pageSize = 25) => {
    try {
      const params = {
        page,
        page_size: pageSize,
        ...filters
      };

      console.log('📤 [Alerts API] Buscando alertas com parâmetros:', params);
      const response = await api.get('/alerts/', { params });
      console.log('📥 [Alerts API] Resposta recebida:', response.data);

      // Backend pode retornar 'alerts' ou 'items'
      return {
        items: response.data.alerts || response.data.items || [],
        total: response.data.total || 0,
        page: response.data.page || page,
        page_size: response.data.page_size || pageSize
      };
    } catch (error) {
      console.error('❌ [Alerts API] Erro ao buscar alertas:', error);
      throw error;
    }
  },

  /**
   * Obter um alerta específico por ID
   * Eine bestimmte Warnung nach ID abrufen
   * 
   * @param {number} id - ID do alerta
   * @returns {Promise<Object>} Alerta completo com dados do contrato
   * @throws {Error} Se não encontrado (404) ou falhar requisição
   * 
   * @example
   * const alert = await alertsApi.getAlert(123);
   */
  getAlert: async (id) => {
    try {
      console.log(`📤 [Alerts API] Buscando alerta ID: ${id}`);
      const response = await api.get(`/alerts/${id}/`);
      console.log('📥 [Alerts API] Alerta recebido:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ [Alerts API] Erro ao buscar alerta ${id}:`, error);
      throw error;
    }
  },

  /**
   * Marcar alerta como lido
   * Warnung als gelesen markieren
   * 
   * @param {number} id - ID do alerta
   * @returns {Promise<Object>} Alerta atualizado
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * await alertsApi.markAsRead(123);
   */
  markAsRead: async (id) => {
    try {
      console.log(`📤 [Alerts API] Marcando alerta ${id} como lido`);
      const response = await api.patch(`/alerts/${id}/read/`);
      console.log('✅ [Alerts API] Alerta marcado como lido:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ [Alerts API] Erro ao marcar alerta ${id} como lido:`, error);
      throw error;
    }
  },

  /**
   * Criar alerta manual (apenas para DIRECTOR e DEPARTMENT_ADM)
   * Manuelle Warnung erstellen (nur für DIRECTOR und DEPARTMENT_ADM)
   * 
   * @param {Object} data - Dados do alerta
   * @param {number} data.contract_id - ID do contrato
   * @param {string} data.scheduled_for - Data/hora de envio (ISO 8601)
   * @param {string} data.recipient - Email destinatário
   * @param {string} data.subject - Assunto do email
   * @param {string} [data.custom_message] - Mensagem customizada (opcional)
   * @returns {Promise<Object>} Alerta criado
   * @throws {Error} Se falhar a requisição ou sem permissão (403)
   * 
   * @example
   * const newAlert = await alertsApi.createAlert({
   *   contract_id: 123,
   *   scheduled_for: '2026-03-15T10:00:00Z',
   *   recipient: 'user@example.com',
   *   subject: 'Lembrete importante',
   *   custom_message: 'Revisar contrato antes do vencimento'
   * });
   */
  createAlert: async (data) => {
    try {
      console.log('📤 [Alerts API] Criando alerta manual:', data);
      // Backend espera query params, não body JSON
      const params = new URLSearchParams({
        contract_id: data.contract_id,
        scheduled_for: data.scheduled_for,
        recipient: data.recipient,
        subject: data.subject
      });
      if (data.custom_message) {
        params.append('custom_message', data.custom_message);
      }
      const response = await api.post(`/alerts/manual/?${params}`);
      console.log('✅ [Alerts API] Alerta criado:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [Alerts API] Erro ao criar alerta:', error);
      throw error;
    }
  },

  /**
   * Deletar alerta (apenas para DIRECTOR - Level 5)
   * Warnung löschen (nur für DIRECTOR - Level 5)
   * 
   * @param {number} id - ID do alerta
   * @returns {Promise<void>}
   * @throws {Error} Se falhar a requisição ou sem permissão (403)
   * 
   * @example
   * await alertsApi.deleteAlert(123);
   */
  deleteAlert: async (id) => {
    try {
      console.log(`📤 [Alerts API] Deletando alerta ${id}`);
      await api.delete(`/alerts/${id}/`);
      console.log(`✅ [Alerts API] Alerta ${id} deletado com sucesso`);
    } catch (error) {
      console.error(`❌ [Alerts API] Erro ao deletar alerta ${id}:`, error);
      throw error;
    }
  },

  /**
   * Obter contagem de alertas não lidos (status = pending)
   * Anzahl ungelesener Warnungen abrufen
   * 
   * @returns {Promise<number>} Número de alertas pendentes
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * const count = await alertsApi.getUnreadCount();
   * console.log(`Você tem ${count} alertas pendentes`);
   */
  getUnreadCount: async () => {
    try {
      console.log('📤 [Alerts API] Buscando contagem de pendentes');
      const response = await api.get('/alerts/', {
        params: {
          status: 'pending',
          page: 1,
          page_size: 1 // Só precisamos do total, não dos itens
        }
      });
      
      const count = response.data.total || 0;
      console.log(`📊 [Alerts API] Alertas pendentes: ${count}`);
      return count;
    } catch (error) {
      console.error('❌ [Alerts API] Erro ao buscar contagem de pendentes:', error);
      // Retorna 0 em caso de erro para não quebrar a UI
      return 0;
    }
  },

  /**
   * Processar todos os alertas pendentes manualmente
   * Alle ausstehenden Warnungen manuell verarbeiten
   * 
   * @returns {Promise<Object>} Resultado do processamento
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * const result = await alertsApi.processAllAlerts();
   * console.log(`Processados ${result.total_processed} alertas`);
   */
  processAllAlerts: async () => {
    try {
      console.log('📤 [Alerts API] Processando todos os alertas');
      const response = await api.post('/alerts/process-all/');
      console.log('✅ [Alerts API] Alertas processados:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [Alerts API] Erro ao processar alertas:', error);
      throw error;
    }
  },

  /**
   * Reprocessar um alerta falhado
   * Fehlgeschlagene Warnung erneut verarbeiten
   * 
   * @param {number} alertId - ID do alerta
   * @returns {Promise<Object>} Alerta reprocessado
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * const alert = await alertsApi.reprocessAlert(123);
   * console.log(`Alerta reprocessado: ${alert.status}`);
   */
  reprocessAlert: async (alertId) => {
    try {
      console.log(`📤 [Alerts API] Reprocessando alerta ${alertId}`);
      const response = await api.post(`/alerts/${alertId}/reprocess/`);
      console.log('✅ [Alerts API] Alerta reprocessado:', response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ [Alerts API] Erro ao reprocessar alerta ${alertId}:`, error);
      throw error;
    }
  }
};

export default alertsApi;
