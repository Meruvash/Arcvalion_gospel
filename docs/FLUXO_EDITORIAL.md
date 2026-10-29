# Fluxo editorial

```
coleta (IA)            rascunho (IA ou repórter)       revisão (pessoa)              publicação
coletar.py  ───────▶   novo.py + JSON  ─────────▶   checar.py + fontes  ───────▶   publicar.py aprovar --revisor
.cache/pauta/          status "rascunho"→"revisao"   skill revisao (apoio)          build.py → deploy
                                                                                     │
                                       correção / atualização / despublicação ◀──────┘
                                       publicar.py corrigir|atualizar|despublicar --revisor
```

1. **Pauta**: `python3 tools/editorial/coletar.py` lista candidatas das fontes primárias de `config/fontes.json`
   (só sugestão). A skill `pauta` faz a triagem e a apuração.
2. **Rascunho**: `python3 tools/novo.py <editoria> <tipo> "<título>"`. Preencha no padrão
   (`docs/PADRAO_EDITORIAL.md`) até `python3 tools/editorial/checar.py <arquivo>` passar; então `status: "revisao"`.
3. **Revisão humana**: a pessoa revisora confere fontes, citações e foto (a skill `revisao` ajuda com um relatório)
   e aprova: `python3 tools/publicar.py aprovar conteudo/artigos/<slug>.json --revisor <slug>`
   (`--agendar 2026-11-02T07:00` para agendar: a matéria só aparece no build a partir dessa data).
4. **Publicação**: `python3 tools/build.py --producao` (no CI, pelo workflow Deploy).
5. **Correção**: corrija o texto no JSON e registre:
   `python3 tools/publicar.py corrigir <arquivo> --revisor <slug> --texto "O valor correto é R$ 2 milhões, e não R$ 20 milhões."`
   Fato novo sem erro: `atualizar`. Tirar do ar: `despublicar --motivo "..."` (o arquivo e o histórico ficam).

**Manchete e destaques**: `"manchete": true` numa matéria publicada (a mais recente com a marca vira a manchete;
sem marca, a mais recente com foto). `"destaque": true` coloca no bloco Destaques. Escolha editorial, nunca paga.

**Agenda de eventos**: `conteudo/agenda.json`, cada evento com nome, data (`AAAA-MM-DD`), local ou `online`,
organizador e `fonte` com link. `"confirmado": false` mostra "data a confirmar"; `"patrocinado": true` mostra
"divulgação paga" e fica fora dos dados estruturados de evento. Evento passado some sozinho.

**Editorias**: `config/editorias.json` (criar, renomear, reordenar, ocultar com `"visivel": false`, trocar cores).
