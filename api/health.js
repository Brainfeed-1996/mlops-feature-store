export default function handler(req, res) { res.status(200).json({ status: 'ok', service: 'mlops-feature-store', timestamp: new Date().toISOString() }); }
