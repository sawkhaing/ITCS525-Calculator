import { useEffect, useState } from "react";
import Button from "./Button";
import { ThemeContext } from "./ThemeContext";

// Same server and endpoints as Lab 6.
const rootAPI = "http://localhost:8000";

async function fetchHistory() {
  const response = await fetch(`${rootAPI}/history`);
  if (!response.ok) throw new Error("Could not load history. Check the calculator server.");
  return response.json();
}

const rows = [
  ["⌫", "AC", "%", "÷"],
  ["7", "8", "9", "×"],
  ["4", "5", "6", "−"],
  ["1", "2", "3", "+"],
  ["±", "0", ".", "="],
];

export default function App() {
  const [input, setInput] = useState("0");
  const [history, setHistory] = useState([]);
  const [theme, setTheme] = useState("light");
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  // Load server history when App mounts, including after a browser refresh.
  useEffect(() => {
    let ignore = false;

    async function loadHistory() {
      try {
        const data = await fetchHistory();
        if (!ignore) setHistory(data);
      } catch {
        if (!ignore) setError("Could not load history. Check the calculator server.");
      } finally {
        if (!ignore) setBusy(false);
      }
    }

    loadHistory();
    // Ignore an old response after unmount (also handles StrictMode's cleanup).
    return () => { ignore = true; };
  }, []);

  async function refreshHistory() {
    try {
      setHistory(await fetchHistory());
    } catch {
      setError("Could not refresh history. Check the calculator server.");
    }
  }

  async function handleClick(value) {
    setError("");
    if (value === "AC") {
      setInput("0");
    } else if (value === "⌫") {
      setInput(input === "Error" || input.length === 1 ? "0" : input.slice(0, -1));
    } else if (value === "±") {
      // Change the sign of the last operand, e.g. 5+3 becomes 5+(-3).
      if (input === "Error") return;
      setInput(input.replace(/\(-\d*\.?\d+\)$|\d*\.?\d+$/, (number) =>
        number.startsWith("(-") ? number.slice(2, -1) : `(-${number})`
      ));
    } else if (value === "=") {
      setBusy(true);
      try {
        const expr = input.replaceAll("÷", "/").replaceAll("×", "*").replaceAll("−", "-");
        const response = await fetch(`${rootAPI}/calculate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ expr }),
        });
        if (!response.ok) throw new Error("Could not calculate. Check the calculator server.");
        const data = await response.json();
        if (!data.ok) throw new Error("Invalid calculation. Press AC and try again.");
        setInput(String(data.result));
      } catch (err) {
        setInput("Error");
        setError(err.message);
      } finally {
        // Wait for POST to finish before reading the updated server history.
        await refreshHistory();
        setBusy(false);
      }
    } else {
      setInput(input === "0" || input === "Error" ? value : input + value);
    }
  }

  async function handleClearHistoryClick() {
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${rootAPI}/history`, { method: "DELETE" });
      if (!response.ok) throw new Error("Could not clear history. Check the calculator server.");
      const data = await response.json();
      if (!data.ok) throw new Error("Could not clear history.");
    } catch (err) {
      setError(err.message);
    } finally {
      // Fetch again rather than assuming that DELETE succeeded.
      await refreshHistory();
      setBusy(false);
    }
  }

  const isDark = theme === "dark";

  return (
    <ThemeContext.Provider value={theme}>
      <main className={`min-h-screen flex flex-col items-center justify-center gap-4 px-4 py-8 ${
        isDark ? "bg-gray-950 text-white" : "bg-gray-100 text-gray-900"
      }`}>
        <h1 className="text-2xl font-bold">Calculator</h1>
        <Button variant="action" onClick={() => setTheme(isDark ? "light" : "dark")}>
          <span className="sr-only">Switch to {isDark ? "light" : "dark"} mode</span>
          <svg
            aria-hidden="true"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {isDark ? (
              <>
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
              </>
            ) : (
              <path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z" />
            )}
          </svg>
        </Button>

        <div className="flex flex-col gap-6 md:flex-row-reverse md:items-start">
          <section aria-label="Calculator" className={`w-80 rounded-4xl p-4 shadow-2xl ${
            isDark ? "bg-gray-800" : "bg-white"
          }`}>
            <div aria-label="Display" aria-live="polite" className="mb-4 overflow-x-auto py-4 text-right text-4xl">
              {input}
            </div>
            {rows.map((row, index) => (
              <div key={index} className="mb-3 grid grid-cols-4 gap-3">
                {row.map((value) => (
                  <Button
                    key={value}
                    onClick={() => handleClick(value)}
                    disabled={busy}
                    variant={["÷", "×", "−", "+", "="].includes(value)
                      ? "operator" : ["⌫", "AC", "%"].includes(value) ? "utility" : "number"}
                  >
                    {value}
                  </Button>
                ))}
              </div>
            ))}
          </section>

          <section aria-label="History" aria-busy={busy} className={`w-80 rounded-2xl p-4 shadow-lg ${
            isDark ? "bg-gray-800" : "bg-white"
          }`}>
            <div className="mb-3 flex items-center justify-between gap-2">
              <h2 className="text-lg font-bold">History</h2>
              <Button variant="action" onClick={handleClearHistoryClick} disabled={busy}>
                Clear
              </Button>
            </div>
            {busy && <p role="status">Loading…</p>}
            {error && <p role="alert" className={`mb-2 ${isDark ? "text-red-300" : "text-red-700"}`}>{error}</p>}
            {!busy && !error && history.length === 0 && <p>No calculations yet.</p>}
            <ul className="max-h-64 space-y-2 overflow-y-auto">
              {history.map((item, index) => (
                <li key={index} className="break-words">
                  {item.expr} = {item.result}
                  <span className="ml-2 text-xs opacity-70">
                    ({new Date(item.timestamp).toLocaleTimeString()})
                  </span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </main>
    </ThemeContext.Provider>
  );
}
