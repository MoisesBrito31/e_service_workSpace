import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/services/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const token = ref(localStorage.getItem('access_token') || null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!token.value);
  const isGestor = computed(() => user.value?.cargo === 'GESTOR' || user.value?.cargo === 'ADMIN');
  const isTecnico = computed(() => user.value?.cargo === 'TECNICO');
  const isVendedor = computed(() => user.value?.cargo === 'VENDEDOR');
  const isComercial = computed(() => user.value?.cargo === 'COMERCIAL');
  const userName = computed(() => user.value?.nome_completo || user.value?.username || 'Usuário');

  async function login(username, password) {
    loading.value = true;
    try {
      const data = await api.post('/auth/token/', { username, password });
      token.value = data.access;
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // Carrega os dados do usuário autenticado
      await fetchUserProfile();
      return true;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUserProfile() {
    if (!token.value) return;
    try {
      const profile = await api.get('/users/me/');
      user.value = profile;
    } catch (err) {
      logout();
    }
  }

  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isGestor,
    isTecnico,
    isVendedor,
    isComercial,
    userName,
    login,
    fetchUserProfile,
    logout,
  };
});
