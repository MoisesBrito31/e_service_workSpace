from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# ViewSets dos domínios do sistema
from apps.authentication.views import UserViewSet
from apps.clientes.views import ClienteViewSet
from apps.catalogo.views import FamiliaItemViewSet, CatalogoItemViewSet
from apps.projetos.views import ProjetoViewSet
from apps.agenda.views import AgendaTecnicaViewSet
from apps.propostas.views import PropostaViewSet, ConjuntoPropostaViewSet, PropostaItemViewSet
from apps.artefatos.views import RelatorioDescritivoViewSet, TopologiaViewSet
from apps.servicos.views import OrdemServicoInstalacaoViewSet, RelatorioServicoCampoViewSet

# View que serve o index.html compilado do Vue 3
from config.views import spa_index_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'familias', FamiliaItemViewSet, basename='familia')
router.register(r'catalogo', CatalogoItemViewSet, basename='catalogo')
router.register(r'projetos', ProjetoViewSet, basename='projeto')
router.register(r'agenda', AgendaTecnicaViewSet, basename='agenda')
router.register(r'propostas', PropostaViewSet, basename='proposta')
router.register(r'conjuntos-proposta', ConjuntoPropostaViewSet, basename='conjunto-proposta')
router.register(r'proposta-itens', PropostaItemViewSet, basename='proposta-item')
router.register(r'relatorios-descritivos', RelatorioDescritivoViewSet, basename='relatorio-descritivo')
router.register(r'topologias', TopologiaViewSet, basename='topologia')
router.register(r'ordens-servico', OrdemServicoInstalacaoViewSet, basename='ordem-servico')
router.register(r'relatorios-campo', RelatorioServicoCampoViewSet, basename='relatorio-campo')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação SimpleJWT
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Principal v1
    path('api/v1/', include(router.urls)),

    # ─── SPA Catch-all ───────────────────────────────────────────────────────
    # Deve ser SEMPRE a última rota.
    # Exclui explicitamente /admin/, /api/, /static/, /media/, /assets/
    # para evitar conflitos. Qualquer outra URL (rotas do Vue Router) recebe
    # o index.html compilado → o Vue Router cuida do roteamento no browser.
    re_path(
        r'^(?!admin/|api/|static/|media/|assets/).*$',
        spa_index_view,
        name='spa-index',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

