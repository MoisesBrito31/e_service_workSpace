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
          <span
            class="px-3 py-1 rounded-full text-xs font-semibold border"
            :class="statusBadgeClass(projeto.status)"
          >
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
          <span
            v-if="tab.id === 'forum' && feedEventos.length"
            class="px-2 py-0.5 rounded-full text-[10px] bg-brand-100 text-brand-800 font-bold ml-1"
          >
            {{ feedEventos.length }}
          </span>
        </button>
      </div>

      <!-- Conteúdo da Aba Ativa -->
      <div class="p-6">
        <!-- Aba 1: Fórum do Projeto & Visão Geral (Unificado estilo WhatsApp / Fórum) -->
        <div v-if="activeTab === 'forum'" class="space-y-6">

          <!-- Painel Retrátil de Resumo da Demanda / Governança -->
          <div class="border border-slate-200 rounded-2xl overflow-hidden bg-slate-50/70">
            <button
              @click="mostrarDetalhesDemanda = !mostrarDetalhesDemanda"
              class="w-full px-5 py-3.5 flex items-center justify-between text-left hover:bg-slate-100/70 transition-colors"
            >
              <div class="flex items-center space-x-2">
                <span class="text-base">📋</span>
                <span class="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Especificação da Demanda & Governança SLA
                </span>
              </div>
              <span class="text-xs text-brand-600 font-semibold flex items-center gap-1">
                {{ mostrarDetalhesDemanda ? 'Ocultar detalhes ▲' : 'Ver detalhes completos ▼' }}
              </span>
            </button>

            <div v-show="mostrarDetalhesDemanda" class="p-5 border-t border-slate-200/80 bg-white space-y-4">
              <div>
                <h4 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Descrição da Demanda</h4>
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
                  {{ projeto.descricao_demanda }}
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                <div class="p-4 rounded-xl border border-slate-200 bg-white">
                  <h4 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Governança Técnica (SLA)</h4>
                  <div v-if="projeto.agenda_tecnica_detalhes" class="text-xs space-y-1.5 text-slate-600">
                    <p>Técnico: <strong class="text-slate-900">{{ projeto.agenda_tecnica_detalhes.tecnico_detalhes?.nome_completo || 'Técnico Alocado' }}</strong></p>
                    <p>Fila de Prioridade: <strong>#{{ projeto.agenda_tecnica_detalhes.ordem_execucao }}</strong></p>
                    <p>Status da Fila: <strong class="text-brand-700">{{ projeto.agenda_tecnica_detalhes.status_agenda_display }}</strong></p>
                    <p>Meta SLA: <strong>{{ projeto.agenda_tecnica_detalhes.horas_estimadas_sla }} horas</strong></p>
                    <p>Horas Efetivas: <strong>{{ projeto.agenda_tecnica_detalhes.horas_efetivas_gastas }} horas</strong></p>
                  </div>
                  <div v-else class="text-xs text-amber-600 font-medium">
                    ⚠️ Demanda aguardando agendamento e ordem pelo Gestor.
                  </div>
                </div>

                <div class="p-4 rounded-xl border border-slate-200 bg-white">
                  <h4 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Origem da Requisição</h4>
                  <div class="text-xs space-y-1.5 text-slate-600">
                    <p>Vendedor: <strong class="text-slate-900">{{ projeto.criado_por?.nome_completo || projeto.criado_por?.username }}</strong></p>
                    <p>E-mail: <strong>{{ projeto.criado_por?.email || 'Não informado' }}</strong></p>
                    <p>Abertura: <strong>{{ new Date(projeto.created_at).toLocaleString('pt-BR') }}</strong></p>
                    <p>Cliente Contato: <strong>{{ projeto.cliente?.responsavel_contato }}</strong> ({{ projeto.cliente?.telefone_contato || 'Sem tel' }})</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Feed do Fórum estilo Conversa / WhatsApp -->
          <div class="border border-slate-200 rounded-2xl bg-slate-100/70 overflow-hidden shadow-inner flex flex-col h-[600px]">
            <!-- Header do Chat / Fórum -->
            <div class="bg-white px-5 py-3 border-b border-slate-200 flex items-center justify-between shadow-sm">
              <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center text-sm shadow-sm">
                  💬
                </div>
                <div>
                  <h4 class="text-xs font-bold text-slate-900">Mural de Discussão & Eventos do Projeto</h4>
                  <p class="text-[11px] text-slate-500">Timeline cronológica com atualizações de status, pausas e mensagens da equipe</p>
                </div>
              </div>
              <span class="text-[11px] text-slate-400 font-medium">
                {{ feedEventos.length }} registros
              </span>
            </div>

            <!-- Corpo da Conversa com rolagem -->
            <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              <div v-if="feedEventos.length === 0" class="text-center py-16 text-slate-400 text-xs">
                Nenhum evento ou comentário registrado ainda. Seja o primeiro a postar!
              </div>

              <!-- Loop da Timeline / Conversa -->
              <template v-for="(item, index) in feedEventos" :key="item.id || index">

                <!-- Separador de Data estilo WhatsApp -->
                <div
                  v-if="deveExibirSeparadorData(index)"
                  class="flex justify-center my-3"
                >
                  <span class="px-3 py-1 rounded-full text-[11px] font-semibold bg-white/90 text-slate-500 border border-slate-200 shadow-xs">
                    {{ formatarDataSeparador(item.data) }}
                  </span>
                </div>

                <!-- 1. EVENTO DO SISTEMA (Mudança de status, pausa de SLA, etc.) -->
                <div
                  v-if="item.tipo === 'evento'"
                  class="flex justify-center my-2"
                >
                  <div
                    class="max-w-lg w-full text-center px-4 py-2.5 rounded-xl border text-xs shadow-xs"
                    :class="eventoClasse(item)"
                  >
                    <div class="font-bold flex items-center justify-center gap-1.5">
                      <span>{{ item.icone }}</span>
                      <span>{{ item.titulo }}</span>
                    </div>

                    <div v-if="item.motivo" class="mt-1 text-slate-600 italic">
                      "{{ item.motivo }}"
                    </div>

                    <div class="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-2">
                      <span>Por: {{ item.usuario_nome }}</span>
                      <span>•</span>
                      <span>{{ formatarHora(item.data) }}</span>
                    </div>
                  </div>
                </div>

                <!-- 2. COMENTÁRIO / MENSAGEM DO USUÁRIO (Balão estilo WhatsApp) -->
                <div
                  v-else-if="item.tipo === 'comentario'"
                  class="flex"
                  :class="item.ehMeu ? 'justify-end' : 'justify-start'"
                >
                  <div
                    class="max-w-[85%] sm:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm border relative text-xs"
                    :class="[
                      item.ehMeu
                        ? 'bg-emerald-50 border-emerald-200 text-slate-900 rounded-tr-xs'
                        : 'bg-white border-slate-200 text-slate-900 rounded-tl-xs'
                    ]"
                  >
                    <!-- Cabeçalho da Mensagem -->
                    <div class="flex items-center justify-between gap-2 mb-1">
                      <div class="flex items-center space-x-1.5">
                        <span class="font-bold text-[11px]" :class="item.ehMeu ? 'text-emerald-800' : 'text-brand-700'">
                          {{ item.ehMeu ? 'Você' : item.autor_nome }}
                        </span>
                        <span
                          v-if="item.autor_cargo"
                          class="px-1.5 py-0.2 rounded text-[9px] font-semibold uppercase"
                          :class="cargoTagClass(item.autor_cargo)"
                        >
                          {{ item.autor_cargo }}
                        </span>
                      </div>
                    </div>

                    <!-- Conteúdo com suporte a marcação @menções exibindo o nome do usuário -->
                    <p class="text-slate-800 leading-relaxed whitespace-pre-wrap break-words" v-html="formatarMensagem(item.conteudo, item)"></p>

                    <!-- Horário no rodapé do balão estilo WhatsApp -->
                    <div class="text-[10px] text-slate-400 text-right mt-1.5 flex items-center justify-end gap-1">
                      <span>{{ formatarHora(item.data) }}</span>
                      <span v-if="item.ehMeu" class="text-emerald-600 font-bold">✓✓</span>
                    </div>
                  </div>
                </div>

              </template>
            </div>

            <!-- Barra de envio estilo WhatsApp / Slack com Dropdown de Menções -->
            <div class="bg-white p-3 border-t border-slate-200 relative">

              <!-- Dropdown de Sugestões de Menção (@usuario) -->
              <div
                v-if="mostrarDropdownMencoes && usuariosFiltrados.length > 0"
                class="absolute bottom-full mb-2 left-3 right-3 sm:right-auto sm:w-80 bg-white rounded-xl border border-slate-200 shadow-2xl overflow-hidden z-30"
              >
                <!-- Cabeçalho do Dropdown -->
                <div class="px-3 py-2 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-[11px]">
                  <span class="font-bold text-slate-600 flex items-center gap-1">
                    <span class="text-brand-600 font-black">@</span> Mencionar Usuário
                  </span>
                  <span class="text-[10px] text-slate-400">Use ↑↓ e Enter</span>
                </div>

                <!-- Lista de Usuários Disponíveis -->
                <div class="max-h-52 overflow-y-auto divide-y divide-slate-100">
                  <button
                    v-for="(user, idx) in usuariosFiltrados"
                    :key="user.id"
                    type="button"
                    @mousedown.prevent="selecionarUsuarioMencao(user)"
                    @mouseenter="indiceMencaoAtivo = idx"
                    class="w-full text-left px-3.5 py-2.5 flex items-center justify-between gap-2 transition-colors text-xs"
                    :class="[
                      indiceMencaoAtivo === idx
                        ? 'bg-brand-50 text-brand-900'
                        : 'hover:bg-slate-50 text-slate-800'
                    ]"
                  >
                    <div class="flex items-center space-x-2.5 min-w-0">
                      <!-- Avatar com iniciais -->
                      <div class="w-7 h-7 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[10px] shrink-0 border border-slate-300">
                        {{ obterIniciais(user) }}
                      </div>
                      <div class="min-w-0">
                        <p class="font-bold text-slate-900 text-xs truncate">
                          {{ user.first_name || user.last_name ? `${user.first_name} ${user.last_name}`.trim() : user.username }}
                        </p>
                        <p class="text-[11px] text-brand-600 font-mono leading-none mt-0.5">
                          @{{ user.username }}
                        </p>
                      </div>
                    </div>

                    <!-- Badge do Cargo -->
                    <span
                      v-if="user.cargo"
                      class="px-2 py-0.5 rounded text-[9px] font-semibold uppercase shrink-0"
                      :class="cargoTagClass(user.cargo)"
                    >
                      {{ user.cargo }}
                    </span>
                  </button>
                </div>
              </div>

              <!-- Formulário com Input -->
              <form @submit.prevent="enviarComentario" class="flex items-center gap-2">
                <div class="relative flex-1">
                  <input
                    ref="inputComentarioRef"
                    v-model="novoComentario"
                    type="text"
                    placeholder="Escreva um comentário no fórum... (digite @ para mencionar um colega)"
                    class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 bg-slate-50 focus:bg-white transition-all text-slate-800 placeholder:text-slate-400"
                    :disabled="enviandoComentario"
                    @input="tratarInputComentario"
                    @keydown="tratarKeydownComentario"
                    @click="verificarMencao"
                    @keyup="verificarMencao"
                  />
                  <!-- Botão rápido de adicionar @ se o input estiver vazio ou quiser inserir fácil -->
                  <button
                    type="button"
                    @click="inserirArroba"
                    class="absolute right-3 top-2.5 text-slate-400 hover:text-brand-600 font-bold text-xs transition-colors"
                    title="Mencionar usuário (@)"
                  >
                    @
                  </button>
                </div>

                <button
                  type="submit"
                  :disabled="!novoComentario.trim() || enviandoComentario"
                  class="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white font-bold text-xs shadow-md shadow-brand-600/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center shrink-0 space-x-1.5"
                >
                  <span v-if="enviandoComentario" class="animate-spin">⏳</span>
                  <span v-else>Enviar</span>
                  <span class="text-sm">✈️</span>
                </button>
              </form>
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/services/api';

const authStore = useAuthStore();
const route = useRoute();

const loading = ref(true);
const projeto = ref(null);
const propostas = ref([]);
const relatorios = ref([]);
const activeTab = ref('forum');
const mostrarDetalhesDemanda = ref(true);

const novoComentario = ref('');
const enviandoComentario = ref(false);
const chatContainer = ref(null);
const inputComentarioRef = ref(null);

// ── Sistema de Menções (@usuario) ───────────────────────────────────────────
const usuariosMencoes = ref([]);
const mostrarDropdownMencoes = ref(false);
const termoMencao = ref('');
const indiceMencaoAtivo = ref(0);

const tabs = [
  { id: 'forum', label: 'Visão Geral & Fórum', icon: '💬' },
  { id: 'proposta', label: 'Proposta & BOM em Árvore', icon: '🌲' },
  { id: 'relatorio', label: 'Relatório Descritivo', icon: '📄' },
];

function statusBadgeClass(status) {
  const map = {
    AGUARDANDO_AGENDAMENTO: 'bg-amber-50 text-amber-700 border-amber-200',
    EM_DESENVOLVIMENTO: 'bg-blue-50 text-blue-700 border-blue-200',
    AGUARDANDO_INFORMACAO: 'bg-orange-50 text-orange-700 border-orange-200',
    DEFINICAO_COMERCIAL: 'bg-purple-50 text-purple-700 border-purple-200',
    INSTALACAO: 'bg-cyan-50 text-cyan-700 border-cyan-200',
    CONCLUIDO: 'bg-green-50 text-green-700 border-green-200',
    CANCELADO: 'bg-slate-100 text-slate-500 border-slate-200',
  };
  return map[status] || 'bg-slate-50 text-slate-700 border-slate-200';
}

function cargoTagClass(cargo) {
  const map = {
    VENDEDOR: 'bg-blue-100 text-blue-800',
    TECNICO: 'bg-emerald-100 text-emerald-800',
    GESTOR: 'bg-purple-100 text-purple-800',
    COMERCIAL: 'bg-amber-100 text-amber-800',
    ADMIN: 'bg-red-100 text-red-800',
  };
  return map[cargo] || 'bg-slate-100 text-slate-700';
}

function obterIniciais(user) {
  if (user.first_name && user.last_name) {
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
  }
  if (user.first_name) {
    return user.first_name.slice(0, 2).toUpperCase();
  }
  return user.username ? user.username.slice(0, 2).toUpperCase() : 'U';
}

/**
 * Filtra usuários para o autocomplete da menção com base no que foi digitado após o @
 */
const usuariosFiltrados = computed(() => {
  if (!mostrarDropdownMencoes.value) return [];
  const termo = termoMencao.value.toLowerCase().trim();

  const lista = usuariosMencoes.value.filter((u) => {
    const nomeCompleto = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase();
    const username = (u.username || '').toLowerCase();
    const cargo = (u.cargo || '').toLowerCase();
    return !termo || username.includes(termo) || nomeCompleto.includes(termo) || cargo.includes(termo);
  });

  return lista.slice(0, 8);
});

/**
 * Verifica se o cursor está logo após um caractere '@'
 */
function verificarMencao() {
  const el = inputComentarioRef.value;
  if (!el) {
    mostrarDropdownMencoes.value = false;
    return;
  }

  const pos = el.selectionStart;
  const textoAntes = novoComentario.value.slice(0, pos);

  // Procura por @ seguido de caracteres de username até a posição do cursor
  const match = textoAntes.match(/@([a-zA-Z0-9_.-]*)$/);

  if (match) {
    termoMencao.value = match[1];
    mostrarDropdownMencoes.value = true;
    if (indiceMencaoAtivo.value >= usuariosFiltrados.value.length) {
      indiceMencaoAtivo.value = 0;
    }
  } else {
    mostrarDropdownMencoes.value = false;
  }
}

function tratarInputComentario() {
  verificarMencao();
}

/**
 * Trata teclas de navegação no dropdown (Setas para cima/baixo, Enter, Tab e Escape)
 */
function tratarKeydownComentario(e) {
  if (!mostrarDropdownMencoes.value || usuariosFiltrados.value.length === 0) {
    return;
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    indiceMencaoAtivo.value = (indiceMencaoAtivo.value + 1) % usuariosFiltrados.value.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    indiceMencaoAtivo.value = (indiceMencaoAtivo.value - 1 + usuariosFiltrados.value.length) % usuariosFiltrados.value.length;
  } else if (e.key === 'Enter' || e.key === 'Tab') {
    e.preventDefault();
    const selecionado = usuariosFiltrados.value[indiceMencaoAtivo.value];
    if (selecionado) {
      selecionarUsuarioMencao(selecionado);
    }
  } else if (e.key === 'Escape') {
    mostrarDropdownMencoes.value = false;
  }
}

/**
 * Insere a menção no texto e reposiciona o cursor
 */
function selecionarUsuarioMencao(usuario) {
  const el = inputComentarioRef.value;
  const pos = el ? el.selectionStart : novoComentario.value.length;
  const textoAntes = novoComentario.value.slice(0, pos);
  const textoDepois = novoComentario.value.slice(pos);

  // Substitui a partir do último '@' encontrado antes do cursor
  const ultimoArroba = textoAntes.lastIndexOf('@');
  if (ultimoArroba !== -1) {
    const textoAntesDoArroba = textoAntes.slice(0, ultimoArroba);
    const mencaoFormatada = `@${usuario.username} `;
    novoComentario.value = textoAntesDoArroba + mencaoFormatada + textoDepois;

    mostrarDropdownMencoes.value = false;
    termoMencao.value = '';

    nextTick(() => {
      if (el) {
        el.focus();
        const novaPos = (textoAntesDoArroba + mencaoFormatada).length;
        el.setSelectionRange(novaPos, novaPos);
      }
    });
  }
}

function inserirArroba() {
  const el = inputComentarioRef.value;
  if (!el) return;
  const pos = el.selectionStart;
  const antes = novoComentario.value.slice(0, pos);
  const depois = novoComentario.value.slice(pos);

  novoComentario.value = `${antes}@${depois}`;
  nextTick(() => {
    el.focus();
    el.setSelectionRange(pos + 1, pos + 1);
    verificarMencao();
  });
}

/**
 * Monta o feed unificado em ordem cronológica (comentários + eventos de histórico).
 */
const feedEventos = computed(() => {
  if (!projeto.value) return [];

  const itens = [];
  const currentUserId = authStore.user?.id;
  const currentUsername = authStore.user?.username;

  // 1. Adiciona comentários
  if (projeto.value.comentarios) {
    projeto.value.comentarios.forEach((c) => {
      const autorId = c.autor_detalhes?.id || c.autor;
      const autorUsername = c.autor_detalhes?.username;
      const ehMeu = (currentUserId && autorId === currentUserId) || (currentUsername && autorUsername === currentUsername);

      itens.push({
        tipo: 'comentario',
        id: `com_${c.id}`,
        data: new Date(c.created_at),
        autor_nome: c.autor_detalhes?.nome_completo || c.autor_detalhes?.username || 'Usuário',
        autor_cargo: c.autor_detalhes?.cargo || '',
        conteudo: c.conteudo,
        mencoes_detalhes: c.mencoes_detalhes || [],
        ehMeu,
      });
    });
  }

  // 2. Adiciona eventos de histórico de status / SLA
  if (projeto.value.historico_status) {
    projeto.value.historico_status.forEach((h) => {
      let icone = '🔄';
      let titulo = `Status alterado: ${h.status_anterior} ➔ ${h.status_novo}`;

      if (h.status_anterior === 'INICIO') {
        icone = '🚀';
        titulo = `Demanda cadastrada no sistema (${h.status_novo})`;
      } else if (h.pausa_contagem_tempo || h.status_novo === 'AGUARDANDO_INFORMACAO') {
        icone = '⏱️';
        titulo = `SLA Congelado: Aguardando Informações`;
      } else if (h.status_novo === 'EM_DESENVOLVIMENTO') {
        icone = '▶️';
        titulo = `Desenvolvimento Técnico Iniciado`;
      } else if (h.status_novo === 'DEFINICAO_COMERCIAL') {
        icone = '💼';
        titulo = `Entregáveis concluídos ➔ Avançado para Definição Comercial`;
      } else if (h.status_novo === 'CONCLUIDO') {
        icone = '✅';
        titulo = `Projeto Concluído com Sucesso`;
      } else if (h.status_novo === 'CANCELADO') {
        icone = '❌';
        titulo = `Projeto Cancelado`;
      }

      itens.push({
        tipo: 'evento',
        id: `hist_${h.id}`,
        data: new Date(h.data_mudanca),
        icone,
        titulo,
        motivo: h.motivo_retorno,
        pausa: h.pausa_contagem_tempo,
        status_novo: h.status_novo,
        usuario_nome: h.usuario_nome || 'Sistema',
      });
    });
  }

  // Ordena cronologicamente: do mais antigo para o mais recente (como WhatsApp)
  return itens.sort((a, b) => a.data - b.data);
});

function eventoClasse(item) {
  if (item.pausa || item.status_novo === 'AGUARDANDO_INFORMACAO') {
    return 'bg-amber-50 border-amber-200 text-amber-900';
  }
  if (item.status_novo === 'CONCLUIDO') {
    return 'bg-green-50 border-green-200 text-green-900';
  }
  if (item.status_novo === 'CANCELADO') {
    return 'bg-red-50 border-red-200 text-red-900';
  }
  return 'bg-slate-50 border-slate-200 text-slate-800';
}

function formatarHora(date) {
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function formatarDataSeparador(date) {
  const hoje = new Date();
  if (date.toDateString() === hoje.toDateString()) {
    return 'Hoje';
  }
  const ontem = new Date();
  ontem.setDate(ontem.getDate() - 1);
  if (date.toDateString() === ontem.toDateString()) {
    return 'Ontem';
  }
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
}

function deveExibirSeparadorData(index) {
  if (index === 0) return true;
  const atual = feedEventos.value[index].data.toDateString();
  const anterior = feedEventos.value[index - 1].data.toDateString();
  return atual !== anterior;
}

function obterNomeExibicao(user) {
  if (!user) return '';
  if (user.nome_completo) return user.nome_completo;
  const partes = [user.first_name, user.last_name].filter(Boolean);
  return partes.length > 0 ? partes.join(' ') : user.username;
}

function formatarMensagem(texto, item) {
  if (!texto) return '';

  // Substitui cada @username pelo nome real do usuário mencionado no comentário
  return texto.replace(/@([\w.-]+)/g, (match, username) => {
    const usernameLower = username.toLowerCase();

    // 1. Busca primeiro nas menções registradas do comentário
    let user = item?.mencoes_detalhes?.find(
      (u) => (u.username || '').toLowerCase() === usernameLower
    );

    // 2. Se não encontrar, busca na lista global de usuários carregados
    if (!user) {
      user = usuariosMencoes.value.find(
        (u) => (u.username || '').toLowerCase() === usernameLower
      );
    }

    if (user) {
      const nome = obterNomeExibicao(user);
      const cargo = user.cargo ? ` • ${user.cargo}` : '';
      return `<span class="inline-flex items-center font-bold text-brand-700 bg-brand-50 px-1.5 py-0.5 rounded border border-brand-200/60 shadow-2xs" title="@${user.username}${cargo}">@${nome}</span>`;
    }

    return `<span class="font-bold text-brand-600 bg-brand-50 px-1.5 py-0.5 rounded border border-brand-200/50">${match}</span>`;
  });
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}

async function loadData() {
  loading.value = true;
  try {
    const id = route.params.id;
    const [projData, propData, relData, mencoesData] = await Promise.all([
      api.get(`/projetos/${id}/`),
      api.get(`/propostas/?projeto_id=${id}`),
      api.get(`/relatorios-descritivos/?projeto_id=${id}`),
      api.get('/users/mencoes/').catch(() => []),
    ]);

    projeto.value = projData;
    propostas.value = propData.results || propData;
    relatorios.value = relData.results || relData;
    usuariosMencoes.value = mencoesData || [];

    scrollToBottom();
  } catch (err) {
    console.error('Erro ao carregar detalhes do projeto:', err);
  } finally {
    loading.value = false;
  }
}

async function enviarComentario() {
  if (!novoComentario.value.trim() || enviandoComentario.value) return;

  mostrarDropdownMencoes.value = false;
  enviandoComentario.value = true;

  try {
    // Identifica usuários mencionados no texto pelo padrão @username
    const matches = novoComentario.value.match(/@([a-zA-Z0-9_.-]+)/g) || [];
    const usernames = matches.map((m) => m.slice(1).toLowerCase());
    const idsMencionados = usuariosMencoes.value
      .filter((u) => usernames.includes((u.username || '').toLowerCase()))
      .map((u) => u.id);

    await api.post(`/projetos/${projeto.value.id}/comentarios/`, {
      conteudo: novoComentario.value.trim(),
      mencoes: idsMencionados,
    });

    novoComentario.value = '';

    // Recarrega projeto atualizado
    const updated = await api.get(`/projetos/${projeto.value.id}/`);
    projeto.value = updated;
    scrollToBottom();
  } catch (err) {
    alert('Erro ao enviar mensagem: ' + (err.data?.detail || err.message));
  } finally {
    enviandoComentario.value = false;
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
