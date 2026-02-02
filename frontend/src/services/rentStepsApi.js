import api from './api';

/**
 * Rent Steps API Service
 * DE: API-Dienst für Mietstaffelungen
 * PT: Serviço de API para escalonamento de aluguel
 * 
 * Endpoints:
 * - GET    /contracts/{contract_id}/rent-steps        - Lista todos os rent steps de um contrato
 * - POST   /contracts/{contract_id}/rent-steps        - Cria novo rent step
 * - GET    /contracts/{contract_id}/rent-steps/{id}   - Obtém um rent step específico
 * - PUT    /contracts/{contract_id}/rent-steps/{id}   - Atualiza um rent step
 * - DELETE /contracts/{contract_id}/rent-steps/{id}   - Remove um rent step
 */

/**
 * Lista todos os rent steps de um contrato
 * DE: Listet alle Mietstaffelungen eines Vertrags
 * PT: Lista todos os escalonamentos de aluguel de um contrato
 * 
 * @param {number} contractId - ID do contrato
 * @returns {Promise<Array>} Array de rent steps ordenados por data efetiva
 */
export const getRentSteps = async (contractId) => {
  const response = await api.get(`/contracts/${contractId}/rent-steps/`);
  return response.data;
};

/**
 * Obtém um rent step específico
 * DE: Ruft eine bestimmte Mietstaffelung ab
 * PT: Obtém um escalonamento de aluguel específico
 * 
 * @param {number} contractId - ID do contrato
 * @param {number} stepId - ID do rent step
 * @returns {Promise<Object>} Rent step
 */
export const getRentStep = async (contractId, stepId) => {
  const response = await api.get(`/contracts/${contractId}/rent-steps/${stepId}/`);
  return response.data;
};

/**
 * Cria um novo rent step
 * DE: Erstellt eine neue Mietstaffelung
 * PT: Cria um novo escalonamento de aluguel
 * 
 * @param {number} contractId - ID do contrato
 * @param {Object} rentStepData - Dados do rent step
 * @param {string} rentStepData.effective_date - Data de vigência (YYYY-MM-DD)
 * @param {number} rentStepData.amount - Valor do aluguel
 * @param {string} [rentStepData.currency='EUR'] - Moeda (EUR, USD, BRL, etc.)
 * @param {string} [rentStepData.note] - Observações
 * @returns {Promise<Object>} Rent step criado
 */
export const createRentStep = async (contractId, rentStepData) => {
  const response = await api.post(`/contracts/${contractId}/rent-steps/`, rentStepData);
  return response.data;
};

/**
 * Atualiza um rent step existente
 * DE: Aktualisiert eine bestehende Mietstaffelung
 * PT: Atualiza um escalonamento de aluguel existente
 * 
 * @param {number} contractId - ID do contrato
 * @param {number} stepId - ID do rent step
 * @param {Object} rentStepData - Dados para atualização
 * @returns {Promise<Object>} Rent step atualizado
 */
export const updateRentStep = async (contractId, stepId, rentStepData) => {
  const response = await api.put(`/contracts/${contractId}/rent-steps/${stepId}/`, rentStepData);
  return response.data;
};

/**
 * Remove um rent step
 * DE: Löscht eine Mietstaffelung
 * PT: Remove um escalonamento de aluguel
 * 
 * @param {number} contractId - ID do contrato
 * @param {number} stepId - ID do rent step
 * @returns {Promise<void>}
 */
export const deleteRentStep = async (contractId, stepId) => {
  await api.delete(`/contracts/${contractId}/rent-steps/${stepId}/`);
};

/**
 * Agrupa rent steps por ano
 * DE: Gruppiert Mietstaffelungen nach Jahr
 * PT: Agrupa escalonamentos de aluguel por ano
 * 
 * @param {Array} rentSteps - Array de rent steps
 * @returns {Object} Objeto com anos como chaves e arrays de rent steps como valores
 */
export const groupRentStepsByYear = (rentSteps) => {
  return rentSteps.reduce((acc, step) => {
    const year = new Date(step.effective_date).getFullYear();
    if (!acc[year]) {
      acc[year] = [];
    }
    acc[year].push(step);
    return acc;
  }, {});
};

/**
 * Calcula o próximo aumento de aluguel
 * DE: Berechnet die nächste Mieterhöhung
 * PT: Calcula o próximo aumento de aluguel
 * 
 * @param {Array} rentSteps - Array de rent steps ordenados
 * @returns {Object|null} Próximo rent step ou null se não houver
 */
export const getNextRentStep = (rentSteps) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const futureSteps = rentSteps.filter(step => {
    const stepDate = new Date(step.effective_date);
    stepDate.setHours(0, 0, 0, 0);
    return stepDate >= today;
  });
  
  if (futureSteps.length === 0) return null;
  
  // Retorna o primeiro step futuro (já ordenado por effective_date)
  return futureSteps[0];
};

/**
 * Calcula aumento percentual entre dois rent steps
 * DE: Berechnet prozentuale Erhöhung zwischen zwei Mietstaffelungen
 * PT: Calcula aumento percentual entre dois escalonamentos
 * 
 * @param {number} previousAmount - Valor anterior
 * @param {number} newAmount - Novo valor
 * @returns {number} Percentual de aumento
 */
export const calculatePercentageIncrease = (previousAmount, newAmount) => {
  if (!previousAmount || previousAmount === 0) return 0;
  return ((newAmount - previousAmount) / previousAmount) * 100;
};

export default {
  getRentSteps,
  getRentStep,
  createRentStep,
  updateRentStep,
  deleteRentStep,
  groupRentStepsByYear,
  getNextRentStep,
  calculatePercentageIncrease,
};
