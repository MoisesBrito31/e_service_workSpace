<template>
  <div class="space-y-6">
    <!-- Header da Fila -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-900">Agenda Técnica & Fila Sequencial</h2>
        <p class="text-sm text-slate-500 mt-0.5">
          Governança de prioridades e controle de SLA com trava sequencial de execução.
        </p>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="fetchFila"
          class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
        >
          🔄 Atualizar Fila
        </button>
      </div>
    </div>

    <!-- Alerta Informativo da Trava Sequencial -->
    <div class="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-start space-x-3">
      <span class="text-lg">🔒</span>
      <div>
        <strong class="font-bold">Regra de Trava Sequencial Ativa:</strong>
        <p class="mt-0.5 text-amber-700">
          O técnico só pode iniciar a execução de projetos seguindo a ordem numérica da sua fila alocada pelo Gestor. Cards com ordem superior ficam bloqueados até a conclusão ou liberação do card anterior.
        </p>
      </div>
    </div>

    <!-- Lista de Cards da Fila -->
    <div v-if="loading" class="p-12 text-center text-slate-400 text-sm">
      Carregando fila técnica...
    </div>

    <div v-else-if="fila.length === 0" class="bg-white p-12 rounded-2xl border border-slate-200 text-center">
      <span class="text-4xl">🎉</span>
      <h3 class="text-base font-bold text-slate-800 mt-2">Nenhum projeto pendente na fila!</h3>
      <p class="text-xs text-slate-400 mt-1">Todos os projetos alocados foram concluídos.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in fila"
        :key="item.id"
        class="bg-white rounded-2xl border p-5 shadow-sm transition-all"
        :class="[
          item.status_agenda === 'EM_ANDAMENTO' ? 'border-brand-500 ring-2 ring-brand-100' : 'border-slate-200'
        ]"
      >
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <!-- Identificação e Ordem -->
          <div class="flex items-start space-x-4">
            <div class="w-12 h-12 rounded-xl bg-slate-100 text-slate-800 flex flex-col items-center justify-center font-bold text-xs shrink-0 border border-slate-200">
              <span class="text-[10px] text-slate-400 uppercase">Fila</span>
              <span class="text-lg leading-none font-black text-brand-600">#{{ item.ordem_execucao }}</span>
            </div>

            <div>
              <div class="flex items-center space-x-2">
                <span class="font-mono font-bold text-brand-700 text-sm">{{ item.projeto_codigo }}</span>
                <span
                  class="px-2 py-0.5 rounded text-[11px] font-semibold"
                  :class="getStatusClass(item.status_agenda)"
                >
                  {{ item.status_agenda_display }}
                </span>
              </div>
              <h4 class="font-bold text-slate-900 text-base mt-0.5">{{ item.projeto_titulo }}</h4>
              <p class="text-xs text-slate-500 mt-1">
                Cliente: <strong class="text-slate-700">{{ item.cliente_nome }}</strong> • Técnico: <strong>{{ item.tecnico_detalhes?.nome_completo }}</strong>
              </p>
            </div>
          </div>

          <!-- Métricas de SLA e Botões de Ação -->
          <div class="flex flex-col sm:items-end justify-between space-y-3">
            <div class="text-xs text-slate-500 space-x-3 sm:text-right">
              <span>Meta SLA: <strong class="text-slate-800">{{ item.horas_estimadas_sla }}h</strong></span>
              <span>Trabalhado: <strong class="text-brand-600">{{ item.horas_efetivas_gastas }}h</strong></span>
            </div>

            <div class="flex items-center space-x-2">
              <!-- Botão Iniciar (Com trava sequencial) -->
              <button
                v-if="item.status_agenda === 'PENDENTE' || item.status_agenda === 'PAUSADO'"
                @click="iniciarProjeto(item)"
                :disabled="!item.bloqueado_por_trava?.pode_iniciar"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white shadow-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center"
                :class="item.bloqueado_por_trava?.pode_iniciar ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-slate-400'"
                :title="item.bloqueado_por_trava?.motivo"
              >
                ▶️ Iniciar Execução
              </button>

              <button
                v-if="item.status_agenda === 'EM_ANDAMENTO'"
                @click="pausarProjeto(item)"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white shadow-sm transition-colors"
              >
                ⏸️ Pausar (Congela SLA)
              </button>

              <button
                v-if="item.status_agenda === 'EM_ANDAMENTO'"
                @click="concluirProjeto(item)"
                class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-colors"
              >
                ✅ Concluir Entrega
              </button>

              <router-link
                :to="`/projetos/${item.projeto}`"
                class="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
              >
                Abrir Card
              </router-link>
            </div>
          </div>
        </div>

        <!-- Mensagem de Bloqueio da Trava se aplicável -->
        <div
          v-if="!item.bloqueado_por_trava?.pode_iniciar && item.status_agenda === 'PENDENTE'"
          class="mt-3 pt-3 border-t border-slate-100 text-xs text-amber-700 flex items-center"
        >
          <span class="mr-1.5">🔒</span> {{ item.bloqueado_por_trava?.motivo }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/services/api';

const loading = ref(true);
const fila = ref([]);

async function fetchFila() {
  loading.value = true;
  try {
    const data = await api.get('/agenda/');
    fila.value = data.results || data;
  } catch (err) {
    console.error('Erro ao carregar fila:', err);
  } finally {
    loading.value = false;
  }
}

async function iniciarProjeto(item) {
  try {
    await api.post(`/agenda/${item.id}/iniciar_execucao/`);
    await fetchFila();
  } catch (err) {
    alert(err.data?.mensagem || err.message);
  }
}

async function pausarProjeto(item) {
  const motivo = prompt('Informe a dúvida técnica ou dados faltantes que justificam a pausa:');
  if (motivo === null) return;

  try {
    await api.post(`/agenda/${item.id}/pausar_execucao/`, { motivo });
    await fetchFila();
  } catch (err) {
    alert(err.data?.mensagem || err.message);
  }
}

async function concluirProjeto(item) {
  if (!confirm('Deseja concluir o desenvolvimento técnico e enviar para a Definição Comercial?')) return;

  try {
    await api.post(`/agenda/${item.id}/concluir_execucao/`);
    await fetchFila();
  } catch (err) {
    alert(err.data?.mensagem || err.message);
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'EM_ANDAMENTO':
      return 'bg-emerald-100 text-emerald-800';
    case 'PAUSADO':
      return 'bg-amber-100 text-amber-800';
    case 'CONCLUIDO':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-slate-100 text-slate-700';
  }
}

onMounted(fetchFila);
</script>
