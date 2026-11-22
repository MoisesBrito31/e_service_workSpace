from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'responsavel_contato', 'local_aproximado', 'telefone_contato', 'ativo', 'created_at')
    search_fields = ('nome_cliente', 'responsavel_contato', 'local_aproximado', 'cnpj')
    list_filter = ('ativo', 'created_at')
