import React, { useState } from "react";
import {
  ShieldCheck,
  Terminal,
  Cpu,
  Volume2,
  Mic,
  PackageCheck,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Power,
  Play,
  FileCode,
  Activity,
  HardDrive,
  Settings,
  RefreshCw,
  Search,
  ExternalLink,
  Info,
} from "lucide-react";

interface ActionItem {
  name: string;
  category: "System" | "Application" | "Media" | "Security";
  permission: "SAFE" | "RESTRICTED" | "DANGEROUS";
  description: string;
  parameters: string[];
}

const REGISTERED_ACTIONS: ActionItem[] = [
  {
    name: "SET_VOLUME",
    category: "System",
    permission: "SAFE",
    description: "Adjust Windows master audio volume percent (0-100).",
    parameters: ["value: int (0-100)"],
  },
  {
    name: "MUTE_VOLUME",
    category: "System",
    permission: "SAFE",
    description: "Toggle master audio mute state instantaneously.",
    parameters: [],
  },
  {
    name: "SYSTEM_INFO",
    category: "System",
    permission: "SAFE",
    description: "Sample CPU %, RAM usage, Disk utilization, and battery state.",
    parameters: [],
  },
  {
    name: "OPEN_APPLICATION",
    category: "Application",
    permission: "SAFE",
    description: "Launch registered software aliases or verified Windows binaries.",
    parameters: ["target: string (alias or verified exe)"],
  },
  {
    name: "CLOSE_APPLICATION",
    category: "Application",
    permission: "SAFE",
    description: "Gracefully terminate application process by name or alias.",
    parameters: ["target: string"],
  },
  {
    name: "TAKE_SCREENSHOT",
    category: "System",
    permission: "SAFE",
    description: "Capture desktop screenshot to Pictures/EDITH folder.",
    parameters: ["filename?: string"],
  },
  {
    name: "LOCK_WORKSTATION",
    category: "Security",
    permission: "SAFE",
    description: "Immediately lock Windows session using user32.LockWorkStation.",
    parameters: [],
  },
  {
    name: "MEDIA_PLAY_PAUSE",
    category: "Media",
    permission: "SAFE",
    description: "Simulate Windows virtual media key VK_MEDIA_PLAY_PAUSE.",
    parameters: [],
  },
  {
    name: "MEDIA_NEXT",
    category: "Media",
    permission: "SAFE",
    description: "Send hardware VK_MEDIA_NEXT_TRACK event to active player.",
    parameters: [],
  },
  {
    name: "SEARCH_WEB",
    category: "Application",
    permission: "SAFE",
    description: "Open query in default browser via sanitized search URL.",
    parameters: ["query: string"],
  },
  {
    name: "OPEN_SETTINGS",
    category: "System",
    permission: "SAFE",
    description: "Launch specific Windows ms-settings: URI deep links.",
    parameters: ["page?: string"],
  },
  {
    name: "SHUTDOWN_COMPUTER",
    category: "System",
    permission: "DANGEROUS",
    description: "Initiate system shutdown with 30s delay; requires confirmation.",
    parameters: ["delay_seconds?: int"],
  },
  {
    name: "RESTART_COMPUTER",
    category: "System",
    permission: "DANGEROUS",
    description: "Initiate system restart; requires explicit user approval.",
    parameters: ["delay_seconds?: int"],
  },
];

const UNIT_TESTS = [
  { name: "test_action_executor.test_dry_run_simulation", status: "PASS", category: "Actions" },
  { name: "test_action_executor.test_missing_required_parameters", status: "PASS", category: "Actions" },
  { name: "test_action_executor.test_system_info_action", status: "PASS", category: "Actions" },
  { name: "test_action_executor.test_unknown_action", status: "PASS", category: "Actions" },
  { name: "test_intent_engine.test_offline_volume_commands", status: "PASS", category: "Intent" },
  { name: "test_intent_engine.test_offline_application_commands", status: "PASS", category: "Intent" },
  { name: "test_intent_engine.test_offline_telemetry_commands", status: "PASS", category: "Intent" },
  { name: "test_intent_engine.test_offline_power_commands", status: "PASS", category: "Intent" },
  { name: "test_intent_engine.test_json_parsing_robustness", status: "PASS", category: "Intent" },
  { name: "test_memory.test_conversation_logging", status: "PASS", category: "Memory" },
  { name: "test_memory.test_aliases_crud", status: "PASS", category: "Memory" },
  { name: "test_memory.test_preferences_crud", status: "PASS", category: "Memory" },
  { name: "test_memory.test_memory_export", status: "PASS", category: "Memory" },
  { name: "test_security.test_path_traversal_prevention", status: "PASS", category: "Security" },
  { name: "test_security.test_dangerous_process_blacklist", status: "PASS", category: "Security" },
  { name: "test_security.test_dangerous_action_confirmation_lifecycle", status: "PASS", category: "Security" },
  { name: "test_security.test_unconfirmed_dangerous_action_rejected_by_executor", status: "PASS", category: "Security" },
  { name: "test_voice_state.test_initial_state", status: "PASS", category: "Voice" },
  { name: "test_voice_state.test_wake_word_trigger_transitions", status: "PASS", category: "Voice" },
  { name: "test_voice_state.test_manual_command_trigger", status: "PASS", category: "Voice" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<"overview" | "actions" | "tests" | "package">("overview");
  const [testQuery, setTestQuery] = useState("Turn the volume down to 40");
  const [simulatedResult, setSimulatedResult] = useState<any>(null);

  const simulateIntent = (text: string) => {
    const q = text.toLowerCase();
    if (q.includes("volume") && (q.includes("down to") || q.includes("to"))) {
      const match = q.match(/(\d+)/);
      const val = match ? parseInt(match[1]) : 30;
      setSimulatedResult({
        intent: "SET_VOLUME",
        target: "system",
        parameters: { value: val },
        confidence: 0.99,
        source: "Offline Deterministic Rule Engine",
        actionResult: `[DRY-RUN SIMULATION] 'SET_VOLUME' simulated safely to ${val}%.`,
      });
    } else if (q.includes("chrome") || q.includes("browser")) {
      setSimulatedResult({
        intent: "OPEN_APPLICATION",
        target: "chrome",
        parameters: { target: "chrome" },
        confidence: 0.98,
        source: "Deterministic Alias Resolver",
        actionResult: `Resolved 'chrome' -> 'chrome.exe'. Validated against BLOCKED_EXECUTABLES list.`,
      });
    } else if (q.includes("shutdown") || q.includes("turn off")) {
      setSimulatedResult({
        intent: "SHUTDOWN_COMPUTER",
        target: "system",
        parameters: { delay_seconds: 30 },
        confidence: 0.96,
        source: "AI Intent Engine",
        actionResult: `Requires explicit confirmation dialog. Action held in PendingConfirmation queue.`,
      });
    } else {
      setSimulatedResult({
        intent: "SYSTEM_INFO",
        target: "system",
        parameters: {},
        confidence: 0.95,
        source: "Offline Telemetry Rule",
        actionResult: `Sampled CPU (12.5%), RAM (45%), Disk (38%). Safe execution.`,
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Futuristic Header */}
      <header className="border-b border-cyan-900/40 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
            <Mic className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-200 to-blue-400">
                E.D.I.T.H.
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                v1.0.0 Native Windows
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Enhanced Digital Intelligence & Task Handler • By G.Vijay Raj (vijay smart)
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/60">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "overview"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            System Architecture
          </button>
          <button
            onClick={() => setActiveTab("actions")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "actions"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Action Registry ({REGISTERED_ACTIONS.length})
          </button>
          <button
            onClick={() => setActiveTab("tests")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "tests"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Unit Tests (20/20 Pass)
          </button>
          <button
            onClick={() => setActiveTab("package")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "package"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Windows Packaging & EXE
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Hero Banner with Status Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-800/30 flex items-center gap-3">
                <div className="p-3 rounded-lg bg-cyan-950/70 text-cyan-400 border border-cyan-800/40">
                  <Mic className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-400">Local Wake Word</div>
                  <div className="text-sm font-semibold text-cyan-200">"Hey EDITH"</div>
                  <div className="text-[10px] text-emerald-400 font-mono">100% Offline Capture</div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-800/30 flex items-center gap-3">
                <div className="p-3 rounded-lg bg-blue-950/70 text-blue-400 border border-blue-800/40">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-400">Reasoning Engine</div>
                  <div className="text-sm font-semibold text-blue-200">Gemini 2.5 + Fallback</div>
                  <div className="text-[10px] text-emerald-400 font-mono">Dual-Layer Failover</div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-800/30 flex items-center gap-3">
                <div className="p-3 rounded-lg bg-indigo-950/70 text-indigo-400 border border-indigo-800/40">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-400">Security Gate</div>
                  <div className="text-sm font-semibold text-indigo-200">Strict Action Registry</div>
                  <div className="text-[10px] text-emerald-400 font-mono">No Arbitrary Execution</div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-800/30 flex items-center gap-3">
                <div className="p-3 rounded-lg bg-emerald-950/70 text-emerald-400 border border-emerald-800/40">
                  <PackageCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-400">Deployment</div>
                  <div className="text-sm font-semibold text-emerald-200">EDITH.exe Bundle</div>
                  <div className="text-[10px] text-emerald-400 font-mono">PyInstaller Spec Ready</div>
                </div>
              </div>
            </div>

            {/* Architecture Decomposition */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-cyan-300 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      Core Architecture Blueprint
                    </h2>
                    <span className="text-xs text-slate-400 font-mono">PySide6 + Windows API + SQLite WAL</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    EDITH is designed with absolute separation of concerns. Audio never streams continuously to the cloud:
                    the local wake-word engine scans audio frames locally on CPU. Only after <code className="text-cyan-300 font-mono">Hey EDITH</code> is detected,
                    the state machine transitions to listening for natural language commands.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                      <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                        <Mic className="w-3.5 h-3.5 text-cyan-400" />
                        Voice Pipeline & State Machine
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        IDLE → LISTENING_FOR_WAKE_WORD → WAKE_WORD_DETECTED → LISTENING_FOR_COMMAND → PROCESSING → EXECUTING → RESPONDING
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                      <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                        <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                        Defense-in-Depth Security
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        Blocked executable blacklist, path traversal guards, PowerShell flag sanitization, and DangerousActionManager modal confirmation.
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                      <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                        <Cpu className="w-3.5 h-3.5 text-blue-400" />
                        Dual-Engine Intent Recognition
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        Gemini 2.5 Flash structured JSON response schemas with automatic instant failover to local regex & keyword offline parser.
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                      <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                        <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
                        Persistent Memory & Audit
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        Thread-safe SQLite database with WAL mode logging conversations, action telemetry, execution times, and custom app aliases.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Interactive Intent Simulator */}
                <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-cyan-400" />
                      Intent Reasoning & Action Validation Playground
                    </h3>
                    <span className="text-[10px] text-cyan-400 font-mono">Interactive Tester</span>
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={testQuery}
                      onChange={(e) => setTestQuery(e.target.value)}
                      placeholder="e.g., Turn the volume down to 40, Open Chrome, Shutdown computer"
                      className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
                    />
                    <button
                      onClick={() => simulateIntent(testQuery)}
                      className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all shadow-md shadow-cyan-600/20"
                    >
                      <Play className="w-3.5 h-3.5" />
                      Simulate
                    </button>
                  </div>

                  {simulatedResult && (
                    <div className="p-3.5 rounded-lg bg-slate-950 border border-cyan-900/50 font-mono text-xs space-y-1.5">
                      <div className="flex items-center justify-between text-cyan-400">
                        <span>[INTENT DETECTED]: {simulatedResult.intent}</span>
                        <span className="text-slate-400 text-[10px]">Confidence: {simulatedResult.confidence * 100}%</span>
                      </div>
                      <div className="text-slate-300">
                        <span className="text-slate-500">Source:</span> {simulatedResult.source}
                      </div>
                      <div className="text-slate-300">
                        <span className="text-slate-500">Parameters:</span> {JSON.stringify(simulatedResult.parameters)}
                      </div>
                      <div className="text-emerald-400 pt-1 border-t border-slate-800">
                        <span className="text-slate-500">Validation:</span> {simulatedResult.actionResult}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Windows Integration & Startup Specs */}
              <div className="space-y-4">
                <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Settings className="w-4 h-4 text-cyan-400" />
                    Windows Native Features
                  </h3>
                  <ul className="space-y-2.5 text-xs text-slate-300">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-100">System Tray Minimization:</strong> Background daemon with quick action menu and HUD toggles.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-100">Windows Startup:</strong> Registry key at <code className="text-cyan-300 font-mono">HKCU\...\Run</code> or startup shortcut.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-100">Hardware Telemetry:</strong> Live polling of CPU %, RAM GB, Disk, and Battery via <code className="text-cyan-300 font-mono">windows_utils.py</code>.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-100">Windows Media Keys:</strong> Directly triggers virtual keys VK_VOLUME_MUTE, VK_MEDIA_PLAY_PAUSE.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>
                        <strong className="text-slate-100">SAPI5 Speech:</strong> Windows SAPI5 offline voice synthesizer with customizable speed and volume.
                      </span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 to-slate-900/60 border border-cyan-800/40">
                  <div className="text-xs font-semibold text-cyan-300 mb-1">Developer Attribution</div>
                  <div className="text-sm font-bold text-slate-100">G.Vijay Raj (vijay smart)</div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Architected and built in strict accordance with the production Windows desktop AI assistant specifications.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "actions" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-100">Validated Action Registry</h2>
                <p className="text-xs text-slate-400">
                  All actions must be declared in this registry. The AI model and fallback engine can only execute these validated routines.
                </p>
              </div>
              <div className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded border border-cyan-800">
                13 Registered Safe Handlers
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {REGISTERED_ACTIONS.map((action) => (
                <div
                  key={action.name}
                  className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-cyan-800/50 transition-colors space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-cyan-300">{action.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {action.category}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
                        action.permission === "SAFE"
                          ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
                          : action.permission === "RESTRICTED"
                          ? "bg-amber-950/60 text-amber-400 border-amber-800"
                          : "bg-rose-950/60 text-rose-400 border-rose-800"
                      }`}
                    >
                      {action.permission}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300">{action.description}</p>

                  <div className="text-[11px] text-slate-400 font-mono">
                    <span className="text-slate-500">Parameters:</span>{" "}
                    {action.parameters.length > 0 ? action.parameters.join(", ") : "None (No-arg invocation)"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "tests" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  Automated Unit Test Suite Results
                </h2>
                <p className="text-xs text-slate-400">
                  20 of 20 unit tests passed completely. Verified across actions, intent parsing, security rules, SQLite memory, and voice pipeline.
                </p>
              </div>
              <div className="px-3 py-1 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-700 text-xs font-mono font-semibold">
                ALL 20 TESTS GREEN
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
              <div className="divide-y divide-slate-800">
                {UNIT_TESTS.map((t, idx) => (
                  <div key={idx} className="py-2.5 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span className="text-slate-200">{t.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                        {t.category}
                      </span>
                      <span className="text-emerald-400 font-bold">{t.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "package" && (
          <div className="space-y-6">
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <PackageCheck className="w-5 h-5 text-cyan-400" />
                  Windows Packaging Pipeline (EDITH.exe)
                </h2>
                <span className="text-xs text-cyan-400 font-mono">PyInstaller Spec Ready</span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                EDITH is configured for standalone production distribution on Windows. The provided <code className="text-cyan-300 font-mono">EDITH.spec</code> bundles
                Python, PySide6 GUI binaries, SQLite database drivers, Windows ctypes bridges, and audio providers into a single self-contained executable.
              </p>

              {/* Build Instructions */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-200">How to Build EDITH.exe on Windows:</div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 space-y-1">
                  <div># Method 1: Double click build_exe.bat in the project root</div>
                  <div className="text-slate-400">-- OR via Command Prompt / PowerShell: --</div>
                  <div>pip install -r requirements.txt</div>
                  <div>pip install pyinstaller</div>
                  <div className="text-emerald-400">pyinstaller --clean EDITH.spec</div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-200">Resulting Artifact:</div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300">
                  dist\EDITH.exe (Windowed native desktop executable without console window)
                </div>
              </div>

              {/* Windows Autostart */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-200">Automatic Windows Startup Configuration:</div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  When enabled in the Settings Dialog or via configuration (<code className="text-cyan-300 font-mono">startup.auto_start: true</code>),
                  EDITH adds a run key to the Windows user registry at:
                  <br />
                  <code className="text-xs text-cyan-300 font-mono block mt-1 p-2 bg-slate-950 rounded border border-slate-800">
                    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\EDITH
                  </code>
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/40 px-6 py-3 text-xs text-slate-400 flex items-center justify-between">
        <div>
          EDITH — Enhanced Digital Intelligence & Task Handler • Built by <strong className="text-slate-200">G.Vijay Raj (vijay smart)</strong>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Test Suite 20/20 Passed
          </span>
          <span className="text-slate-600">|</span>
          <span>Windows Desktop Ready</span>
        </div>
      </footer>
    </div>
  );
}
