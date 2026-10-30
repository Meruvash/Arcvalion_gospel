# O Paladino

Portal jornalístico cristão e conservador: notícias, política e sociedade, família, fé e Bíblia, economia,
cultura cristã e eventos. *Jornalismo com princípios. Fé, cultura e sociedade. Informação com responsabilidade e uma perspectiva cristã
sobre o Brasil e o mundo.* O nome é provisório e configurável em `config/portal.json`.

Site estático gerado por Python (JSON → HTML), sem framework, com um Worker da Cloudflare para comentários,
newsletter, formulários e métricas de anúncio. Arquitetura herdada de um projeto anterior e adaptada; o histórico
da migração está em `docs/`.

```bash
pip install -r requirements.txt
python3 tools/build_home.py                                      # site gerado na raiz (código de front-end do Elite)
python3 tools/checar_seo.py && python3 tools/checar_isolamento.py
python3 tools/montar_publicacao.py _site                         # o que o deploy publica (raiz sem arquivos de trabalho)
python3 -m unittest discover -s tests && node --test tests/worker.test.mjs
```

| Documento | Conteúdo |
|---|---|
| `docs/ENTREGA.md` | resumo da entrega, funcionalidades, checklists de SEO e segurança, pendências |
| `docs/PADRAO_EDITORIAL.md` | premissas editoriais, tipos de conteúdo e formato das matérias |
| `docs/FLUXO_EDITORIAL.md` | do rascunho à publicação com revisão humana; correções |
| `docs/FOTOS.md` | fontes de foto com licença conferida e o robô `tools/fotos.py` |
| `docs/FONTES.md` | mapa de sites cristãos e conservadores para pauta, com feeds testados |
| `docs/DEPLOY.md` | execução local, deploy, domínio, Worker, variáveis de ambiente |
| `docs/ISOLAMENTO.md` | auditoria de separação em relação ao projeto de origem |
| `docs/AUDITORIA_ELITE_BOARDGAMERS.md` | auditoria da arquitetura de origem |
