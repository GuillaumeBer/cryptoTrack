import React, { useState, useEffect, useCallback } from 'react';
import { AlertCircle, RefreshCw, TrendingUp, TrendingDown, DollarSign, Percent, AlertTriangle, CheckCircle, Download, Bell, BellOff, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const LendingPage = () => {
    const [walletAddress, setWalletAddress] = useState('');
    const [positions, setPositions] = useState([]);
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [autoRefresh, setAutoRefresh] = useState(false);
    const [notificationsEnabled, setNotificationsEnabled] = useState(false);
    const [showCharts, setShowCharts] = useState(false);
    const [lastNotificationTime, setLastNotificationTime] = useState({});

    const requestNotificationPermission = async () => {
        if (!('Notification' in window)) {
            alert('Ce navigateur ne supporte pas les notifications');
            return false;
        }
        if (Notification.permission === 'granted') return true;
        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return false;
    };

    const sendNotification = useCallback((title, body, positionKey) => {
        if (!notificationsEnabled || Notification.permission !== 'granted') return;

        const now = Date.now();
        const lastTime = lastNotificationTime[positionKey] || 0;
        if (now - lastTime < 5 * 60 * 1000) return; // 5-minute cooldown

        new Notification(title, { body, icon: '🚨', tag: positionKey });
        setLastNotificationTime(prev => ({ ...prev, [positionKey]: now }));
    }, [notificationsEnabled, lastNotificationTime]);

    const saveHistoricalData = (positionsData) => {
        const timestamp = new Date();
        const dataPoint = {
            time: timestamp.toLocaleTimeString(),
            timestamp: timestamp.getTime(),
            totalSupply: positionsData.reduce((sum, p) => sum + p.collateralValue, 0),
            totalBorrow: positionsData.reduce((sum, p) => sum + p.borrowValue, 0),
            avgHealthFactor: positionsData.length > 0 ? positionsData.reduce((sum, p) => sum + (p.healthFactor || 0), 0) / positionsData.length : 0,
        };
        setHistoricalData(prev => [...prev, dataPoint].slice(-50));
    };

    const fetchPositions = useCallback(async () => {
        if (!walletAddress) {
            setError('Veuillez entrer une adresse de portefeuille Solana.');
            return;
        }
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`http://localhost:8000/api/jupiter-lend-positions/${walletAddress}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erreur lors de la récupération des positions.');
            }

            if (data.length === 0) {
                setError('Aucune position de prêt trouvée pour cette adresse.');
            }

            setPositions(data);
            saveHistoricalData(data);
            setLastUpdate(new Date());

            data.forEach(pos => {
                const posKey = `${pos.collateral}-${pos.borrowed}`;
                if (pos.riskLevel === 'critical') {
                    sendNotification('🚨 ALERTE CRITIQUE!', `Position ${pos.collateral}/${pos.borrowed}: Health Factor ${pos.healthFactor?.toFixed(2)} - Risque de liquidation!`, posKey);
                } else if (pos.riskLevel === 'risky') {
                    sendNotification('⚠️ Alerte Position', `Position ${pos.collateral}/${pos.borrowed}: Health Factor ${pos.healthFactor?.toFixed(2)} - Position à surveiller.`, posKey);
                }
            });

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [walletAddress, sendNotification]);

    useEffect(() => {
        let interval;
        if (autoRefresh && walletAddress) {
            interval = setInterval(fetchPositions, 60000);
        }
        return () => clearInterval(interval);
    }, [autoRefresh, walletAddress, fetchPositions]);

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            fetchPositions();
        }
    };

    const exportToCSV = () => {
        const headers = ['Timestamp', 'Collateral', 'Collateral Value', 'Borrowed', 'Borrow Value', 'LTV', 'Health Factor', 'Risk Level'];
        const rows = positions.map(pos => [
            lastUpdate?.toISOString() || '',
            pos.collateral,
            pos.collateralValue?.toFixed(2),
            pos.borrowed,
            pos.borrowValue?.toFixed(2),
            pos.ratio?.toFixed(2),
            pos.healthFactor?.toFixed(3),
            pos.riskLevel
        ]);
        const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `jupiter_lend_positions_${Date.now()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const toggleNotifications = async () => {
        if (!notificationsEnabled) {
            const granted = await requestNotificationPermission();
            if (granted) {
                setNotificationsEnabled(true);
                new Notification('Notifications activées', { body: 'Vous recevrez des alertes pour vos positions à risque.', icon: '🔔' });
            }
        } else {
            setNotificationsEnabled(false);
        }
    };

    const getRiskColor = (riskLevel) => {
        const styles = {
            risky: 'text-yellow-400 bg-yellow-400/10',
            safe: 'text-green-400 bg-green-400/10',
            critical: 'text-red-400 bg-red-400/10',
        };
        return styles[riskLevel] || 'text-gray-400 bg-gray-400/10';
    };

    const getRiskBorderColor = (riskLevel) => {
        const styles = {
            risky: 'border-yellow-500/30',
            safe: 'border-green-500/30',
            critical: 'border-red-500/30',
        };
        return styles[riskLevel] || 'border-gray-500/30';
    };

    const getRiskIcon = (riskLevel) => {
        const icons = {
            critical: <AlertTriangle className="w-4 h-4" />,
            risky: <AlertCircle className="w-4 h-4" />,
            safe: <CheckCircle className="w-4 h-4" />,
        };
        return icons[riskLevel] || null;
    };

    const totalSupply = positions.reduce((sum, p) => sum + p.collateralValue, 0);
    const totalBorrow = positions.reduce((sum, p) => sum + p.borrowValue, 0);
    const avgHealthFactor = positions.length > 0 ? positions.reduce((sum, p) => sum + (p.healthFactor || 0), 0) / positions.length : 0;

    return (
        <div className="min-h-screen bg-slate-900 text-white p-6 w-full">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                Jupiter Lend Monitor
                            </h1>
                            <p className="text-gray-400 text-sm font-mono">
                                Suivi de portefeuille de prêt
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <button onClick={toggleNotifications} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${notificationsEnabled ? 'bg-green-600 hover:bg-green-700' : 'bg-slate-700 hover:bg-slate-600'}`} title={notificationsEnabled ? 'Désactiver les notifications' : 'Activer les notifications'}>
                                {notificationsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                                <span className="text-sm">Alertes</span>
                            </button>
                            <button onClick={() => setShowCharts(!showCharts)} className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${showCharts ? 'bg-purple-600 hover:bg-purple-700' : 'bg-slate-700 hover:bg-slate-600'}`}>
                                <BarChart3 className="w-4 h-4" />
                                <span className="text-sm">Graphiques</span>
                            </button>
                            <button onClick={exportToCSV} disabled={positions.length === 0} className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded-lg transition-colors" title="Exporter en CSV">
                                <Download className="w-4 h-4" />
                                <span className="text-sm">Export CSV</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mb-6 bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-4">
                    <div className="flex items-center gap-4">
                        <input
                            type="text"
                            value={walletAddress}
                            onChange={(e) => setWalletAddress(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Entrez l'adresse du portefeuille Solana ou 'DEMO'"
                            className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
                        />
                        <button onClick={fetchPositions} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 rounded-lg transition-colors">
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            {loading ? 'Recherche...' : 'Rechercher'}
                        </button>
                    </div>
                </div>

                {showCharts && historicalData.length > 1 && (
                    <div className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                            <h3 className="text-lg font-semibold mb-4">Évolution Supply vs Borrow</h3>
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={historicalData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
                                    <YAxis stroke="#9CA3AF" fontSize={12} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }} labelStyle={{ color: '#9CA3AF' }} />
                                    <Legend />
                                    <Line type="monotone" dataKey="totalSupply" stroke="#10B981" name="Supply ($)" strokeWidth={2} />
                                    <Line type="monotone" dataKey="totalBorrow" stroke="#EF4444" name="Borrow ($)" strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                            <h3 className="text-lg font-semibold mb-4">Health Factor Moyen</h3>
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={historicalData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
                                    <YAxis stroke="#9CA3AF" fontSize={12} domain={[0, 'auto']} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }} labelStyle={{ color: '#9CA3AF' }} />
                                    <Legend />
                                    <Line type="monotone" dataKey="avgHealthFactor" stroke="#A855F7" name="Health Factor" strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    {/* Summary Cards */}
                    <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-2"><span className="text-gray-400 text-sm">Total Supply</span><TrendingUp className="w-5 h-5 text-green-400" /></div>
                        <div className="text-3xl font-bold text-green-400">${totalSupply.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    </div>
                    <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-2"><span className="text-gray-400 text-sm">Total Borrow</span><TrendingDown className="w-5 h-5 text-red-400" /></div>
                        <div className="text-3xl font-bold text-red-400">${totalBorrow.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                    </div>
                    <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-2"><span className="text-gray-400 text-sm">Utilization</span><Percent className="w-5 h-5 text-blue-400" /></div>
                        <div className="text-3xl font-bold text-blue-400">{totalSupply > 0 ? ((totalBorrow / totalSupply) * 100).toFixed(2) : '0.00'}%</div>
                    </div>
                    <div className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-2"><span className="text-gray-400 text-sm">Avg Health Factor</span><DollarSign className="w-5 h-5 text-purple-400" /></div>
                        <div className={`text-3xl font-bold ${avgHealthFactor < 1.2 ? 'text-red-400' : avgHealthFactor < 1.5 ? 'text-yellow-400' : 'text-green-400'}`}>{avgHealthFactor > 0 ? avgHealthFactor.toFixed(2) : 'N/A'}</div>
                    </div>
                </div>

                <div className="flex items-center justify-between mb-6">
                    <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} className="w-4 h-4 rounded" /><span className="text-sm text-gray-300">Auto-refresh (1min)</span></label>
                    {lastUpdate && (<div className="text-sm text-gray-400">Dernière mise à jour: {lastUpdate.toLocaleTimeString()}</div>)}
                </div>

                {error && (<div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">{error}</div>)}

                {positions.length === 0 && !loading && (
                  <div className="text-center py-12 bg-slate-800/30 rounded-xl border border-slate-700">
                    <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-gray-400">Aucune position trouvée pour cette adresse.</p>
                  </div>
                )}

                <div className="space-y-4">
                    {positions.map((position, index) => (
                        <div key={index} className={`bg-slate-800/50 backdrop-blur border ${getRiskBorderColor(position.riskLevel)} rounded-xl p-6 hover:border-purple-500/50 transition-colors`}>
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div>
                                        <div className="text-xl font-bold">{position.collateral} → {position.borrowed}</div>
                                        <div className="text-gray-400 text-sm">{position.collateralAmount?.toLocaleString(undefined, { maximumFractionDigits: 4 })} {position.collateral} supplied</div>
                                    </div>
                                </div>
                                <div className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2 ${getRiskColor(position.riskLevel)}`}>
                                    {getRiskIcon(position.riskLevel)}
                                    {position.riskLevel?.toUpperCase()}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                                <div><div className="text-gray-400 text-xs mb-1">Valeur Collatéral</div><div className="text-lg font-semibold text-green-400">${position.collateralValue?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div></div>
                                <div><div className="text-gray-400 text-xs mb-1">Montant Emprunté</div><div className="text-lg font-semibold text-red-400">${position.borrowValue?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div></div>
                                <div><div className="text-gray-400 text-xs mb-1">Taux Supply</div><div className="text-lg font-semibold text-green-400">{position.supplyRate?.toFixed(2)}%</div></div>
                                <div><div className="text-gray-400 text-xs mb-1">Taux Borrow</div><div className="text-lg font-semibold text-blue-400">{position.borrowRate?.toFixed(2)}%</div></div>
                            </div>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-gray-400">Ratio d'Utilisation</span>
                                        <span className={position.ratio > 70 ? 'text-red-400 font-bold' : position.ratio > 60 ? 'text-yellow-400' : 'text-gray-300'}>{position.ratio?.toFixed(2)}% / {position.liquidationThreshold}%</span>
                                    </div>
                                    <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                                        <div className={`h-full transition-all ${position.ratio > 75 ? 'bg-red-500' : position.ratio > 65 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${Math.min(position.ratio, 100)}%` }} />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-gray-400">Health Factor</span>
                                        <span className={position.healthFactor < 1.2 ? 'text-red-400 font-bold' : position.healthFactor < 1.5 ? 'text-yellow-400' : 'text-green-400'}>{position.healthFactor > 100 ? '∞' : position.healthFactor?.toFixed(3)}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default LendingPage;