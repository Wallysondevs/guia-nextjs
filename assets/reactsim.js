/* =====================================================================
   reactsim.js — o "Experimente" do Guia React.
   Monta as caixas <div class="tryreact" data-goal="…"> com:
   - pre.script (código editável) e pre.solucao (gabarito oculto)
   - Botão ▶ Rodar: compila JSX com Babel standalone e renderiza
     com React 19 UMD dentro de um iframe na própria caixa.
   - Missão: data-goal é uma regex aplicada ao código; se bate, mostra ✅.
   ===================================================================== */
(function () {
  "use strict";

  var VERSAO_REACT = "19";
  var ReactSim = { VERSAO: VERSAO_REACT };

  function escHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  ReactSim.escHtml = escHtml;

  /* Carrega Babel + React UMD uma vez */
  var carregado = false;
  function carregarLibs(cb) {
    if (carregado) return cb();
    var scripts = [
      "https://unpkg.com/react@19/umd/react.production.min.js",
    ];
    var i = 0;
    var usados = []; // URLs que carregaram de verdade (unpkg ou vendor local)
    ReactSim.libUrls = usados;
    function next() {
      if (i >= scripts.length) { carregado = true; return cb(); }
      var s = document.createElement("script");
      s.src = scripts[i++];
      s.onload = function () { usados[i - 1] = s.src; next(); };
      s.onerror = function () {
        // fallback para vendor local
        var local = ["ferramentas/vendor/babel.min.js", "ferramentas/vendor/react.production.min.js", "ferramentas/vendor/react-dom.production.min.js"];
        var ls = document.createElement("script");
        ls.src = local[i - 1];
        ls.onload = function () { usados[i - 1] = ls.src; next(); };
        ls.onerror = function () { usados[i - 1] = ls.src; next(); };
        document.head.appendChild(ls);
      };
      document.head.appendChild(s);
    }
    next();
  }

  /* Extrai o código de um pre.script (desfaz escape HTML) */
  function codigoDe(pre) {
    return pre.textContent;
  }

  /* Compila JSX e retorna código JS executável */
  function compilarJsx(codigo) {
    // Remove imports (React e hooks já estão no escopo global)
    var semImports = codigo.replace(/^\s*import\s+.*?;?\s*$/gm, "");
    var resultado = Babel.transform(semImports, {
      presets: [["react", { runtime: "classic" }]],
      filename: "App.jsx"
    });
    return resultado.code;
  }

  /* Traduz erros comuns para português */
  function traduzirErro(msg) {
    var regras = [
      [/Unexpected token.*?line (\d+)/i, "Erro de sintaxe perto da linha $1. Verifique vírgulas, parênteses e chaves."],
      [/Expected corresponding JSX closing tag/i, "Tag JSX não fechada. Toda tag aberta precisa fechar (ex: <div>…</div>)."],
      [/Adjacent JSX elements/i, "O JSX precisa de um único elemento raiz. Envolva tudo num <div> ou fragmento <>…</>."],
      [/Cannot read propert(?:y|ies) of (null|undefined)/i, "Tentou ler uma propriedade de $1. A variável existe?"],
      [/(\w+) is not defined/i, "'$1' não está definido. Verifique se escreveu o nome certo ou se declaróu a variável."],
      [/is not a function/i, "Isso não é uma função. Verifique se a variável guarda o que você pensa."],
      [/Each child in a list should have a unique "key"/i, "Toda lista renderizada com .map() precisa de uma prop 'key' única em cada item."],
      [/Too many re-renders/i, "Loop infinito: o componente atualiza o próprio estado durante a renderização."],
      [/Minified React error #(\d+)/i, "Erro interno do React #$1. Veja a mensagem completa no console."],
      [/Nothing was returned from render/i, "O componente não retornou nada. Faltou o return?"],
      [/React is not defined/i, "Faltou declarar o React no escopo."],
      [/Element type is invalid/i, "Um componente foi usado antes de ser definido ou não existe."]
    ];
    for (var i = 0; i < regras.length; i++) {
      var m = msg.match(regras[i][0]);
      if (m) return regras[i][1].replace(/\$(\d+)/g, function (_, n) { return m[n] || ""; });
    }
    return msg;
  }

  /* Monta a caixa tryreact */
  document.querySelectorAll(".tryreact").forEach(function (caixa) {
    var script = caixa.querySelector("pre.script");
    var solucao = caixa.querySelector("pre.solucao");
    var goal = caixa.getAttribute("data-goal");
    var task = caixa.querySelector(".try-task");

    if (!script) return;

    // Torna o código editável
    script.setAttribute("contenteditable", "true");
    script.setAttribute("spellcheck", "false");

    // Barra de botões
    var barra = document.createElement("div");
    barra.className = "try-bar";
    barra.innerHTML =
      '<button type="button" class="try-run">▶ Rodar</button>' +
      '<button type="button" class="try-reset">↺ Restaurar</button>' +
      (goal ? '<button type="button" class="try-check">✔ Verificar missão</button>' : '') +
      (solucao ? '<button type="button" class="try-show">Ver solução</button>' : '');
    caixa.insertBefore(barra, script);

    // Área de resultado (iframe)
    var resultado = document.createElement("div");
    resultado.className = "try-out";
    var iframe = document.createElement("iframe");
    iframe.setAttribute("sandbox", "allow-scripts");
    iframe.style.cssText = "width:100%;border:0;min-height:200px;background:#fff;border-radius:0 0 6px 6px;";
    resultado.appendChild(iframe);
    caixa.appendChild(resultado);

    // Área de erro
    var erro = document.createElement("div");
    erro.className = "try-err";
    erro.style.cssText = "display:none;padding:10px 14px;background:#3a1c18;color:#ff9a8a;font:13px monospace;white-space:pre-wrap;border-radius:0 0 6px 6px;";
    caixa.appendChild(erro);

    var codigoOriginal = codigoDe(script);

    function mostrarErro(msg) {
      erro.style.display = "block";
      erro.textContent = "⚠ " + traduzirErro(msg);
      iframe.style.display = "none";
    }
    function esconderErro() {
      erro.style.display = "none";
      iframe.style.display = "block";
    }

    function rodar() {
      esconderErro();
      carregarLibs(function () {
        var codigo = codigoDe(script);
        var js;
        try {
          js = compilarJsx(codigo);
        } catch (e) {
          mostrarErro(e.message);
          return;
        }
        // Monta o HTML do iframe com React no escopo
        // usa no iframe as MESMAS URLs que carregaram na página (unpkg ou vendor local — evita bloqueio ORB/offline)
        var localLib = ["ferramentas/vendor/babel.min.js", "ferramentas/vendor/react.production.min.js", "ferramentas/vendor/react-dom.production.min.js"];
        var lib = [0, 1, 2].map(function (k) {
          return (ReactSim.libUrls && ReactSim.libUrls[k]) ? ReactSim.libUrls[k] : new URL(localLib[k], location.href).href;
        });
        var html = '<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;font-family:system-ui,sans-serif;}</style></head><body><div id="root"></div>' +
          '<script src="' + lib[0] + '"></scr' + 'ipt>' +
          '<script src="' + lib[1] + '"></scr' + 'ipt>' +
          '<script src="' + lib[2] + '"></scr' + 'ipt>' +
          '<scr' + 'ipt>' +
          'try {' +
          '  var React = window.React, ReactDOM = window.ReactDOM;' +
          '  var useState = React.useState, useEffect = React.useEffect, useRef = React.useRef, useContext = React.useContext, useMemo = React.useMemo, useCallback = React.useCallback;' +
          '  ' + js + ';' +
          '  var root = ReactDOM.createRoot(document.getElementById("root"));' +
          '  root.render(React.createElement(App));' +
          '} catch(e) { parent.postMessage({type:"erro", msg:e.message}, "*"); }' +
          '<\/scr' + 'ipt></body></html>';
        iframe.srcdoc = html;
      });
    }

    function restaurar() {
      script.textContent = codigoOriginal;
      erro.style.display = "none";
    }

    function verificar() {
      if (!goal) return;
      var codigo = codigoDe(script);
      // data-goal pode ser "campo:regex" — aplica só no campo indicado, ou no código todo
      var partes = goal.split(":");
      var alvo = partes.length > 1 ? codigo : codigo;
      var regex = partes.length > 1 ? partes[1] : partes[0];
      try {
        var re = new RegExp(regex, "s");
        if (re.test(alvo)) {
          task && task.classList.add("ok");
          barra.querySelector(".try-check").textContent = "✅ Missão cumprida!";
        } else {
          task && task.classList.remove("ok");
          barra.querySelector(".try-check").textContent = "❌ Ainda não — tente de novo.";
        }
      } catch (e) {
        // goal simples: compara substring
        if (codigo.indexOf(goal) !== -1) {
          task && task.classList.add("ok");
          barra.querySelector(".try-check").textContent = "✅ Missão cumprida!";
        }
      }
    }

    function mostrarSolucao() {
      if (solucao) {
        solucao.style.display = solucao.style.display === "none" ? "block" : "none";
      }
    }

    barra.querySelector(".try-run").addEventListener("click", rodar);
    barra.querySelector(".try-reset").addEventListener("click", restaurar);
    if (goal) barra.querySelector(".try-check").addEventListener("click", verificar);
    if (solucao) {
      solucao.style.display = "none";
      barra.querySelector(".try-show").addEventListener("click", mostrarSolucao);
    }

    // Ctrl+Enter roda
    script.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); rodar(); }
    });
  });

  // Recebe erros do iframe
  window.addEventListener("message", function (e) {
    if (e.data && e.data.type === "erro") {
      document.querySelectorAll(".tryreact").forEach(function (c) {
        var err = c.querySelector(".try-err");
        if (err && c.querySelector("iframe").style.display !== "none") return;
      });
    }
  });

  window.ReactSim = ReactSim;
})();
