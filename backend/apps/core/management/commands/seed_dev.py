from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from apps.authentication.models import User
from apps.clientes.models import Cliente
from apps.catalogo.models import FamiliaItem, CatalogoItem
from apps.projetos.models import Projeto, HistoricoStatus, ComentarioProjeto
from apps.agenda.models import AgendaTecnica
from apps.propostas.models import Proposta, ConjuntoProposta, PropostaItem
from apps.artefatos.models import RelatorioDescritivo

class Command(BaseCommand):
    help = 'Popula dados de teste completos para desenvolvimento e validação preliminar'

    def handle(self, *args, **options):
        self.stdout.write("--- Inicializando dados de teste preliminares ---")

        # 1. Usuários
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@eservice.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'cargo': User.CargoChoices.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('admin123')
        admin.save()

        vendedor, _ = User.objects.get_or_create(
            username='vendedor',
            defaults={
                'email': 'vendedor@eservice.com',
                'first_name': 'Carlos',
                'last_name': 'Vendas',
                'cargo': User.CargoChoices.VENDEDOR
            }
        )
        vendedor.set_password('senha123')
        vendedor.save()

        gestor, _ = User.objects.get_or_create(
            username='gestor',
            defaults={
                'email': 'gestor@eservice.com',
                'first_name': 'Marcos',
                'last_name': 'Engenharia',
                'cargo': User.CargoChoices.GESTOR,
                'is_staff': True
            }
        )
        gestor.set_password('senha123')
        gestor.save()

        tecnico, _ = User.objects.get_or_create(
            username='tecnico',
            defaults={
                'email': 'tecnico@eservice.com',
                'first_name': 'André',
                'last_name': 'Automação',
                'cargo': User.CargoChoices.TECNICO
            }
        )
        tecnico.set_password('senha123')
        tecnico.save()

        comercial, _ = User.objects.get_or_create(
            username='comercial',
            defaults={
                'email': 'comercial@eservice.com',
                'first_name': 'Juliana',
                'last_name': 'Comercial',
                'cargo': User.CargoChoices.COMERCIAL
            }
        )
        comercial.set_password('senha123')
        comercial.save()

        self.stdout.write(self.style.SUCCESS("✓ Usuários criados: admin, vendedor, gestor, tecnico, comercial (senhas: admin123 / senha123)"))

        # 2. Cliente
        cliente, _ = Cliente.objects.get_or_create(
            nome_cliente='Fábrica Piraquê Alimentos',
            defaults={
                'responsavel_contato': 'Sandro',
                'local_aproximado': 'Piraquê - Madureira (RJ)',
                'email_contato': 'sandro@piraque.com.br',
                'telefone_contato': '(21) 99888-7766'
            }
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Cliente criado: {cliente}"))

        # 3. Famílias e Itens do Catálogo
        fam_banner, _ = FamiliaItem.objects.get_or_create(
            nome=FamiliaItem.FamiliaChoices.BANNER,
            defaults={'descricao': 'Sensores e Visão Banner Engineering'}
        )
        fam_eletrica, _ = FamiliaItem.objects.get_or_create(
            nome=FamiliaItem.FamiliaChoices.ELETRICA,
            defaults={'descricao': 'Painéis e Componentes Elétricos'}
        )
        fam_servico, _ = FamiliaItem.objects.get_or_create(
            nome=FamiliaItem.FamiliaChoices.SERVICO,
            defaults={'descricao': 'Serviços de Engenharia e Instalação'}
        )

        item_radar, _ = CatalogoItem.objects.get_or_create(
            sku_codigo='QT50R-US-AF2Q',
            codigo_identificador='88383',
            defaults={
                'familia': fam_banner,
                'nome': 'Sensor de Radar para Volume',
                'especificacao_tecnica': 'Sensor radar contínuo para medição de nível de líquidos e sólidos com faixa estendida.',
                'preco_base': Decimal('4850.00'),
                'unidade_medida': 'UN'
            }
        )
        item_painel, _ = CatalogoItem.objects.get_or_create(
            sku_codigo='PAINEL-600X400',
            codigo_identificador='10420',
            defaults={
                'familia': fam_eletrica,
                'nome': 'Painel Elétrico Inox 600x400x250mm',
                'especificacao_tecnica': 'Quadro em Aço Inox 304 com placa de montagem e fecho chave.',
                'preco_base': Decimal('2100.00'),
                'unidade_medida': 'UN'
            }
        )
        item_eng, _ = CatalogoItem.objects.get_or_create(
            sku_codigo='SERV-ENG-01',
            codigo_identificador='9001',
            defaults={
                'familia': fam_servico,
                'nome': 'Engenharia de Aplicação e Parametrização',
                'especificacao_tecnica': 'Horas de engenharia sênior para comissionamento e startup de radar.',
                'preco_base': Decimal('250.00'),
                'unidade_medida': 'H'
            }
        )
        self.stdout.write(self.style.SUCCESS("✓ Catálogo central populado com itens de exemplo."))

        # 4. Projeto Industrial de Teste
        projeto, _ = Projeto.objects.get_or_create(
            codigo_projeto_alfanumerico='PR-132-01',
            defaults={
                'titulo': 'Medição de Volume do Tanque de Xarope',
                'descricao_demanda': 'Cliente necessita de um sistema que mede volume de um tanque de xarope com sensor radar sem contato e transmissão 4-20mA.',
                'cliente': cliente,
                'criado_por': vendedor,
                'status': Projeto.StatusChoices.EM_DESENVOLVIMENTO
            }
        )

        # 5. Agenda Técnica com Fila e SLA
        agenda, _ = AgendaTecnica.objects.get_or_create(
            projeto=projeto,
            defaults={
                'tecnico': tecnico,
                'ordem_execucao': 1,
                'data_programada': timezone.now().date(),
                'horas_estimadas_sla': Decimal('16.0'),
                'horas_efetivas_gastas': Decimal('4.5'),
                'status_agenda': AgendaTecnica.StatusAgendaChoices.EM_ANDAMENTO
            }
        )

        # 6. Proposta com BOM Hierárquica em Árvore
        proposta, _ = Proposta.objects.get_or_create(
            projeto=projeto,
            versao=1,
            defaults={
                'status_proposta': Proposta.StatusPropostaChoices.RASCUNHO,
                'observacoes': 'Proposta técnica preliminar para sistema de medição contínua.'
            }
        )

        conjunto, _ = ConjuntoProposta.objects.get_or_create(
            proposta=proposta,
            nome_conjunto='Painel e Instrumentação do Tanque 01',
            defaults={'ordem': 1}
        )

        item_pai, _ = PropostaItem.objects.get_or_create(
            conjunto=conjunto,
            catalogo_item=item_painel,
            defaults={
                'quantidade': Decimal('1.00'),
                'preco_unitario_aplicado': item_painel.preco_base,
                'ordem': 1
            }
        )

        sub_item, _ = PropostaItem.objects.get_or_create(
            conjunto=conjunto,
            catalogo_item=item_radar,
            parent=item_pai,
            defaults={
                'quantidade': Decimal('1.00'),
                'preco_unitario_aplicado': item_radar.preco_base,
                'observacao_tecnica': 'Instalado no flange superior do tanque',
                'ordem': 2
            }
        )

        proposta.recalcular_total()

        # 7. Relatório Descritivo com HTML do TipTap
        RelatorioDescritivo.objects.get_or_create(
            projeto=projeto,
            versao=1,
            defaults={
                'titulo': 'Memorial Descritivo - Medição de Volume por Radar',
                'conteudo_html': """
                <h2>1. Objetivo</h2>
                <p>Fornecimento de sistema completo para medição contínua de nível e cálculo de volume do tanque de xarope da unidade Madureira.</p>
                <h2>2. Topologia e Instrumentação</h2>
                <ul>
                    <li>Sensor de Radar QT50RAFQ sem contato com grau sanitário.</li>
                    <li>Painel Inox de proteção IP66 com barreira intrínseca.</li>
                </ul>
                """
            }
        )

        # 8. Comentário estilo Planner
        comentario, _ = ComentarioProjeto.objects.get_or_create(
            projeto=projeto,
            autor=vendedor,
            defaults={
                'conteudo': 'Olá @tecnico, inseri as fotos do bocal do tanque na pasta do projeto.'
            }
        )
        comentario.mencoes.add(tecnico)

        self.stdout.write(self.style.SUCCESS(f"\n✓ Projeto criado: {projeto.codigo_projeto_alfanumerico} com proposta (Total: R$ {proposta.valor_total}) e fila técnica."))
        self.stdout.write(self.style.SUCCESS("--- Carga de dados concluída com sucesso! ---"))
