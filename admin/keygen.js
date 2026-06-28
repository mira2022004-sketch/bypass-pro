// Gerador de chaves local
// Uso: node keygen.js <senha_admin> <quantidade>
// Exemplo: node keygen.js minhaSenha 5

const https = require('https');

const [,, password, quantity = '1'] = process.argv;

if (!password) {
  console.log('Uso: node keygen.js <senha_admin> [quantidade]');
  console.log('Exemplo: node keygen.js Admin123 5');
  process.exit(1);
}

const SERVER_URL = process.env.SERVER_URL || 'http://localhost:3000';

function generate(serverUrl) {
  return new Promise((resolve, reject) => {
    const url = new URL('/api/generate', serverUrl);
    const data = JSON.stringify({
      adminPassword: password,
      quantity: parseInt(quantity) || 1
    });

    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          resolve(result);
        } catch (e) {
          reject(new Error('Erro ao parsear resposta: ' + body));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  try {
    const result = await generate(SERVER_URL);
    if (result.keys && result.keys.length > 0) {
      console.log(`\n=== ${result.generated} chave(s) gerada(s) ===\n`);
      result.keys.forEach((key, i) => {
        console.log(`${i + 1}. ${key}`);
      });
      console.log('');
    } else {
      console.log('Erro:', result.message || 'Nenhuma chave gerada.');
    }
  } catch (err) {
    console.error('Erro de conexão:', err.message);
    console.log('\nCertifique-se de que o servidor está rodando e a URL está correta.');
    console.log('Defina a variável SERVER_URL se necessário.');
  }
})();
