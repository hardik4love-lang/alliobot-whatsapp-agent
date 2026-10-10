const express = require('express');
const cors = require('cors');
const QRCode = require('qrcode');
const pino = require('pino');
const http = require('http');
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
    downloadMediaMessage
} = require('@whiskeysockets/baileys');
const { usePostgresAuthState } = require('./postgres-auth');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 10000;
const FASTAPI_WEBHOOK_URL = process.env.FASTAPI_WEBHOOK_URL || 'http://localhost:8000/webhook/whatsapp';

let sock = null;
let currentQR = null;
let qrDataURL = null;
let connectionStatus = 'initializing';
let connectedPhone = null;

async function startWhatsApp() {
    let authState;
    const dbUrl = process.env.DATABASE_URL;
    if (dbUrl && (dbUrl.startsWith('postgres://') || dbUrl.startsWith('postgresql://'))) {
        try {
            console.log('Connecting to PostgreSQL for WhatsApp session persistence...');
            authState = await usePostgresAuthState(dbUrl);
            console.log('✅ PostgreSQL WhatsApp Auth Store active! Session will survive container restarts.');
        } catch (dbErr) {
            console.warn('PostgreSQL auth failed, falling back to local file auth:', dbErr.message);
            authState = await useMultiFileAuthState('./auth_session');
        }
    } else {
        authState = await useMultiFileAuthState('./auth_session');
    }
    const { state, saveCreds } = authState;
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        logger: pino({ level: 'silent' }),
        browser: ['AllioBot', 'Chrome', '1.0.0']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            currentQR = qr;
            qrDataURL = await QRCode.toDataURL(qr);
            connectionStatus = 'qr_ready';
            console.log('⚡ New WhatsApp QR Code generated! Open http://localhost:8080 to scan.');
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log(`Connection closed due to ${lastDisconnect?.error}, reconnecting: ${shouldReconnect}`);
            connectionStatus = 'disconnected';
            currentQR = null;
            qrDataURL = null;
            if (shouldReconnect) {
                startWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('🎉 WhatsApp Connected Successfully!');
            connectionStatus = 'connected';
            currentQR = null;
            qrDataURL = null;
            connectedPhone = sock.user?.id ? sock.user.id.split(':')[0] : 'Connected';
        }
    });

    // Handle incoming messages and forward to FastAPI
    sock.ev.on('messages.upsert', async (m) => {
        if (m.type !== 'notify') return;

        for (const msg of m.messages) {
            if (!msg.message || msg.key.fromMe) continue;

            const remoteJid = msg.key.remoteJid;
            let text = msg.message.conversation ||
                         msg.message.extendedTextMessage?.text ||
                         '';
            let audioPayload = null;

            // Handle WhatsApp Audio / Push-To-Talk Voice Notes
            const audioMsg = msg.message.audioMessage;
            if (audioMsg) {
                try {
                    const audioBuffer = await downloadMediaMessage(msg, 'buffer', {});
                    audioPayload = {
                        base64: audioBuffer.toString('base64'),
                        mimetype: audioMsg.mimetype || 'audio/ogg; codecs=opus'
                    };
                    console.log(`🎙️ Voice note received from ${remoteJid} (${audioBuffer.length} bytes)`);
                } catch (audioErr) {
                    console.error('Failed to download voice note audio:', audioErr.message);
                }
            }

            if (!text && !audioPayload) continue;

            console.log(`📩 Inbound message from ${remoteJid}: "${text || '[Voice Note]'}"`);

            // Forward to FastAPI Webhook
            const payload = {
                event: 'messages.upsert',
                data: {
                    key: {
                        remoteJid: remoteJid,
                        fromMe: false,
                        id: msg.key.id
                    },
                    message: {
                        conversation: text
                    },
                    audio: audioPayload
                }
            };

            try {
                const req = http.request(FASTAPI_WEBHOOK_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                req.on('error', (err) => console.log('FastAPI forwarding notice:', err.message));
                req.write(JSON.stringify(payload));
                req.end();
            } catch (err) {
                console.log('Error forwarding message to FastAPI:', err.message);
            }
        }
    });
}

// Web UI showing QR code or connection state
app.get(['/', '/manager'], (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>AllioBot WhatsApp Gateway</title>
        <meta http-equiv="refresh" content="${connectionStatus === 'connected' ? '15' : '3'}">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b141a; color: #e9edef; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .card { background: #111b21; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; max-width: 440px; border: 1px solid #222e35; }
            h1 { font-size: 24px; margin-bottom: 8px; color: #00a884; }
            p { font-size: 14px; color: #8696a0; margin-bottom: 24px; }
            .qr-box { background: white; padding: 16px; border-radius: 12px; display: inline-block; }
            .status-badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; }
            .badge-connected { background: #1f3b2f; color: #25d366; }
            .badge-waiting { background: #3b301f; color: #ffd279; }
            .footer { margin-top: 24px; font-size: 12px; color: #8696a0; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🧄 AllioBot WhatsApp Gateway</h1>
            <p>Direct WhatsApp Session for Surat Garlic Sales</p>

            ${connectionStatus === 'connected' ? `
                <div class="status-badge badge-connected">● Active & Connected</div>
                <div style="font-size: 48px; margin: 20px 0;">✅</div>
                <h2 style="color: #e9edef; font-size: 18px;">Phone: +${connectedPhone}</h2>
                <p style="color: #00a884; font-weight: 500;">AllioBot AI is listening for incoming customer messages!</p>
            ` : qrDataURL ? `
                <div class="status-badge badge-waiting">● Scan QR to Connect</div>
                <div class="qr-box">
                    <img src="${qrDataURL}" alt="WhatsApp QR Code" width="280" height="280" />
                </div>
                <p style="margin-top: 16px;">Open WhatsApp on your phone → <b>Linked Devices</b> → <b>Link a Device</b></p>
            ` : `
                <div class="status-badge badge-waiting">● Generating Session...</div>
                <div style="font-size: 36px; margin: 30px 0;">⏳</div>
                <p>Initializing WhatsApp crypto session. Please wait 5 seconds...</p>
            `}
            <div class="footer">Zero-Docker Native Windows Architecture</div>
        </div>
    </body>
    </html>
    `);
});

// Evolution API compatible send endpoint
app.post(['/message/sendText/:instance', '/message/sendText'], async (req, res) => {
    try {
        const body = req.body;
        const rawNumber = body.number || '';
        const text = body.textMessage?.text || body.text || '';

        if (!sock || connectionStatus !== 'connected') {
            return res.status(503).json({ error: 'WhatsApp is not connected yet' });
        }

        let jid = rawNumber.includes('@') ? rawNumber : `${rawNumber.replace(/\D/g, '')}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text });
        console.log(`📤 Outbound message dispatched to ${jid}`);
        return res.json({ status: 'SUCCESS', jid });
    } catch (e) {
        console.error('Send error:', e);
        return res.status(500).json({ error: e.message });
    }
});

// Evolution API compatible presence endpoint
app.post(['/chat/sendPresence/:instance', '/chat/sendPresence'], async (req, res) => {
    try {
        const rawNumber = req.body.number || '';
        const presence = req.body.presence || 'composing';
        if (sock && connectionStatus === 'connected') {
            const jid = rawNumber.includes('@') ? rawNumber : `${rawNumber.replace(/\D/g, '')}@s.whatsapp.net`;
            await sock.sendPresenceUpdate(presence, jid);
        }
        return res.json({ status: 'SUCCESS' });
    } catch (e) {
        return res.json({ status: 'IGNORED' });
    }
});

// Evolution API compatible group fetch endpoint
app.get(['/group/fetchAllGroups/:instance', '/group/fetchAllGroups'], async (req, res) => {
    try {
        if (!sock || connectionStatus !== 'connected') {
            return res.json([]);
        }
        const groups = await sock.groupFetchAllParticipating();
        const result = Object.values(groups).map(g => ({
            id: g.id,
            subject: g.subject
        }));
        return res.json(result);
    } catch (e) {
        return res.json([]);
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        whatsapp_status: connectionStatus,
        connected_phone: connectedPhone,
        uptime_seconds: Math.floor(process.uptime()),
        timestamp: new Date().toISOString()
    });
});

// Proxy route for triggering scraping via public URL
app.post('/leads/scrape', (req, res) => {
    const proxyReq = http.request('http://localhost:8000/leads/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }, (proxyRes) => {
        proxyRes.pipe(res);
    });
    proxyReq.on('error', (err) => res.status(502).json({ error: 'FastAPI unreachable: ' + err.message }));
    req.pipe(proxyReq);
});

// Proxy route for triggering safe outbound batch
app.post('/leads/dispatch-outbound', (req, res) => {
    const proxyReq = http.request('http://localhost:8000/leads/dispatch-outbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }, (proxyRes) => {
        proxyRes.pipe(res);
    });
    proxyReq.on('error', (err) => res.status(502).json({ error: 'FastAPI unreachable: ' + err.message }));
    req.pipe(proxyReq);
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`====================================================`);
    console.log(`🚀 AllioBot WhatsApp Gateway running on port ${PORT}`);
    console.log(`👉 Open http://localhost:${PORT}/manager in your browser!`);
    console.log(`====================================================`);
    startWhatsApp();
});
