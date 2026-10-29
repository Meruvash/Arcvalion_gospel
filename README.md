# Portal Cristão

Portal jornalístico cristão e conservador: notícias, política e sociedade, família, fé e Bíblia, economia,
cultura cristã e eventos. *Jornalismo, fé e sociedade. Informação com responsabilidade e uma perspectiva cristã
sobre o Brasil e o mundo.* O nome é provisório e configurável em `config/portal.json`.

Site estático gerado por Python (JSON → HTML), sem framework, com um Worker da Cloudflare para comentários,
newsletter, formulários e métricas de anúncio. Arquitetura herdada de um projeto anterior e adaptada; o histórico
da migração está em `docs/`.

```bash
pip install -r requirements.txt
python3 exemplos/gerar.py && python3 tools/build.py --exemplo   # prévia fictícia em publico-exemplo/
python3 tools/build.py                                           # site real em publico/
python3 -m unittest discover -s tests && node --test tests/worker.test.mjs
```

| Documento | Conteúdo |
|---|---|
| `docs/ENTREGA.md` | resumo da entrega, funcionalidades, checklists de SEO e segurança, pendências |
| `docs/PADRAO_EDITORIAL.md` | premissas editoriais, tipos de conteúdo e formato das matérias |
| `docs/FLUXO_EDITORIAL.md` | do rascunho à publicação com revisão humana; correções |
| `docs/DEPLOY.md` | execução local, deploy, domínio, Worker, variáveis de ambiente |
| `docs/ISOLAMENTO.md` | auditoria de separação em relação ao projeto de origem |
| `docs/AUDITORIA_ELITE_BOARDGAMERS.md` | auditoria da arquitetura de origem |
