import html2docx
from django.core.files.base import ContentFile
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RelatorioDescritivo, Topologia
from .serializers import RelatorioDescritivoSerializer, TopologiaSerializer

class RelatorioDescritivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para edição e versionamento de Relatórios Descritivos.
    Integração com editor TipTap e exportação para .docx no Object Storage.
    """
    queryset = RelatorioDescritivo.objects.select_related('projeto').all().order_by('projeto', '-versao')
    serializer_class = RelatorioDescritivoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        projeto_id = self.request.query_params.get('projeto_id')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset

    @action(detail=True, methods=['post'])
    def exportar_docx(self, request, pk=None):
        """
        Gera arquivo Word (.docx) a partir do HTML do editor TipTap via html2docx
        e persiste o binário diretamente no Object Storage (MinIO / S3).
        """
        relatorio = self.get_object()

        if not relatorio.conteudo_html:
            return Response(
                {'erro': 'O relatório não possui conteúdo HTML para exportação.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Gera o buffer binário com html2docx
        doc_stream = html2docx.html2docx(
            relatorio.conteudo_html,
            title=relatorio.titulo or f"Relatório Técnico {relatorio.projeto.codigo_projeto_alfanumerico}"
        )

        filename = f"Relatorio_{relatorio.projeto.codigo_projeto_alfanumerico}_v{relatorio.versao}.docx"
        relatorio.arquivo_docx.save(filename, ContentFile(doc_stream.getvalue()), save=True)

        return Response({
            'status': 'sucesso',
            'mensagem': 'Arquivo Word gerado e armazenado com sucesso no Object Storage.',
            'arquivo_docx_url': relatorio.arquivo_docx.url,
            'versao': relatorio.versao
        })

    @action(detail=True, methods=['post'])
    def nova_versao(self, request, pk=None):
        """
        Gera uma nova versão do relatório (v2, v3...) mantendo a versão anterior arquivada.
        """
        relatorio_atual = self.get_object()
        projeto = relatorio_atual.projeto

        maior_versao = RelatorioDescritivo.objects.filter(projeto=projeto).order_by('-versao').first().versao
        nova_versao_numero = maior_versao + 1

        novo_relatorio = RelatorioDescritivo.objects.create(
            projeto=projeto,
            versao=nova_versao_numero,
            titulo=relatorio_atual.titulo,
            conteudo_html=relatorio_atual.conteudo_html,
            conteudo_json=relatorio_atual.conteudo_json
        )

        return Response(
            RelatorioDescritivoSerializer(novo_relatorio).data,
            status=status.HTTP_201_CREATED
        )


class TopologiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para envio e organização de diagramas e topologias do projeto.
    """
    queryset = Topologia.objects.select_related('projeto').all().order_by('-data_upload')
    serializer_class = TopologiaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        projeto_id = self.request.query_params.get('projeto_id')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset
