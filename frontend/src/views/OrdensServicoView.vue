<template>
  <div class="space-y-6">
    <!-- Cabeçalho -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Ordens de Serviço (OS) & Campo</h2>
        <p class="text-sm text-slate-500 mt-0.5">
          Processo de instalação, montagem e relatórios de serviços futuros pós-aprovação comercial.
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="fetchOrdens"
          class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
        >
          🔄 Atualizar
        </button>
      </div>
    </div>

    <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
      Carregando ordens de serviço...
    </div>

    <div v-else-if="ordens.length === 0" class="bg-white p-12 rounded-2xl border border-slate-200 text-center">
      <span class="text-4xl">🛠️</span>
      <h3 class="text-sm font-bold text-slate-800 mt-2">Nenhuma Ordem de Serviço em aberto</h3>
      <p class="text-xs text-slate-400 mt-1">
        Ordens de serviço são abertas automaticamente quando o comercial aprova um projeto e proposta.
      </p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="os in ordens"
        :key="os.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3"
      >
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-mono font-bold text-brand-700 text-xs">Projeto {{ os.projeto_codigo }}</span>
              <span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                {{ os.status_os_display }}
              </span>
            </div>
            <h3 class="font-bold text-slate-900 text-sm mt-1">Cliente: {{ os.cliente_nome }}</h3>
          </div>
          <span class="text-[11px] text-slate-400">
            Abertura: {{ new Date(os.data_abertura).toLocaleDateString('pt-BR') }}
          </span>
        </div>

        <p class="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <strong>Escopo:</strong> {{ os.escopo_servico }}
        </p>

        <div class="pt-2 flex justify-between items-center text-xs">
          <span class="text-slate-400">Relatórios de Campo: {{ os.relatorios_campo?.length || 0 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/services/api';

const loading = ref(true);
const ordens = ref([]);

async function fetchOrdens() {
  loading.value = true;
  try {
    const data = await api.get('/ordens-servico/');
    ordens.value = data.results || data;
  } catch (err) {
    console.error('Erro ao buscar ordens de serviço:', err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchOrdens);
</script>
