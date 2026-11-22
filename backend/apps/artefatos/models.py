from django.db import models
from apps.core.models import TimeStampedModel, BaseUUIDModel
from apps.projetos.models import Projeto

class RelatorioDescritivo(TimeStampedModel):
    """
    Relatório Descritivo técnico elaborado pelo desenvolvedor.
    Editável via TipTap no frontend e exportável em .docx (html2docx) e .pdf (WeasyPrint).
    Armazenado diretamente no Object Storage (MinIO / S3).
    """
    projeto = models.ForeignKey(
        Projeto,
        verbose_name='Projeto Associado',
        related_name='relatorios_descritivos',
        on_delete=models.CASCADE
    )
    versao = models.PositiveIntegerField('Versão do Relatório', default=1)
    titulo = models.CharField('Título do Relatório', max_length=255)
    conteudo_html = models.TextField(
        'Conteúdo HTML Rico',
        help_text='HTML gerado pelo editor TipTap com textos, listas, tabelas e imagens inline'
    )
    conteudo_json = models.JSONField(
        'Estrutura TipTap JSON',
        blank=True,
        null=True,
        help_text='Árvore de nós JSON do TipTap para reidratação exata no editor'
    )
    arquivo_docx = models.FileField(
        'Arquivo Word (.docx)',
        upload_to='artefatos/relatorios/docx/%Y/%m/',
        blank=True,
        null=True,
        help_text='Arquivo binário gerado salvo diretamente no Object Storage'
    )
    arquivo_pdf = models.FileField(
        'Arquivo PDF (.pdf)',
        upload_to='artefatos/relatorios/pdf/%Y/%m/',
        blank=True,
        null=True,
        help_text='Arquivo binário gerado salvo diretamente no Object Storage'
    )

    class Meta:
        verbose_name = 'Relatório Descritivo'
        verbose_name_plural = 'Relatórios Descritivos'
        ordering = ['projeto', '-versao']
        constraints = [
            models.UniqueConstraint(
                fields=['projeto', 'versao'],
                name='unique_versao_relatorio_por_projeto'
            )
        ]

    def __str__(self):
        return f"{self.projeto.codigo_projeto_alfanumerico} - Relatório v{self.versao}: {self.titulo}"


class Topologia(BaseUUIDModel):
    """
    Diagrama ou Topologia explicativa de rede/hardware do projeto industrial.
    Armazenado diretamente no Object Storage.
    """
    projeto = models.ForeignKey(
        Projeto,
        verbose_name='Projeto',
        related_name='topologias',
        on_delete=models.CASCADE
    )
    nome_arquivo = models.CharField('Nome do Arquivo / Diagrama', max_length=255)
    arquivo = models.FileField(
        'Arquivo da Topologia (Imagem/PDF/DWG)',
        upload_to='artefatos/topologias/%Y/%m/'
    )
    descricao_explicativa = models.TextField(
        'Descrição Explicativa da Topologia',
        blank=True,
        help_text='Explicação da arquitetura de comunicação, sensores e barramentos'
    )
    data_upload = models.DateTimeField('Data de Upload', auto_now_add=True)

    class Meta:
        verbose_name = 'Topologia do Projeto'
        verbose_name_plural = 'Topologias do Projeto'
        ordering = ['-data_upload']

    def __str__(self):
        return f"{self.projeto.codigo_projeto_alfanumerico} - Topologia: {self.nome_arquivo}"
