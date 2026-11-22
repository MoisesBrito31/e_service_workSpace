import os
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

@never_cache
def spa_index_view(request):
    """
    Serve o arquivo index.html compilado do Vue 3 para o SPA (HTML5 History Mode).
    Garante que o navegador nunca armazene em cache o HTML de entrada para evitar conflitos
    de hash após novas compilações (npm run deploy).
    """
    dist_index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'

    if not dist_index.exists():
        return HttpResponse(
            """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>E-Service | Build Pendente</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: #0f172a;
            color: #f8fafc;
        }
        .card {
            background: #1e293b;
            padding: 36px;
            border-radius: 16px;
            border: 1px solid #334155;
            max-width: 480px;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .icon {
            font-size: 40px;
            margin-bottom: 12px;
            display: inline-block;
        }
        h2 { margin: 0 0 8px 0; color: #38bdf8; font-size: 20px; }
        p { color: #94a3b8; font-size: 14px; line-height: 1.5; margin: 12px 0; }
        .cmd {
            background: #090d16;
            padding: 14px 18px;
            border-radius: 10px;
            font-family: Consolas, Monaco, monospace;
            color: #34d399;
            font-size: 13px;
            text-align: left;
            border: 1px solid #1e293b;
            margin: 16px 0;
        }
        .tip { font-size: 12px; color: #64748b; }
    </style>
</head>
<body>
    <div class="card">
        <span class="icon">⚡</span>
        <h2>E-Service Engenharia</h2>
        <p>O frontend Vue 3 ainda não foi compilado para ser servido pelo Django.</p>
        <div class="cmd">
            cd frontend<br>
            npm run deploy
        </div>
        <p class="tip">Após a compilação, recarregue esta página.</p>
    </div>
</body>
</html>""",
            content_type='text/html',
            status=503
        )

    # Lê o arquivo diretamente do dist para refletir imediatamente novos builds
    return HttpResponse(dist_index.read_text(encoding='utf-8'), content_type='text/html')
