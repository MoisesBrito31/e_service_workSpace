<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 border border-slate-100">
      <!-- Cabeçalho -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600 text-white text-2xl font-black mb-3 shadow-lg shadow-brand-500/30">
          ⚡
        </div>
        <h2 class="text-2xl font-bold text-slate-900">E-Service Engenharia</h2>
        <p class="text-sm text-slate-500 mt-1">Gestão Integrada de Projetos Industriais</p>
      </div>

      <!-- Alerta de Erro -->
      <div
        v-if="errorMessage"
        class="mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs font-medium flex items-center"
      >
        <span class="mr-2 text-base">⚠️</span> {{ errorMessage }}
      </div>

      <!-- Formulário de Login -->
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
            Usuário / Login
          </label>
          <input
            v-model="username"
            type="text"
            required
            autocomplete="username"
            placeholder="Ex: tecnico, gestor, vendedor"
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all text-slate-800 placeholder:text-slate-400"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
            Senha
          </label>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all text-slate-800 placeholder:text-slate-400"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full py-3 px-4 rounded-xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-semibold text-sm shadow-md shadow-brand-600/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <span v-if="authStore.loading" class="animate-spin mr-2">⏳</span>
          <span>{{ authStore.loading ? 'Entrando...' : 'Acessar Sistema' }}</span>
        </button>
      </form>

      <!-- Botões de Acesso Rápido para Testes Preliminares -->
      <div class="mt-8 pt-6 border-t border-slate-100">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5 text-center">
          Acesso Rápido para Testes
        </p>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <button
            type="button"
            @click="quickLogin('tecnico', 'senha123')"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors text-left"
          >
            🔧 <strong>Técnico</strong>
          </button>
          <button
            type="button"
            @click="quickLogin('gestor', 'senha123')"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors text-left"
          >
            👔 <strong>Gestor</strong>
          </button>
          <button
            type="button"
            @click="quickLogin('vendedor', 'senha123')"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors text-left"
          >
            💼 <strong>Vendedor</strong>
          </button>
          <button
            type="button"
            @click="quickLogin('admin', 'admin123')"
            class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors text-left"
          >
            👑 <strong>Admin</strong>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

async function handleSubmit() {
  errorMessage.value = '';
  try {
    await authStore.login(username.value, password.value);
    const redirect = route.query.redirect || '/dashboard';
    router.push(redirect);
  } catch (err) {
    errorMessage.value = err.data?.detail || 'Usuário ou senha incorretos.';
  }
}

function quickLogin(user, pass) {
  username.value = user;
  password.value = pass;
  handleSubmit();
}
</script>
