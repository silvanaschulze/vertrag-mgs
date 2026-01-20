/**
 * Contracts API Service
 * Serviço de API de Contratos
 * 
 * Este módulo contém funções para CRUD de contratos no backend.
 * Dieses Modul enthält Funktionen für CRUD von Verträgen im Backend.
 */

import api from './api';

/**
 * Contracts API endpoints
 * Endpoints da API de Contratos
 */
const contractsApi = {
  /**
   * Listar contratos com filtros, paginação e ordenação
   * Verträge mit Filtern, Paginierung und Sortierung auflisten
   * 
   * @param {Object} params - Parâmetros de filtro e paginação
   * @param {number} params.page - Página atual (1-based)
   * @param {number} params.page_size - Itens por página
   * @param {string} params.sort_by - Campo para ordenar (ex: 'title', '-start_date')
   * @param {string} params.status - Filtro por status
   * @param {string} params.contract_type - Filtro por tipo
   * @param {string} params.search - Busca por título ou parceiro
   * @returns {Promise<Object>} { items: Contract[], total: number, page: number, page_size: number }
   * @throws {Error} Se falhar a requisição
   * 
   * @example
   * const result = await contractsApi.getContracts({ page: 1, page_size: 25, status: 'aktiv' });
   * console.log(result.items, result.total);
   */
  getContracts: async (params = {}) => {
    try {
      const response = await api.get('/contracts/', { params });
      // Backend retorna 'contracts', mapeamos para 'items' para consistência
      return {
        items: response.data.contracts || [],
        total: response.data.total || 0,
        page: response.data.page || 1,
        page_size: response.data.per_page || params.page_size || 25
      };
    } catch (error) {
      console.error('Error fetching contracts:', error);
      throw error;
    }
  },

  /**
   * Obter um contrato específico por ID
   * Einen bestimmten Vertrag nach ID abrufen
   * 
   * @param {number} id - ID do contrato
   * @returns {Promise<Object>} Contrato completo com rent_steps
   * @throws {Error} Se não encontrado (404) ou falhar requisição
   * 
   * @example
   * const contract = await contractsApi.getContract(123);
   */
  getContract: async (id) => {
    try {
      const response = await api.get(`/contracts/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching contract ${id}:`, error);
      throw error;
    }
  },

  /**
   * Criar novo contrato
   * Neuen Vertrag erstellen
   * 
   * @param {Object} data - Dados do contrato
   * @param {string} data.title - Título do contrato
   * @param {string} data.client_name - Nome do parceiro/cliente
   * @param {string} data.contract_type - Tipo (miete, pacht, etc)
   * @param {string} data.status - Status (entwurf, aktiv, etc)
   * @param {string} data.start_date - Data início (YYYY-MM-DD)
   * @param {string} data.end_date - Data fim (YYYY-MM-DD)
   * @param {number} data.value - Valor mensal
   * @param {string} data.description - Descrição
   * @param {string} data.department - Departamento
   * @param {string} data.team - Time
   * @param {number} data.responsible_user_id - ID do responsável
   * @param {File} data.pdfFile - Arquivo PDF do contrato (opcional)
   * @returns {Promise<Object>} Contrato criado
   * @throws {Error} Se validação falhar (400) ou não autorizado (403)
   * 
   * @example
   * const newContract = await contractsApi.createContract({
   *   title: 'Office Lease',
   *   client_name: 'ABC Corp',
   *   contract_type: 'miete',
   *   status: 'aktiv',
   *   start_date: '2024-01-01',
   *   end_date: '2025-12-31',
   *   value: 1500.00,
   *   department: 'IT und Datenschutz'
   * });
   */
  createContract: async (data) => {
    try {
      // Decidir qual endpoint usar / Decide which endpoint to use
      const useFormData = !!data.pdfFile;
      
      if (useFormData) {
        // Usar novo endpoint com FormData / Use new endpoint with FormData
        const formData = new FormData();
        
        // Adicionar todos os campos / Add all fields
        Object.keys(data).forEach(key => {
          if (key === 'pdfFile') {
            // Adicionar arquivo / Add file
            formData.append('pdf_file', data.pdfFile);
          } else if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
            // Adicionar campo (converter para string se necessário)
            // Add field (convert to string if needed)
            const value = data[key];
            if (value instanceof Date) {
              formData.append(key, value.toISOString().split('T')[0]);
            } else if (typeof value === 'number' || typeof value === 'boolean') {
              formData.append(key, value.toString());
            } else {
              formData.append(key, value);
            }
          }
        });
        
        const response = await api.post('/contracts/with-upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
      } else {
        // Usar endpoint JSON tradicional (sem PDF)
        // Use traditional JSON endpoint (without PDF)
        const { pdfFile, ...contractData } = data;
        const response = await api.post('/contracts', contractData);
        return response.data;
      }
    } catch (error) {
      console.error('Error creating contract:', error);
      throw error;
    }
  },

  /**
   * Atualizar contrato existente
   * Bestehenden Vertrag aktualisieren
   * 
   * @param {number} id - ID do contrato
   * @param {Object} data - Dados a atualizar (mesmos campos do create)
   * @param {File} data.pdfFile - Arquivo PDF do contrato (opcional)
   * @returns {Promise<Object>} Contrato atualizado
   * @throws {Error} Se não encontrado (404), sem permissão (403) ou validação falhar
   * 
   * @example
   * const updated = await contractsApi.updateContract(123, { 
   *   value: 1800.00,
   *   status: 'aktiv' 
   * });
   */
  updateContract: async (id, data) => {
    try {
      // Decidir qual endpoint usar / Decide which endpoint to use
      const useFormData = !!data.pdfFile;
      
      if (useFormData) {
        // Usar novo endpoint com FormData / Use new endpoint with FormData
        const formData = new FormData();
        
        // Adicionar todos os campos / Add all fields
        Object.keys(data).forEach(key => {
          if (key === 'pdfFile') {
            // Adicionar arquivo / Add file
            formData.append('pdf_file', data.pdfFile);
          } else if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
            // Adicionar campo (converter para string se necessário)
            // Add field (convert to string if needed)
            const value = data[key];
            if (value instanceof Date) {
              formData.append(key, value.toISOString().split('T')[0]);
            } else if (typeof value === 'number' || typeof value === 'boolean') {
              formData.append(key, value.toString());
            } else {
              formData.append(key, value);
            }
          }
        });
        
        const response = await api.put(`/contracts/${id}/with-upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
      } else {
        // Usar endpoint JSON tradicional (sem PDF)
        // Use traditional JSON endpoint (without PDF)
        const { pdfFile, ...contractData } = data;
        const response = await api.put(`/contracts/${id}`, contractData);
        return response.data;
      }
    } catch (error) {
      console.error(`Error updating contract ${id}:`, error);
      throw error;
    }
  },

  /**
   * Anexar PDF original a contrato existente
   * Original-PDF an bestehenden Vertrag anhängen
   * 
   * @param {number} id - ID do contrato
   * @param {File} file - Arquivo PDF
   * @returns {Promise<Object>} Resposta com mensagem e path
   * @throws {Error} Se falhar upload
   */
  uploadPdf: async (id, file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(`/contracts/${id}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error(`Error uploading PDF for contract ${id}:`, error);
      throw error;
    }
  },

  /**
   * Deletar contrato
   * Vertrag löschen
   * 
   * @param {number} id - ID do contrato
   * @returns {Promise<void>}
   * @throws {Error} Se não encontrado (404) ou sem permissão (403)
   * 
   * @example
   * await contractsApi.deleteContract(123);
   */
  deleteContract: async (id) => {
    try {
      await api.delete(`/contracts/${id}`);
    } catch (error) {
      console.error(`Error deleting contract ${id}:`, error);
      throw error;
    }
  }
};

export default contractsApi;
