# ferramentas/ — fotos REAIS das telas do Guia Next.js

Pipeline (igual ao do guia-react):

1. `extrair-telas.py <pagina.html>` — extrai o código de cada caixa
   `<div class="tryreact">` (o `<pre class="script">` do "▶ Rodar") das páginas
   `.html` na raiz do guia. Páginas sem tryreact caem nos `<pre class="file">`
   (terminal vira janela de terminal; .jsx/.css viram página com shims).
2. `gerar-fotos.sh` — gera um app React real por código em
   `apps/<pagina>-<n>/index.html` a partir de `apps/template.html`
   (React 18 UMD + Babel em `vendor/`, offline) com **shims de Next.js**
   (`Link` = `<a>`, `useRouter`/`usePathname`/`useSearchParams` = mocks,
   `Image` = `<img>`, `next/font` = fonte fake, `React.lazy` cacheado,
   hooks como globais, `export default` convertido, import removido).
3. Sobe `python3 -m http.server` na raiz do guia e tira screenshot de cada app
   com **Chromium headless** (`foto.js` + `puppeteer-core`), viewport
   1280x800, esperando o React renderizar (inclui React.lazy/Suspense).
4. Salva em `assets/telas/<pagina>-<n>.png`, atualiza cada
   `<figure class="tela"><img src="assets/telas/...">` das páginas
   (`atualizar-figuras.py`) e remove os placeholders antigos.

Uso:

    ./gerar-fotos.sh                 # pipeline completo (43 telas)
    ./gerar-fotos.sh --lista         # só apps + lista-fotos.txt
    ./gerar-fotos.sh --pagina page.html
    ./gerar-fotos.sh --limpar        # apaga apps/ e assets/telas/ antes

Env: `CHROME_PATH`, `PORTA`, `LARGURA`/`ALTURA`/`ESPERA` (padrão 1280 800 4500).
O Chrome é resolvido em `~/.cache/puppeteer/chrome/...` (foto.js resolve sozinho).
