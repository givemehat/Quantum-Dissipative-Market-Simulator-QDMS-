import { useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart 
} from 'recharts';
import { Activity, Zap, Play, AlertTriangle, ShieldCheck, Database } from 'lucide-react';
import './index.css';

interface SimulationResult {
  status: string;
  config: {
    num_assets: number;
    shock_intensity: number;
    time_steps: number;
  };
  result: {
    status: string;
    regime_prediction: string;
    ohlcv_data: any[];
  };
}

function App() {
  const [numAssets, setNumAssets] = useState(4);
  const [shockIntensity, setShockIntensity] = useState(0.5);
  const [timeSteps, setTimeSteps] = useState(50);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  const runSimulation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          num_assets: numAssets,
          shock_intensity: shockIntensity,
          time_steps: timeSteps,
        }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error running simulation", error);
      alert("Failed to connect to the simulation backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const isCrash = result?.result?.regime_prediction.includes('Crash');

  return (
    <div className="dashboard-container">
      <header>
        <div className="brand">
          <Activity size={32} />
          <h1>Quantum-Dissipative Market Simulator</h1>
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--success)', fontSize: '14px', fontWeight: 500 }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', display: 'inline-block' }}></span>
            API Connected
          </div>
        </div>
      </header>

      <aside className="glass-panel controls-sidebar">
        <h2 style={{ fontSize: '18px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={20} className="glow-text-cyan" />
          Simulation Parameters
        </h2>
        
        <div className="control-group">
          <label>Number of Assets (Hilbert Space Dim: 2^n)</label>
          <input 
            type="number" 
            value={numAssets} 
            onChange={(e) => setNumAssets(Number(e.target.value))}
            min="2" max="10"
          />
        </div>

        <div className="control-group">
          <label>Shock Intensity (Decoherence Rate)</label>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input 
              type="range" 
              value={shockIntensity} 
              onChange={(e) => setShockIntensity(Number(e.target.value))}
              min="0" max="2" step="0.1"
            />
            <span style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-primary)' }}>{shockIntensity}</span>
          </div>
        </div>

        <div className="control-group">
          <label>Time Steps (Evolution Horizon)</label>
          <input 
            type="number" 
            value={timeSteps} 
            onChange={(e) => setTimeSteps(Number(e.target.value))}
            min="10" max="200"
          />
        </div>

        <button 
          className="run-btn" 
          onClick={runSimulation}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Zap size={20} className="spinner" />
              Simulating...
            </>
          ) : (
            <>
              <Play size={20} />
              Run Quantum Engine
            </>
          )}
        </button>

        {result && (
          <div style={{ marginTop: 'auto', paddingTop: '24px', borderTop: '1px solid var(--panel-border)' }}>
            <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>Execution Metrics</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Status</span>
              <span style={{ color: 'var(--success)' }}>{result.result.status}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Data Points</span>
              <span style={{ fontFamily: 'JetBrains Mono' }}>{result.result.ohlcv_data.length}</span>
            </div>
          </div>
        )}
      </aside>

      <main className="main-content">
        {result ? (
          <>
            <div className={`glass-panel status-banner ${isCrash ? 'crash' : 'stable'}`}>
              {isCrash ? <AlertTriangle size={28} color="var(--danger)" /> : <ShieldCheck size={28} color="var(--success)" />}
              <div>
                <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>XGBoost ML Prediction</div>
                <div style={{ color: isCrash ? 'var(--danger)' : 'var(--success)' }}>
                  {result.result.regime_prediction}
                </div>
              </div>
            </div>

            <div className="glass-panel chart-container">
              <h3>Market Trajectory (Asset Value vs Time)</h3>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={result.result.ohlcv_data}>
                  <defs>
                    <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={isCrash ? "var(--danger)" : "var(--accent-cyan)"} stopOpacity={0.8}/>
                      <stop offset="95%" stopColor={isCrash ? "var(--danger)" : "var(--accent-cyan)"} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis 
                    dataKey="time" 
                    tickFormatter={(val) => Number(val).toFixed(1)}
                    stroke="var(--panel-border)"
                  />
                  <YAxis 
                    domain={['auto', 'auto']} 
                    stroke="var(--panel-border)"
                    tickFormatter={(val) => `$${val.toFixed(0)}`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--bg-dark)', 
                      border: '1px solid var(--panel-border)',
                      borderRadius: '8px'
                    }}
                    labelStyle={{ color: 'var(--text-secondary)' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="close" 
                    stroke={isCrash ? "var(--danger)" : "var(--accent-cyan)"} 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorClose)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <Activity size={64} style={{ opacity: 0.2, marginBottom: '24px' }} />
            <h2 style={{ fontSize: '24px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '8px' }}>Waiting for Data</h2>
            <p>Configure parameters on the left and run the Quantum Engine to generate the market simulation.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
