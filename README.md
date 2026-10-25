# Lab 8 solution: useEffect and useContext

[Lab requirements](https://app.notion.com/p/northanapon/useEffect-and-useContext-236dd5f44b7f806c972fc87f79c81c77)

This solution merges Lab 6's client/server calculator with Lab 7's Tailwind calculator design, then adds history loading and a light/dark theme. Previous lecture examples are left intact.

## Use the same setup

- **Server:** `calculator-server` follows the [OOP refactoring lab](https://app.notion.com/p/northanapon/Apply-OOP-concepts-to-refactor-a-project-236dd5f44b7f80a094f9f5278bae5f24), with inherited schemas, FastAPI dependencies, and separate calculator/history routers. It keeps the earlier server's endpoints and React request/response format. See its [README](calculator-server/README.md) for the structure and tests.
- **Client:** React 19, Vite 7, Tailwind CSS 4, and the same package manifest and lockfile as `lecture-06/calculator-react`.
- **Components:** keep `App.jsx` and `Button.jsx`, adding only `ThemeContext.js`. Use `fetch`, `useState`, `useEffect`, and `useContext`; no additional libraries.

## Run

Open two terminals at the repository root. Use Node.js 22.12+ (or 20.19+) for Vite 7 and Python 3.13 with uv for the calculator server, as in the earlier labs.

Terminal 1 — install dependencies and start the included server:

```sh
cd lecture-08-solution/calculator-server
uv sync --frozen
uv run fastapi dev app/main.py
```

The API runs at `http://localhost:8000`; its documentation is at `http://localhost:8000/docs`.

Terminal 2 — start the solution:

```sh
cd lecture-08-solution/calculator-react
npm ci
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

## Walk through the solution

1. **Merge Labs 6 and 7.** `App.jsx` keeps the input, button rows, expression normalization, and API calls from Lab 6. The rounded panel, four-column grid, circular buttons, and orange operators follow Lab 7. Expressions are evaluated by the existing server.
2. **Fetch on mount.** `useEffect(..., [])` loads `GET /history`. Its cleanup ignores responses from an effect that has already been cleaned up. In development, `StrictMode` may run the effect twice; this is expected.
3. **Fetch after `=`.** The click handler awaits `POST /calculate`, displays the result, and then awaits `GET /history`. The new calculation appears without refreshing the page.
4. **Fetch after Clear.** The handler awaits `DELETE /history` and then fetches `GET /history` again. The UI reflects the server's actual history rather than assuming the deletion worked. Clear affects history; AC resets only the display.
5. **Create context.** `src/ThemeContext.js` exports `createContext("light")` from its own file.
6. **Provide context.** `App` owns the theme state and wraps the UI with `<ThemeContext.Provider value={theme}>`. The toggle changes between `"light"` and `"dark"`.
7. **Consume context.** `Button` calls `useContext(ThemeContext)` and chooses the matching Tailwind classes. Its `variant` prop identifies number, utility, operator, or action styling; the theme comes from context.

The shared `fetchHistory()` function handles the GET request. The effect uses its own cleanup, while the click handlers use `refreshHistory()` to update state. Buttons are disabled while requests are pending so a calculation and history deletion cannot race. Failed requests show an error without falsely clearing existing history.

`%` uses the earlier server's percentage rules, including `100 − 6% = 94`. `±` toggles the sign of the final numeric operand, for example `5+3` becomes `5+(-3)`. Calculation errors can be reset with AC or by entering a new number.

## Verify

```sh
cd lecture-08-solution/calculator-react
npm run lint
npm run build
```

With both servers running:

| Action | Expected result |
| --- | --- |
| Calculate `7 × 8 =` | Display shows `56`; history contains `7*8 = 56`. |
| Refresh the browser | Existing server history loads automatically. |
| Calculate `100 − 6% =` | Display shows `94`; history updates. |
| Click Clear | History is deleted on the server and fetched again; the empty message appears. |
| Refresh after Clear | History remains empty. |
| Toggle the theme | Page, panels, and buttons change theme; input and history stay intact. |
| Calculate `1 ÷ 0 =` | An error is shown; successful history remains available. |
| Stop the API and click Clear | A connection error appears; existing displayed history is retained. |

History is stored in memory by the existing server, so restarting that server clears it. Theme state resets to light on a browser refresh; persistence is outside the lab requirements.
