<template>
  <div class="space-y-6">
    <!-- Topo: Título e Botão Nova Demanda -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Projetos Industriais</h2>
        <p class="text-sm text-slate-500 mt-0.5">
          Acompanhamento de ponta a ponta das demandas de engenharia de aplicação.
        </p>
      </div>

      <button
        v-if="authStore.isVendedor || authStore.isGestor"
        @click="showModal = true"
        class="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-md shadow-brand-600/20 transition-all flex items-center justify-center shrink-0"
      >
        <span class="mr-1.5 text-base">+</span> Nova Requisição de Projeto
      </button>
    </div>

    <!-- Filtros de Busca e Status -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="relative flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por código (ex: PR-132-01), título ou cliente..."
            class="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          />
          <span class="absolute left-3 top-2.5 text-slate-400 text-xs">🔍</span>
        </div>
      </div>

      <!-- Filtro Rápido por Status -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        <button
          v-for="st in statusOptions"
          :key="st.value"
          @click="selectedStatus = st.value"
          class="px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap"
          :class="[
            selectedStatus === st.value
              ? 'bg-slate-900 text-white shadow-sm'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          ]"
        >
          {{ st.label }}
        </button>
      </div>
    </div>

    <!-- Lista de Projetos -->
    <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
      Carregando projetos...
    </div>

    <div v-else-if="filteredProjetos.length === 0" class="bg-white p-12 rounded-2xl border border-slate-200 text-center">
      <span class="text-3xl">📂</span>
      <h3 class="text-sm font-bold text-slate-800 mt-2">Nenhum projeto encontrado</h3>
      <p class="text-xs text-slate-400 mt-1">Tente ajustar seus termos de busca ou filtros de status.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="proj in filteredProjetos"
        :key="proj.id"
        class="bg-white rounded-2xl border border-slate-200 hover:border-brand-300 p-5 shadow-sm hover:shadow transition-all flex flex-col justify-between"
      >
        <div>
          <!-- Header do Card -->
          <div class="flex items-start justify-between gap-2">
            <span class="px-2.5 py-1 rounded-lg bg-slate-100 font-mono font-bold text-xs text-brand-700">
              {{ proj.codigo_projeto_alfanumerico }}
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              {{ proj.status_display }}
            </span>
          </div>

          <h3 class="font-bold text-slate-900 text-sm mt-3 line-clamp-2">
            {{ proj.titulo }}
          </h3>

          <!-- Informações do Cliente -->
          <div class="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-1">
            <p>🏭 Cliente: <strong class="text-slate-700">{{ proj.cliente_nome }}</strong></p>
            <p>📍 Local: <span>{{ proj.cliente_local }}</span></p>
            <p>👤 Contato: <span>{{ proj.cliente_contato }}</span></p>
          </div>
        </div>

        <!-- Footer do Card -->
        <div class="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
          <div class="text-[11px] text-slate-400">
            <span v-if="proj.tecnico_alocado">
              🔧 {{ proj.tecnico_alocado.nome }}
            </span>
            <span v-else class="text-amber-600 font-medium">
              ⚠️ Sem técnico alocado
            </span>
          </div>

          <router-link
            :to="`/projetos/${proj.id}`"
            class="px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-brand-50 text-brand-700 hover:text-brand-800 text-xs font-semibold border border-slate-200 hover:border-brand-200 transition-colors"
          >
            Abrir Detalhes &rarr;
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/services/api';

const authStore = useAuthStore();
const loading = ref(true);
const showModal = ref(false);
const projetos = ref([]);
const searchQuery = ref('');
const selectedStatus = ref('TODOS');

const statusOptions = [
  { value: 'TODOS', label: 'Todos os Status' },
  { value: 'AGUARDANDO_AGENDAMENTO', label: 'Aguardando Agendamento' },
  { value: 'EM_DESENVOLVIMENTO', label: 'Em Desenvolvimento' },
  { value: 'AGUARDANDO_INFORMACAO', label: 'Pausado (Aguardando Info)' },
  { value: 'DEFINICAO_COMERCIAL', label: 'Definição Comercial' },
  { value: 'CONCLUIDO', label: 'Concluídos' },
];

async function fetchProjetos() {
  loading.value = true;
  try {
    const data = await api.get('/projetos/');
    projetos.value = data.results || data;
  } catch (err) {
    console.error('Erro ao listar projetos:', err);
  } finally {
    loading.value = false;
  }
}

const filteredProjetos = computed(() => {
  return projetos.value.filter(p => {
    const matchesSearch =
      !searchQuery.value ||
      p.codigo_projeto_alfanumerico.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.titulo.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (p.cliente_nome && p.cliente_nome.toLowerCase().includes(searchQuery.value.toLowerCase()));

    const matchesStatus =
      selectedStatus.value === 'TODOS' || p.status === selectedStatus.value;

    return matchesSearch && matchesStatus;
  });
});

onMounted(fetchProjetos);
</script>
