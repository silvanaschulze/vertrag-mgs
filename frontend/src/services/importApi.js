/**
 * Import API Service
 * Serviço de API de Importação de Contratos/PDFs
 *
 * Este módulo contém funções para upload, extração e preview de PDFs de contratos.
 * Dieses Modul enthält Funktionen für Upload, Extraktion und Vorschau von Vertrags-PDFs.
 */

import api from './api';

/**
 * Import API endpoints
 * Endpoints da API de Importação
 */
const importApi = {
  /**
   * Faz upload de um PDF e retorna dados extraídos
   * Lädt ein PDF hoch und gibt extrahierte Daten zurück
   * @param {File} file - Arquivo PDF
   * @param {Object} [options] - Opções de extração
   * @param {string} [options.extraction_method] - Método de extração ("combined", "pdfplumber", etc)
   * @param {string} [options.language] - Idioma para OCR ("de", "pt")
   * @param {boolean} [options.include_ocr] - Incluir OCR
   * @returns {Promise<Object>} Dados extraídos do contrato
   */
  uploadPDF: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('extraction_method', options.extraction_method || 'combined');
    formData.append('language', options.language || 'de');
    formData.append('include_ocr', options.include_ocr !== undefined ? options.include_ocr : true);
    const response = await api.post('/contracts/import/pdf/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  /**
   * Confirma importação e salva contrato após edição dos dados extraídos
   * Bestätigt den Import und speichert den Vertrag nach Bearbeitung der extrahierten Daten
   * @param {Object} data - Dados do contrato editados
   * @returns {Promise<Object>} Contrato criado
   */
  confirmImport: async (data) => {
    // Espera-se que o backend aceite os dados extraídos + referência ao arquivo temporário
    const response = await api.post('/contracts/import/confirm/', data);
    return response.data;
  },

  /**
   * Faz download do PDF original do contrato
   * Lädt das Original-PDF des Vertrags herunter
   * @param {number|string} contractId - ID do contrato
   * @returns {Promise<Blob>} Blob do PDF
   */
  downloadPDF: async (contractId) => {
    const response = await api.get(`/contracts/${contractId}/pdf/`, {
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Obtém URL para preview inline do PDF
   * Holt die URL für die Inline-Vorschau des PDFs
   * @param {number|string} contractId - ID do contrato
   * @returns {string} URL para usar em iframe/object
   */
  previewPDF: (contractId) => {
    return `/api/contracts/${contractId}/pdf/preview/`;
  },
};

export default importApi;
