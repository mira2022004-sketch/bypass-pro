const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const path = require('path');
const Database = require('better-sqlite3');

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123'; // Mude isso!

app.use(cors());
app.use(express.json());

// Banco de dados
const db = new Database(path.join(__dirname, 'keys.db'));
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL UNIQUE,
    hardware_id TEXT,
    activated INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    activated_at DATETIME
  )
`);

// Gera uma chave de licença
function generateKey() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let key = '';
  for (let i = 0; i < 20; i++) {
    key += chars[crypto.randomInt(chars.length)];
    if (i === 4 || i === 9 || i === 14) key += '-';
  }
  return key;
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Validar / ativar chave
app.post('/api/validate', (req, res) => {
  const { licenseKey, hardwareId } = req.body;

  if (!licenseKey || !hardwareId) {
    return res.status(400).json({ valid: false, message: 'Parâmetros incompletos.' });
  }

  const key = db.prepare('SELECT * FROM keys WHERE license_key = ?').get(licenseKey);

  if (!key) {
    return res.status(404).json({ valid: false, message: 'Chave inválida.' });
  }

  if (key.activated === 1 && key.hardware_id !== hardwareId) {
    // Já ativada em outro hardware
    return res.status(403).json({
      valid: false,
      message: 'Esta chave já está em uso em outro computador.'
    });
  }

  if (key.activated === 1 && key.hardware_id === hardwareId) {
    // Mesma máquina - reativação permitida
    return res.json({
      valid: true,
      message: 'Chave válida (reativada no mesmo hardware).'
    });
  }

  // Primeira ativação
  db.prepare(
    'UPDATE keys SET hardware_id = ?, activated = 1, activated_at = CURRENT_TIMESTAMP WHERE license_key = ?'
  ).run(hardwareId, licenseKey);

  res.json({
    valid: true,
    message: 'Chave ativada com sucesso!'
  });
});

// Gerar novas chaves (protegido por senha)
app.post('/api/generate', (req, res) => {
  const { adminPassword, quantity } = req.body;

  if (adminPassword !== ADMIN_PASSWORD) {
    return res.status(401).json({ message: 'Senha de administrador inválida.' });
  }

  const count = Math.min(quantity || 1, 50);
  const keys = [];

  for (let i = 0; i < count; i++) {
    let licenseKey;
    let attempts = 0;
    do {
      licenseKey = generateKey();
      attempts++;
    } while (db.prepare('SELECT id FROM keys WHERE license_key = ?').get(licenseKey) && attempts < 10);

    if (attempts < 10) {
      db.prepare('INSERT INTO keys (license_key) VALUES (?)').run(licenseKey);
      keys.push(licenseKey);
    }
  }

  res.json({ keys, generated: keys.length });
});

// Listar chaves (protegido por senha)
app.post('/api/list', (req, res) => {
  const { adminPassword } = req.body;
  if (adminPassword !== ADMIN_PASSWORD) {
    return res.status(401).json({ message: 'Senha de administrador inválida.' });
  }
  const keys = db.prepare('SELECT * FROM keys ORDER BY created_at DESC').all();
  res.json({ keys });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
