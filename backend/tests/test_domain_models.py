from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.authentication.models import User
from apps.clientes.models import Cliente
from apps.catalogo.models import FamiliaItem, CatalogoItem
from apps.projetos.models import Projeto, HistoricoStatus, ComentarioProjeto
from apps.agenda.models import AgendaTecnica
from apps.propostas.models import Proposta, ConjuntoProposta, PropostaItem
from apps.artefatos.models import RelatorioDescritivo, Topologia
from apps.servicos.models import OrdemServicoInstalacao, RelatorioServicoCampo

class DomainModelsTestCase(TestCase):
    def setUp(self):
        # 1. Usuários de diferentes papéis
        self.vendedor = User.objects.create_user(
            username='vendedor_carlos',
            email='carlos@eservice.com',
            password='secretpassword123',
            first_name='Carlos',
            cargo=User.CargoChoices.VENDEDOR
        )
        self.gestor = User.objects.create_user(
            username='gestor_marcos',
            email='marcos@eservice.com',
            password='secretpassword123',
            first_name='Marcos',
            cargo=User.CargoChoices.GESTOR
        )
        self.tecnico = User.objects.create_user(
            username='tecnico_andre',
            email='andre@eservice.com',
            password='secretpassword123',
            first_name='André',
            cargo=User.CargoChoices.TECNICO
        )

        # 2. Cliente
        self.cliente = Cliente.objects.create(
            nome_cliente='Fábrica Piraquê',
            responsavel_contato='Sandro',
            local_aproximado='Piraquê - Madureira'
        )

        # 3. Famílias e Catálogo
        self.fam_banner = FamiliaItem.objects.create(nome=FamiliaItem.FamiliaChoices.BANNER)
        self.fam_eletrica = FamiliaItem.objects.create(nome=FamiliaItem.FamiliaChoices.ELETRICA)

        self.sensor_radar = CatalogoItem.objects.create(
            familia=self.fam_banner,
            sku_codigo='QT50R-US-AF2Q',
            codigo_identificador='88383',
            nome='Sensor de Radar para Volume',
            especificacao_tecnica='Sensor de nível contínuo por radar de ondas milimétricas',
            preco_base=Decimal('4500.00'),
            unidade_medida='UN'
        )

        self.borne_wago = CatalogoItem.objects.create(
            familia=self.fam_eletrica,
            sku_codigo='2002-1201',
            codigo_identificador='40508',
            nome='Borne de Passagem 2.5mm',
            especificacao_tecnica='Borne conexão mola push-in cinza',
            preco_base=Decimal('8.50'),
            unidade_medida='UN'
        )

    def test_codigo_identificador_e_codigo_completo(self):
        """Valida a formatação de identificação Modelo(CodigoIdentificador) no padrão industrial."""
        self.assertEqual(self.sensor_radar.codigo_completo, 'QT50R-US-AF2Q(88383)')
        self.assertIn('[QT50R-US-AF2Q(88383)]', str(self.sensor_radar))

        # Item sem código identificador
        item_sem_id = CatalogoItem.objects.create(
            familia=self.fam_eletrica,
            sku_codigo='CABO-PP-4X1.5',
            nome='Cabo PP 4x1.5mm',
            especificacao_tecnica='Cabo flexível',
            preco_base=Decimal('15.00')
        )
        self.assertEqual(item_sem_id.codigo_completo, 'CABO-PP-4X1.5')

    def test_criacao_projeto_e_identificacao(self):
        """Valida criação de projeto com código alfanumérico e cliente."""
        projeto = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-132-01',
            titulo='Medição de Nível Tanque de Xarope',
            descricao_demanda='Cliente necessita de um sistema que mede volume de um tanque',
            cliente=self.cliente,
            criado_por=self.vendedor,
            status=Projeto.StatusChoices.AGUARDANDO_AGENDAMENTO
        )
        self.assertEqual(projeto.codigo_projeto_alfanumerico, 'PR-132-01')
        self.assertEqual(projeto.cliente.responsavel_contato, 'Sandro')
        self.assertEqual(projeto.status, Projeto.StatusChoices.AGUARDANDO_AGENDAMENTO)

    def test_trava_sequencial_agenda_tecnica(self):
        """Valida que o técnico não pode iniciar card com ordem maior que card pendente."""
        proj1 = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-100-01',
            titulo='Projeto Prioritário 1',
            descricao_demanda='Demanda 1',
            cliente=self.cliente,
            criado_por=self.vendedor,
            status=Projeto.StatusChoices.EM_DESENVOLVIMENTO
        )
        proj2 = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-100-02',
            titulo='Projeto Secundário 2',
            descricao_demanda='Demanda 2',
            cliente=self.cliente,
            criado_por=self.vendedor,
            status=Projeto.StatusChoices.EM_DESENVOLVIMENTO
        )

        agenda1 = AgendaTecnica.objects.create(
            projeto=proj1,
            tecnico=self.tecnico,
            ordem_execucao=1,
            data_programada=timezone.now().date(),
            horas_estimadas_sla=Decimal('10.0'),
            status_agenda=AgendaTecnica.StatusAgendaChoices.PENDENTE
        )

        agenda2 = AgendaTecnica.objects.create(
            projeto=proj2,
            tecnico=self.tecnico,
            ordem_execucao=2,
            data_programada=timezone.now().date(),
            horas_estimadas_sla=Decimal('8.0'),
            status_agenda=AgendaTecnica.StatusAgendaChoices.PENDENTE
        )

        # Agenda 1 pode ser iniciada (ordem 1 é a primeira)
        pode, msg = agenda1.pode_iniciar()
        self.assertTrue(pode)

        # Agenda 2 NÃO pode ser iniciada enquanto a 1 estiver pendente
        pode, msg = agenda2.pode_iniciar()
        self.assertFalse(pode)
        self.assertIn("Trava Sequencial", msg)

        # Ao concluir a Agenda 1, a Agenda 2 é liberada
        agenda1.status_agenda = AgendaTecnica.StatusAgendaChoices.CONCLUIDO
        agenda1.save()

        pode_depois, msg_depois = agenda2.pode_iniciar()
        self.assertTrue(pode_depois)

    def test_bom_hierarquica_e_recalculo_proposta(self):
        """Valida montagem de proposta com conjuntos, itens e subitens recursivos."""
        projeto = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-200-01',
            titulo='Projeto Visão',
            descricao_demanda='Inspeção de tampas',
            cliente=self.cliente,
            criado_por=self.vendedor
        )

        proposta = Proposta.objects.create(
            projeto=projeto,
            versao=1,
            status_proposta=Proposta.StatusPropostaChoices.RASCUNHO
        )

        conjunto = ConjuntoProposta.objects.create(
            proposta=proposta,
            nome_conjunto='Painel Elétrico Sistema de Visão 01',
            ordem=1
        )

        # Item principal
        item_radar = PropostaItem.objects.create(
            conjunto=conjunto,
            catalogo_item=self.sensor_radar,
            quantidade=Decimal('2.00'),
            preco_unitario_aplicado=Decimal('4500.00'),
            ordem=1
        )
        self.assertFalse(item_radar.eh_subitem)
        self.assertEqual(item_radar.subtotal, Decimal('9000.00'))

        # Sub-item recursivo dentro do conjunto
        subitem_borne = PropostaItem.objects.create(
            conjunto=conjunto,
            catalogo_item=self.borne_wago,
            parent=item_radar,
            quantidade=Decimal('10.00'),
            preco_unitario_aplicado=Decimal('8.50'),
            ordem=2
        )
        self.assertTrue(subitem_borne.eh_subitem)
        self.assertEqual(subitem_borne.subtotal, Decimal('85.00'))

        total_calculado = proposta.recalcular_total()
        self.assertEqual(total_calculado, Decimal('9085.00'))

    def test_pausa_sla_no_historico(self):
        """Valida registro no histórico e flag de pausa quando status muda para AGUARDANDO_INFORMACAO."""
        projeto = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-300-01',
            titulo='Projeto Medição Pressão',
            descricao_demanda='Medir pressão em caldeira',
            cliente=self.cliente,
            criado_por=self.vendedor,
            status=Projeto.StatusChoices.EM_DESENVOLVIMENTO
        )

        historico = HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=self.tecnico,
            status_anterior=Projeto.StatusChoices.EM_DESENVOLVIMENTO,
            status_novo=Projeto.StatusChoices.AGUARDANDO_INFORMACAO,
            motivo_retorno='Falta informação da rosca de conexão e fluido do processo.',
            pausa_contagem_tempo=True
        )

        self.assertTrue(historico.pausa_contagem_tempo)
        self.assertEqual(historico.status_novo, Projeto.StatusChoices.AGUARDANDO_INFORMACAO)
