#!/usr/bin/env python3
"""
extrair-telas.py — extrai o código que vai virar FOTO REAL da tela de cada
página do Guia Next.js (raiz do projeto).

Regras por página (.html na raiz):

1. Se a página tem <div class="tryreact">: cada caixa vira um app usando o
   código do <pre class="script"> (código do experimento "▶ Rodar").
   data-goal vira o título.

2. Se a página NÃO tem tryreact: monta um app a partir dos <pre class="file">:
   - data-file="terminal"        -> app de TERMINAL (janela escura com os comandos)
   - arquivos .jsx/.css          -> app de PÁGINA: css entra num <style>,
                                    .jsx viram componentes (shims de next/* no template)

Uso:
  python3 extrair-telas.py <pagina.html>
Saída (JSON no stdout):
  [{"pagina": "...", "nome": "...-1", "titulo": "...", "tipo": "jsx|terminal",
    "codigo": "...", "css": "..."}, ...]
"""
import html
import json
import os
import re
import sys
from html.parser import HTMLParser


# --------------------------------------------------------------------- parser
class ParserPagina(HTMLParser):
    """Extrai divs .tryreact (com pre.script/pre.solucao) e pre.file da página."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tryreacts = []   # [{"goal": str, "script": str, "solucao": str}]
        self.files = []       # [{"file": str, "codigo": str}]
        self._prof = 0
        self._atual = None
        self._pre_alvo = None  # None | "script" | "solucao" | "file"
        self._buf = []
        self._file_atual = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = re.split(r"\s+", (a.get("class") or "").strip())
        if tag == "div" and "tryreact" in classes and self._atual is None:
            self._atual = {"goal": a.get("data-goal", ""), "script": "", "solucao": ""}
            self._prof = 1
            return
        if self._atual is not None:
            if tag == "div":
                self._prof += 1
            elif tag == "pre":
                if "script" in classes:
                    self._pre_alvo = "script"
                elif "solucao" in classes:
                    self._pre_alvo = "solucao"
                else:
                    self._pre_alvo = None
                self._buf = []
            return
        if tag == "pre" and "file" in classes:
            self._pre_alvo = "file"
            self._file_atual = a.get("data-file", "arquivo")
            self._buf = []

    def handle_endtag(self, tag):
        if self._pre_alvo is not None and tag == "pre":
            texto = html.unescape("".join(self._buf)).strip("\n")
            if self._pre_alvo == "file":
                self.files.append({"file": self._file_atual, "codigo": texto})
            elif self._atual is not None:
                self._atual[self._pre_alvo] = texto
            self._pre_alvo = None
            self._buf = []
            return
        if tag == "div" and self._atual is not None:
            self._prof -= 1
            if self._prof <= 0:
                self.tryreacts.append(self._atual)
                self._atual = None

    def handle_data(self, data):
        if self._pre_alvo is not None:
            self._buf.append(data)


# ------------------------------------------------------------- preprocessing
def remover_imports(codigo):
    codigo = re.sub(r"^[ \t]*import\s[\s\S]*?from\s*['\"][^'\"]*['\"]\s*;?[ \t]*$", "", codigo, flags=re.M)
    codigo = re.sub(r"^[ \t]*import\s*['\"][^'\"]*['\"]\s*;?[ \t]*$", "", codigo, flags=re.M)
    return codigo


def exportar_para_variaveis(codigo):
    """Transforma exports em código de script classic (sem módulo)."""
    default = []

    def sub_fn(m):
        default.append(m.group(2))
        return (m.group(1) or "") + "function " + m.group(2)

    def sub_class(m):
        default.append(m.group(1))
        return "class " + m.group(1)

    codigo = re.sub(r"export\s+default\s+(async\s+)?function\s+(\w+)", sub_fn, codigo)
    codigo = re.sub(r"export\s+default\s+class\s+(\w+)", sub_class, codigo)
    codigo = re.sub(r"export\s+default\s+", "var __default = ", codigo)
    codigo = re.sub(r"export\s+(const|let|var)\s+", r"\1 ", codigo)
    codigo = re.sub(r"export\s+(async\s+function|function|class)\s+", r"\1 ", codigo)
    codigo = re.sub(r"^[ \t]*export\s*\{[^}]*\}\s*;?[ \t]*$", "", codigo, flags=re.M)
    if default:
        codigo += f"\nvar __default = {default[0]};\n"
    return codigo


def preparar_codigo(codigo, trocar_html_body=False, assets_locais=False):
    codigo = remover_imports(codigo)
    codigo = exportar_para_variaveis(codigo)
    if trocar_html_body:
        codigo = re.sub(r"<html\b", "<div", codigo)
        codigo = codigo.replace("</html>", "</div>")
        codigo = re.sub(r"<body\b", "<div", codigo)
        codigo = codigo.replace("</body>", "</div>")
    if assets_locais:
        # /foto.png etc. passa a ser relativo ao app (o servidor serve a raiz do guia)
        codigo = re.sub(r'(src|href)="/', r'\1="./', codigo)
    return codigo.strip("\n")


# ------------------------------------------------------------- app de terminal
def app_terminal(linhas, titulo):
    arr = ",\n".join(json.dumps(l, ensure_ascii=False) for l in linhas)
    return f"""
function App() {{
  const linhas = [
{arr}
  ];
  function cor(l) {{
    if (l.indexOf('✔') >= 0 || l.indexOf('Success') >= 0) return '#4ade80';
    if (l.indexOf('✖') >= 0 || l.indexOf('Error') >= 0) return '#f87171';
    if (l.indexOf('▲') >= 0 || l.indexOf('✓') >= 0 || l.indexOf('➜') >= 0) return '#a5b4fc';
    if (/^\\S+@\\S+/.test(l)) return '#e5e5e5';
    return '#a3a3a3';
  }}
  return (
    <div style={{{{ margin: 0, padding: 24, background: '#0c0c0e', minHeight: '100vh', boxSizing: 'border-box', fontFamily: 'monospace' }}}}>
      <div style={{{{ maxWidth: 980, margin: '0 auto', background: '#0c0c0e', border: '1px solid #2a2a30', borderRadius: 12, overflow: 'hidden', boxShadow: '0 10px 40px rgba(0,0,0,.5)' }}}}>
        <div style={{{{ display: 'flex', alignItems: 'center', gap: 8, background: '#18181c', padding: '10px 14px', borderBottom: '1px solid #2a2a30' }}}}>
          <span style={{{{ width: 13, height: 13, borderRadius: '50%', background: '#ef4444' }}}} />
          <span style={{{{ width: 13, height: 13, borderRadius: '50%', background: '#f59e0b' }}}} />
          <span style={{{{ width: 13, height: 13, borderRadius: '50%', background: '#22c55e' }}}} />
          <span style={{{{ margin: '0 auto', color: '#8b8b93', fontSize: 14, fontFamily: 'sans-serif' }}}}>{titulo}</span>
        </div>
        <div style={{{{ padding: '18px 20px', fontSize: 16, lineHeight: 1.65, whiteSpace: 'pre-wrap' }}}}>
          {{linhas.map((l, i) => <div key={{i}} style={{{{ color: cor(l) }}}}>{{l || ' '}}</div>)}}
        </div>
      </div>
    </div>
  );
}}
""".strip("\n")


# ------------------------------------------------- páginas sem tryreact
def montar_app_de_arquivos(files, slug):
    """Monta um app a partir dos pre.file de uma página sem tryreact."""
    terminais = [f["codigo"] for f in files
                 if f["file"] == "terminal" or f["file"].startswith("term")]
    if terminais:
        linhas = []
        for t in terminais:
            linhas.extend(t.split("\n"))
            linhas.append("")
        while linhas and linhas[-1] == "":
            linhas.pop()
        return {"tipo": "terminal",
                "codigo": app_terminal(linhas, f"ana@notebook: ~/meu-app — {slug}"),
                "css": "", "titulo": "terminal"}

    css = "\n".join(f["codigo"] for f in files if f["file"].endswith(".css"))
    jsxs = [f for f in files
            if re.search(r"\.(jsx|tsx|js)$", f["file"])
            and not f["file"].endswith(("config.mjs", "package.json"))]
    if not jsxs:
        linhas = []
        for f in files:
            linhas.append(f"// ===== {f['file']} =====")
            linhas.extend(f["codigo"].split("\n"))
            linhas.append("")
        return {"tipo": "terminal", "codigo": app_terminal(linhas, slug),
                "css": "", "titulo": "arquivos"}

    def score(f):
        nome = f["file"]
        s = 0
        if re.search(r"page\.(jsx|tsx)$", nome):
            s -= 10
        if "fetch(" in f["codigo"]:
            s += 5
        if "layout" in nome:
            s -= 5
        return s

    jsxs_ordenados = sorted(jsxs, key=score)
    principal = jsxs_ordenados[0]
    outros = [f for f in jsxs if f is not principal]

    layout = next((f for f in jsxs if "layout" in f["file"]), None)
    pagina = next((f for f in jsxs if re.search(r"page\.(jsx|tsx)$", f["file"])), None)

    partes = []
    if layout and pagina:
        # renderiza <RootLayout><Home /></RootLayout>
        code_layout = preparar_codigo(layout["codigo"], trocar_html_body=True, assets_locais=True)
        code_page = preparar_codigo(pagina["codigo"], assets_locais=True)
        nome_page = (re.search(r"var __default = (\w+);", code_page) or [None, "Home"])[1]
        nome_layout = (re.search(r"var __default = (\w+);", code_layout) or [None, "RootLayout"])[1]
        partes.append(code_layout)
        partes.append(code_page)
        partes.append(f"function App() {{ return <{nome_layout}><{nome_page} /></{nome_layout}>; }}")
    elif layout:
        # só layout.jsx: renderiza com um conteúdo de página de exemplo
        code = preparar_codigo(layout["codigo"], trocar_html_body=True, assets_locais=True)
        m = re.search(r"var __default = (\w+);", code)
        nome_layout = m.group(1) if m else "RootLayout"
        partes.append(code)
        partes.append(
            "function App() { return <" + nome_layout + ">"
            + '<main style={{ fontFamily: "sans-serif", padding: 24 }}>'
            + "<h1>Página inicial</h1>"
            + "<p>O conteúdo da page entra aqui, dentro do layout.</p>"
            + "</main></" + nome_layout + ">; }")
    else:
        code_principal = preparar_codigo(principal["codigo"], assets_locais=True)
        partes.append(code_principal)
        m = re.search(r"var __default = (\w+);", code_principal)
        nome_principal = m.group(1) if m else None
        extras = []
        for f in outros:
            code_outro = preparar_codigo(f["codigo"], assets_locais=True)
            m2 = re.search(r"var __default = (\w+);", code_outro)
            nome_outro = m2.group(1) if m2 else None
            if nome_outro and nome_outro in code_principal:
                partes.append(code_outro)          # usado pelo principal (ex.: Contador)
            elif nome_outro:
                extras.append((nome_outro, code_outro))
        for _, code_outro in extras:
            partes.append(code_outro)
        if nome_principal:
            if extras:
                pecas = [f"<{nome_principal} />"]
                for n, _ in extras:
                    pecas.append("<hr />")
                    pecas.append(f"<{n} />")
                partes.append('function App() { return <div style={{ fontFamily: "sans-serif", padding: 24 }}>'
                              + "".join(pecas) + "</div>; }")
            else:
                partes.append(f"function App() {{ return <{nome_principal} />; }}")
        else:
            partes.append('function App() { return <main style={{ fontFamily: "sans-serif", padding: 24 }}>{__default}</main>; }')

    if any(f["file"].endswith(".module.css") for f in files):
        partes.insert(0, 'var styles = new Proxy({}, { get: function (t, k) { return String(k); } });')

    return {"tipo": "jsx", "codigo": "\n\n".join(partes), "css": css, "titulo": principal["file"]}


# --------------------------------------------------------------------- main
def main():
    if len(sys.argv) != 2:
        print("Uso: extrair-telas.py <pagina.html>", file=sys.stderr)
        sys.exit(1)
    caminho = sys.argv[1]
    slug = os.path.splitext(os.path.basename(caminho))[0]
    with open(caminho, encoding="utf-8") as f:
        conteudo = f.read()
    p = ParserPagina()
    p.feed(conteudo)
    p.close()
    if p._atual is not None:
        p.tryreacts.append(p._atual)

    apps = []
    for i, caixa in enumerate(p.tryreacts, 1):
        codigo = caixa["script"] or caixa["solucao"]
        if not codigo.strip():
            continue
        apps.append({
            "pagina": slug,
            "nome": f"{slug}-{i}",
            "titulo": caixa["goal"] or f"{slug} #{i}",
            "tipo": "jsx",
            "codigo": preparar_codigo(codigo),
            "css": "",
        })

    if not apps and p.files:
        app = montar_app_de_arquivos(p.files, slug)
        app.update({"pagina": slug, "nome": f"{slug}-1"})
        apps.append(app)

    json.dump(apps, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
