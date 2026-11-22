from rest_framework import serializers
from .models import RelatorioDescritivo, Topologia

class RelatorioDescritivoSerializer(serializers.ModelSerializer):
    """
    Serializer para o Relatório Descritivo (TipTap HTML/JSON).
    """
    projeto_codigo = serializers.CharField(source='projeto.codigo_projeto_alfanumerico', read_only=True)
    arquivo_docx_url = serializers.SerializerMethodField()
    arquivo_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = RelatorioDescritivo
        fields = [
            'id',
            'projeto',
            'projeto_codigo',
            'versao',
            'titulo',
            'conteudo_html',
            'conteudo_json',
            'arquivo_docx',
            'arquivo_docx_url',
            'arquivo_pdf',
            'arquivo_pdf_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'projeto_codigo', 'arquivo_docx_url', 'arquivo_pdf_url', 'created_at', 'updated_at']

    def get_arquivo_docx_url(self, obj):
        return obj.arquivo_docx.url if obj.arquivo_docx else None

    def get_arquivo_pdf_url(self, obj):
        return obj.arquivo_pdf.url if obj.arquivo_pdf else None


class TopologiaSerializer(serializers.ModelSerializer):
    """
    Serializer para envio e visualização de topologias industriais.
    """
    projeto_codigo = serializers.CharField(source='projeto.codigo_projeto_alfanumerico', read_only=True)
    arquivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Topologia
        fields = [
            'id',
            'projeto',
            'projeto_codigo',
            'nome_arquivo',
            'arquivo',
            'arquivo_url',
            'descricao_explicativa',
            'data_upload',
        ]
        read_only_fields = ['id', 'projeto_codigo', 'arquivo_url', 'data_upload']

    def get_arquivo_url(self, obj):
        return obj.arquivo.url if obj.arquivo else None
