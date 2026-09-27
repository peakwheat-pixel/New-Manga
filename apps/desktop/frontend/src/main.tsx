import ReactDOM from "react-dom/client";
import App from "./App";

// No StrictMode: the ?probe=1 evidence matrix must execute exactly once.
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(<App />);
