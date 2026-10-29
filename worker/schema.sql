-- Banco D1 do serviço de interações do portal. Banco PRÓPRIO: crie com `wrangler d1 create portal-cristao-interacoes`.
-- Nada de IP em claro: ip_hash é um SHA-256 do IP com um sal que muda todo dia, usado só para limitar abuso.

CREATE TABLE IF NOT EXISTS curtidas (
  pagina      TEXT NOT NULL,
  dispositivo TEXT NOT NULL,          -- identificador aleatório guardado no navegador (localStorage), não é cookie
  criado      TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (pagina, dispositivo)
);

CREATE TABLE IF NOT EXISTS comentarios (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  pagina      TEXT NOT NULL,
  nome        TEXT NOT NULL,
  email       TEXT,                   -- opcional, nunca publicado
  texto       TEXT NOT NULL,
  criado      TEXT NOT NULL DEFAULT (datetime('now')),
  estado      TEXT NOT NULL DEFAULT 'pendente',   -- pendente | aprovado | reprovado | duvidoso
  parecer     TEXT,
  decidido_por TEXT,                  -- 'ia' ou 'editor'
  decidido_em TEXT,
  ip_hash     TEXT
);
CREATE INDEX IF NOT EXISTS comentarios_pagina ON comentarios (pagina, estado, criado);
CREATE INDEX IF NOT EXISTS comentarios_estado ON comentarios (estado, criado);

-- Newsletter e cadastro voluntário de leitores (LGPD: consentimento com data e texto aceito; cancelamento pelo token)
CREATE TABLE IF NOT EXISTS inscritos (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL UNIQUE,
  nome        TEXT,
  editorias   TEXT NOT NULL DEFAULT '',          -- slugs separados por vírgula
  consentimento_em    TEXT NOT NULL DEFAULT (datetime('now')),
  consentimento_texto TEXT NOT NULL,
  origem      TEXT,
  estado      TEXT NOT NULL DEFAULT 'ativo',     -- ativo | cancelado
  saiu_em     TEXT,
  token       TEXT NOT NULL UNIQUE,              -- vai no link de descadastro de cada mensagem
  criado      TEXT NOT NULL DEFAULT (datetime('now')),
  ip_hash     TEXT
);
CREATE INDEX IF NOT EXISTS inscritos_ip ON inscritos (ip_hash, criado);

-- Formulários: comercial (anuncie), evento (divulgue), correção e contato geral
CREATE TABLE IF NOT EXISTS contatos (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo        TEXT NOT NULL,                     -- comercial | evento | correcao | geral
  nome        TEXT NOT NULL,
  email       TEXT NOT NULL,
  empresa     TEXT,
  detalhe     TEXT,                              -- data/cidade do evento ou link da matéria a corrigir
  mensagem    TEXT NOT NULL,
  pagina      TEXT,
  consentimento_texto TEXT,
  estado      TEXT NOT NULL DEFAULT 'novo',      -- novo | respondido | arquivado
  criado      TEXT NOT NULL DEFAULT (datetime('now')),
  ip_hash     TEXT
);
CREATE INDEX IF NOT EXISTS contatos_estado ON contatos (estado, criado);
CREATE INDEX IF NOT EXISTS contatos_ip ON contatos (ip_hash, criado);

-- Métricas dos espaços publicitários: só contadores agregados por dia (nenhum dado de pessoa)
CREATE TABLE IF NOT EXISTS metricas_anuncios (
  dia      TEXT NOT NULL,
  espaco   TEXT NOT NULL,
  editoria TEXT NOT NULL DEFAULT '',
  evento   TEXT NOT NULL,                        -- impressao | clique
  casa     INTEGER NOT NULL DEFAULT 0,           -- 1 = anúncio da casa (Anuncie conosco)
  n        INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (dia, espaco, editoria, evento, casa)
);
