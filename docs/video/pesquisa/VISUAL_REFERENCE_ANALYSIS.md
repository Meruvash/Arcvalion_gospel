# Análise de referências visuais — Vox, Johnny Harris, EarnEdits

## 0. Limite desta análise (leia antes)

- **Não assisti a nenhum vídeo.** Este ambiente não reproduz vídeo do YouTube, e não baixei vídeos
  de terceiros. Por isso, nada aqui descreve um vídeo como "visto".
- As evidências sobre **como** essas equipes trabalham vêm de **textos**: transcrições, entrevistas e
  artigos, com link e data em `research/notes/referencias-vox-harris-earnedits.md`.
- As descrições de técnica (como um movimento funciona e como reproduzi-lo) vêm do vocabulário
  corrente de motion design e estão marcadas **[H]**. São hipóteses de trabalho para validar
  assistindo aos vídeos com você, quadro a quadro, numa etapa seguinte.
- **EarnEdits:** o site bloqueou o acesso automático (403). O que sei vem de blogs de afiliados.
  É uma loja de projetos de After Effects, com uma categoria chamada "VOX Edits".

## 1. O que as fontes primárias dizem

| Fonte | O que afirma | Implicação para nós |
|---|---|---|
| Johnny Harris, transcrição de "How I Make My Maps" (2020) | Faz mapas no **After Effects** com o plugin **GEOlayers**; usa **Mapbox Studio**; cronometra no **Premiere** | O padrão-ouro dele é composição 2D/2.5D sobre dados geográficos reais, não 3D generativo. Isso é reproduzível com MapLibre/d3 + câmera virtual |
| Jason Boone, animador contratado por Harris (PremiumBeat, 2022) | GEOlayers como ferramenta principal; Google Earth Studio para exportar trilhas de câmera 3D | Os planos "voando sobre o globo" de verdade usam imagem de satélite 3D, que tem custo e termos de uso |
| Sam Ellis, Vox Atlas (Storybench, 2020) | Anima no After Effects; dados do CSIS; 3–4 semanas por vídeo | O tempo vai em **pesquisa e dados**; animação é a última camada |
| Joey Sendaydiego, Vox (Storybench, 2024) | "Mapas são dos gráficos mais tediosos de fazer"; 2–3 semanas por vídeo; um vídeo feito em papel-cartão | Automatizar **mapas** é onde o código dá mais retorno |
| Estelle Caswell, Vox (School of Motion) | "Meu trabalho não era decorar o vídeo"; "a prioridade é sempre a evidência visual" | Regra editorial: todo elemento animado precisa ser **evidência** (documento, dado, lugar), não enfeite |
| Vox, "How to make more Vox videos happen" (2018) | Semanas de pesquisa e entrevistas; seis rodadas de revisão | O processo precisa de **pontos de revisão** formais, não só de render |

**Conclusão verificada:** nenhuma das três referências trabalha "por prompt". Todas partem de
**evidência** (dado, documento, mapa, foto de arquivo) e a montam com ferramentas de composição
(After Effects + plugins). A fraqueza que você descreveu (movimento genérico, inconsistência) é o
que se espera quando a etapa de evidência e a de linguagem visual são substituídas por geração. Esta
última frase é minha inferência [H].

## 2. Os 10 eixos pedidos — princípios técnicos [H]

1. **Movimento de câmera.** A câmera tem motivação narrativa: aproxima para revelar, recua para dar
   contexto. Usa curvas lentas, com entrada e saída suaves; em mapa, o zoom deve ser interpolado em
   **escala logarítmica** (velocidade percebida constante), o que implementamos nas PoCs. Quase nunca
   fica parada: quando "segura", ainda deriva de 1 a 3%.
2. **Composição.** Há uma hierarquia clara por quadro: um sujeito, um rótulo, uma fonte. Margens
   de segurança largas. Texto ancorado numa grade fixa por série.
3. **Tipografia cinética.** Serve à leitura: revelação por máscara (a linha "sobe" de dentro de uma
   caixa), números que contam até o valor, sublinhado ou marcador que se desenha. Pouco texto por quadro.
4. **Mapas.** Projeção escolhida pela história (ortográfica para "onde fica", plana para comparar
   países); destaque por cor de acento; pino com pulso; linha de chamada; zoom contínuo até o lugar,
   que muitas vezes vira transição para a foto ou o vídeo do local.
5. **Paralaxe em fotografias (2.5D).** A foto é recortada em 2 a 4 planos, cada um se move numa
   velocidade e o fundo é retocado. Em profissionais, o recorte e o retoque costumam ser **manuais**
   (Photoshop) [H]. A PoC mostrou por quê: o recorte automático gera artefatos visíveis.
6. **Transições.** Raramente gratuitas: *match cut* (pino que vira íris para a foto), empurrão de
   uma "folha" de papel, máscara seguindo uma forma do quadro, corte seco no tempo da fala.
7. **Gráficos.** Um dado por vez; eixos mínimos; a barra ou linha "cresce" no ritmo da frase que a
   anuncia; fonte sempre visível.
8. **Profundidade.** Sombras projetadas em recortes, desfoque de planos (*rack focus*), textura de
   papel e grão que unificam material de origens diferentes.
9. **Sincronização com a narração.** A animação dispara na **palavra**, não na frase. Isso exige
   transcrição com tempo por palavra (Whisper/WhisperX) e um roteiro com "pistas" (*cues*). Na PoC
   ficou só o esqueleto: `narracao_referencia` no `spec.json`.
10. **Ritmo e som.** Alternância entre planos rápidos e respiros; *risers* e *whooshes* discretos nos
    movimentos; ducking da trilha sob a voz; loudness de entrega padronizado (por exemplo -14 LUFS
    para web).

## 3. Taxonomia de técnicas: o que o código resolve

Legenda de viabilidade: **C** = reproduzível só com código (testado ou trivial no motor escolhido);
**C+P** = código mais pré-processamento local (modelo de profundidade, bake de tiles); **F** = exige
ferramenta ou etapa adicional, humana ou paga.

| Família | Técnica | Viab. | Como (no stack proposto) | Testado na PoC? |
|---|---|---|---|---|
| Câmera | Push/pull, deriva, tilt sobre foto | C | transformações CSS com easing por token | **Sim** |
| Câmera | Zoom de mapa em escala log | C | d3-geo `scale` com interpolação logarítmica | **Sim** |
| Câmera | Voo 3D sobre terreno real | C+P / F | MapLibre com terreno (bake quadro a quadro); fotorrealista exige Google 3D Tiles/Cesium ion (cota) | Não |
| Câmera | *Rack focus* entre planos | C | `filter: blur` animado por camada (caro no render) | Não |
| Câmera | Desfoque de movimento | C | `@remotion/motion-blur` ou *trail* manual; no HF, regra própria (`media-treatment`) | Não |
| Composição | Grade, margens seguras, hierarquia | C | tokens + componentes; o `check` do HF valida área segura | Parcial |
| Tipografia | Revelação por máscara | C | `overflow:hidden` + translateY | **Sim** |
| Tipografia | Contagem numérica | C | interpolação + `Intl.NumberFormat('pt-BR')` | **Sim** |
| Tipografia | Sublinhado/marcador desenhado à mão | C | SVG `stroke-dashoffset` | Não (trivial) |
| Tipografia | Texto que se ajusta à largura | C | `fitTextFontSize` (HF) ou medição própria | Não |
| Mapas | Globo, destaque de país, pino, rótulo | C | d3-geo + Natural Earth | **Sim** |
| Mapas | Rotas animadas, arcos, fluxos | C | d3 (traço progressivo) ou deck.gl TripsLayer | Não |
| Mapas | Coropletas a partir de dados | C | d3-scale + GeoJSON | Não |
| Mapas | Basemap de satélite/ruas | C+P | MapLibre + Protomaps PMTiles assado antes; satélite exige fonte licenciada | Não |
| Mapas | Mapa histórico (fronteiras antigas) | F | precisa de dados históricos georreferenciados com fonte (por exemplo IBGE, atlas digitalizados) | Não |
| Foto | Ken Burns | C | transformações | **Sim** (base) |
| Foto | Paralaxe 2.5D automática | C+P | Depth-Anything-V2-**Small** + camadas + inpainting | **Sim, com artefatos** |
| Foto | Paralaxe 2.5D profissional | F | recorte e retoque manual das camadas (Photoshop/GIMP/Krita) | Não |
| Foto | Recorte com borda "adesivo", sombra | C+P | máscara (manual ou segmentação) + CSS `drop-shadow` | Não |
| Foto | Colorização de foto P&B | F | evitar, ou declarar como reconstrução; conflita com "nada inventado" | — |
| Transição | Íris/match a partir de um ponto | C | `clip-path: circle()` | **Sim** |
| Transição | Folha de papel empurrando | C | transform + sombra | **Sim** |
| Transição | Rasgo de papel, máscara orgânica | C+P | textura de rasgo própria (escaneada ou feita à mão) + máscara | Não |
| Gráficos | Barras, linhas, contadores | C | componentes com d3-scale | Parcial (contadores) |
| Profundidade | Grão/papel unificador | C | textura procedural com semente fixa | **Sim** |
| Profundidade | Luz, vazamento de luz, poeira | C+P | `@remotion/light-leaks` ou texturas próprias | Não |
| Sincronização | Disparo por palavra | C+P | whisper.cpp/WhisperX → `cues.json` → tempos do spec | Esqueleto |
| Som | Mix, ducking, loudness | C | ffmpeg `sidechaincompress` + `loudnorm` | Não |
| Som | Desenho de som (*whooshes*, ambiências) | F | biblioteca licenciada (CC0/CC-BY com atribuição, ou comprada) | Não |
| Narração | Locução | F | voz humana (recomendado); TTS só com licença de voz clara | Não |

**Resumo:** cerca de 70% do vocabulário (câmera, tipografia, mapas vetoriais, transições, gráficos)
é **inteiramente código**. Ficam de fora quatro pontos, que pedem processo ou ferramenta extra:
(a) camadas 2.5D com acabamento profissional, (b) basemaps de satélite e terreno fotorrealista,
(c) desenho de som e (d) narração.

## 4. Lições da PoC que entram na linguagem
- O motor não muda o resultado. As duas PoCs, com o mesmo spec, têm SSIM médio de 0,969 entre si.
  **A qualidade vem do sistema de design (tokens, curvas, regras) e da evidência**, não do motor.
- Paralaxe automática precisa de **amplitude pequena**: no máximo cerca de 4% de deslocamento
  relativo entre planos vizinhos. Acima disso, o inpainting aparece.
- O mapa em 1:50m serve para "onde fica"; para zoom de cidade é preciso 1:10m ou basemap. Na PoC,
  com zoom alto o litoral fica poligonal.
- Texto de crédito com 17 px é ilegível no celular (o `check` do HyperFrames apontou). O piso é 28 px a 1080p.
