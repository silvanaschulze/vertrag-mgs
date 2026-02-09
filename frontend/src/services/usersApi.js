// usersApi.js - API de gerenciamento de usuários
import api from './api';

const API_URL = '/users/';

export const getUsers = async (params) => {
  const { data } = await api.get(API_URL, { params });
  // Se vier array direto, adapta para formato paginado
  if (Array.isArray(data)) {
    return { items: data, total: data.length };
  }
  // Se vier objeto paginado, mantém padrão
  return {
    items: data.items || data.users || [],
    total: data.total || (data.items ? data.items.length : 0)
  };
};

export const getUser = async (id) => {
  const { data } = await api.get(`${API_URL}${id}/`);
  return data;
};


// Remove access_level do payload antes de enviar
export const createUser = async (user) => {
  const { access_level, ...userData } = user;
  const { data } = await api.post(API_URL, userData);
  return data;
};


// Remove access_level do payload antes de enviar
export const updateUser = async (id, user) => {
  const { access_level, ...userData } = user;
  const { data } = await api.put(`${API_URL}${id}/`, userData);
  return data;
};

export const resetPassword = async (id, newPassword) => {
  const { data } = await api.post(`${API_URL}${id}/reset-password/`, { new_password: newPassword });
  return data;
};

export const activateUser = async (id) => {
  const { data } = await api.patch(`${API_URL}${id}/activate/`);
  return data;
};

export const deactivateUser = async (id) => {
  const { data } = await api.patch(`${API_URL}${id}/deactivate/`);
  return data;
};

export const deleteUser = async (id) => {
  const { data } = await api.delete(`${API_URL}${id}/`);
  return data;
};

export default {
  getUsers,
  getUser,
  createUser,
  updateUser,
  resetPassword,
  activateUser,
  deactivateUser,
  deleteUser,
};
