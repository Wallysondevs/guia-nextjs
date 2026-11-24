#!/usr/bin/env node
/**
 * foto.js — tira screenshot REAL de um app React servindo em uma URL local,
 * usando puppeteer-core + Chromium/Chrome headless.
 *
 * Uso:
 *   node foto.js <url> <arquivo-saida.png> [largura] [altura] [esperaMs] [fullPage=0|1]
 *
 * Exemplo:
 *   node foto.js http://localhost:8777/ferramentas/apps/ola-mundo-1/ \
 *                ../assets/telas/ola-mundo-1.png 800 500 2000 1
 *
 * - Navega até a URL (waitUntil: networkidle0)
 * - Espera o React renderizar (padrão: 2000 ms após o load + #root ter conteúdo)
 * - Tira screenshot full page (padrão) no viewport 800x500, fundo branco
 *
 * O executável do Chrome é resolvido nesta ordem:
 *   1. variável de ambiente CHROME_PATH
 *   2. instalação do puppeteer em ~/.cache/puppeteer/chrome/...
 *   3. chromium / chromium-browser / google-chrome no PATH
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const puppeteer = require('puppeteer-core');

function uso(code) {
  console.error('Uso: node foto.js <url> <saida.png> [largura=800] [altura=500] [esperaMs=2000] [fullPage=1]');
  process.exit(code);
}

function resolverChrome() {
  const candidatos = [];
  if (process.env.CHROME_PATH) candidatos.push(process.env.CHROME_PATH);

  // ~/.cache/puppeteer/chrome/**/chrome (puppeteer browsers install chrome)
  const cacheDir = path.join(os.homedir(), '.cache', 'puppeteer');
  const percorre = (dir, profundidade) => {
    if (profundidade > 6) return;
    let itens;
    try { itens = fs.readdirSync(dir, { withFileTypes: true }); } catch (_) { return; }
    for (const item of itens) {
      const p = path.join(dir, item.name);
      if (item.isDirectory()) {
        percorre(p, profundidade + 1);
      } else if (item.name === 'chrome' || item.name === 'headless_shell') {
        candidatos.push(p); // ordem: mais recente primeiro (sort reverso abaixo)
      }
    }
  };
  if (fs.existsSync(cacheDir)) percorre(cacheDir, 0);
  candidatos.sort().reverse();

  // caminhos comuns do sistema
  candidatos.push(
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/snap/bin/chromium'
  );

  for (const c of candidatos) {
    try {
      if (fs.existsSync(c) && fs.accessSync(c, fs.constants.X_OK) === undefined) return c;
    } catch (_) { /* ignora */ }
  }
  throw new Error(
    'Executável do Chrome/Chromium não encontrado. Defina CHROME_PATH ou rode: npx puppeteer browsers install chrome'
  );
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2 || args[0] === '-h' || args[0] === '--help') uso(args.length < 2 ? 1 : 0);

  const url = args[0];
  const saida = path.resolve(args[1]);
  const largura = parseInt(args[2] || '800', 10);
  const altura = parseInt(args[3] || '500', 10);
  const esperaMs = parseInt(args[4] || '2000', 10);
  const fullPage = (args[5] || '1') !== '0';

  const executavel = resolverChrome();
  console.log(`[foto.js] Chrome: ${executavel}`);
  console.log(`[foto.js] URL: ${url}`);
  console.log(`[foto.js] Saída: ${saida} (viewport ${largura}x${altura}, espera ${esperaMs}ms, fullPage=${fullPage})`);

  fs.mkdirSync(path.dirname(saida), { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: executavel,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--hide-scrollbars',
      '--force-device-scale-factor=1',
      '--window-size=' + largura + ',' + altura,
      '--default-background-color=FFFFFFFF',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: largura, height: altura, deviceScaleFactor: 1 });

    // fundo branco garantido, sem bordas/margens do navegador
    await page.evaluateOnNewDocument(() => {
      const css = 'html,body{margin:0 !important;padding:0 !important;background:#ffffff !important;}';
      const aplicar = () => {
        const s = document.createElement('style');
        s.textContent = css;
        (document.head || document.documentElement).appendChild(s);
      };
      if (document.head) aplicar();
      else document.addEventListener('DOMContentLoaded', aplicar);
    });

    await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });

    // espera o React renderizar: 2s fixos + até #root ter conteúdo (máx. 10s extra)
    await new Promise((r) => setTimeout(r, esperaMs));
    try {
      await page.waitForFunction(
        () => {
          const root = document.getElementById('root') || document.body;
          return root && root.innerHTML.trim().length > 0;
        },
        { timeout: 10000, polling: 200 }
      );
    } catch (_) {
      console.warn('[foto.js] aviso: #root não encheu no tempo extra; screenshot mesmo assim.');
    }
    // pequena espera final para fontes/estado assíncrono estabilizar
    await new Promise((r) => setTimeout(r, 300));

    await page.screenshot({ path: saida, fullPage, type: 'png' });
    const stat = fs.statSync(saida);
    console.log(`[foto.js] OK: ${saida} (${stat.size} bytes)`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('[foto.js] ERRO:', err.message);
  process.exit(1);
});
