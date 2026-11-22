<template>
  <div class="space-y-6">
    <!-- Banner de Boas-Vindas -->
    <div class="p-6 rounded-2xl bg-gradient-to-r from-brand-700 to-brand-900 text-white shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold">Olá, {{ authStore.userName }}! 👋</h2>
        <p class="text-brand-100 text-sm mt-1">
          Você está conectado com o perfil <strong class="underline">{{ authStore.user?.cargo_display }}</strong>.
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          to="/agenda"
          class="px-4 py-2 rounded-xl bg-white text-brand-800 font-semibold text-xs hover:bg-brand-50 transition-colors shadow-sm"
        >
          ⏱️ Ver Minha Fila Técnica
        </router-link>
        <router-link
          to="/projetos"
          class="px-4 py-2 rounded-xl bg-brand-800 text-white font-semibold text-xs hover:bg-brand-950 transition-colors border border-brand-600"
        >
          📁 Todos os Projetos
        </router-link>
      </div>
    </div>

    <!-- Cards de Métricas e Indicadores Preliminares -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Projetos Ativos</p>
          <p class="text-2xl font-black text-slate-900 mt-1">{{ stats.totalProjetos }}</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl">
          📁
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fila Técnica</p>
          <p class="text-2xl font-black text-amber-600 mt-1">{{ stats.filaTecnica }}</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-xl">
          ⏱️
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Clientes Cadastrados</p>
          <p class="text-2xl font-black text-emerald-600 mt-1">{{ stats.totalClientes }}</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl">
          🏭
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Itens no Catálogo</p>
          <p class="text-2xl font-black text-purple-600 mt-1">{{ stats.totalItens }}</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center text-xl">
          📦
        </div>
      </div>
    </div>

    <!-- Projetos Recentes -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="p-5 border-b border-slate-100 flex items-center justify-between">
        <h3 class="font-bold text-slate-900 text-base">Últimas Requisições de Projetos</h3>
        <router-link to="/projetos" class="text-brand-600 hover:text-brand-700 text-xs font-semibold">
          Ver todos &rarr;
        </router-link>
      </div>

      <div v-if="loading" class="p-8 text-center text-slate-400 text-sm">
        Carregando projetos preliminares...
      </div>

      <div v-else-if="projetos.length === 0" class="p-8 text-center text-slate-400 text-sm">
        Nenhum projeto encontrado.
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div
          v-for="proj in projetos"
          :key="proj.id"
          class="p-4 hover:bg-slate-50 flex items-center justify-between transition-colors"
        >
          <div class="flex items-center space-x-3">
            <span class="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs">
              {{ proj.codigo_projeto_alfanumerico.substring(0, 5) }}
            </span>
            <div>
              <router-link
                :to="`/projetos/${proj.id}`"
                class="font-semibold text-slate-900 text-sm hover:text-brand-600"
              >
                {{ proj.codigo_projeto_alfanumerico }} - {{ proj.titulo }}
              </router-link>
              <p class="text-xs text-slate-400">
                Cliente: <strong class="text-slate-600">{{ proj.cliente_nome }}</strong> ({{ proj.cliente_local }})
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              {{ proj.status_display }}
            </span>
            <router-link
              :to="`/projetos/${proj.id}`"
              class="text-xs font-semibold text-slate-500 hover:text-brand-600 px-3 py-1.5 rounded-lg border border-slate-200"
            >
              Abrir
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/services/api';

const authStore = useAuthStore();
const loading = ref(true);
const projetos = ref([]);
const stats = ref({
  totalProjetos: 0,
  filaTecnica: 0,
  totalClientes: 0,
  totalItens: 0,
});

onMounted(async () => {
  try {
    const [resProjetos, resAgenda, resClientes, resCatalogo] = await Promise.all([
      api.get('/projetos/'),
      api.get('/agenda/'),
      api.get('/clientes/'),
      api.get('/catalogo/'),
    ]);

    projetos.value = resProjetos.results || resProjetos;
    stats.value.totalProjetos = resProjetos.count || projetos.value.length;
    stats.value.filaTecnica = resAgenda.count || (resAgenda.results || resAgenda).length;
    stats.value.totalClientes = resClientes.count || (resClientes.results || resClientes).length;
    stats.value.totalItens = resCatalogo.count || (resCatalogo.results || resCatalogo).length;
  } catch (err) {
    console.error('Erro ao carregar dados preliminares:', err);
  } finally {
    loading.value = false;
  }
});
</script>
