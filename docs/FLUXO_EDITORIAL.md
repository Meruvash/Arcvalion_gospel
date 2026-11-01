# Fluxo editorial

```
rotina (skills noticias, estudo, discipulado)                                        no ar
coleta → crivo → texto → foto → validador ──▶ publicar.py aprovar --automatica ──▶ build + deploy (push na main)
                                                                                     ▲
                                              verificação noturna (21h) confere e corrige o que já está no ar
```

**Publicação automática em todas as rotinas** (ordem do responsável editorial em 29/10/2026, reforçada em 01/11/2026):
nenhuma rotina deixa conteúdo esperando aprovação humana. O que passa nos validadores é aprovado pela própria rotina
(`--automatica`, registrado como aprovação automática) e publicado no mesmo push; o que não passa não sai.

1. **Rotina** (skills `noticias`, `estudo` e `discipulado`, todo dia): coleta, crivo, texto no padrão, foto com licença,
   validador (`checar_noticia.py`, `checar_estudo.py`, `checar_licao.py`), `publicar.py aprovar <arquivo> --revisor
   anderson-pelicioni-de-castro --automatica`, build, push. O deploy publica em cerca de 1 minuto.
2. **Verificação** (skill `verificacao`, todo dia às 21h): confere contra as fontes o que foi publicado no dia e corrige
   sozinha na origem, com `publicar.py corrigir`; o que não se confirma sai do texto, e notícia cujo fato central não se
   confirma sai do ar com `publicar.py despublicar`.
3. **Comentários** (skill `comentarios`): a rotina aprova ou reprova cada comentário, sem fila para a redação.
4. **Divulgação**: `python3 tools/divulgacao.py` gera os textos de WhatsApp, Telegram e Instagram do dia.
5. **Correção**: corrija o JSON e registre `python3 tools/publicar.py corrigir <arquivo> --revisor <slug> --texto "..."`.
