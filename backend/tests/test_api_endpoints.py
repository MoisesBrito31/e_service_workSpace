from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User
from apps.clientes.models import Cliente
from apps.catalogo.models import FamiliaItem, CatalogoItem
from apps.projetos.models import Projeto, HistoricoStatus
from apps.agenda.models import AgendaTecnica
from apps.propostas.models import Proposta, ConjuntoProposta, PropostaItem
from apps.artefatos.models import RelatorioDescritivo

class ApiEndpointsTestCase(APITestCase):
    def setUp(self):
        # Usuários
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

        # Cliente
        self.cliente = Cliente.objects.create(
            nome_cliente='Fábrica Piraquê',
            responsavel_contato='Sandro',
            local_aproximado='Piraquê - Madureira'
        )

        # Catálogo
        self.familia = FamiliaItem.objects.create(nome=FamiliaItem.FamiliaChoices.BANNER)
        self.item_catalogo = CatalogoItem.objects.create(
            familia=self.familia,
            sku_codigo='QT50R-US-AF2Q',
            codigo_identificador='88383',
            nome='Sensor de Radar',
            especificacao_tecnica='Radar de volume para tanques',
            preco_base=Decimal('5000.00')
        )

    def test_jwt_auth_e_perfil_usuario(self):
        """Valida emissão de token JWT e rota /api/v1/users/me/."""
        url_token = reverse('token_obtain_pair')
        resp = self.client.post(url_token, {
            'username': 'tecnico_andre',
            'password': 'secretpassword123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

        # Autentica via Bearer
        token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url_me = reverse('user-me')
        resp_me = self.client.get(url_me)
        self.assertEqual(resp_me.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_me.data['username'], 'tecnico_andre')
        self.assertEqual(resp_me.data['cargo'], User.CargoChoices.TECNICO)

    def test_criacao_projeto_e_pausa_sla(self):
        """Valida cadastro de projeto e congelamento de SLA na transição de status."""
        self.client.force_authenticate(user=self.vendedor)

        url_projetos = reverse('projeto-list')
        data_projeto = {
            'codigo_projeto_alfanumerico': 'PR-132-01',
            'titulo': 'Medição de Nível de Tanque de Xarope',
            'descricao_demanda': 'Cliente necessita de um sistema que mede volume de um tanque',
            'cliente': str(self.cliente.id)
        }
        resp = self.client.post(url_projetos, data_projeto, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        projeto_id = resp.data['id']

        # Transiciona para AGUARDANDO_INFORMACAO
        url_status = reverse('projeto-mudar-status', kwargs={'pk': projeto_id})
        resp_status = self.client.post(url_status, {
            'status_novo': Projeto.StatusChoices.AGUARDANDO_INFORMACAO,
            'motivo_retorno': 'Faltam dados dimensionais do tanque'
        }, format='json')
        self.assertEqual(resp_status.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_status.data['pausa_contagem_tempo'])

        # Verifica histórico no banco
        historico = HistoricoStatus.objects.filter(projeto_id=projeto_id, status_novo=Projeto.StatusChoices.AGUARDANDO_INFORMACAO).first()
        self.assertIsNotNone(historico)
        self.assertTrue(historico.pausa_contagem_tempo)

    def test_trava_sequencial_na_api_agenda(self):
        """Valida que o endpoint iniciar_execucao recusa Play com HTTP 400 se houver anterior pendente."""
        proj1 = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-101',
            titulo='Projeto 1',
            descricao_demanda='Demanda 1',
            cliente=self.cliente,
            criado_por=self.vendedor
        )
        proj2 = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-102',
            titulo='Projeto 2',
            descricao_demanda='Demanda 2',
            cliente=self.cliente,
            criado_por=self.vendedor
        )

        agenda1 = AgendaTecnica.objects.create(
            projeto=proj1,
            tecnico=self.tecnico,
            ordem_execucao=1,
            data_programada='2026-11-15',
            status_agenda=AgendaTecnica.StatusAgendaChoices.PENDENTE
        )
        agenda2 = AgendaTecnica.objects.create(
            projeto=proj2,
            tecnico=self.tecnico,
            ordem_execucao=2,
            data_programada='2026-11-15',
            status_agenda=AgendaTecnica.StatusAgendaChoices.PENDENTE
        )

        self.client.force_authenticate(user=self.tecnico)

        # Técnico tenta iniciar Projeto 2 (Fila #2) enquanto Fila #1 está pendente
        url_iniciar_2 = reverse('agenda-iniciar-execucao', kwargs={'pk': str(agenda2.id)})
        resp_block = self.client.post(url_iniciar_2)
        self.assertEqual(resp_block.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_block.data['erro'], 'BLOQUEIO_TRAVA_SEQUENCIAL')

        # Inicia Projeto 1 (Fila #1) -> deve aceitar
        url_iniciar_1 = reverse('agenda-iniciar-execucao', kwargs={'pk': str(agenda1.id)})
        resp_ok = self.client.post(url_iniciar_1)
        self.assertEqual(resp_ok.status_code, status.HTTP_200_OK)

        # Conclui Projeto 1
        url_concluir_1 = reverse('agenda-concluir-execucao', kwargs={'pk': str(agenda1.id)})
        resp_concluir = self.client.post(url_concluir_1)
        self.assertEqual(resp_concluir.status_code, status.HTTP_200_OK)

        # Agora tentar Projeto 2 deve passar com sucesso
        resp_2_liberado = self.client.post(url_iniciar_2)
        self.assertEqual(resp_2_liberado.status_code, status.HTTP_200_OK)

    def test_proposta_bom_arvore_e_nova_versao(self):
        """Valida montagem de proposta em árvore, recálculo e clonagem para nova versão."""
        self.client.force_authenticate(user=self.tecnico)

        projeto = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-500',
            titulo='Projeto BOM',
            descricao_demanda='Teste de BOM',
            cliente=self.cliente,
            criado_por=self.vendedor
        )

        proposta = Proposta.objects.create(projeto=projeto, versao=1)
        conjunto = ConjuntoProposta.objects.create(proposta=proposta, nome_conjunto='Painel Visão', ordem=1)

        # Cria item pai
        item_pai = PropostaItem.objects.create(
            conjunto=conjunto,
            catalogo_item=self.item_catalogo,
            quantidade=Decimal('2.00'),
            preco_unitario_aplicado=Decimal('5000.00'),
            ordem=1
        )

        # Cria subitem filho
        sub_item = PropostaItem.objects.create(
            conjunto=conjunto,
            catalogo_item=self.item_catalogo,
            parent=item_pai,
            quantidade=Decimal('1.00'),
            preco_unitario_aplicado=Decimal('5000.00'),
            ordem=2
        )

        # Endpoint de recálculo
        url_recalcular = reverse('proposta-recalcular', kwargs={'pk': str(proposta.id)})
        resp_rec = self.client.post(url_recalcular)
        self.assertEqual(resp_rec.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_rec.data['valor_total'], '15000.00')

        # Endpoint de nova versão (revisão comercial)
        url_nova_versao = reverse('proposta-nova-versao', kwargs={'pk': str(proposta.id)})
        resp_v2 = self.client.post(url_nova_versao)
        self.assertEqual(resp_v2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp_v2.data['versao'], 2)
        self.assertEqual(Decimal(resp_v2.data['valor_total']), Decimal('15000.00'))

    def test_exportacao_docx_relatorio_descritivo(self):
        """Valida geração de documento .docx a partir de HTML TipTap com html2docx."""
        self.client.force_authenticate(user=self.tecnico)

        projeto = Projeto.objects.create(
            codigo_projeto_alfanumerico='PR-DOCX-01',
            titulo='Projeto Documento',
            descricao_demanda='Teste docx',
            cliente=self.cliente,
            criado_por=self.vendedor
        )

        relatorio = RelatorioDescritivo.objects.create(
            projeto=projeto,
            versao=1,
            titulo='Especificação de Engenharia',
            conteudo_html='<h1>Projeto E-Service</h1><p>Sistema automatizado de medição com radar.</p>'
        )

        url_docx = reverse('relatorio-descritivo-exportar-docx', kwargs={'pk': str(relatorio.id)})
        resp = self.client.post(url_docx)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('arquivo_docx_url', resp.data)

        # Recarrega do banco
        relatorio.refresh_from_db()
        self.assertTrue(bool(relatorio.arquivo_docx))
        self.assertTrue(relatorio.arquivo_docx.name.endswith('.docx'))
