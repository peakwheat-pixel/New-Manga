import ReactDOM from "react-dom/client";
import App from "./App";
import { FpsRecorderPanel } from "./perf/FpsRecorderPanel";
import { readFpsRecorderRequest, startFpsRecorder } from "./perf/fpsRecorder";

// No StrictMode: the ?probe=1 evidence matrix must execute exactly once.

// P20-AC4-FPS-1: opt-in rAF frame-time sampling. Default path evaluates the
// three explicit switches once (build flag / ?m2_fps=1 / localStorage) and
// then moves on — no rAF registration, no sample array, no panel mounted.
const fpsSamplingRequested = readFpsRecorderRequest();
const fpsRecorder = fpsSamplingRequested ? startFpsRecorder() : null;

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <>
    <App />
    {fpsRecorder ? <FpsRecorderPanel recorder={fpsRecorder} /> : null}
  </>,
);
