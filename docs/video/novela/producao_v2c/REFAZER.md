# «A marca da Estrela»: pontos para refazer (lista do editor, 23/11/2026)

Vídeo conferido: `planos/marca_da_estrela_v2c.mp4` (75 s). Os tempos são do filme montado.

| # | Onde | O que está errado | Origem | Como refazer (proposta) |
|---|---|---|---|---|
| 1 | ~1:04, Dr.: "E ladra, na frente de todos, é calúnia." | **resolvido: a fala saiu do roteiro** (decisão do editor, pronúncia ruim); sai também o cartão do Código Penal | — | — |
| 2 | ~0:04–0:08, Rosa: "É a Estrela. Criei na mamadeira." | "mamadeira" saiu muito errado | k1 (cena 1) | refazer o plano da Rosa |

| 3 | todas as falas do Dr. (~0:48, ~0:58, ~1:04) | não é a voz clonada do editor | o Seedance usa a amostra só como "guia de timbre" e inventa uma voz parecida | trocar só a voz das falas do Dr. depois de prontas (voice change do Higgsfield com o clone `95b656d3…`), mantendo o tempo de cada sílaba: a boca continua sincronizada |

| 4 | ~0:35, Valdir: "Roça de pobre não cria vaca assim." | "roça" saiu com a pronúncia errada; precisa da força e do som aberto no O | k3 | no prompt, escrever a palavra com acento como guia de pronúncia ("Róça", ó aberto e tônico, RÓ-ssa) e refazer o plano do Valdir |

| 5 | ~0:48 Dr.: "Ela vai dizer que marcou na anca."; ~0:50 Cleide: "Marquei na anca, sim! Pode olhar!"; ~0:57 Dr.: "Na anca, a lei não deixa marcar." | "anca" saiu como "ança" (som de S no lugar do K) nas três falas | k4 e k5 | no prompt, guia de pronúncia "anca = ÂN-ka, with a hard K sound, never 'ança'"; refazer os três planos |

## Refação feita (23/11/2026)

- Planos refeitos no Seedance 2.5 (720p, 210 créditos, prompts com guia de pronúncia): `r1` Rosa "mamadeira", `r2` Valdir "Róça", `r3` previsão do Dr. + Cleide "anca", `r4` Dr. "Na anca, a lei não deixa marcar." O transcritor confirma as palavras certas.
- Voz do Dr.: voice change do Higgsfield com o clone `95b656d3…` só nos trechos em que só o Dr. fala (r3 0–3,78 s; r4 0–4,25 s), 1 crédito cada. O tempo das palavras não mudou (boca sincronizada).
- Nova montagem: `montagem/montagem.json` (a anterior ficou em `montagem_v1.json`). Filme: `planos/marca_da_estrela_v2c_r2.mp4`, 68,2 s, −18,1 LUFS, 14 falas completas no transcritor.
- Gasto da refação: 212 créditos.
