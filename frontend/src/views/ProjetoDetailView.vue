<template>
  <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
    Carregando detalhes do projeto...
  </div>

  <div v-else-if="!projeto" class="p-12 text-center text-red-500 text-sm">
    Projeto não encontrado.
  </div>

  <div v-else class="space-y-6">
    <!-- Cabeçalho do Projeto -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <span class="font-mono font-black text-brand-700 bg-brand-50 border border-brand-200 px-3 py-1 rounded-xl text-sm">
            {{ projeto.codigo_projeto_alfanumerico }}
          </span>
          <span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            {{ projeto.status_display }}
          </span>
        </div>
        <h2 class="text-xl font-bold text-slate-900 mt-2">{{ projeto.titulo }}</h2>
        <p class="text-xs text-slate-500 mt-0.5">
          Cliente: <strong class="text-slate-800">{{ projeto.cliente?.nome_cliente }}</strong> •
          Responsável: <strong>{{ projeto.cliente?.responsavel_contato }}</strong> ({{ projeto.cliente?.local_aproximado }})
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <router-link
          to="/projetos"
          class="px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
        >
          &larr; Voltar
        </router-link>
      </div>
    </div>

    <!-- Navegação por Abas (Tabs) -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div class="flex border-b border-slate-200 overflow-x-auto text-xs font-semibold bg-slate-50/50">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-5 py-3.5 border-b-2 transition-all whitespace-nowrap flex items-center space-x-2"
          :class="[
            activeTab === tab.id
              ? 'border-brand-600 text-brand-700 bg-white font-bold'
              : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- Conteúdo da Aba Ativa -->
      <div class="p-6">
        <!-- Aba 1: Visão Geral -->
        <div v-if="activeTab === 'geral'" class="space-y-6">
          <div>
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Descrição da Demanda</h3>
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 leading-relaxed">
              {{ projeto.descricao_demanda }}
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-xl border border-slate-200 bg-white">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Governança Técnica (SLA)</h4>
              <div v-if="projeto.agenda_tecnica_detalhes" class="text-xs space-y-1.5 text-slate-600">
                <p>Técnico: <strong class="text-slate-900">{{ projeto.agenda_tecnica_detalhes.tecnico_detalhes?.nome_completo }}</strong></p>
                <p>Fila: <strong>#{{ projeto.agenda_tecnica_detalhes.ordem_execucao }}</strong></p>
                <p>Status da Fila: <strong class="text-brand-700">{{ projeto.agenda_tecnica_detalhes.status_agenda_display }}</strong></p>
                <p>Meta SLA: <strong>{{ projeto.agenda_tecnica_detalhes.horas_estimadas_sla }} horas</strong></p>
                <p>Horas Trabalhadas: <strong>{{ projeto.agenda_tecnica_detalhes.horas_efetivas_gastas }} horas</strong></p>
              </div>
              <div v-else class="text-xs text-amber-600">
                Demanda ainda aguardando agendamento pelo Gestor.
              </div>
            </div>

            <div class="p-4 rounded-xl border border-slate-200 bg-white">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Solicitante</h4>
              <div class="text-xs space-y-1.5 text-slate-600">
                <p>Vendedor: <strong class="text-slate-900">{{ projeto.criado_por?.nome_completo }}</strong></p>
                <p>E-mail: <strong>{{ projeto.criado_por?.email }}</strong></p>
                <p>Data da Demanda: <strong>{{ new Date(projeto.created_at).toLocaleDateString('pt-BR') }}</strong></p>
              </div>
            </div>
          </div>
        </div>

        <!-- Aba 2: BOM e Proposta -->
        <div v-else-if="activeTab === 'proposta'" class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-slate-800 text-sm">Lista de Materiais (BOM Hierárquica)</h3>
            <span class="text-xs text-slate-400">Total calculado diretamente do catálogo central</span>
          </div>

          <div v-if="propostas.length === 0" class="p-8 text-center text-slate-400 text-xs">
            Nenhuma proposta técnica vinculada a este projeto ainda.
          </div>

          <div v-else v-for="prop in propostas" :key="prop.id" class="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-4">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-800 text-sm">Proposta v{{ prop.versao }} [{{ prop.status_proposta_display }}]</span>
              <span class="font-mono font-black text-brand-700 text-base">R$ {{ prop.valor_total }}</span>
            </div>

            <div v-for="cj in prop.conjuntos" :key="cj.id" class="bg-white p-3 rounded-lg border border-slate-200">
              <p class="font-bold text-xs text-slate-900 mb-2">📁 Conjunto: {{ cj.nome_conjunto }}</p>
              <div class="space-y-1.5 text-xs text-slate-700 divide-y divide-slate-100">
                <div v-for="it in cj.itens" :key="it.id" class="pt-1.5 flex justify-between items-center">
                  <span>{{ it.quantidade }}x <strong>[{{ it.catalogo_item_detalhes?.codigo_completo }}]</strong> {{ it.catalogo_item_detalhes?.nome }}</span>
                  <span class="font-mono font-semibold">R$ {{ it.subtotal }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Aba 3: Relatório Descritivo -->
        <div v-else-if="activeTab === 'relatorio'" class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-slate-800 text-sm">Memorial Técnico Descritivo (TipTap)</h3>
          </div>

          <div v-if="relatorios.length === 0" class="p-8 text-center text-slate-400 text-xs">
            Nenhum relatório elaborado até o momento.
          </div>

          <div v-else v-for="rel in relatorios" :key="rel.id" class="border border-slate-200 rounded-xl p-5 bg-white space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="font-bold text-slate-900 text-sm">{{ rel.titulo }} (v{{ rel.versao }})</h4>
              <button
                @click="exportarDocx(rel)"
                class="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold hover:bg-blue-100 transition-colors"
              >
                📥 Exportar .docx
              </button>
            </div>
            <div class="p-4 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-800 prose prose-sm max-w-none" v-html="rel.conteudo_html"></div>
          </div>
        </div>

        <!-- Aba 4: Comentários (Planner) -->
        <div v-else-if="activeTab === 'comentarios'" class="space-y-4">
          <div class="space-y-3">
            <div
              v-for="com in projeto.comentarios"
              :key="com.id"
              class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-slate-900">{{ com.autor_detalhes?.nome_completo }}</span>
                <span class="text-[10px] text-slate-400">{{ new Date(com.created_at).toLocaleString('pt-BR') }}</span>
              </div>
              <p class="text-slate-700 leading-relaxed">{{ com.conteudo }}</p>
            </div>
          </div>

          <!-- Input para novo comentário -->
          <div class="flex gap-2 pt-2">
            <input
              v-model="novoComentario"
              type="text"
              placeholder="Escreva um comentário ou use @usuario para mencionar..."
              class="flex-1 px-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
              @keyup.enter="enviarComentario"
            />
            <button
              @click="enviarComentario"
              class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs transition-colors shrink-0"
            >
              Enviar
            </button>
          </div>
        </div>

        <!-- Aba 5: Histórico de SLA e Rastreabilidade -->
        <div v-else-if="activeTab === 'historico'" class="space-y-3">
          <h3 class="font-bold text-slate-800 text-sm mb-2">Linha do Tempo e Pausas de SLA</h3>
          <div class="divide-y divide-slate-100 text-xs">
            <div
              v-for="h in projeto.historico_status"
              :key="h.id"
              class="py-2.5 flex items-start justify-between"
            >
              <div>
                <p class="font-semibold text-slate-900">
                  {{ h.status_anterior }} &rarr; <span class="text-brand-700">{{ h.status_novo }}</span>
                  <span v-if="h.pausa_contagem_tempo" class="ml-2 px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px]">
                    ⏱️ SLA Congelado
                  </span>
                </p>
                <p v-if="h.motivo_retorno" class="text-slate-500 mt-0.5">Motivo: "{{ h.motivo_retorno }}"</p>
                <p class="text-[10px] text-slate-400 mt-0.5">Responsável: {{ h.usuario_nome }}</p>
              </div>
              <span class="text-[10px] text-slate-400 whitespace-nowrap">
                {{ new Date(h.data_mudanca).toLocaleString('pt-BR') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { api } from '@/services/api';

const route = useRoute();
const loading = ref(true);
const projeto = ref(null);
const propostas = ref([]);
const relatorios = ref([]);
const activeTab = ref('geral');
const novoComentario = ref('');

const tabs = [
  { id: 'geral', label: 'Visão Geral & Demanda', icon: '📋' },
  { id: 'proposta', label: 'Proposta & BOM em Árvore', icon: '🌲' },
  { id: 'relatorio', label: 'Relatório Descritivo', icon: '📄' },
  { id: 'comentarios', label: 'Discussões & Menções', icon: '💬' },
  { id: 'historico', label: 'Histórico & SLA', icon: '⏱️' },
];

async function loadData() {
  loading.value = true;
  try {
    const id = route.params.id;
    const [projData, propData, relData] = await Promise.all([
      api.get(`/projetos/${id}/`),
      api.get(`/propostas/?projeto_id=${id}`),
      api.get(`/relatorios-descritivos/?projeto_id=${id}`),
    ]);

    projeto.value = projData;
    propostas.value = propData.results || propData;
    relatorios.value = relData.results || relData;
  } catch (err) {
    console.error('Erro ao carregar detalhes do projeto:', err);
  } finally {
    loading.value = false;
  }
}

async function enviarComentario() {
  if (!novoComentario.value.trim()) return;

  try {
    await api.post(`/projetos/${projeto.value.id}/comentarios/`, {
      conteudo: novoComentario.value
    });
    novoComentario.value = '';
    const updated = await api.get(`/projetos/${projeto.value.id}/`);
    projeto.value = updated;
  } catch (err) {
    alert('Erro ao enviar comentário: ' + err.message);
  }
}

async function exportarDocx(rel) {
  try {
    const res = await api.post(`/relatorios-descritivos/${rel.id}/exportar_docx/`);
    alert(res.mensagem || 'Arquivo Word gerado no Object Storage!');
    if (res.arquivo_docx_url) {
      window.open(res.arquivo_docx_url, '_blank');
    }
  } catch (err) {
    alert('Erro ao exportar docx: ' + (err.data?.erro || err.message));
  }
}

onMounted(loadData);
</script>
