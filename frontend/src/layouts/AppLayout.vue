<template>
  <div class="min-h-screen bg-slate-100 flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 w-64 bg-slate-900 text-slate-300 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 flex flex-col',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo do Sistema -->
      <div class="h-16 flex items-center px-6 bg-slate-950 text-white font-bold text-lg tracking-wider border-b border-slate-800">
        <span class="text-brand-400 mr-2">⚡</span> E-SERVICE
        <span class="text-xs ml-2 px-2 py-0.5 bg-brand-900 text-brand-300 rounded font-normal">v1.0</span>
      </div>

      <!-- Links de Navegação Principal -->
      <nav class="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="flex items-center px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="[
            $route.path.startsWith(item.to)
              ? 'bg-brand-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          ]"
          @click="sidebarOpen = false"
        >
          <span class="text-lg mr-3">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- Rodapé da Sidebar: Usuário Logado -->
      <div class="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between">
        <div class="flex items-center min-w-0">
          <div class="w-9 h-9 rounded-full bg-brand-700 text-white flex items-center justify-center font-bold text-sm shrink-0">
            {{ userInitial }}
          </div>
          <div class="ml-3 truncate">
            <p class="text-sm font-semibold text-white truncate">{{ authStore.userName }}</p>
            <p class="text-xs text-brand-400 truncate">{{ authStore.user?.cargo_display || 'Colaborador' }}</p>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="text-slate-400 hover:text-red-400 p-1.5 rounded transition-colors text-sm"
          title="Sair do sistema"
        >
          🚪
        </button>
      </div>
    </aside>

    <!-- Overlay para Mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-20 bg-black/50 lg:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Conteúdo Principal -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Header Superior -->
      <header class="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between shrink-0">
        <div class="flex items-center">
          <button
            class="lg:hidden mr-3 text-slate-600 hover:text-slate-900 p-2 rounded-md hover:bg-slate-100"
            @click="sidebarOpen = !sidebarOpen"
          >
            ☰
          </button>
          <h1 class="text-xl font-bold text-slate-800 tracking-tight">
            {{ $route.meta.title || 'Sistema de Projetos' }}
          </h1>
        </div>

        <div class="flex items-center space-x-3">
          <!-- Status Tag do Cargo -->
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200">
            <span class="w-2 h-2 mr-1.5 rounded-full bg-green-500"></span>
            {{ authStore.user?.cargo_display }}
          </span>

          <button
            @click="handleLogout"
            class="text-xs text-slate-500 hover:text-slate-800 font-medium px-3 py-1.5 rounded border border-slate-200 hover:bg-slate-50 transition-colors"
          >
            Sair
          </button>
        </div>
      </header>

      <!-- View Dinâmica -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const sidebarOpen = ref(false);

const navItems = [
  { name: 'dashboard', to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { name: 'agenda', to: '/agenda', label: 'Agenda & Fila Técnica', icon: '⏱️' },
  { name: 'projetos', to: '/projetos', label: 'Projetos Industriais', icon: '📁' },
  { name: 'catalogo', to: '/catalogo', label: 'Catálogo Central Único', icon: '📦' },
  { name: 'clientes', to: '/clientes', label: 'Clientes', icon: '🏭' },
  { name: 'ordens-servico', to: '/ordens-servico', label: 'Ordens de Serviço (OS)', icon: '🛠️' },
];

const userInitial = computed(() => {
  const name = authStore.userName;
  return name ? name.charAt(0).toUpperCase() : 'U';
});

function handleLogout() {
  authStore.logout();
  router.push({ name: 'login' });
}
</script>
