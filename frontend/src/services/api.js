/**
 * Configuração do Axios com interceptors
 * Axios-Konfiguration mit Interceptors
 */
import axios from 'axios';
import { useAuthStore } from '../store/authStore';

// Cria instância do Axios / Axios-Instanz erstellen
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// REQUEST INTERCEPTOR - Adiciona token em todas as requisições
// REQUEST INTERCEPTOR - Token zu allen Anfragen hinzufügen
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// RESPONSE INTERCEPTOR - Trata erros automaticamente
// RESPONSE INTERCEPTOR - Fehler automatisch behandeln
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 Unauthorized - Token inválido/expirado → Logout
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    
    // 403 Forbidden - Sem permissão (será tratado por toast no componente)
    // Não fazemos nada aqui, deixamos o componente decidir
    
    return Promise.reject(error);
  }
);

export default api;
