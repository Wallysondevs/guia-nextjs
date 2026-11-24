/* =====================================================================
   site.js — Guia Next.js
   Monta a sidebar de navegação (Níveis 1–3), o pager (anterior/próximo
   dentro do nível), os quizzes (.mc com data-answer, 1 = primeira opção)
   e os exercícios (.exercise com data-answer texto ou data-regex).
   Se a página tiver caixas .tryreact, carrega o assets/reactsim.js
   (o editor "Experimente" que compila JSX com Babel e renderiza React 19).
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- Catálogo de páginas por nível ---------- */
  var NIVEIS = [
    { nome: "Nível 1 · Fundamentos", paginas: [
      ["o-que-e-nextjs.html", "O que é o Next.js"],
      ["app-vs-pages.html", "App Router vs Pages Router"],
      ["instalando.html", "Instalando Node e npm"],
      ["criar-projeto.html", "Criando o projeto"],
      ["estrutura-pastas.html", "Estrutura de pastas"],
      ["primeira-pagina.html", "Sua primeira página"],
      ["rodando.html", "Rodando o servidor de dev"],
      ["layout.html", "Layout raiz (layout.jsx)"],
      ["page.html", "Páginas (page.jsx)"],
      ["navegacao-link.html", "Navegação com Link"],
      ["estilos-css.html", "Estilos e CSS"],
      ["fontes-imagens.html", "Fontes e imagens"],
      ["server-client.html", "Server vs Client Components"],
      ["componentes.html", "Componentes"],
      ["props.html", "Props"]
    ]},
    { nome: "Nível 2 · Intermediário", paginas: [
      ["rotas-dinamicas.html", "Rotas dinâmicas [id]"],
      ["catch-all.html", "Catch-all [...slug]"],
      ["generateStaticParams.html", "Geração estática (SSG)"],
      ["grupos-rotas.html", "Grupos de rotas (grupo)"],
      ["estados-especiais.html", "loading, error e 404"],
      ["fetch-server-component.html", "Fetch em Server Component"],
      ["cache-revalidate.html", "Cache e revalidação"],
      ["api-routes.html", "API Routes"],
      ["server-actions.html", "Server Actions"],
      ["formularios-actions.html", "Formulários com Actions"],
      ["middleware.html", "Middleware"],
      ["cookies-sessoes.html", "Cookies e sessões"]
    ]},
    { nome: "Nível 3 · Avançado", paginas: [
      ["ssr-ssg-isr.html", "SSR, SSG e ISR"],
      ["streaming-suspense.html", "Streaming e Suspense"],
      ["partial-prerendering.html", "Partial Prerendering (PPR)"],
      ["image-font.html", "Imagens e fontes (next/image, next/font)"],
      ["bundle-analyzer.html", "Analisando o bundle"],
      ["performance.html", "Performance e Core Web Vitals"],
      ["vercel-deploy.html", "Deploy na Vercel"],
      ["variaveis-ambiente.html", "Variáveis de ambiente"],
      ["dominio-custom.html", "Domínio próprio"]
    ]},
    { nome: "Projetos", paginas: [
      ["projeto-blog.html", "Projeto: Blog (SSG + markdown)"],
      ["projeto-loja.html", "Projeto: Loja (carrinho + Server Actions + Stripe)"],
      ["projeto-dashboard.html", "Projeto: Dashboard (auth + gráficos)"],
      ["projeto-saas.html", "Projeto: SaaS (auth + banco + assinatura)"],
      ["projeto-portfolio.html", "Projeto: Portfólio (PPR + imagens)"]
    ]},
    { nome: "Referência", paginas: [
      ["ref-estructura.html", "Estrutura de pastas (app/)"]
    ]}
  ];

  var atual = (location.pathname.split("/").pop() || "index.html").toLowerCase();

  /* acha o nível e o índice da página atual */
  var nivelIdx = -1, idx = -1;
  for (var n = 0; n < NIVEIS.length; n++) {
    for (var i = 0; i < NIVEIS[n].paginas.length; i++) {
      if (NIVEIS[n].paginas[i][0].toLowerCase() === atual) { nivelIdx = n; idx = i; break; }
    }
    if (nivelIdx >= 0) break;
  }
  var PAGINAS = nivelIdx >= 0 ? NIVEIS[nivelIdx].paginas : [];
  if (nivelIdx < 0) { nivelIdx = 0; idx = 0; PAGINAS = NIVEIS[0].paginas; }

  /* ---------- reactsim.js (caixas .tryreact "Experimente") ---------- */
  if (document.querySelector(".tryreact") && !window.ReactSim &&
      !document.querySelector('script[src*="reactsim.js"]')) {
    var rs = document.createElement("script");
    rs.src = "assets/reactsim.js";
    document.head.appendChild(rs);
  }

  /* ---------------- sidebar ---------------- */
  var nav = document.getElementById("sidebar");
  if (nav) {
    var html = '<div class="sidebar-filter"><input type="search" placeholder="Buscar no guia…" aria-label="Buscar no guia"></div>';
    for (var n2 = 0; n2 < NIVEIS.length; n2++) {
      html += "<h2>" + NIVEIS[n2].nome + "</h2><ul>";
      for (var j = 0; j < NIVEIS[n2].paginas.length; j++) {
        var ehAtual = (n2 === nivelIdx && j === idx);
        html += '<li><a href="' + NIVEIS[n2].paginas[j][0] + '"' + (ehAtual ? ' class="active"' : '') + '>' +
          NIVEIS[n2].paginas[j][1] + '</a></li>';
      }
      html += "</ul>";
    }
    nav.innerHTML = html;

    var filtro = nav.querySelector("input");
    if (filtro) {
      filtro.addEventListener("input", function () {
        var q = filtro.value.trim().toLowerCase();
        nav.classList.toggle("buscando", q.length > 0);
        var lis = nav.querySelectorAll("li");
        for (var k = 0; k < lis.length; k++) {
          var txt = lis[k].textContent.toLowerCase();
          lis[k].style.display = (!q || txt.indexOf(q) !== -1) ? "" : "none";
        }
      });
    }
  }

  /* ---------------- pager ---------------- */
  function pagerHtml() {
    var prev = idx > 0 ? PAGINAS[idx - 1] : null;
    var next = idx < PAGINAS.length - 1 ? PAGINAS[idx + 1] : null;
    var h = "";
    if (prev) h += '<a href="' + prev[0] + '">← ' + prev[1] + '</a>';
    else h += '<span></span>';
    h += '<span class="pager-pos">' + (idx + 1) + ' / ' + PAGINAS.length + '</span>';
    if (next) h += '<a class="next" href="' + next[0] + '">' + next[1] + ' →</a>';
    else h += '<span></span>';
    return h;
  }
  var pagers = document.querySelectorAll(".pager");
  for (var p = 0; p < pagers.length; p++) pagers[p].innerHTML = pagerHtml();

  /* ---------------- quiz .mc (data-answer começa em 1) ---------------- */
  var mcs = document.querySelectorAll(".mc");
  for (var m = 0; m < mcs.length; m++) {
    (function (mc, mi) {
      var ans = parseInt(mc.getAttribute("data-answer"), 10);
      var radios = mc.querySelectorAll('input[type="radio"]');
      var fb = mc.querySelector(".mc-feedback");
      for (var r = 0; r < radios.length; r++) {
        (function (radio, i) {
          radio.name = "mc" + mi + "-" + Math.random().toString(36).slice(2, 8);
          radio.addEventListener("change", function () {
            for (var rr = 0; rr < radios.length; rr++) {
              var lab = radios[rr].closest("label");
              if (lab) lab.classList.remove("ok", "bad");
            }
            var label = radio.closest("label");
            if (i + 1 === ans) {
              if (label) label.classList.add("ok");
              if (fb) { fb.textContent = "✔ Correto!"; fb.style.color = "var(--ok)"; }
            } else {
              if (label) label.classList.add("bad");
              if (fb) { fb.textContent = "✘ Ainda não — releia a seção acima e tente de novo."; fb.style.color = "var(--bad)"; }
            }
          });
        })(radios[r], r);
      }
    })(mcs[m], m);
  }

  /* ---------------- .exercise ----------------
     Formas suportadas:
     <div class="exercise" data-answer="texto esperado"> com um <input class="ex-input">
     ou <div class="exercise" data-regex="^\\d+$"> com input — compara com RegExp. */
  var exs = document.querySelectorAll(".exercise");
  for (var e = 0; e < exs.length; e++) {
    (function (ex) {
      var btn = ex.querySelector(".ex-actions button:not(.secondary)");
      var input = ex.querySelector(".ex-code input, input.ex-input");
      var res = ex.querySelector(".ex-result");
      var dicaBtn = ex.querySelector(".ex-actions button.secondary");
      var dica = ex.querySelector(".ex-dica");
      if (dicaBtn && dica) {
        dicaBtn.addEventListener("click", function () {
          dica.style.display = dica.style.display === "block" ? "none" : "block";
        });
      }
      if (!btn || !input || !res) return;
      btn.addEventListener("click", function () {
        var cru = input.value;
        var v = cru.trim().replace(/\s+/g, " ");
        var ans = ex.getAttribute("data-answer");
        var rex = ex.getAttribute("data-regex");
        var ok;
        if (rex) {
          try { ok = new RegExp(rex).test(cru); } catch (err) { ok = false; }
        } else {
          ok = v.toLowerCase() === String(ans == null ? "" : ans).trim().replace(/\s+/g, " ").toLowerCase();
        }
        input.classList.remove("ok", "bad");
        res.classList.remove("ok", "bad");
        if (ok) {
          input.classList.add("ok");
          res.classList.add("ok");
          res.textContent = "✔ Muito bem! Resposta certa.";
        } else {
          input.classList.add("bad");
          res.classList.add("bad");
          res.textContent = "✘ Quase! Revise o código acima e tente de novo.";
        }
      });
      input.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") btn.click();
      });
    })(exs[e]);
  }
})();
