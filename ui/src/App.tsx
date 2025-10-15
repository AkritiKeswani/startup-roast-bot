import { useRef, useState } from "react";

const API = import.meta.env.VITE_API_BASE as string || "http://localhost:5000";

interface CompanyResult {
  company: {
    name: string;
    website: string;
  };
  roast?: string;
  screenshot_url?: string;
  status: string;
  error_reason?: string;
}

export default function App() {
  const [mode, setMode] = useState<"yc" | "custom">("yc");
  const [batch, setBatch] = useState("F25");
  const [limit, setLimit] = useState(24);
  const [urls, setUrls] = useState("");
  const [style, setStyle] = useState("spicy");
  const [rows, setRows] = useState<CompanyResult[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const addLog = (s: string) => setLog(x => [...x, `${new Date().toLocaleTimeString()}: ${s}`]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    addLog("Copied to clipboard!");
  };

  async function start() {
    if (isRunning) return;
    
    setIsRunning(true);
    setRows([]);
    setLog([]);
    
    const body = mode === "yc"
      ? { 
          source: "yc", 
          yc: { batch: batch || null, limit }, 
          style, 
          max_steps: 6 
        }
      : { 
          source: "custom", 
          custom: { urls: urls.split("\n").filter(Boolean) }, 
          style, 
          max_steps: 6 
        };

    try {
      addLog("Starting roast run...");
      const r = await fetch(`${API}/run`, {
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify(body)
      });
      
      if (!r.ok) {
        throw new Error(`HTTP ${r.status}: ${await r.text()}`);
      }
      
      const j = await r.json();
      addLog(`Run started: ${j.run_id}`);
      
      const wsUrl = `${API.replace(/^http/, "ws")}${j.stream_url}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => addLog("WebSocket connected");
      ws.onmessage = ev => {
        const msg = JSON.parse(ev.data);
        if (msg.company) {
          setRows(x => [msg, ...x]);
          addLog(`Processed: ${msg.company.name}`);
        }
        if (msg.status === "finished") {
          addLog("Run completed!");
          setIsRunning(false);
        }
        if (msg.status === "failed") {
          addLog(`Run failed: ${msg.error_reason || "Unknown error"}`);
          setIsRunning(false);
        }
      };
      ws.onerror = () => addLog("WebSocket error");
      ws.onclose = () => {
        addLog("WebSocket closed");
        setIsRunning(false);
      };
      
    } catch (error) {
      addLog(`Error: ${error instanceof Error ? error.message : String(error)}`);
      setIsRunning(false);
    }
  }

  const stop = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsRunning(false);
    addLog("Run stopped");
  };

  return (
    <div className="mx-auto max-w-6xl p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🔥 Startup Roast Bot</h1>
        <p className="text-gray-600">AI-powered landing page analysis and roasting</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl border p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Configuration</h2>
            
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input 
                    type="radio" 
                    checked={mode === "yc"} 
                    onChange={() => setMode("yc")}
                    className="text-blue-600"
                  />
                  <span className="font-medium">YC Directory</span>
                </label>
                <label className="flex items-center gap-2">
                  <input 
                    type="radio" 
                    checked={mode === "custom"} 
                    onChange={() => setMode("custom")}
                    className="text-blue-600"
                  />
                  <span className="font-medium">Custom URLs</span>
                </label>
              </div>

              {mode === "yc" ? (
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Batch (optional)
                    </label>
                    <input 
                      className="input" 
                      placeholder="e.g. F25, S24" 
                      value={batch} 
                      onChange={e => setBatch(e.target.value)} 
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Limit
                    </label>
                    <input 
                      className="input" 
                      type="number" 
                      value={limit} 
                      onChange={e => setLimit(parseInt(e.target.value || "24"))}
                      min="1"
                      max="100"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    URLs (one per line)
                  </label>
                  <textarea 
                    className="input h-32" 
                    placeholder="https://site1.com&#10;https://site2.com&#10;https://site3.com"
                    value={urls} 
                    onChange={e => setUrls(e.target.value)} 
                  />
                </div>
              )}

              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Roast Style
                  </label>
                  <select 
                    className="input" 
                    value={style} 
                    onChange={e => setStyle(e.target.value)}
                  >
                    <option value="spicy">🌶️ Spicy</option>
                    <option value="kind">😊 Kind</option>
                    <option value="deadpan">😐 Deadpan</option>
                  </select>
                </div>
                <div className="flex items-end">
                  {isRunning ? (
                    <button 
                      onClick={stop}
                      className="w-full px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
                    >
                      Stop Run
                    </button>
                  ) : (
                    <button 
                      onClick={start}
                      className="w-full px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 transition-colors"
                    >
                      🔥 Start Roasting
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border shadow-sm">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">Results</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="p-3 text-left font-medium text-gray-700">Company / Website</th>
                    <th className="p-3 text-left font-medium text-gray-700">Roast</th>
                    <th className="p-3 text-left font-medium text-gray-700">Screenshot</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="p-8 text-center text-gray-500">
                        No results yet. Start a roast run to see companies here.
                      </td>
                    </tr>
                  ) : (
                    rows.map((r, i) => (
                      <tr key={i} className="border-t hover:bg-gray-50">
                        <td className="p-3">
                          <div className="font-medium text-gray-900">{r.company?.name || "—"}</div>
                          <a 
                            className="text-blue-600 hover:underline text-sm" 
                            href={r.company?.website} 
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {r.company?.website}
                          </a>
                        </td>
                        <td className="p-3">
                          {r.roast ? (
                            <div className="space-y-2">
                              <div className="text-gray-800">{r.roast}</div>
                              <button
                                onClick={() => copyToClipboard(r.roast!)}
                                className="text-xs text-blue-600 hover:underline"
                              >
                                Copy
                              </button>
                            </div>
                          ) : r.error_reason ? (
                            <div className="text-red-600 text-sm">{r.error_reason}</div>
                          ) : (
                            <div className="text-gray-400">—</div>
                          )}
                        </td>
                        <td className="p-3">
                          {r.screenshot_url ? (
                            <img 
                              src={r.screenshot_url} 
                              className="h-20 w-32 object-cover rounded border" 
                              alt="Screenshot"
                            />
                          ) : (
                            <div className="text-gray-400">—</div>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-xl border p-4 shadow-sm">
            <div className="font-semibold mb-3 text-gray-900">Status Log</div>
            <pre className="text-xs whitespace-pre-wrap max-h-96 overflow-auto bg-gray-50 p-3 rounded text-gray-700">
              {log.length === 0 ? "No logs yet..." : log.join("\n")}
            </pre>
          </div>
          
          <div className="bg-blue-50 rounded-xl border border-blue-200 p-4">
            <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
            <div className="text-sm text-blue-800 space-y-2">
              <div>
                <strong>YC Mode:</strong>
                <ul className="ml-4 space-y-1">
                  <li>• Scrapes https://www.ycombinator.com/companies</li>
                  <li>• Visits each company's YC profile page</li>
                  <li>• Extracts their actual website URL</li>
                  <li>• Visits the company website</li>
                  <li>• Roasts the landing page</li>
                </ul>
              </div>
              <div>
                <strong>Custom Mode:</strong>
                <ul className="ml-4 space-y-1">
                  <li>• Uses your provided URLs directly</li>
                  <li>• Visits each website</li>
                  <li>• Takes screenshots and extracts data</li>
                  <li>• Generates AI roasts</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
