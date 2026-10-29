// Abre uma página montada com JavaScript num Chromium sem janela e devolve o HTML final. Chamado por robo.py.
// Uso: node tools/imagens/navegador.js <url> <user-agent>
// Antes de cada pedido do navegador (scripts, chamadas de API), pergunta ao robo.py pela entrada padrão se o
// robots.txt permite: escreve {"id": n, "url": "..."} e espera "n 1" (pode) ou "n 0" (não pode). Imagens, fontes
// e CSS não são baixados aqui; as imagens vêm depois pelo cliente educado do robo.py.
// Saída final: uma linha {"status": 200, "html": "..."}.
const { chromium } = require('playwright');
const readline = require('readline');

const [url, ua] = process.argv.slice(2);
const pendentes = new Map();
let proximo = 0;
readline.createInterface({ input: process.stdin }).on('line', linha => {
  const [id, ok] = linha.trim().split(' ');
  const resolver = pendentes.get(id);
  if (resolver) { pendentes.delete(id); resolver(ok === '1'); }
});
const perguntar = u => new Promise(resolve => {
  const id = String(proximo++);
  pendentes.set(id, resolve);
  process.stdout.write(JSON.stringify({ id, url: u }) + '\n');
});

(async () => {
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  const nav = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
  const ctx = await nav.newContext({ userAgent: ua, locale: 'pt-BR', viewport: { width: 1280, height: 900 } });
  await ctx.route('**/*', async route => {
    const req = route.request();
    if (['image', 'media', 'font', 'stylesheet'].includes(req.resourceType())) return route.abort();
    if (req.url().startsWith('data:')) return route.continue();
    return (await perguntar(req.url())) ? route.continue() : route.abort();
  });
  const pg = await ctx.newPage();
  let status = 0, html = '';
  try {
    const resp = await pg.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    status = resp ? resp.status() : 0;
    if (status < 400) {
      for (let i = 0; i < 12; i++) {  // rola devagar para as galerias com carregamento preguiçoso aparecerem
        await pg.mouse.wheel(0, 1400);
        await pg.waitForTimeout(400);
      }
      await pg.waitForLoadState('networkidle').catch(() => {});
      html = await pg.content();
    }
  } catch (e) {
    process.stdout.write(JSON.stringify({ status: 0, erro: String(e.message || e) }) + '\n');
    await nav.close();
    process.exit(0);
  }
  process.stdout.write(JSON.stringify({ status, html }) + '\n');
  await nav.close();
  process.exit(0);
})();
