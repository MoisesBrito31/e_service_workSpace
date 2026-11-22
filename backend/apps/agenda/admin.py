from django.contrib import admin
from .models import AgendaTecnica

@admin.register(AgendaTecnica)
class AgendaTecnicaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ordem_execucao',
        'tecnico',
        'projeto',
        'status_agenda',
        'data_programada',
        'horas_estimadas_sla',
        'horas_efetivas_gastas',
    )
    list_display_links = ('id', 'projeto')
    list_filter = ('status_agenda', 'tecnico', 'data_programada')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'tecnico__username', 'tecnico__first_name')
    list_editable = ('ordem_execucao', 'status_agenda')
