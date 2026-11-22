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
        @click="abrirModalNovoProjeto"
        class="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-md shadow-brand-600/20 transition-all flex items-center justify-center shrink-0 gap-1.5"
      >
        <span class="text-base font-black">+</span> Nova Requisição de Projeto
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
            <span
              class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border"
              :class="statusClass(proj.status)"
            >
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

    <!-- ─── MODAL: Cadastrar Novo Projeto ─────────────────────────────────── -->
    <Transition name="fade">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="fecharModal"
      >
        <!-- Overlay -->
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="fecharModal"></div>

        <!-- Painel do Modal -->
        <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">

          <!-- Cabeçalho -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50 shrink-0">
            <div>
              <h3 class="text-base font-bold text-slate-900">📋 Nova Requisição de Projeto</h3>
              <p class="text-xs text-slate-500 mt-0.5">Preencha todos os campos essenciais para registrar a demanda.</p>
            </div>
            <button @click="fecharModal" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Corpo (scrollável) -->
          <div class="overflow-y-auto p-6 space-y-6">

            <!-- Alerta de erro global -->
            <div v-if="formError" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2">
              <span class="text-base mt-0.5 shrink-0">⚠️</span>
              <span>{{ formError }}</span>
            </div>

            <!-- SEÇÃO 1: Identificação do Projeto -->
            <div>
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                1. Identificação do Projeto
              </h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                <!-- Código -->
                <div>
                  <label class="block text-xs font-semibold text-slate-700 mb-1.5">
                    Código do Projeto <span class="text-red-500">*</span>
                  </label>
                  <div class="flex gap-2">
                    <input
                      v-model="form.codigo_projeto_alfanumerico"
                      type="text"
                      placeholder="Ex: PR-132-01"
                      class="flex-1 px-3 py-2 rounded-xl border text-xs font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                      :class="errors.codigo ? 'border-red-300 bg-red-50' : 'border-slate-200'"
                    />
                    <button
                      type="button"
                      @click="gerarCodigo"
                      :disabled="gerandoCodigo"
                      title="Gerar próximo código automaticamente"
                      class="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors disabled:opacity-50 shrink-0"
                    >
                      {{ gerandoCodigo ? '...' : '⚡ Auto' }}
                    </button>
                  </div>
                  <p v-if="errors.codigo" class="mt-1 text-[11px] text-red-500">{{ errors.codigo }}</p>
                  <p class="mt-1 text-[11px] text-slate-400">Padrão: PR-[número]-01. Clique em ⚡ Auto para gerar.</p>
                </div>

                <!-- Título -->
                <div>
                  <label class="block text-xs font-semibold text-slate-700 mb-1.5">
                    Título Resumido da Demanda <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.titulo"
                    type="text"
                    placeholder="Ex: Medição de Nível no Tanque de Xarope"
                    maxlength="200"
                    class="w-full px-3 py-2 rounded-xl border text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                    :class="errors.titulo ? 'border-red-300 bg-red-50' : 'border-slate-200'"
                  />
                  <p v-if="errors.titulo" class="mt-1 text-[11px] text-red-500">{{ errors.titulo }}</p>
                </div>
              </div>

              <!-- Descrição da Demanda -->
              <div class="mt-4">
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">
                  Descrição Detalhada da Demanda <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="form.descricao_demanda"
                  rows="4"
                  placeholder="Descreva em detalhes o que o cliente necessita. Ex: Cliente necessita de um sistema que mede volume de um tanque de produtos químicos, com saída 4-20mA para CLP Siemens S7-1200..."
                  class="w-full px-3 py-2 rounded-xl border text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none leading-relaxed"
                  :class="errors.descricao_demanda ? 'border-red-300 bg-red-50' : 'border-slate-200'"
                ></textarea>
                <p v-if="errors.descricao_demanda" class="mt-1 text-[11px] text-red-500">{{ errors.descricao_demanda }}</p>
                <p class="mt-1 text-[11px] text-slate-400">Inclua: objetivo, instrumentação existente, integração com sistemas, restrições de espaço/temperatura, etc.</p>
              </div>
            </div>

            <!-- SEÇÃO 2: Cliente -->
            <div class="border-t border-slate-100 pt-6">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  2. Cliente Demandante
                </h4>
                <button
                  type="button"
                  @click="modoNovoCliente = !modoNovoCliente; form.cliente = null; clienteSelecionado = null"
                  class="text-xs text-brand-600 hover:text-brand-800 font-semibold transition-colors"
                >
                  {{ modoNovoCliente ? '← Buscar cliente existente' : '+ Cadastrar novo cliente' }}
                </button>
              </div>

              <!-- Busca de cliente existente -->
              <div v-if="!modoNovoCliente">
                <div class="relative">
                  <input
                    v-model="buscaCliente"
                    @input="buscarClientes"
                    type="text"
                    placeholder="Buscar cliente pelo nome, contato ou local..."
                    class="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                    :class="errors.cliente ? 'border-red-300 bg-red-50' : 'border-slate-200'"
                  />
                  <span class="absolute left-3 top-2.5 text-slate-400 text-xs">🏭</span>
                </div>

                <!-- Resultados da busca -->
                <div v-if="clientesBusca.length > 0 && !clienteSelecionado" class="mt-2 border border-slate-200 rounded-xl overflow-hidden shadow-lg">
                  <button
                    v-for="c in clientesBusca"
                    :key="c.id"
                    type="button"
                    @click="selecionarCliente(c)"
                    class="w-full text-left px-4 py-3 hover:bg-brand-50 border-b border-slate-100 last:border-0 transition-colors"
                  >
                    <p class="text-xs font-bold text-slate-900">{{ c.nome_cliente }}</p>
                    <p class="text-[11px] text-slate-500 mt-0.5">📍 {{ c.local_aproximado }} • 👤 {{ c.responsavel_contato }}</p>
                  </button>
                </div>

                <!-- Cliente selecionado -->
                <div v-if="clienteSelecionado" class="mt-2 p-3 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-between">
                  <div>
                    <p class="text-xs font-bold text-brand-900">✅ {{ clienteSelecionado.nome_cliente }}</p>
                    <p class="text-[11px] text-brand-700 mt-0.5">📍 {{ clienteSelecionado.local_aproximado }} • 👤 {{ clienteSelecionado.responsavel_contato }}</p>
                  </div>
                  <button type="button" @click="clienteSelecionado = null; form.cliente = null; buscaCliente = ''" class="text-brand-600 hover:text-red-600 text-xs font-bold transition-colors">✕</button>
                </div>

                <p v-if="errors.cliente" class="mt-1 text-[11px] text-red-500">{{ errors.cliente }}</p>
              </div>

              <!-- Formulário novo cliente -->
              <div v-else class="bg-slate-50 rounded-xl border border-slate-200 p-4 space-y-3">
                <p class="text-[11px] text-slate-500 font-medium">O cliente será cadastrado junto com o projeto.</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Nome do Cliente / Razão Social <span class="text-red-500">*</span></label>
                    <input v-model="novoCliente.nome_cliente" type="text" placeholder="Ex: Fábrica Piraquê S.A."
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                      :class="errors.novoClienteNome ? 'border-red-300 bg-red-50' : ''"
                    />
                    <p v-if="errors.novoClienteNome" class="mt-1 text-[11px] text-red-500">{{ errors.novoClienteNome }}</p>
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Responsável pelo Contato <span class="text-red-500">*</span></label>
                    <input v-model="novoCliente.responsavel_contato" type="text" placeholder="Ex: Sandro"
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                      :class="errors.novoClienteContato ? 'border-red-300 bg-red-50' : ''"
                    />
                    <p v-if="errors.novoClienteContato" class="mt-1 text-[11px] text-red-500">{{ errors.novoClienteContato }}</p>
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Local Aproximado <span class="text-red-500">*</span></label>
                    <input v-model="novoCliente.local_aproximado" type="text" placeholder="Ex: Piraquê - Madureira, RJ"
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                      :class="errors.novoClienteLocal ? 'border-red-300 bg-red-50' : ''"
                    />
                    <p v-if="errors.novoClienteLocal" class="mt-1 text-[11px] text-red-500">{{ errors.novoClienteLocal }}</p>
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Telefone / WhatsApp</label>
                    <input v-model="novoCliente.telefone_contato" type="text" placeholder="(21) 99999-9999"
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">E-mail de Contato</label>
                    <input v-model="novoCliente.email_contato" type="email" placeholder="contato@empresa.com.br"
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">CNPJ</label>
                    <input v-model="novoCliente.cnpj" type="text" placeholder="00.000.000/0001-00"
                      class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- SEÇÃO 3: Contexto Adicional -->
            <div class="border-t border-slate-100 pt-6">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                3. Contexto Adicional (Opcional)
              </h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-700 mb-1.5">Urgência / Prazo Desejado</label>
                  <select v-model="form.urgencia"
                    class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
                  >
                    <option value="">Sem prazo definido</option>
                    <option value="NORMAL">Normal (sem urgência)</option>
                    <option value="URGENTE">Urgente (até 1 semana)</option>
                    <option value="CRITICO">Crítico (até 2 dias)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-700 mb-1.5">Referência / Oportunidade Comercial</label>
                  <input v-model="form.referencia_comercial" type="text" placeholder="Ex: ORC-2026-089, RFQ-01"
                    class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <div class="mt-4">
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Observações para o Técnico</label>
                <textarea v-model="form.obs_tecnico" rows="2"
                  placeholder="Informações que podem ajudar o técnico antes de iniciar o desenvolvimento (restrições, contatos diretos, visitas já realizadas, etc.)..."
                  class="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
                ></textarea>
              </div>
            </div>

          </div><!-- /body -->

          <!-- Rodapé fixo com ações -->
          <div class="px-6 py-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-3 shrink-0">
            <div class="text-[11px] text-slate-400">
              <span class="text-red-400">*</span> Campos obrigatórios
            </div>
            <div class="flex gap-2">
              <button
                type="button"
                @click="fecharModal"
                class="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                @click="salvarProjeto"
                :disabled="salvando"
                class="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span v-if="salvando" class="animate-spin">⏳</span>
                {{ salvando ? 'Cadastrando...' : '✅ Cadastrar Projeto' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/services/api';

const authStore = useAuthStore();
const router = useRouter();

const loading = ref(true);
const showModal = ref(false);
const projetos = ref([]);
const searchQuery = ref('');
const selectedStatus = ref('TODOS');

// ── Estado do formulário ──────────────────────────────────────────────────────
const salvando = ref(false);
const gerandoCodigo = ref(false);
const formError = ref('');
const errors = ref({});
const modoNovoCliente = ref(false);
const buscaCliente = ref('');
const clientesBusca = ref([]);
const clienteSelecionado = ref(null);
let buscaTimeout = null;

const form = ref({
  codigo_projeto_alfanumerico: '',
  titulo: '',
  descricao_demanda: '',
  cliente: null,
  urgencia: '',
  referencia_comercial: '',
  obs_tecnico: '',
});

const novoCliente = ref({
  nome_cliente: '',
  responsavel_contato: '',
  local_aproximado: '',
  telefone_contato: '',
  email_contato: '',
  cnpj: '',
});

// ── Status ────────────────────────────────────────────────────────────────────
const statusOptions = [
  { value: 'TODOS', label: 'Todos os Status' },
  { value: 'AGUARDANDO_AGENDAMENTO', label: 'Aguardando Agendamento' },
  { value: 'EM_DESENVOLVIMENTO', label: 'Em Desenvolvimento' },
  { value: 'AGUARDANDO_INFORMACAO', label: 'Pausado (Aguardando Info)' },
  { value: 'DEFINICAO_COMERCIAL', label: 'Definição Comercial' },
  { value: 'CONCLUIDO', label: 'Concluídos' },
];

function statusClass(status) {
  const map = {
    AGUARDANDO_AGENDAMENTO: 'bg-amber-50 text-amber-700 border-amber-200',
    EM_DESENVOLVIMENTO:     'bg-blue-50 text-blue-700 border-blue-200',
    AGUARDANDO_INFORMACAO:  'bg-orange-50 text-orange-700 border-orange-200',
    DEFINICAO_COMERCIAL:    'bg-purple-50 text-purple-700 border-purple-200',
    INSTALACAO:             'bg-cyan-50 text-cyan-700 border-cyan-200',
    CONCLUIDO:              'bg-green-50 text-green-700 border-green-200',
    CANCELADO:              'bg-slate-100 text-slate-500 border-slate-200',
  };
  return map[status] || 'bg-slate-100 text-slate-600 border-slate-200';
}

// ── Busca / Filtros ───────────────────────────────────────────────────────────
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
    const q = searchQuery.value.toLowerCase();
    const matchesSearch =
      !q ||
      p.codigo_projeto_alfanumerico.toLowerCase().includes(q) ||
      p.titulo.toLowerCase().includes(q) ||
      (p.cliente_nome && p.cliente_nome.toLowerCase().includes(q)) ||
      (p.cliente_contato && p.cliente_contato.toLowerCase().includes(q));

    const matchesStatus =
      selectedStatus.value === 'TODOS' || p.status === selectedStatus.value;

    return matchesSearch && matchesStatus;
  });
});

// ── Modal ─────────────────────────────────────────────────────────────────────
async function abrirModalNovoProjeto() {
  resetForm();
  showModal.value = true;
  await gerarCodigo();
}

function fecharModal() {
  showModal.value = false;
  resetForm();
}

function resetForm() {
  form.value = { codigo_projeto_alfanumerico: '', titulo: '', descricao_demanda: '', cliente: null, urgencia: '', referencia_comercial: '', obs_tecnico: '' };
  novoCliente.value = { nome_cliente: '', responsavel_contato: '', local_aproximado: '', telefone_contato: '', email_contato: '', cnpj: '' };
  errors.value = {};
  formError.value = '';
  buscaCliente.value = '';
  clientesBusca.value = [];
  clienteSelecionado.value = null;
  modoNovoCliente.value = false;
}

// ── Gerador de código ─────────────────────────────────────────────────────────
async function gerarCodigo() {
  gerandoCodigo.value = true;
  try {
    const data = await api.get('/projetos/proximo-codigo/');
    form.value.codigo_projeto_alfanumerico = data.codigo;
  } catch (e) {
    console.error('Erro ao gerar código:', e);
  } finally {
    gerandoCodigo.value = false;
  }
}

// ── Busca de clientes ─────────────────────────────────────────────────────────
function buscarClientes() {
  clearTimeout(buscaTimeout);
  if (buscaCliente.value.length < 2) {
    clientesBusca.value = [];
    return;
  }
  buscaTimeout = setTimeout(async () => {
    try {
      const data = await api.get(`/clientes/?search=${encodeURIComponent(buscaCliente.value)}`);
      clientesBusca.value = (data.results || data).slice(0, 6);
    } catch (e) {
      clientesBusca.value = [];
    }
  }, 300);
}

function selecionarCliente(cliente) {
  clienteSelecionado.value = cliente;
  form.value.cliente = cliente.id;
  buscaCliente.value = cliente.nome_cliente;
  clientesBusca.value = [];
  errors.value.cliente = '';
}

// ── Validação ─────────────────────────────────────────────────────────────────
function validar() {
  const e = {};
  if (!form.value.codigo_projeto_alfanumerico.trim())
    e.codigo = 'O código do projeto é obrigatório.';
  else if (!/^PR-\d+-\d+$/.test(form.value.codigo_projeto_alfanumerico.trim()))
    e.codigo = 'Formato inválido. Use o padrão PR-XXX-01.';

  if (!form.value.titulo.trim())
    e.titulo = 'O título da demanda é obrigatório.';

  if (!form.value.descricao_demanda.trim())
    e.descricao_demanda = 'A descrição detalhada da demanda é obrigatória.';
  else if (form.value.descricao_demanda.trim().length < 20)
    e.descricao_demanda = 'Descreva a demanda com pelo menos 20 caracteres.';

  if (!modoNovoCliente.value) {
    if (!form.value.cliente)
      e.cliente = 'Selecione um cliente existente ou cadastre um novo.';
  } else {
    if (!novoCliente.value.nome_cliente.trim())
      e.novoClienteNome = 'Nome do cliente é obrigatório.';
    if (!novoCliente.value.responsavel_contato.trim())
      e.novoClienteContato = 'Responsável pelo contato é obrigatório.';
    if (!novoCliente.value.local_aproximado.trim())
      e.novoClienteLocal = 'Local aproximado é obrigatório.';
  }

  errors.value = e;
  return Object.keys(e).length === 0;
}

// ── Salvar ────────────────────────────────────────────────────────────────────
async function salvarProjeto() {
  formError.value = '';
  if (!validar()) return;

  salvando.value = true;
  try {
    // 1. Se for novo cliente, cadastra primeiro
    if (modoNovoCliente.value) {
      const clienteCriado = await api.post('/clientes/', novoCliente.value);
      form.value.cliente = clienteCriado.id;
    }

    // 2. Monta payload sem campos extras do UI
    const payload = {
      codigo_projeto_alfanumerico: form.value.codigo_projeto_alfanumerico.trim(),
      titulo: form.value.titulo.trim(),
      descricao_demanda: form.value.descricao_demanda.trim(),
      cliente: form.value.cliente,
    };

    // 3. Adiciona obs ao final da descrição se houver
    if (form.value.obs_tecnico?.trim()) {
      payload.descricao_demanda += `\n\n📝 Observações para o técnico:\n${form.value.obs_tecnico.trim()}`;
    }

    // 4. Cria o projeto
    const projeto = await api.post('/projetos/', payload);

    // 5. Atualiza a lista e redireciona
    fecharModal();
    await fetchProjetos();
    router.push(`/projetos/${projeto.id}`);

  } catch (err) {
    if (err.data) {
      // Erros de validação do DRF
      if (err.data.codigo_projeto_alfanumerico) {
        errors.value.codigo = Array.isArray(err.data.codigo_projeto_alfanumerico)
          ? err.data.codigo_projeto_alfanumerico[0]
          : err.data.codigo_projeto_alfanumerico;
      }
      formError.value = err.data.detail || err.data.non_field_errors?.[0] || 'Verifique os campos e tente novamente.';
    } else {
      formError.value = err.message || 'Erro de conexão. Tente novamente.';
    }
  } finally {
    salvando.value = false;
  }
}

onMounted(fetchProjetos);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
