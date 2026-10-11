const { initAuthCreds, BufferJSON, proto } = require('@whiskeysockets/baileys');
const { Pool } = require('pg');

/**
 * PostgreSQL Authentication Adapter for Baileys
 * Persists WhatsApp Web multi-device session credentials and encryption keys
 * into a remote PostgreSQL database (e.g. free Neon or Supabase tier),
 * preventing QR code re-scan upon container restarts on Render free tier.
 */
async function usePostgresAuthState(connectionString, tableName = 'baileys_auth_store') {
    const cleanConnectionString = connectionString.replace(/([?&])channel_binding=[^&]*(&|$)/, '$1').replace(/[?&]$/, '');
    const isLocalhost = cleanConnectionString.includes('localhost') || cleanConnectionString.includes('127.0.0.1');
    const pool = new Pool({
        connectionString: cleanConnectionString,
        ssl: isLocalhost ? false : { rejectUnauthorized: false },
        connectionTimeoutMillis: 10000
    });

    // Create table if not present
    await pool.query(`
        CREATE TABLE IF NOT EXISTS ${tableName} (
            id VARCHAR(255) PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    `);

    const readData = async (id) => {
        try {
            const res = await pool.query(`SELECT value FROM ${tableName} WHERE id = $1`, [id]);
            if (res.rows.length === 0) return null;
            return JSON.parse(res.rows[0].value, BufferJSON.reviver);
        } catch (err) {
            console.error(`Postgres auth read error [${id}]:`, err.message);
            return null;
        }
    };

    const writeData = async (id, value) => {
        try {
            const str = JSON.stringify(value, BufferJSON.replacer);
            await pool.query(`
                INSERT INTO ${tableName} (id, value, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (id) DO UPDATE SET value = $2, updated_at = NOW();
            `, [id, str]);
        } catch (err) {
            console.error(`Postgres auth write error [${id}]:`, err.message);
        }
    };

    const removeData = async (id) => {
        try {
            await pool.query(`DELETE FROM ${tableName} WHERE id = $1`, [id]);
        } catch (err) {
            console.error(`Postgres auth delete error [${id}]:`, err.message);
        }
    };

    // Load or initialize base credentials
    let creds = await readData('creds');
    if (!creds) {
        creds = initAuthCreds();
        await writeData('creds', creds);
    }

    return {
        state: {
            creds,
            keys: {
                get: async (type, ids) => {
                    const data = {};
                    await Promise.all(ids.map(async (id) => {
                        let value = await readData(`${type}-${id}`);
                        if (type === 'app-state-sync-key' && value) {
                            value = proto.Message.AppStateSyncKeyData.fromObject(value);
                        }
                        data[id] = value;
                    }));
                    return data;
                },
                set: async (data) => {
                    const tasks = [];
                    for (const category in data) {
                        for (const id in data[category]) {
                            const value = data[category][id];
                            const key = `${category}-${id}`;
                            tasks.push(value ? writeData(key, value) : removeData(key));
                        }
                    }
                    await Promise.all(tasks);
                }
            }
        },
        saveCreds: () => writeData('creds', creds),
        pool
    };
}

module.exports = { usePostgresAuthState };
