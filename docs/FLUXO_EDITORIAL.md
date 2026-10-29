# Fluxo editorial

```
rotina (skill noticias / estudo)      prévia                      revisão humana                    no ar
coleta → crivo → texto → foto  ──▶  status "revisao"  ──▶  pessoa revisora confere  ──▶  publicar.py aprovar --revisor
                                      /previa/ (noindex)        fontes, citações e foto         build + deploy (push na main)
```

1. **Rotina** (skill `noticias`, todo dia; skill `estudo`): coleta em três rodadas, crivo por pontos, texto no padrão,
   foto com licença (`tools/imagens/baixar.py`), `checar_noticia.py`, build, push. As notas ficam em `/previa/`.
2. **Revisão**: a pessoa revisora lê cada prévia em `<site>/previa/` e confere as fontes (a skill `verificacao` ajuda).
3. **Aprovação**: `python3 tools/publicar.py aprovar conteudo/noticias/<arquivo>.json --revisor <slug>` (ou peça na conversa,
   nome por nome, que o agente roda com o seu slug). Push na main: o deploy publica em cerca de 1 minuto.
4. **Divulgação**: `python3 tools/divulgacao.py` gera os textos de WhatsApp, Telegram e Instagram do dia.
5. **Correção**: corrija o JSON e registre `python3 tools/publicar.py corrigir <arquivo> --revisor <slug> --texto "..."`.
