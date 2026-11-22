<template>
  <div class="space-y-6">
    <!-- Cabeçalho -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Clientes Industriais</h2>
        <p class="text-sm text-slate-500 mt-0.5">
          Cadastro de plantas industriais, locais de atendimento e contatos técnicos responsáveis.
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="fetchClientes"
          class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
        >
          🔄 Atualizar
        </button>
      </div>
    </div>

    <!-- Lista de Clientes -->
    <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
      Carregando clientes...
    </div>

    <div v-else-if="clientes.length === 0" class="bg-white p-12 rounded-2xl border border-slate-200 text-center">
      <span class="text-3xl">🏭</span>
      <h3 class="text-sm font-bold text-slate-800 mt-2">Nenhum cliente cadastrado</h3>
      <p class="text-xs text-slate-400 mt-1">Os clientes cadastrados via vendedores aparecerão aqui.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="cli in clientes"
        :key="cli.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3"
      >
        <div class="flex items-start justify-between">
          <div class="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold text-base">
            🏭
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
            {{ cli.total_projetos || 0 }} Projetos
          </span>
        </div>

        <div>
          <h3 class="font-bold text-slate-900 text-base">{{ cli.nome_cliente }}</h3>
          <p class="text-xs text-slate-500 mt-1">
            📍 Local: <strong class="text-slate-700">{{ cli.local_aproximado }}</strong>
          </p>
          <p class="text-xs text-slate-500">
            👤 Responsável: <strong class="text-slate-700">{{ cli.responsavel_contato }}</strong>
          </p>
          <p v-if="cli.telefone_contato" class="text-xs text-slate-500">
            📞 Telefone: <span>{{ cli.telefone_contato }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/services/api';

const loading = ref(true);
const clientes = ref([]);

async function fetchClientes() {
  loading.value = true;
  try {
    const data = await api.get('/clientes/');
    clientes.value = data.results || data;
  } catch (err) {
    console.error('Erro ao buscar clientes:', err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchClientes);
</script>
