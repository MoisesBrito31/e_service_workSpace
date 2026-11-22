from django.core.management.base import BaseCommand
from apps.catalogo.models import FamiliaItem

class Command(BaseCommand):
    help = 'Popula as 8 famílias base de itens no Catálogo Central'

    def handle(self, *args, **options):
        familias = [
            (FamiliaItem.FamiliaChoices.BANNER, 'Sensores, Visão e Segurança Banner Engineering'),
            (FamiliaItem.FamiliaChoices.TURCK, 'Sensores, Conectividade e Barramentos de Campo Turck'),
            (FamiliaItem.FamiliaChoices.REDLION, 'IHMs, Controladores e Roteadores Industriais Red Lion'),
            (FamiliaItem.FamiliaChoices.SMAC_MCA, 'Atuadores Elétricos de Precisão SMAC / MCA'),
            (FamiliaItem.FamiliaChoices.WAGO, 'Bornes, PLCs e Conexão a Mola WAGO'),
            (FamiliaItem.FamiliaChoices.ELETRICA, 'Componentes Elétricos de Painel e Automação'),
            (FamiliaItem.FamiliaChoices.MECANICA, 'Peças de Usinagem, Perfis de Alumínio e Suportes'),
            (FamiliaItem.FamiliaChoices.SERVICO, 'Serviços de Engenharia, Programação e Instalação em Campo'),
        ]

        criados = 0
        for nome, desc in familias:
            obj, created = FamiliaItem.objects.get_or_create(
                nome=nome,
                defaults={'descricao': desc}
            )
            if created:
                criados += 1
                self.stdout.write(self.style.SUCCESS(f"Família criada: {obj.get_nome_display()}"))
            else:
                self.stdout.write(f"Família já existente: {obj.get_nome_display()}")

        self.stdout.write(self.style.SUCCESS(f"\nFinalizado! {criados} novas famílias cadastradas."))
