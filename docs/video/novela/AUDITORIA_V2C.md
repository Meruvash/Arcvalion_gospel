# Auditoria de «A marca da Estrela» (V2c): o que fez o vídeo dar certo (25/11/2026)

O vídeo passou por três versões:
1. **Primeiro filme** (75 s): bonito, mas com pronúncias erradas e a voz do Dr. que não era a dele.
2. **Correção** (68 s): pronúncia e voz certas, mas, nas palavras do editor, "não tem história".
3. **Reescrita** (85 s): aprovada pelo editor ("Ficou bom").

Esta auditoria separa o que fez diferença do que foi desperdício, para o próximo episódio sair certo de primeira.

## 1. Números
| Etapa | Créditos do Higgsfield | Resultado |
|---|---|---|
| Referências (folhas, placa, amostras de voz) | cerca de 15 | elenco e lugar iguais em todas as cenas |
| Prévias em 480p (cena 1, duas vezes) e teste de pronúncia | cerca de 108 | acharam "novilha" saindo "novela" e "Cleide" saindo "Cledi" |
| 5 clipes em 720p (k1 a k5) | 546 | primeiro filme, com erros de pronúncia e sem a voz do Dr. |
| Refação de 4 planos por 4 palavras | 210 | **desperdício**: o conserto do áudio custaria perto de zero |
| Troca de voz do Dr. (voice change) | 3 | a voz do editor com a boca sincronizada |
| Reescrita: 4 cenas novas e 3 falas só de voz | 134 | **a versão aprovada** |
| **Total** | **cerca de 1.020** | |

O que fez a versão aprovada custou **134 créditos**: o roteiro reescrito. O que mais custou (os 210 da refação) não
mudou a opinião do editor sobre a história.

## 2. O que mais pesou no sucesso (em ordem)

### 1º. A história fechada, que ninguém mediu antes ("teste da história")
- **O problema:** o primeiro filme passou em todos os verificadores (tempo, palavras por minuto, posições) e mesmo assim
  "não tinha história".
- **O que fez a reescrita funcionar:**
  - **a prova que prova:** a anca limpa mostrada na tela, não só a lei;
  - **o plantio antes da virada:** a Rosa mostra o R no pescoço;
  - **o Dr. com uma ação:** a armadilha ("pergunta onde ela marcou antes de olhar a vaca");
  - **um final que responde ao começo:** a vaca vendida, a terra salva e a vilã punida na tela;
  - **um gancho que paga o que foi plantado:** o celular da Cleide.
- **A regra virou documento:** `REGRAS_ROTEIRO.md` §10.
- **Pedido do editor (25/11/2026):** o Dr. tem que "farmar aura". Entrada, previsão, lei, dedução e fecho, com
  alguém da cena reagindo ou dando razão a ele (`roteiros/drama/v3_o_video_inteiro.md`).

### 2º. O método Drama do Higgsfield, com as referências na ordem certa
- **Ordem das imagens no prompt:**
  1. placa do quadro: um quadro do primeiro clipe sem os personagens, que segura o lugar, a plateia e a luz;
  2. folha do lugar;
  3. folhas dos personagens;
  4. folhas de objeto (a Estrela).

  Depois vêm as amostras de voz, ligadas por "@AudioN is the voice of @ImageM".
- **Resultado:** os rostos, as roupas, a arena e a luz ficaram iguais em 13 planos gerados em dias diferentes.
- **Parâmetros:**
  - `seedance_2_5`, `omni_reference`, `generate_audio: true`, 720p, 9:16, `use_unlim: false`, `drama_ads_id`;
  - o prompt vai por referência a um arquivo da sandbox, e o sha256 devolvido é conferido.
- **Ferramentas:** o gerador de prompts está em `tools/video/novela/drama_prompt.py`. O método completo do Higgsfield
  está em `referencias/higgsfield_drama_ads/drama.md` e `clips.md`. O verificador em português está em
  `referencias/filme_v2c/checks_pt.py`.

### 3º. Voz: o Seedance não clona, e a troca de voz conserta sem mexer na boca
- **O problema:** a amostra de voz é só um "guia de timbre". Por isso o Dr. saiu com outra voz, mesmo com a amostra
  dele.
- **O conserto:** `voice_change` do Higgsfield com o clone do editor (`95b656d3…`, `element`), **só no trecho em que só
  o Dr. fala** (corte o trecho, suba, troque e emende). Custa 1 crédito por trecho e mantém o tempo de cada sílaba, por
  isso a boca continua sincronizada.
- **As vozes de cada personagem:**
  - Rosa e Valdir: clones feitos a partir de amostras de 26 a 29 s (o mínimo é 10 s);
  - Cleide: Roxie;
  - leiloeiro: Gideon.

  Os IDs estão em `drama_prompt.py` (`VOZ`).

### 4º. Pronúncia: palavra de risco fora da boca, guia fonético no prompt e ouvido do editor
- **Palavras que saíram erradas:**

  | Palavra | Como saiu |
  |---|---|
  | novilha | "novela" |
  | Cleide | "Cledi" |
  | calúnia | "calúdia" |
  | anca | "ança" |
  | roça | sem o O aberto |
  | mamadeira | errada (o editor ouviu) |
- **O que funcionou:** o guia logo depois da fala, no prompt. Por exemplo: `He pronounces "anca" as ÂN-ka, with a hard
  K sound, never "ança"`. O teste de 18 créditos confirmou que funciona.
- **O que funcionou melhor:** **não falar a palavra**. A calúnia virou cartão escrito, e "renúncia" (que termina igual a
  "calúnia") fica fora da boca na parte 2.
- **Atenção:** o transcritor (scribe_v1) **deixou passar** erros que o editor ouviu na hora. Ele confere se a palavra
  está lá, não se a pronúncia está certa.

### 5º. Conserto barato antes de regerar
- **O erro:** foram 210 créditos para refazer 4 planos por causa de 4 palavras.
- **A regra nova** (skill `novela`, passo 7):
  1. primeiro o conserto só do áudio (cerca de 0 a 1 crédito);
  2. se não convencer, mostrar o custo de regerar ao editor e esperar o OK;
  3. regerar só quando a boca mostrar o erro.

### 6º. Falas "só de voz" sobre planos sem boca na tela
- **Como:** "Dona Cleide, onde fica a sua marca?" sobre a Cleide calada, "Doze mil. Vendida." sobre o martelo e a Rosa
  fora do quadro sobre o close do R.
- **Custo:** 0,2 crédito cada, sem risco de sincronia.
- **Ferramenta:** `generate_audio_batch` com `seed_audio`.
- **Atenção:** confira a transcrição. Saiu "vendidas" na primeira vez; com "Doze mil... Vendida!" saiu certo.

### 7º. Regras de cada plano, que fizeram as cenas novas saírem certas de primeira
- **Fala:**
  - um falante por plano;
  - no máximo 10 palavras;
  - começando entre 0,6 e 0,8 s;
  - 1 s ou mais de silêncio no fim do plano.
- **Duração:** planos curtos, de 4 a 8 s, que se trocam barato quando dão errado.
- **No prompt:** rosto em três quartos, postura de cada pessoa e lado da câmera.
- **Insertos sem gente:** no Seedance 2.0 Mini (1 crédito por segundo).
- **O resultado:** as 4 cenas novas da reescrita (e as 3 falas) passaram na primeira geração. Só a fala "Vendida"
  precisou de outra tentativa, de 0,2 crédito.

### 8º. Trilha nas viradas certas
- **Como:** ElevenLabs Music com `composition_plan` de 4 trechos, alinhados à linha do tempo da montagem: tensão até a
  chegada do Dr., suspense na armadilha, virada na prova e acorde suspenso no gancho (`producao_v2c/trilha/plano_trilha_v3.json`).
- **Atenção:** a música sai com cerca de 1,1 s de silêncio no começo; alinhe ou corte.

### 9º. Montagem medida, não chutada
- **Cortes:** saem dos cortes medidos (`ffmpeg scdet`) e do tempo de cada palavra na transcrição, nunca no meio de uma
  fala.
- **Ferramenta:** `tools/video/novela/montar_cena.py`, com legenda amarela, cartão da lei literal
  (`tools/video/novela/cartao_lei.py`), trilha com sidechain, "PARTE 2" e aviso de dramatização.
- **Defeito corrigido:** duas legendas apareciam no mesmo quadro na troca de bloco.
- **Teste final:**
  - transcrição do filme inteiro, com todas as falas na ordem;
  - `crivo_qualidade.py` e `auditar_video.py`;
  - folha de quadros.

### 10º. Entrega que o editor consegue abrir
- **O que não funcionou:**
  - o Drive pelo conector aceita no máximo cerca de 3 MB por envio;
  - o link comprido quebrou no celular ("acesso negado");
  - a página do Higgsfield não abriu no celular.
- **O que funcionou:** o arquivo mandado direto na conversa, em duas versões:
  - o original (48 MB);
  - **uma cópia de 15 MB** em 1080×1920, a 1,25 Mbps (`ffmpeg -b:v 1250k`, duas passadas).

## 3. O que deu errado e a regra que nasceu
| Erro | Causa | Regra |
|---|---|---|
| "Não tem história" | os verificadores medem forma, não lógica | `REGRAS_ROTEIRO.md` §10 |
| 210 créditos por 4 palavras | regerar foi a primeira opção | skill `novela`, passo 7 |
| Voz do Dr. que não era a dele | o Seedance não clona | voice change só no trecho do Dr. |
| Pronúncias erradas que o transcritor não pegou | o STT não mede pronúncia | guia fonético, palavra de risco fora da boca, ouvido do editor |
| Cortar a fala da calúnia tirou a única ação do Dr. | ninguém refez o teste depois do corte | §10, item 7 |
| Pedidos de confirmação a cada passo | o modo da sessão | lista de autorizações em `.claude/settings.json` |

## 4. Lista de conferência do próximo episódio
1. **Roteiro:**
   - teste da história (§10);
   - os 5 momentos de aura do Dr.;
   - previsão com os 4 testes;
   - lei lida na fonte;
   - palavras de risco fora da boca.
2. **Aprovação do roteiro pelo editor** antes de gastar qualquer crédito.
3. **Referências:** folhas e placa do quadro, conferidas de perto.
4. **Primeiro plano sozinho**, conferido. Ele vira a placa para os outros.
5. **Lote dos outros planos**, com a cotação na hora (`get_drama_ads_config`).
6. **Conferência de cada plano:** transcrição, boca e quadros. O áudio se conserta antes de regerar.
7. **Voice change** nos trechos do Dr.
8. **Trilha** alinhada à montagem real.
9. **Montagem e conferências.**
10. **Entrega:** o original e a cópia de 15 MB, os créditos gastos e a legenda sem entregar a trama.

## 5. Onde está cada coisa no repositório
- **Roteiros:**
  - `roteiros/drama/v2c_a_marca_da_estrela.json` (a primeira versão);
  - `roteiros/drama/v2c_reescrita.md` (a aprovada);
  - `roteiros/drama/v3_o_video_inteiro.md` (parte 2, aprovada).
- **Prompts enviados:**
  - `referencias/filme_v2c/` (clip-k1…k5, r1…r4, n1…n4, folhas, placa, `refacao.json`, `novas.py`, `jobs.json`);
  - `producao_v2c/drama/prompts_cenas_novas.md`.
- **Script no formato Drama:** `producao_v2c/drama/script.json`.
- **Montagem:**
  - `producao_v2c/montagem/montagem.json` (a aprovada);
  - `montagem_v1.json` e `montagem_v2.json` (as anteriores).
- **Trilha:** `producao_v2c/trilha/plano_trilha.json` e `plano_trilha_v3.json`.
- **Correções:** `producao_v2c/REFAZER.md`.
- **Legendas do Instagram:** `producao_v2c/LEGENDA_INSTAGRAM.md` (a versão que conta tudo e a sem entregar a trama).
- **Ferramentas:**
  - `tools/video/novela/drama_prompt.py`, `montar_cena.py` e `cartao_lei.py`;
  - `referencias/filme_v2c/conferir.py` (transcrição e cortes de um clipe).
- **Método do Higgsfield que eu li para aprender:**
  - `referencias/higgsfield_drama_ads/drama.md`: o roteiro da direção do filme;
  - `referencias/higgsfield_drama_ads/clips.md`: como dividir em clipes, emendas, referências e placas;
  - `referencias/higgsfield_drama_ads/live-action.md`: o estilo;
  - `checks.py` e `assemble.py`: o verificador e a montagem do próprio Higgsfield.

  Os outros arquivos do método (`characters.md`, `location.md`, `models.md`, `script-format.md`, `story-rules.md`,
  `sheet-realism.md` e outros) são lidos na hora com `get_workflow_bundle_file` (workflow `drama-ads`, pasta
  `references`), porque o Higgsfield atualiza.
- **Modelos de roteiro do editor:** `docs/video/pesquisa/reel_novela/REEL_NOVELA_ROTEIRO_PADRAO.md` e
  `REEL_NOVELA_ROTEIRO_EVIDENCIAS.md`.
- **Notas do teste de sincronia (LatentSync e LTX):** `SINCRONIA.md` e `referencias/ltx2_notas.md`. Só 2 de 13 clipes
  passaram, por isso a boca passou a ser gerada junto com a fala.
- **Passagem para a próxima sessão:** `producao_v3/LEIA_PRIMEIRO.md`.
- **Vídeos e áudios:** ficam fora do git (`.gitignore`). O filme aprovado é `producao_v2c/planos/marca_da_estrela_v2c_r3.mp4`.
