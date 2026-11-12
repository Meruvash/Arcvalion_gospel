# Trilha dos vídeos do agro: padrões do modão e como gerar

Pesquisa de 12/11/2026, a pedido do editor. Vale para todo vídeo da skill `video-agro`. Os fatos sobre os gêneros vêm das
fontes listadas no fim. O que é escolha nossa de produção (andamento, volume, estrutura) está marcado como **decisão nossa**.

## 1. O que o público do agro ouve

- **Não há pesquisa com amostra de produtores rurais** sobre gosto musical. Não achamos nenhuma, e não vamos afirmar
  números sobre isso.
- **Dois polos convivem.**
  - O **modão** (moda de viola, sertanejo raiz) é tratado pela imprensa do setor como a música das rodas depois do
    trabalho (Agrofy News, "Playlist do agro").
  - O **agronejo** (sertanejo pop com temática do agro, a partir de 2021) domina o streaming. Um artigo acadêmico o aponta
    como o gênero mais ouvido do país em 2023, sem citar a medição (UFPE, revista Mutirõ).
- **Para nós:** o modão (viola, violão e terças) passa respeito, origem e confiança, o tom certo para quem está
  endividado. O agronejo fica como opção leve, sem bateria pesada, para assunto de boa notícia.

## 2. Os padrões musicais, com fonte

**Viola caipira**
- Dez cordas em cinco pares, tocadas com os dedos e não com palheta (Wikipedia, "Viola caipira").
- Mais de 20 afinações no Brasil, quase todas abertas.
- A **cebolão**, das mais difundidas em SP e no sul de MG, tem som "tão bonito que fazia chorar as mulheres, como se estivessem
  descascando cebolas" (Vilela, citado em Amaral, Rev. Tulha, 2016; SESC SP, 2002).

**Pagode de viola** (gravado pela primeira vez em 1959)
- "Assenta-se sob o compasso binário, com a combinação polirrítmica de dois instrumentos de corda, a viola e violão"
  (Dias, ANPPOM 2014).
- **Viola:** faz "solos complexos e vigorosos durante a introdução e os interlúdios", com arrastes e ligados. Na batida, a mão
  direita abafa as cordas ("mata" o som) no primeiro tempo.
- **Violão:** é o acompanhador e acentua "os contratempos no tempo fraco". Os violeiros chamam essa batida de "cipó-preto".
- Matrizes do ritmo: catira, recortado, cururu e a própria moda de viola (Amaral, 2016; Vilela, 2013).
- **Uso nosso:** energia e urgência; bom para gancho de prazo.

**Moda de viola**
- É a narrativa cantada.
- "Entre uma estrofe e outra a viola caipira sempre faz os interlúdios instrumentais chamados repique ou recortado"
  (SimpleStudy, resumo ENEM; confirmar em fonte acadêmica antes de citar em matéria).
- **Uso nosso:** a forma casa com o nosso roteiro, com a viola **entre** as falas e quieta **durante** a voz.

**Arranjo clássico do sertanejo raiz** (anos 1950–60)
- Viola, violões, cavaquinho, acordeom (sanfona), percussão, baixo e às vezes guitarra havaiana.
- "Usa-se da abertura de melodias em terças geralmente entre violões, acordeons, tanto nas introduções como nas costuras"
  (Amaral, 2016).
- **As terças são a assinatura sonora do gênero.** No canto em dupla também: vozes "especially major thirds" e vibrato
  frequente (Wikipedia, "Sertanejo music").

**Guarânia, rasqueado e polca paraguaia**
- Vieram do Paraguai e do Mato Grosso do Sul e têm "em comum o andamento em compasso ternário" (Wikipedia,
  "Rasqueado"). Entraram no repertório das duplas a partir dos anos 1950.
- **Uso nosso:** emoção, saudade e drama; bom para assunto pesado, como a recuperação judicial.

**Outros ritmos do repertório caipira:** cururu, cateretê ou catira (com sapateado e palmas), toada, cana-verde, arrasta-pé,
xote, valsa, mazurca e polca (SESC SP, 2002).

**Sertanejo moderno** (inclui o agronejo)
- Entram guitarra elétrica, teclado e bateria. A guitarra elétrica chegou no fim dos anos 1960 (Wikipedia, "Sertanejo
  music").
- O sertanejo universitário é "mais despojado, acústico", com influência do pop.

## 3. Regras de trilha nos nossos vídeos

1. **Sempre instrumental.** Depois de gerar, rode o speech-to-text: a transcrição tem de achar **0 palavras**.
2. **Nada de nome no prompt**: nem artista, nem dupla, nem título de música ou álbum, nem gravadora. Os termos da ElevenLabs
   proíbem isso (Music Terms, seção 2.1). Descreva gênero, instrumento, ritmo e clima.
3. **Viola nos respiros, quieta sob a voz** (**decisão nossa**, inspirada no recortado). Peça introdução curta de viola
   solo de 1 a 2 s, acompanhamento discreto durante a fala e frase de viola resolvendo na cartela.
4. **Volume** (**decisão nossa**): a trilha entra em cerca de 0,15 (uns −16 dB) sob a narração. O master final fica em
   −14,5 LUFS e −1,5 dBTP.
5. **Uma trilha nova por vídeo, sem repetir o estilo do vídeo anterior.** Registre em `docs/video/CENAS_USADAS.md`, na
   seção de trilhas.
6. **Nada de imitar música existente**, nem de "parecer" uma música famosa. Os prompts terminam com "Do not imitate any
   existing song".

## 4. Estilos prontos (`tools/video/agro-arte/trilha/gerar_trilha.py --estilo <nome>`)

| Estilo | Ritmo | Clima | Quando usar |
|---|---|---|---|
| `toada` | toada lenta, binária | reflexivo, nostálgico, entardecer | dado triste, endividamento, "você sabia" calmo |
| `pagode` | pagode de viola, binário com contratempo no violão | energia, firmeza, urgência | prazo, corrida, aprovação de lei |
| `guarania` | guarânia em compasso ternário, lenta | emoção, drama, saudade | recuperação judicial, perdas, clima |
| `catira` | catira/cateretê: palmas e sapateado, viola rasqueada | festa, vitória, orgulho do campo | boa notícia, safra recorde, direito conquistado |
| `agronejo` | sertanejo leve e moderno, violão e sanfona, percussão discreta, sem bateria pesada | otimista, jovem | público jovem, assunto leve |

Os andamentos e tonalidades dos estilos são **decisão nossa**. As fontes não dão BPM. O andamento é escolhido para caber sob
a narração, e a tonalidade conversa com a afinação aberta da viola (Ré e Mi).

## 5. Como gerar

```sh
cd tools/video/agro-arte/trilha
python3 gerar_trilha.py ../../../../trilha.mp3 66000 --estilo pagode   # duração em ms ≈ duração do vídeo + 1 s
# conferência de voz cantada (deve dar 0 palavras):
curl -sS -X POST https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: dummy" -F model_id=scribe_v1 -F file=@trilha.mp3
```

- Se a API devolver `bad_prompt`, ela sugere um prompt alternativo. Leia, tire o que fere a regra 2 e gere de novo.
- **Próximo passo possível:** a API aceita um *composition plan* com seções e durações. Com ele, dá para casar a introdução
  de viola e a resolução com os tempos exatos das falas. Ainda não foi testado aqui.

## Fontes

- Dias, S. "Desatando os nós do pagode sertanejo". Anais do XXIV Congresso da ANPPOM, 2014:
  https://anppom.org.br/anais/anaiscongresso_anppom_2014/3193/public/3193-9941-1-PB.pdf
- Amaral, J. P. "A trajetória do violeiro Tião Carreiro". Rev. Tulha, v. 2, n. 1, 2016:
  https://revistas.usp.br/revistadatulha/article/download/125299/122410/237938
- SESC SP, "No ritmo da viola", 01/09/2002: https://portal.sescsp.org.br/online/artigo/compartilhar/1404_NO+RITMO+DA+VIOLA
- Wikipedia, "Viola caipira", "Sertanejo music" e "Rasqueado" (pt), consultadas em 12/11/2026.
- Agrofy News, "Playlist do agro": https://news.agrofy.com.br/noticia/201052/playlist-do-agro-listamos-os-10-maiores-idolos-do-sertanejo
- UFPE, "O AGRO (NEJO) é POP": https://periodicos.ufpe.br/revistas/mutiro/article/view/262033
- ElevenLabs, Music Terms (atualizado em 09/10/2026), seção 2.1: https://elevenlabs.io/music-terms
- SimpleStudy, "Moda de Viola" (resumo ENEM): https://simplestudy.com/pt-br/enem/artes/resumos/musica/moda-de-viola
