/**
 * API de Autenticação / Authentifizierungs-API
 * 
 * Endpoints: /api/auth/*
 */
import api from './api';

/**
 * Login do usuário / Benutzer-Login
 * 
 * @param {string} email - Email do usuário
 * @param {string} password - Senha
 * @returns {Promise<{access_token: string, user: object}>}
 */
export const login = async (email, password) => {
  // Backend espera form-data (OAuth2)
  const formData = new URLSearchParams();
  formData.append('username', email);  // OAuth2 chama de 'username'
  formData.append('password', password);

  // Garantir que não há GET automático
  if (!email || !password) {
    throw new Error('Credenciais não fornecidas');
  }

  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });

  return response.data;
};

/**
 * Busca dados do usuário logado / Eingeloggte Benutzerdaten abrufen
 * 
 * @returns {Promise<object>} Dados do usuário
 */
export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

/**
 * Logout (apenas limpeza local, backend não tem endpoint)
 * Logout (nur lokale Bereinigung, Backend hat keinen Endpunkt)
 */
export const logout = () => {
  // Backend não tem endpoint de logout (JWT é stateless)
  // Apenas limpamos o token no frontend
  return Promise.resolve();
};
