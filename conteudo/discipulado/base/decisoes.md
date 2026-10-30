# Decisões editoriais

Decisões que afetam mais de uma lição. Registrar data, decisão e motivo. Mudar uma decisão exige revisar as lições já produzidas.

## 2026-10-30

- **Tradução bíblica do aluno: NTLH (SBB).** Motivo: é a tradução brasileira feita para leitores comuns, por equivalência dinâmica. A licença da SBB permite citar até 500 versículos sem autorização escrita, desde que não ultrapasse 25% da obra e não reproduza um livro inteiro. Linha de crédito obrigatória: "Texto bíblico: Nova Tradução na Linguagem de Hoje. Copyright Sociedade Bíblica do Brasil. Usado com permissão." Conferir a redação exata da linha de crédito na edição NTLH mais recente antes da publicação.
- **Tradução de comparação no guia: NAA ou NVI.** Usar quando a NTLH simplificar algo que o discipulador precisa ver com mais precisão.
- **Contagem de versículos.** Manter em `conteudo/discipulado/base/versiculos.md` a soma de versículos reproduzidos na coleção inteira, para não estourar o limite de 500.
- **Orientação confessional provisória: assembleiana clássica.** Até a instituição definir confissão própria.
- **Sem travessão em nenhum texto.**
- **Legibilidade do texto do aluno medida pelo `tools/discipulado/legibilidade.py`, meta Flesch 75+.** O índice é portão de entrada para a auditoria, não substitui leitura por pessoas reais.
- **Padrão de citação de referência bíblica.** Primeira vez na lição por extenso ("João, capítulo 1, versículo 14"), depois "João 1:14". A Lição 5 explica o sistema de capítulos e versículos.
- **A coleção mora no portal O Paladino.** Pasta de cada lição: `conteudo/discipulado/NN-slug/` (licao.json, dossie.md, aluno.md, discipulador.md, auditoria.md). Página: `discipulado/<slug>/`, gerada por `tools/build_discipulado.py`. A aba Discipulado ocupa no menu o lugar que era da Agenda (pedido do editor, 30/10/2026); a página `lancamentos/` continua no ar, fora do menu.
- **Referência confessional do portal: Declaração de Fé das Assembleias de Deus (CGADB).** É a linha editorial pentecostal do portal (docs/PADRAO_EDITORIAL.md). Nas lições 1 a 4 não há polêmica denominacional; divergências vão para o guia do discipulador.
- **Publicação automática, como nas outras rotinas do portal.** A lição que passa em `tools/discipulado/checar_licao.py` (inclui o medidor de legibilidade) e tem auditoria independente com nota 85 ou mais vai ao ar com `tools/publicar.py aprovar ... --automatica`. A página diz que a nota é preliminar e que não houve leitura por pessoas do público.
