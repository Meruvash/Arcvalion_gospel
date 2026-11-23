# Resultado do teste do LTX-2.3 no Kaggle grátis (23/11/2026)

**Conclusão:** o LTX-2.3 22B **não é viável na T4 grátis do Kaggle** para gerar gente. Nenhum vídeo saiu em 4 tentativas.
A 4ª tentativa gastou 83 minutos de GPU.

## O que funcionou
- Compactar o modelo durante o download: o checkpoint passou de 46,1 GB para 27,6 GB, com 2.688 tensores convertidos, em
  6 min.
- Baixar todos os arquivos: 10 min no total.
- Codificar o texto com o Gemma (pasta do LTX-2).

## O que falhou (log da versão 4)
1. **O senhor falando com a sua voz (áudio para vídeo):**
   - Erro: `RuntimeError: ... expected input to have 2 channels, but got 1`.
   - Causa: o pipeline exige áudio estéreo, e a voz foi enviada em mono.
   - É fácil de corrigir, mas a geração esbarraria no limite de memória do item 2.
2. **A Rosa, 10 s (texto para vídeo):**
   - Erro: `CUDA out of memory`. A atenção pediu 7,99 GB, e a T4 tinha 3,66 GB livres.
   - Quando falhou: depois de 66 min, já na geração.
   - Causa: a T4 (2018) não roda a atenção econômica das placas novas, e 241 quadros em 704×384 não cabem nos 16 GB.

## Por que parar aqui
- **Para caber**, seria preciso cortar para cerca de 3 a 5 s em resolução baixa. Isso não serve para avaliar rosto e
  boca.
- **O tempo e a cota não compensam:** cada tentativa leva mais de 1 hora, e a cota grátis é de 30 h por semana.
- **A qualidade é baixa no ranking:** no ranking cego de imagem para vídeo (Artificial Analysis, 22/11/2026), o LTX-2.5
  está em 32º lugar.
- **O caminho do teste agora é o Google Flow grátis:** ver `../previa_flow/PROMPTS_FLOW_V1.md`. O LTX volta a ser opção
  se houver GPU alugada com 48 GB ou mais.
