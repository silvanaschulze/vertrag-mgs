import api from './api';

/**
 * Approvals API Service
 * DE: API-Dienst für Genehmigungen
 * PT: Serviço de API para aprovações
 * 
 * Endpoints:
 * - GET    /contracts/{contract_id}/approvals  - Lista aprovações de um contrato
 * - POST   /contracts/{contract_id}/approve    - Aprovar contrato
 * - POST   /contracts/{contract_id}/reject     - Rejeitar contrato
 */

/**
 * Lista todas as aprovações de um contrato
 * DE: Listet alle Genehmigungen eines Vertrags
 * PT: Lista todas as aprovações de um contrato
 * 
 * @param {number} contractId - ID do contrato
 * @returns {Promise<Array>} Array de aprovações
 */
export const getContractApprovals = async (contractId) => {
  const response = await api.get(`/contracts/${contractId}/approval-history`);
  return response.data;
};

/**
 * Aprovar um contrato
 * DE: Einen Vertrag genehmigen
 * PT: Aprovar um contrato
 * 
 * @param {number} contractId - ID do contrato
 * @param {Object} approvalData - Dados da aprovação
 * @param {string} [approvalData.comments] - Comentários opcionais
 * @returns {Promise<Object>} Resultado da aprovação
 */
export const approveContract = async (contractId, approvalData = {}) => {
  const response = await api.post(`/contracts/${contractId}/approve`, approvalData);
  return response.data;
};

/**
 * Rejeitar um contrato
 * DE: Einen Vertrag ablehnen
 * PT: Rejeitar um contrato
 * 
 * @param {number} contractId - ID do contrato
 * @param {Object} rejectionData - Dados da rejeição
 * @param {string} rejectionData.reason - Motivo da rejeição (obrigatório)
 * @param {string} [rejectionData.comments] - Comentários adicionais
 * @returns {Promise<Object>} Resultado da rejeição
 */
export const rejectContract = async (contractId, rejectionData) => {
  const response = await api.post(`/contracts/${contractId}/reject`, rejectionData);
  return response.data;
};

/**
 * Lista todas as aprovações pendentes do usuário atual
 * DE: Listet alle ausstehenden Genehmigungen des aktuellen Benutzers
 * PT: Lista todas as aprovações pendentes do usuário atual
 * 
 * @param {Object} [filters] - Filtros opcionais
 * @param {number} [filters.page=1] - Página
 * @param {number} [filters.pageSize=25] - Itens por página
 * @returns {Promise<Object>} Lista paginada de aprovações pendentes
 */
export const getPendingApprovals = async (filters = {}) => {
  const params = {
    page: filters.page || 1,
    page_size: filters.pageSize || 25,
    status: 'pending',
    ...filters
  };
  
  const response = await api.get('/approvals', { params });
  return response.data;
};

/**
 * Obter estatísticas de aprovações
 * DE: Genehmigungsstatistiken abrufen
 * PT: Obter estatísticas de aprovações
 * 
 * @returns {Promise<Object>} Estatísticas (total pendente, aprovado, rejeitado)
 */
export const getApprovalsStats = async () => {
  const response = await api.get('/approvals/stats');
  return response.data;
};

export default {
  getContractApprovals,
  approveContract,
  rejectContract,
  getPendingApprovals,
  getApprovalsStats
};
