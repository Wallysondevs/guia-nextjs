#!/usr/bin/env python3
"""
atualizar-figuras.py — aponta cada <figure class="tela"><img src="assets/telas/...">
das páginas do guia para a FOTO REAL gerada (assets/telas/<pagina>-<n>.png)
e remove os PNGs placeholder antigos que ficaram sem referência.

Uso:
  python3 atualizar-figuras.py <raiz-do-guia> [--manter-antigos]
"""
import glob
import os
import re
import sys


def main():
    root = os.path.abspath(sys.argv[1])
    manter = "--manter-antigos" in sys.argv
    telas = os.path.join(root, "assets", "telas")

    slugs = {os.path.splitext(os.path.basename(p))[0]
             for p in glob.glob(os.path.join(root, "*.html"))}

    def eh_novo(nome):
        m = re.match(r"^(.+)-(\d+)\.png$", nome)
        return bool(m) and m.group(1) in slugs

    if not os.path.isdir(telas):
        print("  (sem assets/telas)")
        return
    gerados = {p for p in os.listdir(telas) if eh_novo(p)}

    # 1) atualiza o src da figure de cada página que ganhou foto nova
    for pagina in sorted(glob.glob(os.path.join(root, "*.html"))):
        slug = os.path.splitext(os.path.basename(pagina))[0]
        nova = f"{slug}-1.png"
        if nova not in gerados:
            continue
        with open(pagina, encoding="utf-8") as f:
            conteudo = f.read()
        novo, n = re.subn(
            r'(<figure class="tela"><img src=")assets/telas/[^"]+"',
            lambda m: m.group(1) + f"assets/telas/{nova}\"",
            conteudo, count=1)
        if n and novo != conteudo:
            with open(pagina, "w", encoding="utf-8") as f:
                f.write(novo)
            print(f"  figura atualizada: {os.path.basename(pagina)} -> assets/telas/{nova}")

    # 2) coleta todas as referências atuais
    referenced = set()
    for pagina in glob.glob(os.path.join(root, "*.html")):
        with open(pagina, encoding="utf-8") as f:
            for m in re.finditer(r'assets/telas/([A-Za-z0-9_-]+\.png)', f.read()):
                referenced.add(m.group(1))

    # 3) remove placeholders antigos (não referenciados e fora do esquema novo)
    if not manter:
        for png in sorted(os.listdir(telas)):
            if png in referenced or png in gerados:
                continue
            os.remove(os.path.join(telas, png))
            print(f"  placeholder antigo removido: {png}")


if __name__ == "__main__":
    main()
