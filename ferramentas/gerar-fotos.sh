#!/usr/bin/env bash
#
# gerar-fotos.sh — gera FOTOS REAIS das telas do Guia Next.js.
#
# Pipeline:
#   1. Percorre todas as páginas HTML na RAIZ do guia (*.html)
#   2. Extrai o código de cada caixa <div class="tryreact"> (pre.script) —
#      páginas sem tryreact usam os <pre class="file"> (terminal ou .jsx/.css)
#      (extrair-telas.py)
#   3. Cria um app React temporário por código em ferramentas/apps/<pagina>-<n>/index.html
#      (template.html + React UMD + Babel em ferramentas/vendor/ + shims de next/*)
#   4. Gera ferramentas/lista-fotos.txt (foto -> código fonte do app)
#   5. Sobe um servidor local (python3 -m http.server) na raiz do guia
#   6. Tira screenshot de cada app com Chromium headless via foto.js (puppeteer-core),
#      viewport 1280x800, espera o React renderizar (lazy/Suspense), full page
#   7. Salva as fotos em assets/telas/<pagina>-<n>.png
#   8. Atualiza cada <figure class="tela"><img src="assets/telas/..."> das páginas
#      para apontar para a foto real e remove os placeholders antigos
#
# Uso:
#   ./gerar-fotos.sh              # pipeline completo
#   ./gerar-fotos.sh --lista      # gera só apps + lista-fotos.txt (sem screenshots)
#   ./gerar-fotos.sh --limpar     # antes, apaga apps/ e telas/ antigos
#   ./gerar-fotos.sh --pagina ARQ # gera só uma página específica
#
# Variáveis de ambiente:
#   CHROME_PATH   caminho do executável Chrome/Chromium (foto.js também resolve sozinho)
#   PORTA         porta do servidor local (padrão: 8791, tenta 8791-8820)
#   LARGURA/ALTURA/ESPERA  viewport e espera do React (padrões: 1280 800 4500)
#
set -euo pipefail

FER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$FER_DIR/.." && pwd)"
TELAS="$ROOT/assets/telas"
APPS="$FER_DIR/apps"
LISTA="$FER_DIR/lista-fotos.txt"
TEMPLATE="$APPS/template.html"
EXTRATOR="$FER_DIR/extrair-telas.py"
FIGURAS="$FER_DIR/atualizar-figuras.py"
FOTO="$FER_DIR/foto.js"
FOTO_EXEMPLO="$FER_DIR/foto-exemplo.png"   # imagem de exemplo copiada para os apps (src="./foto.png")

LARGURA="${LARGURA:-1280}"
ALTURA="${ALTURA:-800}"
ESPERA="${ESPERA:-4500}"
PORTA="${PORTA:-8791}"

MODO_LISTA=0
MODO_LIMPAR=0
PAGINA_ESPECIFICA=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lista) MODO_LISTA=1; shift ;;
    --limpar) MODO_LIMPAR=1; shift ;;
    --pagina) PAGINA_ESPECIFICA="$2"; shift 2 ;;
    --pagina=*) PAGINA_ESPECIFICA="${1#--pagina=}"; shift ;;
    -h|--help) sed -n '2,32p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$TELAS" "$APPS"

if [[ $MODO_LIMPAR -eq 1 ]]; then
  echo "==> Limpando apps e telas antigos..."
  find "$APPS" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
  rm -f "$TELAS"/*.png 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# 1+2+3+4) Extrair código das telas, gerar apps e a lista de fotos
# ---------------------------------------------------------------------------
echo "==> Extraindo telas das páginas do guia..."
python3 - "$ROOT" "$APPS" "$LISTA" "$TEMPLATE" "$EXTRATOR" "$FOTO_EXEMPLO" "$PAGINA_ESPECIFICA" <<'PYEOF'
import glob, json, os, re, shutil, subprocess, sys

ROOT, APPS, LISTA, TEMPLATE, EXTRATOR, FOTO_EXEMPLO, PAGINA_ESPECIFICA = sys.argv[1:8]

with open(TEMPLATE, encoding="utf-8") as f:
    template = f.read()

if PAGINA_ESPECIFICA:
    paginas = [PAGINA_ESPECIFICA if os.path.isabs(PAGINA_ESPECIFICA)
               else os.path.join(ROOT, PAGINA_ESPECIFICA)]
else:
    paginas = sorted(glob.glob(os.path.join(ROOT, "*.html")))

entradas = []  # (nome, titulo, codigo)
for pagina in paginas:
    if not os.path.isfile(pagina):
        print(f"  [aviso] página não encontrada: {pagina}", file=sys.stderr)
        continue
    r = subprocess.run([sys.executable, EXTRATOR, pagina], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [erro] falha ao extrair {pagina}: {r.stderr}", file=sys.stderr)
        continue
    try:
        telas = json.loads(r.stdout)
    except json.JSONDecodeError:
        telas = []
    slug = os.path.splitext(os.path.basename(pagina))[0]
    print(f"  {os.path.basename(pagina)}: {len(telas)} tela(s)")
    for tela in telas:
        nome = tela["nome"]
        titulo = tela.get("titulo") or nome
        codigo = (tela.get("codigo") or "").strip("\n")
        css = tela.get("css") or ""
        if not codigo:
            continue
        # protege o HTML do app: </script> dentro do código quebraria o bloco babel
        codigo_seguro = codigo.replace("</script", "<\\/script")
        app_html = (template
                    .replace("{{TITULO}}", titulo)
                    .replace("{{CODIGO}}", codigo_seguro)
                    .replace("{{CSS}}", css))
        app_dir = os.path.join(APPS, nome)
        os.makedirs(app_dir, exist_ok=True)
        with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(app_html)
        # imagem de exemplo para apps que usam src="./foto.png" (next/image)
        if os.path.isfile(FOTO_EXEMPLO) and '"./foto' in codigo:
            shutil.copy(FOTO_EXEMPLO, os.path.join(app_dir, "foto.png"))
        entradas.append((nome, titulo))

with open(LISTA, "w", encoding="utf-8") as f:
    f.write("# lista-fotos.txt — fotos REAIS a gerar, geradas por ferramentas/gerar-fotos.sh\n")
    f.write("# Formato: <arquivo da foto em assets/telas/>  ->  <código fonte do app React>\n")
    f.write("# Cada app é um HTML com React UMD + Babel (ferramentas/vendor/) + shims de next/*\n")
    f.write("# + o código extraído da página (pre.script da caixa tryreact, ou pre.file).\n")
    f.write("# Para gerar as fotos: ferramentas/gerar-fotos.sh\n\n")
    for nome, titulo in entradas:
        f.write(f"assets/telas/{nome}.png  ->  ferramentas/apps/{nome}/index.html   # {titulo}\n")

print(f"  -> {len(entradas)} app(s) gerado(s) em ferramentas/apps/")
print(f"  -> lista salva em ferramentas/lista-fotos.txt")
PYEOF
# nomes dos apps para o bash tirar as fotos (mesma ordem da lista)
python3 - "$ROOT" "$EXTRATOR" "$PAGINA_ESPECIFICA" > "$FER_DIR/.apps-tmp.txt" <<'PY'
import glob, json, os, subprocess, sys
ROOT, EXTRATOR, PAG = sys.argv[1:4]
paginas = [PAG if os.path.isabs(PAG) else os.path.join(ROOT, PAG)] if PAG else sorted(glob.glob(os.path.join(ROOT, "*.html")))
for pagina in paginas:
    if not os.path.isfile(pagina):
        continue
    r = subprocess.run([sys.executable, EXTRATOR, pagina], capture_output=True, text=True)
    try:
        telas = json.loads(r.stdout)
    except Exception:
        continue
    for t in telas:
        if (t.get("codigo") or "").strip():
            print(t["nome"])
PY
APPS_NOMES=()
while read -r nome; do APPS_NOMES+=("$nome"); done < "$FER_DIR/.apps-tmp.txt"
rm -f "$FER_DIR/.apps-tmp.txt"

if [[ $MODO_LISTA -eq 1 ]]; then
  echo "==> Modo --lista: apps e lista-fotos.txt gerados; fotos não tiradas."
  exit 0
fi

# ---------------------------------------------------------------------------
# 5) Servidor local na raiz do guia
# ---------------------------------------------------------------------------
porta_livre() {
  python3 - "$1" <<'PY'
import socket, sys
p = int(sys.argv[1])
while p < int(sys.argv[1]) + 30:
    try:
        s = socket.create_server(("127.0.0.1", p))
        s.close()
        print(p)
        sys.exit(0)
    except OSError:
        p += 1
sys.exit(1)
PY
}

PORTA="$(porta_livre "$PORTA")"
echo "==> Subindo servidor local na porta $PORTA (raiz: $ROOT)..."
python3 -m http.server "$PORTA" --bind 127.0.0.1 --directory "$ROOT" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

for i in $(seq 1 50); do
  if curl -s -o /dev/null "http://127.0.0.1:$PORTA/ferramentas/vendor/react.production.min.js"; then
    break
  fi
  sleep 0.2
done

# ---------------------------------------------------------------------------
# 6+7) Screenshot de cada app com Chromium headless (foto.js / puppeteer-core)
# ---------------------------------------------------------------------------
NODE_BIN="$(command -v node || true)"
if [[ -z "$NODE_BIN" && -x "$HOME/.local/node/bin/node" ]]; then
  NODE_BIN="$HOME/.local/node/bin/node"
fi
export PATH="$(dirname "$NODE_BIN"):$PATH"
export NODE_PATH="$FER_DIR/node_modules"

echo "==> Tirando ${#APPS_NOMES[@]} foto(s) com Chromium headless (${LARGURA}x${ALTURA}, espera ${ESPERA}ms)..."
FALHAS=0
for nome in "${APPS_NOMES[@]}"; do
  url="http://127.0.0.1:$PORTA/ferramentas/apps/$nome/"
  saida="$TELAS/$nome.png"
  if "$NODE_BIN" "$FOTO" "$url" "$saida" "$LARGURA" "$ALTURA" "$ESPERA" 1; then
    :
  else
    echo "  [FALHOU] $nome" >&2
    FALHAS=$((FALHAS+1))
  fi
done

# ---------------------------------------------------------------------------
# 8) Atualiza as <figure class="tela"> das páginas e remove placeholders antigos
# ---------------------------------------------------------------------------
echo "==> Atualizando figures das páginas para as fotos reais..."
python3 "$FIGURAS" "$ROOT"

echo "==> Fim: ${#APPS_NOMES[@]} foto(s), $FALHAS falha(s). Fotos em assets/telas/"
[[ $FALHAS -eq 0 ]]
