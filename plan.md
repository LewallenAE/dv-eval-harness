# DV Eval Harness — Frontend Plan

**Stack:** Next.js 14 (App Router), TypeScript, Tailwind CSS  
**Backend:** FastAPI running on `http://localhost:8000`  
**Root dir:** `dv-eval-harness/frontend/`

---

## API Contract (what the frontend talks to)

| Method | Endpoint | Returns |
|--------|----------|---------|
| `GET` | `/cases` | `string[]` — list of case IDs |
| `POST` | `/run-case/{case_id}` | `Trajectory` |
| `GET` | `/traces` | `Trajectory[]` |
| `GET` | `/` | `{ status: string, service: string }` |

---

## Directory Structure

```
frontend/
  app/
    layout.tsx
    page.tsx              ← home
    run/
      page.tsx            ← run a case
    traces/
      page.tsx            ← trace history
  components/
    nav/
      NavBar.tsx
    cases/
      CaseSelector.tsx
      CaseUploader.tsx
      CasePreview.tsx
    results/
      TrajectoryViewer.tsx
      ScoreCard.tsx
      ActionTimeline.tsx
      EvidencePanel.tsx
      RTLDiff.tsx
    traces/
      TracesTable.tsx
    ui/
      ScoreBadge.tsx
      RunButton.tsx
      LoadingSpinner.tsx
  lib/
    api.ts
    types.ts
```

---

## Components — Build in This Order

Dependencies must be built before the components that import them.

### 1. Project Scaffold
**Agent task:** Initialize the Next.js 14 project with TypeScript and Tailwind. No component code — just the working skeleton.
- `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
- Delete boilerplate from `app/page.tsx` and `app/globals.css`
- Set up `next.config.ts` with `NEXT_PUBLIC_API_URL` env var (default `http://localhost:8000`)
- Create the full folder structure above (empty files are fine)

---

### 2. `lib/types.ts`
**Agent task:** TypeScript types that mirror the backend Pydantic schemas exactly.

Types needed:
```ts
DVCase         // matches backend DVCase schema
AgentAction    // step, tool_name, input, output
EvaluationScores  // 5 floats, all 0.0–1.0
Trajectory     // case_id, root_cause, proposed_fix, actions, evidence, scores, penalties, r_total
```

---

### 3. `lib/api.ts`
**Agent task:** Typed async fetch functions for each endpoint. No React — pure TypeScript module.

Functions:
```ts
fetchCases(): Promise<string[]>
runCase(caseId: string): Promise<Trajectory>
fetchTraces(): Promise<Trajectory[]>
```
- Read base URL from `process.env.NEXT_PUBLIC_API_URL`
- Throw descriptive errors on non-2xx responses

---

### 4. `components/ui/ScoreBadge.tsx`
**Agent task:** Single reusable badge that displays a 0.0–1.0 float with color coding.
- Green if ≥ 0.8, yellow if ≥ 0.5, red if < 0.5
- Shows value as a percentage (e.g. `1.0 → 100%`)
- Props: `score: number`, `label?: string`

---

### 5. `components/ui/RunButton.tsx`
**Agent task:** Button with three states — idle, loading, error.
- Props: `onClick`, `loading: boolean`, `disabled?: boolean`
- Shows spinner from `LoadingSpinner` during loading state

---

### 6. `components/ui/LoadingSpinner.tsx`
**Agent task:** Simple animated spinner component.
- Props: `size?: 'sm' | 'md' | 'lg'`
- Tailwind animated spin

---

### 7. `components/nav/NavBar.tsx`
**Agent task:** Top navigation bar.
- Project name: "DV Eval Harness"
- Links: "Run Case" (`/run`), "Traces" (`/traces`)
- Active link highlighted

---

### 8. `components/cases/CaseSelector.tsx`
**Agent task:** Dropdown that fetches `GET /cases` on mount and lets the user pick one.
- Props: `onSelect: (caseId: string) => void`, `selected: string | null`
- Shows loading state while fetching
- Shows error state if fetch fails

---

### 9. `components/cases/CaseUploader.tsx`
**Agent task:** File input that accepts a `.json` file, parses it as `DVCase`, and returns it.
- Props: `onUpload: (case: DVCase) => void`, `onError: (msg: string) => void`
- Validate that required fields are present (`id`, `bug_signature`, `rtl`, etc.)
- Show filename and a clear/reset button after upload

---

### 10. `components/cases/CasePreview.tsx`
**Agent task:** Read-only display of a parsed `DVCase` before running.
- Props: `case: DVCase`
- Show: title, description, expected_root_cause, RTL (monospace, scrollable), valid_signals, forbidden_targets
- Collapsible RTL block (it can be long)

---

### 11. `components/results/ScoreCard.tsx`
**Agent task:** Displays the five evaluation scores and r_total.
- Props: `scores: EvaluationScores`, `rTotal: number`, `penalties: string[]`
- One row per score dimension with label + `ScoreBadge`
- `r_total` displayed prominently at the top
- If `penalties` is non-empty, list them with a warning style

---

### 12. `components/results/ActionTimeline.tsx`
**Agent task:** Vertical timeline of the 5 agent pipeline steps.
- Props: `actions: AgentAction[]`
- Each step: step number, tool name, collapsible input/output (output can be long JSON)
- Tool names as readable labels (e.g. `run_simulator_before_fix` → "Simulator (before fix)")

---

### 13. `components/results/EvidencePanel.tsx`
**Agent task:** Displays the list of evidence strings collected during the run.
- Props: `evidence: string[]`
- Each evidence item in a monospace block
- Section header: "Evidence Collected"

---

### 14. `components/results/RTLDiff.tsx`
**Agent task:** Side-by-side view of buggy RTL vs fixed RTL.
- Props: `original: string`, `fixed: string`
- Two labeled monospace panels: "Buggy RTL" and "Fixed RTL"
- Highlight lines that differ (simple line-by-line diff — no need for a diff library, split on `;` or space)

---

### 15. `components/results/TrajectoryViewer.tsx`
**Agent task:** Container that assembles the four result components.
- Props: `trajectory: Trajectory`
- Layout: ScoreCard at top, then ActionTimeline, then RTLDiff, then EvidencePanel
- Also shows: `root_cause` string in a callout box labeled "Inferred Root Cause"

---

### 16. `components/traces/TracesTable.tsx`
**Agent task:** Table of past evaluation runs fetched from `GET /traces`.
- Fetches on mount, shows loading/empty/error states
- Columns: Case ID, R-Total, Root Cause, Timestamp (if present, else run index)
- Clicking a row expands inline `TrajectoryViewer` for that trace
- Sort by r_total descending by default

---

### 17. `app/run/page.tsx` — Run Page
**Agent task:** Assembles the full run flow.
- Two tabs or toggle: "Select Existing Case" (CaseSelector) vs "Upload JSON" (CaseUploader)
- Once a case is selected/uploaded: show CasePreview + RunButton
- On run: POST to `/run-case/{id}` or if uploaded, POST the JSON directly (see note below)
- On result: show TrajectoryViewer

**Note on uploaded cases:** The backend `POST /run-case/{case_id}` looks up cases by file. To support arbitrary uploaded JSON, the backend needs a new endpoint — flag this for later or save the uploaded case to a temp file server-side. For MVP, the run page can POST to a new endpoint `POST /run-case-json` with the full case body. That endpoint is a one-liner addition to `main.py`.

---

### 18. `app/traces/page.tsx` — Traces Page
**Agent task:** Renders `TracesTable` with a page header.
- "Evaluation History" heading
- Refresh button to re-fetch traces

---

### 19. `app/page.tsx` — Home Page
**Agent task:** Simple landing page.
- Project name + one-line description
- Two cards: "Run a Case" and "View Traces" with links
- Status indicator: fetches `GET /` and shows green/red dot for API health

---

### 20. `app/layout.tsx` — Root Layout
**Agent task:** Root layout wrapping all pages.
- Includes `NavBar`
- Sets HTML metadata (title: "DV Eval Harness")
- Tailwind base styles

---

## Build Order (dependency graph)

```
1  → Scaffold
2  → types.ts
3  → api.ts            (needs types.ts)
4  → ScoreBadge
5  → LoadingSpinner
6  → RunButton          (needs LoadingSpinner)
7  → NavBar
8  → CaseSelector       (needs api.ts)
9  → CaseUploader       (needs types.ts)
10 → CasePreview        (needs types.ts)
11 → ScoreCard          (needs types.ts, ScoreBadge)
12 → ActionTimeline     (needs types.ts)
13 → EvidencePanel      (needs types.ts)
14 → RTLDiff            (needs types.ts)
15 → TrajectoryViewer   (needs 11, 12, 13, 14)
16 → TracesTable        (needs api.ts, TrajectoryViewer)
17 → run/page.tsx       (needs 8, 9, 10, 6, 15)
18 → traces/page.tsx    (needs 16)
19 → page.tsx           (needs api.ts)
20 → layout.tsx         (needs NavBar)
```

---

## Backend Addition Needed

For uploaded JSON cases (component 17), add one endpoint to `backend/app/main.py`:

```python
@app.post("/run-case-json")
def run_case_json(case: DVCase):
    trajectory = run_agent_on_case(case)
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(trajectory.model_dump_json() + "\n")
    return trajectory
```

This is 5 lines and unblocks the upload flow entirely.

---

## Environment

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```
