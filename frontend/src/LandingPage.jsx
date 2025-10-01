import React from 'react';
import { TrendingUp, Activity } from 'lucide-react';

const LandingPage = ({ setView }) => {
    return (
        <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-6">
            <div className="text-center mb-12">
                <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Crypto Dashboard
                </h1>
                <p className="text-gray-400 text-lg">
                    Your central hub for crypto tools.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
                {/* Card for Price Checker */}
                <div
                    className="bg-slate-800/50 backdrop-blur border border-purple-500/20 rounded-xl p-8 hover:border-purple-500/50 transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
                    onClick={() => setView('priceChecker')}
                >
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-purple-500/10 rounded-lg">
                            <TrendingUp className="w-8 h-8 text-purple-400" />
                        </div>
                        <h2 className="text-2xl font-bold">Crypto Price Checker</h2>
                    </div>
                    <p className="text-gray-400">
                        Check real-time prices for thousands of cryptocurrencies against USDC. Fast and reliable data from top exchanges.
                    </p>
                </div>

                {/* Card for Jupiter Lending */}
                <div
                    className="bg-slate-800/50 backdrop-blur border border-pink-500/20 rounded-xl p-8 hover:border-pink-500/50 transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
                    onClick={() => setView('lending')}
                >
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-pink-500/10 rounded-lg">
                            <Activity className="w-8 h-8 text-pink-400" />
                        </div>
                        <h2 className="text-2xl font-bold">Jupiter Lend Monitor</h2>
                    </div>
                    <p className="text-gray-400">
                        Monitor your Jupiter lending and borrowing positions to avoid liquidation. Keep track of your portfolio's health.
                    </p>
                </div>
            </div>

            <div className="mt-16 text-center text-gray-500">
                <p>Select an option to begin.</p>
            </div>
        </div>
    );
};

export default LandingPage;