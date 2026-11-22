import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true, title: 'Login' }
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: 'Dashboard Geral' }
      },
      {
        path: 'agenda',
        name: 'agenda',
        component: () => import('@/views/AgendaView.vue'),
        meta: { title: 'Agenda & Fila Técnica' }
      },
      {
        path: 'projetos',
        name: 'projetos',
        component: () => import('@/views/ProjetosView.vue'),
        meta: { title: 'Gestão de Projetos' }
      },
      {
        path: 'projetos/:id',
        name: 'projeto-detalhe',
        component: () => import('@/views/ProjetoDetailView.vue'),
        meta: { title: 'Detalhes do Projeto' }
      },
      {
        path: 'catalogo',
        name: 'catalogo',
        component: () => import('@/views/CatalogoView.vue'),
        meta: { title: 'Catálogo Central Único' }
      },
      {
        path: 'clientes',
        name: 'clientes',
        component: () => import('@/views/ClientesView.vue'),
        meta: { title: 'Clientes Industriais' }
      },
      {
        path: 'ordens-servico',
        name: 'ordens-servico',
        component: () => import('@/views/OrdensServicoView.vue'),
        meta: { title: 'Ordens de Serviço & Campo' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Define o título da página
  document.title = to.meta.title ? `${to.meta.title} | E-Service` : 'E-Service - Projetos Industriais';

  // Se tem token mas ainda não carregou o perfil do usuário
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserProfile();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router;
