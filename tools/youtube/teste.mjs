// Testes offline (sem rede): node --test tools/youtube/teste.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { extrairId, normalizar, escolherFormatos, nomeArquivo, explicarErro, verificar } from "./baixar.mjs";

test("extrairId aceita os formatos de link comuns e recusa o resto", () => {
  for (const u of ["aqz-KE-bpKQ", "https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=10", "https://youtu.be/aqz-KE-bpKQ?si=x",
    "https://m.youtube.com/watch?v=aqz-KE-bpKQ", "https://www.youtube.com/shorts/aqz-KE-bpKQ", "https://www.youtube-nocookie.com/embed/aqz-KE-bpKQ"])
    assert.equal(extrairId(u), "aqz-KE-bpKQ", u);
  for (const u of ["", "https://vimeo.com/123", "https://www.youtube.com/watch?v=curto", "nada"]) assert.equal(extrairId(u), null, u);
});

// formatos no estilo do @distube/ytdl-core e do youtubei.js, como vieram no teste real de 17/11/2026
const DISTUBE = [
  { itag: 18, height: 360, mimeType: 'video/mp4; codecs="avc1.42001E, mp4a.40.2"', hasVideo: true, hasAudio: true, bitrate: 500000 },
  { itag: 401, height: 2160, fps: 60, mimeType: 'video/mp4; codecs="av01.0.13M.08"', hasVideo: true, bitrate: 20e6 },
  { itag: 315, height: 2160, fps: 60, mimeType: 'video/webm; codecs="vp9"', hasVideo: true, bitrate: 25e6 },
  { itag: 299, height: 1080, fps: 60, mimeType: 'video/mp4; codecs="avc1.64002a"', hasVideo: true, bitrate: 6e6 },
  { itag: 399, height: 1080, fps: 60, mimeType: 'video/mp4; codecs="av01.0.09M.08"', hasVideo: true, bitrate: 4e6 },
  { itag: 136, height: 720, fps: 30, mimeType: 'video/mp4; codecs="avc1.4d401f"', hasVideo: true, bitrate: 2e6 },
  { itag: 140, mimeType: 'audio/mp4; codecs="mp4a.40.2"', hasAudio: true, bitrate: 130000 },
  { itag: 251, mimeType: 'audio/webm; codecs="opus"', hasAudio: true, bitrate: 160000 },
];

test("escolhe a maior resolução em MP4 e o melhor áudio M4A", () => {
  const e = escolherFormatos(DISTUBE);
  assert.equal(e.tipo, "adaptativo");
  assert.equal(e.video.itag, 401); // 2160p só existe em AV1 dentro de MP4
  assert.equal(e.audio.itag, 140);
});

test("no empate de altura prefere H.264; --max-altura e --h264 respeitados", () => {
  assert.equal(escolherFormatos(DISTUBE, { maxAltura: 1080 }).video.itag, 299);
  assert.equal(escolherFormatos(DISTUBE, { h264: true }).video.itag, 299);
  assert.equal(escolherFormatos(DISTUBE, { maxAltura: 720 }).video.itag, 136);
});

test("sem adaptativo cai no progressivo com áudio; sem nada devolve null", () => {
  const e = escolherFormatos([DISTUBE[0], DISTUBE[2]]);
  assert.equal(e.tipo, "progressivo");
  assert.equal(e.video.itag, 18);
  assert.equal(escolherFormatos([DISTUBE[2]]), null);
});

test("áudio estéreo vence 5.1 mesmo com bitrate menor", () => {
  const f = [DISTUBE[3], { itag: 258, mimeType: 'audio/mp4; codecs="mp4a.40.2"', hasAudio: true, bitrate: 390000, audioChannels: 6 },
    { itag: 140, mimeType: 'audio/mp4; codecs="mp4a.40.2"', hasAudio: true, bitrate: 130000, audioChannels: 2 }];
  assert.equal(escolherFormatos(f).audio.itag, 140);
});

test("normalizar entende o formato do youtubei.js", () => {
  const n = normalizar({ itag: 137, height: 1080, fps: 30, mime_type: 'video/mp4; codecs="avc1.640028"', has_video: true, has_audio: false, bitrate: 4e6, content_length: "123" });
  assert.deepEqual([n.itag, n.altura, n.mime, n.codec, n.video, n.audio, n.tamanho], [137, 1080, "video/mp4", "avc1.640028", true, false, 123]);
});

test("nomeArquivo remove caracteres proibidos e inclui o id", () => {
  assert.equal(nomeArquivo('A/B: "C"?', "aqz-KE-bpKQ"), "AB C [aqz-KE-bpKQ].mp4");
});

test("explicarErro reconhece os bloqueios conhecidos", () => {
  assert.match(explicarErro("playability LOGIN_REQUIRED"), /anti-robô/);
  assert.match(explicarErro("HTTP 429"), /429/);
  assert.match(explicarErro("media answered HTTP 403"), /diagnostico/);
  assert.match(explicarErro("The server responded with a non 2xx status code"), /diagnostico/);
  assert.equal(explicarErro("outra coisa"), null);
});

const temFfmpeg = spawnSync("ffmpeg", ["-version"]).status === 0;

test("verificar aprova MP4 íntegro com vídeo e áudio e reprova arquivo truncado", { skip: !temFfmpeg }, () => {
  const d = mkdtempSync(path.join(tmpdir(), "yt-teste-"));
  const ok = path.join(d, "ok.mp4");
  const r = spawnSync("ffmpeg", ["-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=25:duration=4",
    "-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-c:v", "libx264", "-c:a", "aac", "-shortest", ok]);
  assert.equal(r.status, 0);
  const v = verificar(ok, 4, { decodificar: true });
  assert.equal(v.video.altura, 240);
  assert.equal(v.audio.codec, "aac");
  assert.throws(() => verificar(ok, 60), /duração/);
  const so = path.join(d, "sem_audio.mp4");
  spawnSync("ffmpeg", ["-y", "-v", "error", "-i", ok, "-an", "-c", "copy", so]);
  assert.throws(() => verificar(so, 4), /sem trilha de áudio/);
  const cortado = path.join(d, "cortado.mp4");
  const bytes = readFileSync(ok);
  writeFileSync(cortado, bytes.subarray(0, Math.floor(bytes.length / 2)));
  assert.throws(() => verificar(cortado, 4, { decodificar: true }));
});
