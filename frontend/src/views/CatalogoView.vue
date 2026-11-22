<template>
  <div class="space-y-6">
    <!-- Cabeçalho -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Catálogo Central Único de Materiais & Serviços</h2>
        <p class="text-sm text-slate-500 mt-0.5">
          Elimina planilhas descentralizadas e padroniza a codificação industrial: Modelo(Identificador).
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="fetchCatalogo"
          class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
        >
          🔄 Atualizar
        </button>
      </div>
    </div>

    <!-- Barra de Pesquisa e Filtros de Famílias -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Pesquisar por modelo, código identificador (ex: 88383), nome ou descrição técnica..."
          class="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <span class="absolute left-3 top-2.5 text-slate-400 text-xs">🔍</span>
      </div>

      <!-- Famílias Base -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        <button
          @click="selectedFamilia = null"
          class="px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap"
          :class="[!selectedFamilia ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']"
        >
          Todas as Famílias
        </button>
        <button
          v-for="fam in familias"
          :key="fam.id"
          @click="selectedFamilia = fam.id"
          class="px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap"
          :class="[selectedFamilia === fam.id ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']"
        >
          {{ fam.nome_display }}
        </button>
      </div>
    </div>

    <!-- Tabela do Catálogo -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
        Carregando itens do catálogo...
      </div>

      <div v-else-if="filteredItens.length === 0" class="p-12 text-center text-slate-400 text-sm">
        Nenhum item encontrado no catálogo.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
            <tr>
              <th class="px-5 py-3">Código Padrão</th>
              <th class="px-5 py-3">Nome / Descrição</th>
              <th class="px-5 py-3">Família</th>
              <th class="px-5 py-3">Preço Base (R$)</th>
              <th class="px-5 py-3">UN</th>
              <th class="px-5 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr
              v-for="it in filteredItens"
              :key="it.id"
              class="hover:bg-slate-50/80 transition-colors"
            >
              <td class="px-5 py-3.5 font-mono font-bold text-brand-700">
                {{ it.codigo_completo }}
              </td>
              <td class="px-5 py-3.5">
                <p class="font-semibold text-slate-900">{{ it.nome }}</p>
                <p class="text-[11px] text-slate-400 line-clamp-1">{{ it.especificacao_tecnica }}</p>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium text-[11px]">
                  {{ it.familia_nome }}
                </span>
              </td>
              <td class="px-5 py-3.5 font-mono font-semibold text-slate-900">
                R$ {{ it.preco_base }}
              </td>
              <td class="px-5 py-3.5 font-medium text-slate-500">
                {{ it.unidade_medida }}
              </td>
              <td class="px-5 py-3.5 text-center">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="it.ativo ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'"
                >
                  {{ it.ativo ? 'ATIVO' : 'INATIVO' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '@/services/api';

const loading = ref(true);
const itens = ref([]);
const familias = ref([]);
const searchQuery = ref('');
const selectedFamilia = ref(null);

async function fetchCatalogo() {
  loading.value = true;
  try {
    const [resItens, resFamilias] = await Promise.all([
      api.get('/catalogo/'),
      api.get('/familias/'),
    ]);
    itens.value = resItens.results || resItens;
    familias.value = resFamilias.results || resFamilias;
  } catch (err) {
    console.error('Erro ao carregar catálogo:', err);
  } finally {
    loading.value = false;
  }
}

const filteredItens = computed(() => {
  return itens.value.filter(it => {
    const search = searchQuery.value.toLowerCase();
    const matchesSearch =
      !search ||
      it.codigo_completo?.toLowerCase().includes(search) ||
      it.sku_codigo?.toLowerCase().includes(search) ||
      it.codigo_identificador?.toLowerCase().includes(search) ||
      it.nome.toLowerCase().includes(search) ||
      it.especificacao_tecnica?.toLowerCase().includes(search);

    const matchesFamilia =
      !selectedFamilia.value || it.familia === selectedFamilia.value;

    return matchesSearch && matchesFamilia;
  });
});

onMounted(fetchCatalogo);
</script>
