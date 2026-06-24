const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

app.use(cors());
app.use(express.json());

// ---- Database setup ----
const DATABASE_URL = process.env.DATABASE_URL;

let db;

async function initDatabase() {
  if (DATABASE_URL) {
    // PostgreSQL (Railway)
    const { Pool } = require('pg');
    const pool = new Pool({ connectionString: DATABASE_URL, ssl: { rejectUnauthorized: false } });
    await pool.query(`
      CREATE TABLE IF NOT EXISTS keys (
        id SERIAL PRIMARY KEY,
        license_key TEXT NOT NULL UNIQUE,
        hardware_id TEXT,
        activated INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        activated_at TIMESTAMP
      )
    `);
    db = {
      get: (sql, params) => pool.query(sql, params).then(r => r.rows[0]),
      run: (sql, params) => pool.query(sql, params),
      all: (sql, params) => pool.query(sql, params).then(r => r.rows),
      close: () => pool.end()
    };
    console.log('Conectado ao PostgreSQL');
  } else {
    // SQLite (local)
    const Database = require('better-sqlite3');
    const sdb = new Database(path.join(__dirname, 'keys.db'));
    sdb.pragma('journal_mode = WAL');
    sdb.exec(`
      CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT NOT NULL UNIQUE,
        hardware_id TEXT,
        activated INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        activated_at DATETIME
      )
    `);
    db = {
      get: (sql, params) => sdb.prepare(sql).get(...params),
      run: (sql, params) => sdb.prepare(sql).run(...params),
      all: (sql, params) => sdb.prepare(sql).all(...params),
      close: () => sdb.close()
    };
    console.log('Conectado ao SQLite');
  }
}

function generateKey() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let key = '';
  for (let i = 0; i < 20; i++) {
    key += chars[crypto.randomInt(chars.length)];
    if (i === 4 || i === 9 || i === 14) key += '-';
  }
  return key;
}

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.post('/api/validate', async (req, res) => {
  try {
    const { licenseKey, hardwareId } = req.body;
    if (!licenseKey || !hardwareId) {
      return res.status(400).json({ valid: false, message: 'Parâmetros incompletos.' });
    }
    const key = await db.get('SELECT * FROM keys WHERE license_key = $1', [licenseKey]);
    if (!key) {
      return res.status(404).json({ valid: false, message: 'Chave inválida.' });
    }
    if (key.activated === 1 && key.hardware_id !== hardwareId) {
      return res.status(403).json({ valid: false, message: 'Esta chave já está em uso em outro computador.' });
    }
    if (key.activated === 1 && key.hardware_id === hardwareId) {
      return res.json({ valid: true, message: 'Chave válida (reativada no mesmo hardware).' });
    }
    await db.run(
      'UPDATE keys SET hardware_id = $1, activated = 1, activated_at = CURRENT_TIMESTAMP WHERE license_key = $2',
      [hardwareId, licenseKey]
    );
    res.json({ valid: true, message: 'Chave ativada com sucesso!' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ valid: false, message: 'Erro interno do servidor.' });
  }
});

app.post('/api/generate', async (req, res) => {
  try {
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
      } while ((await db.get('SELECT id FROM keys WHERE license_key = $1', [licenseKey])) && attempts < 10);
      if (attempts < 10) {
        await db.run('INSERT INTO keys (license_key) VALUES ($1)', [licenseKey]);
        keys.push(licenseKey);
      }
    }
    res.json({ keys, generated: keys.length });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Erro interno do servidor.' });
  }
});

app.post('/api/list', async (req, res) => {
  try {
    const { adminPassword } = req.body;
    if (adminPassword !== ADMIN_PASSWORD) {
      return res.status(401).json({ message: 'Senha de administrador inválida.' });
    }
    const keys = await db.all('SELECT * FROM keys ORDER BY created_at DESC');
    res.json({ keys });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Erro interno do servidor.' });
  }
});

initDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
  });
}).catch(err => {
  console.error('Erro ao iniciar banco de dados:', err);
  process.exit(1);
});
