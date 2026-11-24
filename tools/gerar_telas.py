#!/usr/bin/env python3
# Gera as telas (screenshots simulados) do Guia Next.js em assets/telas/*.png
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 800
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "telas")
os.makedirs(OUT, exist_ok=True)

FD = "/usr/share/fonts/truetype/dejavu/"
def F(name, size): return ImageFont.truetype(FD + name, size)
SANS = lambda s: F("DejaVuSans.ttf", s)
BOLD = lambda s: F("DejaVuSans-Bold.ttf", s)
MONO = lambda s: F("DejaVuSansMono.ttf", s)
MONOB = lambda s: F("DejaVuSansMono-Bold.ttf", s)

# paleta
BRANCO = (255, 255, 255)
CINZA_CLARO = (243, 244, 246)
BORDA = (229, 231, 235)
TEXTO = (17, 24, 39)
MUTED = (107, 114, 128)
PRETO = (0, 0, 0)
VERDE = (22, 163, 74)
VERDE_BG = (220, 252, 231)
AZUL = (37, 99, 235)
AZUL_BG = (219, 234, 254)
AMARELO = (217, 119, 6)
AMARELO_BG = (254, 243, 199)
VERMELHO = (220, 38, 38)
VERMELHO_BG = (254, 226, 226)
TERMINAL_BG = (12, 12, 14)
CINZA_TERM = (163, 163, 175)


def nova():
    img = Image.new("RGB", (W, H), BRANCO)
    return img, ImageDraw.Draw(img)


def rr(d, x, y, w, h, fill=None, outline=None, radius=8, width=1):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width)


def texto(d, x, y, s, font, fill=TEXTO):
    d.text((x, y), s, font=font, fill=fill)


def seta(d, x1, y1, x2, y2, cor=TEXTO, width=4):
    d.line([x1, y1, x2, y2], fill=cor, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    for a in (ang + 2.6, ang - 2.6):
        d.line([x2, y2, x2 + 18 * math.cos(a), y2 + 18 * math.sin(a)], fill=cor, width=width)


def navegador(d, url, corpo, x=60, y=50, w=W - 120, h=H - 100):
    """Desenha uma janela de navegador; corpo(d, x, y, w, h) desenha o conteúdo."""
    rr(d, x, y, w, h, fill=BRANCO, outline=BORDA, radius=12, width=2)
    # barra superior
    d.rounded_rectangle([x, y, x + w, y + 56], radius=12, fill=CINZA_CLARO)
    d.rectangle([x, y + 40, x + w, y + 56], fill=CINZA_CLARO)
    for i, c in enumerate([(239, 68, 68), (245, 158, 11), (34, 197, 94)]):
        d.ellipse([x + 22 + i * 26, y + 20, x + 22 + i * 26 + 16, y + 36], fill=c)
    rr(d, x + 110, y + 12, w - 240, 32, fill=BRANCO, outline=BORDA, radius=16)
    texto(d, x + 130, y + 18, url, MONO(17), MUTED)
    corpo(d, x + 1, y + 57, w - 2, h - 58)


def terminal(d, linhas, x=60, y=50, w=W - 120, h=H - 100, titulo="ana@notebook: ~"):
    """linhas: lista de (cor, texto, fonte) """
    rr(d, x, y, w, h, fill=TERMINAL_BG, outline=(40, 40, 46), radius=12, width=2)
    d.rounded_rectangle([x, y, x + w, y + 46], radius=12, fill=(24, 24, 28))
    d.rectangle([x, y + 30, x + w, y + 46], fill=(24, 24, 28))
    for i, c in enumerate([(239, 68, 68), (245, 158, 11), (34, 197, 94)]):
        d.ellipse([x + 20 + i * 24, y + 16, x + 20 + i * 24 + 13, y + 29], fill=c)
    texto(d, x + w // 2 - len(titulo) * 5, y + 13, titulo, SANS(15), CINZA_TERM)
    cy = y + 66
    for cor, s, fonte in linhas:
        texto(d, x + 28, cy, s, fonte, cor)
        cy += fonte.size + 14


def salvar(img, nome):
    img.save(os.path.join(OUT, nome), "PNG")
    print("gerado", nome)


# ---------------------------------------------------------------- 1. o-que-e-nextjs
def t_o_que_e():
    img, d = nova()
    navegador(d, "https://nextjs.org", lambda d, x, y, w, h: None)
    # barra preta do site
    d.rectangle([x := 61, y := 108, 61 + 1158, 108 + 64], fill=PRETO)
    d.ellipse([85, 120, 125, 160], fill=BRANCO)
    texto(d, 97, 128, "N", BOLD(26), PRETO)
    texto(d, 145, 127, "Next.js", BOLD(26), BRANCO)
    for i, t in enumerate(["Docs", "Blog", "Showcase", "Enterprise"]):
        texto(d, 900 + i * 80, 130, t, SANS(18), (200, 200, 200))
    # hero
    texto(d, 110, 230, "The React Framework", BOLD(58), TEXTO)
    texto(d, 110, 300, "for the Web", BOLD(58), TEXTO)
    texto(d, 110, 395, "Usado por equipes do mundo inteiro para construir", SANS(24), MUTED)
    texto(d, 110, 428, "aplicações web full-stack rápidas e escaláveis.", SANS(24), MUTED)
    rr(d, 110, 490, 210, 56, fill=PRETO, radius=10)
    texto(d, 135, 503, "Começar", BOLD(22), BRANCO)
    rr(d, 340, 490, 240, 56, fill=BRANCO, outline=BORDA, radius=10, width=2)
    texto(d, 365, 503, "Ver no GitHub", SANS(22), TEXTO)
    # cards
    for i, (titulo, desc) in enumerate([
        ("Rotas por arquivo", "app/page.jsx vira a rota /"),
        ("Renderiza no servidor", "HTML pronto chega antes do JS"),
        ("Otimizado por padrão", "imagens, fontes e prefetch"),
    ]):
        cx = 110 + i * 370
        rr(d, cx, 600, 340, 130, fill=CINZA_CLARO, outline=BORDA, radius=12)
        texto(d, cx + 20, 620, titulo, BOLD(21), TEXTO)
        texto(d, cx + 20, 655, desc, SANS(18), MUTED)
    salvar(img, "o-que-e-nextjs.png")


# ---------------------------------------------------------------- 2. app-vs-pages
def t_app_vs_pages():
    img, d = nova()
    texto(d, 60, 40, "Qual pasta usar: pages/  vs  app/", BOLD(36), TEXTO)
    # coluna pages
    rr(d, 60, 110, 560, 600, fill=BRANCO, outline=BORDA, radius=14, width=2)
    rr(d, 60, 110, 560, 64, fill=CINZA_CLARO, radius=14)
    d.rectangle([60, 140, 620, 174], fill=CINZA_CLARO)
    texto(d, 84, 126, "pages/  (antigo — Pages Router)", BOLD(24), MUTED)
    linhas = ["pages/index.js      → rota /", "pages/sobre.js      → rota /sobre",
              "pages/blog/[id].js  → rota dinâmica", "", "cada arquivo exporta uma página",
              "sem layout compartilhado nativo", "getServerSideProps / getStaticProps"]
    for i, l in enumerate(linhas):
        texto(d, 84, 200 + i * 44, l, MONO(20), TEXTO if l else MUTED)
    texto(d, 84, 200 + 7 * 44 + 10, "ainda funciona, mas está em modo de", SANS(18), MUTED)
    texto(d, 84, 200 + 7 * 44 + 36, "manutenção (não recebe novidades)", SANS(18), MUTED)
    # coluna app
    rr(d, 660, 110, 560, 600, fill=VERDE_BG, outline=VERDE, radius=14, width=3)
    rr(d, 660, 110, 560, 64, fill=(209, 250, 229), radius=14)
    d.rectangle([660, 140, 1220, 174], fill=(209, 250, 229))
    texto(d, 684, 126, "app/  (atual — App Router)  ✓", BOLD(24), VERDE)
    linhas = ["app/page.jsx        → rota /", "app/sobre/page.jsx  → rota /sobre",
              "app/blog/[id]/page.jsx", "", "layout.jsx envolve as páginas",
              "Server Components por padrão", "React 19 + streaming + Suspense"]
    for i, l in enumerate(linhas):
        texto(d, 684, 200 + i * 44, l, MONO(20), TEXTO)
    texto(d, 684, 200 + 7 * 44 + 10, "é o padrão do create-next-app desde", SANS(18), VERDE)
    texto(d, 684, 200 + 7 * 44 + 36, "o Next.js 13 — é para cá que vamos", SANS(18), VERDE)
    salvar(img, "app-vs-pages.png")


# ---------------------------------------------------------------- 3. instalando
def t_instalando():
    img, d = nova()
    terminal(d, [
        (VERDE, "ana@notebook:~$ ", MONOB(22)), (BRANCO, "node -v", MONO(22)),
        (CINZA_TERM, "v20.18.1", MONO(22)),
        (BRANCO, "", MONO(22)),
        (VERDE, "ana@notebook:~$ ", MONOB(22)), (BRANCO, "npm -v", MONO(22)),
        (CINZA_TERM, "10.9.2", MONO(22)),
        (BRANCO, "", MONO(22)),
        (VERDE, "ana@notebook:~$ ", MONOB(22)), (BRANCO, "node -e \"console.log('Node OK, mínimo 18.17')\"", MONO(22)),
        (CINZA_TERM, "Node OK, mínimo 18.17", MONO(22)),
    ])
    salvar(img, "instalando.png")


# ---------------------------------------------------------------- 4. criar-projeto
def t_criar_projeto():
    img, d = nova()
    P = VERDE
    terminal(d, [
        (P, "ana@notebook:~$ ", MONOB(21)), (BRANCO, "npx create-next-app@latest meu-app", MONO(21)),
        (BRANCO, "", MONO(21)),
        (CINZA_TERM, "✔ Qual o nome do projeto? … meu-app", MONO(21)),
        (CINZA_TERM, "✔ Usar TypeScript? … Yes", MONO(21)),
        (CINZA_TERM, "✔ Usar ESLint? … Yes", MONO(21)),
        (CINZA_TERM, "✔ Usar Tailwind CSS? … No", MONO(21)),
        (CINZA_TERM, "✔ Usar o diretório src/? … No", MONO(21)),
        (VERDE, "✔ Usar App Router? … Yes", MONOB(21)),
        (CINZA_TERM, "✔ Usar Turbopack para o dev? … Yes", MONO(21)),
        (CINZA_TERM, "✔ Personalizar o alias de import (@/*)? … No", MONO(21)),
        (BRANCO, "", MONO(21)),
        (CINZA_TERM, "Creating a new Next.js app in /home/ana/meu-app.", MONO(21)),
        (VERDE, "Success! Project created. Happy coding! ✨", MONOB(21)),
    ])
    salvar(img, "criar-projeto.png")


# ---------------------------------------------------------------- 5. estrutura-pastas
def t_estrutura():
    img, d = nova()
    texto(d, 60, 36, "meu-app/", BOLD(34), TEXTO)
    x0, y0 = 90, 100
    fonte = MONO(23)
    esp = 40
    itens = [
        ("📁", "app/", "as rotas do site (app/page.jsx = página inicial)", VERDE),
        ("  📄", "app/layout.jsx", "o layout raiz (html + body)", TEXTO),
        ("  📄", "app/page.jsx", "a página /", TEXTO),
        ("  🎨", "app/globals.css", "CSS global", TEXTO),
        ("📁", "public/", "arquivos públicos (imagens, favicon) servidos direto", AZUL),
        ("📁", "node_modules/", "dependências instaladas pelo npm", MUTED),
        ("📄", "package.json", "nome, scripts (dev/build/start) e dependências", TEXTO),
        ("📄", "next.config.mjs", "configurações do Next", TEXTO),
        ("📄", ".gitignore", "o que o git ignora (.next/, node_modules/)", TEXTO),
        ("📁", ".next/", "build gerado pelo servidor de dev (não commitar)", MUTED),
    ]
    y = y0
    for icone, nome, desc, cor in itens:
        texto(d, x0, y, icone, fonte, cor)
        texto(d, x0 + 56, y, nome, MONOB(23), TEXTO)
        texto(d, x0 + 56 + d.textlength(nome, font=MONOB(23)) + 24, y + 2, "# " + desc, SANS(19), MUTED)
        y += esp + 6
    salvar(img, "estrutura-pastas.png")


# ---------------------------------------------------------------- 6. primeira-pagina
def t_primeira_pagina():
    img, d = nova()
    def corpo(d, x, y, w, h):
        texto(d, x + 60, y + 120, "Olá, Next.js! 👋", BOLD(64), TEXTO)
        texto(d, x + 60, y + 220, "Minha primeira página com App Router.", SANS(28), MUTED)
        rr(d, x + 60, y + 300, 190, 54, fill=PRETO, radius=10)
        texto(d, x + 82, y + 314, "Começar", BOLD(22), BRANCO)
    navegador(d, "http://localhost:3000", corpo)
    salvar(img, "primeira-pagina.png")


# ---------------------------------------------------------------- 7. rodando
def t_rodando():
    img, d = nova()
    terminal(d, [
        (VERDE, "ana@notebook:~/meu-app$ ", MONOB(21)), (BRANCO, "npm run dev", MONO(21)),
        (BRANCO, "", MONO(21)),
        (CINZA_TERM, "  ▲ Next.js 15.1.6 (Turbopack)", MONO(21)),
        (VERDE, "  ✓ Ready in 412ms", MONO(21)),
        (BRANCO, "  ➜ Local:   http://localhost:3000", MONOB(21)),
        (BRANCO, "  ➜ Network: http://192.168.0.10:3000", MONO(21)),
        (BRANCO, "", MONO(21)),
        (CINZA_TERM, "  (edite um arquivo e salve — a página atualiza sozinha)", SANS(19)),
    ], x=40, y=40, w=720, h=380, titulo="ana@notebook: ~/meu-app")
    # mini navegador ao lado
    def corpo(d, x, y, w, h):
        texto(d, x + 24, y + 40, "Olá, Next.js!", BOLD(30), TEXTO)
        texto(d, x + 24, y + 88, "hot reload ativo ⚡", SANS(19), VERDE)
    navegador(d, "http://localhost:3000", corpo, x=790, y=40, w=450, h=380)
    # barrinha de dev indicator
    rr(d, 40, 460, 1200, 300, fill=CINZA_CLARO, outline=BORDA, radius=12)
    texto(d, 70, 485, "Salvar app/page.jsx dispara o Fast Refresh:", BOLD(24), TEXTO)
    for i, l in enumerate(["1. o servidor recompila só o que mudou", "2. o navegador recebe o novo HTML/JS sem perder o estado dos componentes", "3. você vê a mudança na hora, sem apertar F5"]):
        texto(d, 70, 530 + i * 40, l, SANS(21), MUTED)
    salvar(img, "rodando.png")


# ---------------------------------------------------------------- 8. layout
def t_layout():
    img, d = nova()
    def corpo(d, x, y, w, h):
        # header comum (vem do layout)
        d.rectangle([x, y, x + w, y + 64], fill=PRETO)
        texto(d, x + 24, y + 18, "MeuSite", BOLD(24), BRANCO)
        texto(d, x + w - 220, y + 20, "Início   Sobre", SANS(20), (210, 210, 210))
        # conteúdo da página
        texto(d, x + 40, y + 110, "Conteúdo da página /", BOLD(40), TEXTO)
        texto(d, x + 40, y + 170, "O header preto acima veio do app/layout.jsx", SANS(22), MUTED)
        texto(d, x + 40, y + 202, "e aparece em TODAS as páginas.", SANS(22), MUTED)
        rr(d, x + 40, y + 260, 560, 2, fill=AZUL)
    navegador(d, "http://localhost:3000", corpo)
    salvar(img, "layout.png")


# ---------------------------------------------------------------- 9. page vs layout
def t_page():
    img, d = nova()
    texto(d, 60, 36, "mesmo layout, páginas diferentes", BOLD(32), TEXTO)
    def corpo1(d, x, y, w, h):
        d.rectangle([x, y, x + w, y + 52], fill=PRETO)
        texto(d, x + 18, y + 14, "MeuSite", BOLD(20), BRANCO)
        texto(d, x + 40, y + 100, "Página inicial /", BOLD(30), TEXTO)
        texto(d, x + 40, y + 145, "(app/page.jsx)", MONO(19), MUTED)
    def corpo2(d, x, y, w, h):
        d.rectangle([x, y, x + w, y + 52], fill=PRETO)
        texto(d, x + 18, y + 14, "MeuSite", BOLD(20), BRANCO)
        texto(d, x + 40, y + 100, "Página /sobre", BOLD(30), TEXTO)
        texto(d, x + 40, y + 145, "(app/sobre/page.jsx)", MONO(19), MUTED)
    navegador(d, "http://localhost:3000/", corpo1, x=40, y=90, w=580, h=560)
    navegador(d, "http://localhost:3000/sobre", corpo2, x=660, y=90, w=580, h=560)
    seta(d, 625, 370, 655, 370, MUTED, 3)
    texto(d, 40, 690, "app/layout.jsx envolve as duas — por isso o header não pisca na navegação.", SANS(22), MUTED)
    salvar(img, "page.png")


# ---------------------------------------------------------------- 10. navegacao-link
def t_navegacao():
    img, d = nova()
    def corpo(d, x, y, w, h):
        d.rectangle([x, y, x + w, y + 64], fill=PRETO)
        texto(d, x + 24, y + 18, "MeuSite", BOLD(24), BRANCO)
        texto(d, x + 200, y + 20, "Início", SANS(20), BRANCO)
        rr(d, x + 290, y + 14, 96, 36, fill=(60, 60, 60), radius=8)
        texto(d, x + 306, y + 21, "Sobre →", SANS(20), BRANCO)
        texto(d, x + 40, y + 120, "Navegação sem recarregar a página", BOLD(34), TEXTO)
        texto(d, x + 40, y + 175, "<Link href=\"/sobre\"> faz prefetch automático", SANS(22), MUTED)
        texto(d, x + 40, y + 207, "da rota /sobre assim que entra no viewport.", SANS(22), MUTED)
        rr(d, x + 40, y + 270, 420, 110, fill=AZUL_BG, outline=AZUL, radius=10, width=2)
        texto(d, x + 60, y + 288, "⚡ prefetch: ao clicar, a página /sobre", SANS(20), AZUL)
        texto(d, x + 60, y + 318, "já está pronta — a troca é instantânea.", SANS(20), AZUL)
    navegador(d, "http://localhost:3000", corpo)
    salvar(img, "navegacao-link.png")


# ---------------------------------------------------------------- 11. estilos-css
def t_estilos():
    img, d = nova()
    texto(d, 60, 36, "Antes e depois do CSS", BOLD(32), TEXTO)
    # antes
    rr(d, 40, 90, 580, 620, fill=BRANCO, outline=BORDA, radius=12, width=2)
    texto(d, 60, 110, "SEM ESTILO (HTML puro)", BOLD(20), MUTED)
    texto(d, 60, 170, "Título sem formatação", SANS(30), PRETO)
    texto(d, 60, 220, "Um parágrafo comum, preto no", SANS(22), PRETO)
    texto(d, 60, 252, "branco, fonte padrão do navegador.", SANS(22), PRETO)
    texto(d, 60, 300, "Link azul sublinhado", SANS(22), (0, 0, 238))
    # depois
    rr(d, 660, 90, 580, 620, fill=CINZA_CLARO, outline=VERDE, radius=12, width=3)
    texto(d, 680, 110, "COM globals.css + módulo", BOLD(20), VERDE)
    rr(d, 680, 165, 480, 480, fill=BRANCO, outline=BORDA, radius=16)
    d.rectangle([680, 165, 1160, 265], fill=PRETO)
    d.rounded_rectangle([680, 165, 1160, 265], radius=16, outline=None)
    d.rectangle([680, 230, 1160, 265], fill=PRETO)
    texto(d, 700, 190, "Título estilizado", BOLD(32), BRANCO)
    texto(d, 700, 300, "Um parágrafo com espaçamento,", SANS(22), TEXTO)
    texto(d, 700, 332, "cor e fonte choisis no CSS.", SANS(22), TEXTO)
    rr(d, 700, 390, 150, 46, fill=AZUL, radius=8)
    texto(d, 722, 401, "Botão", BOLD(20), BRANCO)
    salvar(img, "estilos-css.png")


# ---------------------------------------------------------------- 12. fontes-imagens
def t_fontes_imagens():
    img, d = nova()
    def corpo(d, x, y, w, h):
        texto(d, x + 50, y + 50, "Um título grande na fonte Inter", BOLD(44), TEXTO)
        texto(d, x + 50, y + 115, "carregada e self-hosted pelo next/font — sem layout shift.", SANS(22), MUTED)
        # "imagem" otimizada
        rr(d, x + 50, y + 180, 500, 320, fill=(186, 230, 253), outline=BORDA, radius=12)
        d.polygon([(x + 50, y + 500), (x + 200, y + 300), (x + 320, y + 500)], fill=(100, 116, 139))
        d.polygon([(x + 230, y + 500), (x + 390, y + 260), (x + 550, y + 500)], fill=(71, 85, 105))
        d.ellipse([x + 400, y + 210, x + 460, y + 270], fill=(250, 204, 21))
        texto(d, x + 50, y + 520, "<Image src=\"/foto.png\" width={500} height={320} alt=\"...\" />", MONO(19), MUTED)
        rr(d, x + 620, y + 180, 460, 340, fill=VERDE_BG, outline=VERDE, radius=12, width=2)
        texto(d, x + 640, y + 200, "next/image faz sozinho:", BOLD(22), VERDE)
        for i, l in enumerate(["• redimensiona para o tamanho certo", "• converte para WebP/AVIF", "• lazy loading abaixo da dobra", "• não quebra o layout (placeholder)"]):
            texto(d, x + 640, y + 245 + i * 38, l, SANS(20), TEXTO)
    navegador(d, "http://localhost:3000", corpo)
    salvar(img, "fontes-imagens.png")


# ---------------------------------------------------------------- 13. server-client
def t_server_client():
    img, d = nova()
    texto(d, 60, 40, "Quem faz o quê: Servidor vs Navegador", BOLD(34), TEXTO)
    # caixa servidor
    rr(d, 60, 120, 520, 420, fill=AZUL_BG, outline=AZUL, radius=14, width=3)
    texto(d, 90, 145, "🖥  SERVIDOR (padrão)", BOLD(26), AZUL)
    for i, l in enumerate(["• lê banco de dados e arquivos", "• busca dados em APIs", "• monta o HTML inicial",
                           "• componente async", "• sem useState / onClick", "• código nem vai pro navegador"]):
        texto(d, 90, 195 + i * 46, l, SANS(21), TEXTO)
    # seta
    seta(d, 590, 330, 690, 330, TEXTO, 5)
    texto(d, 560, 280, "HTML +", SANS(19), MUTED)
    texto(d, 560, 305, "RSC payload", SANS(19), MUTED)
    # caixa cliente
    rr(d, 700, 120, 520, 420, fill=AMARELO_BG, outline=AMARELO, radius=14, width=3)
    texto(d, 730, 145, "📱 NAVEGADOR (\"use client\")", BOLD(26), AMARELO)
    for i, l in enumerate(["• interatividade: cliques, inputs", "• useState, useEffect, onClick", "• APIs do navegador (localStorage,", "   window, geolocation)", "• o JS desse componente vai pro bundle"]):
        texto(d, 730, 195 + i * 46, l, SANS(21), TEXTO)
    rr(d, 60, 590, 1160, 130, fill=CINZA_CLARO, outline=BORDA, radius=12)
    texto(d, 90, 615, "Regra de ouro:", BOLD(24), TEXTO)
    texto(d, 90, 655, "Component Server por padrão. Só adicione \"use client\" na primeira linha quando precisar de interatividade.", SANS(22), MUTED)
    salvar(img, "server-client.png")


# ---------------------------------------------------------------- 14. componentes
def t_componentes():
    img, d = nova()
    texto(d, 60, 40, "Componentes: peças de LEGO do seu app", BOLD(34), TEXTO)
    def caixa(x, y, w, h, titulo, sub, cor, bg):
        rr(d, x, y, w, h, fill=bg, outline=cor, radius=12, width=3)
        texto(d, x + 20, y + 16, titulo, BOLD(24), TEXTO)
        texto(d, x + 20, y + 52, sub, MONO(17), MUTED)
    caixa(440, 110, 400, 100, "App (page.jsx)", "export default function Home()", PRETO, CINZA_CLARO)
    caixa(60, 330, 330, 100, "<Header />", "components/Header.jsx", AZUL, AZUL_BG)
    caixa(475, 330, 330, 100, "<Card />", "components/Card.jsx", VERDE, VERDE_BG)
    caixa(890, 330, 330, 100, "<Footer />", "components/Footer.jsx", AMARELO, AMARELO_BG)
    for x in (225, 640, 1055):
        seta(d, 640, 210, x + 165 - (640 - (640 - x)) if False else x + 165, 330, MUTED, 4)
    rr(d, 60, 520, 1160, 200, fill=BRANCO, outline=BORDA, radius=12, width=2)
    texto(d, 90, 545, "Por que separar em componentes?", BOLD(24), TEXTO)
    for i, l in enumerate(["• cada peça faz uma coisa só e faz bem feito", "• você reutiliza: o mesmo <Card /> aparece em várias páginas", "• achou bug? Olha só naquele arquivo, não no arquivão"]):
        texto(d, 90, 590 + i * 40, l, SANS(21), MUTED)
    salvar(img, "componentes.png")


# ---------------------------------------------------------------- 15. props
def t_props():
    img, d = nova()
    texto(d, 60, 40, "Props: passar dados de um componente para outro", BOLD(32), TEXTO)
    # pai
    rr(d, 60, 110, 540, 240, fill=AZUL_BG, outline=AZUL, radius=14, width=3)
    texto(d, 90, 135, "PAI — page.jsx", BOLD(24), AZUL)
    texto(d, 90, 185, "<Saudacao nome=\"Ana\" idade={20} />", MONOB(22), TEXTO)
    texto(d, 90, 225, "<Saudacao nome=\"Bruno\" idade={31} />", MONOB(22), TEXTO)
    # setas com rótulos
    seta(d, 610, 190, 700, 190, TEXTO, 4)
    texto(d, 600, 150, "nome=\"Ana\"", MONO(18), MUTED)
    seta(d, 610, 280, 700, 330, TEXTO, 4)
    texto(d, 600, 300, "nome=\"Bruno\"", MONO(18), MUTED)
    # filho
    rr(d, 710, 110, 510, 420, fill=VERDE_BG, outline=VERDE, radius=14, width=3)
    texto(d, 740, 135, "FILHO — Saudacao.jsx", BOLD(24), VERDE)
    for i, l in enumerate(["function Saudacao({ nome, idade }) {", "  return (", "    <h1>Olá, {nome}!</h1>", "    <p>Você tem {idade} anos.</p>", "  )", "}"]):
        texto(d, 740, 185 + i * 42, l, MONO(21), TEXTO)
    rr(d, 60, 400, 540, 130, fill=BRANCO, outline=BORDA, radius=12, width=2)
    texto(d, 90, 425, "Renderizado:", BOLD(22), TEXTO)
    texto(d, 90, 465, "Olá, Ana!        Olá, Bruno!", BOLD(24), VERDE)
    texto(d, 60, 580, "Props fluem de cima para baixo (pai → filho).", SANS(24), MUTED)
    texto(d, 60, 620, "O filho não altera as props; ele só as lê.", SANS(24), MUTED)
    salvar(img, "props.png")


if __name__ == "__main__":
    t_o_que_e()
    t_app_vs_pages()
    t_instalando()
    t_criar_projeto()
    t_estrutura()
    t_primeira_pagina()
    t_rodando()
    t_layout()
    t_page()
    t_navegacao()
    t_estilos()
    t_fontes_imagens()
    t_server_client()
    t_componentes()
    t_props()
    print("todas as telas geradas em", os.path.abspath(OUT))
