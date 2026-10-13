"use strict";
// AJCC8 anatomic grouping: NCI PDQ Breast Cancer Treatment, Table 8.
// Clinical/pathological prognostic stage is not calculated here.
function stageAnatomic(t, n, m) {
  const ts = ["Tis", "T0", "T1", "T2", "T3", "T4", "TX"];
  const ns = ["N0", "N1mi", "N1", "N2", "N3", "NX"];
  const ms = ["M0", "M1"];
  if (!ts.includes(t) || !ns.includes(n) || !ms.includes(m)) {
    throw new Error("Select valid T, N and M categories.");
  }
  if (m === "M1") return "IV";
  if (t === "TX" || n === "NX") throw new Error("Stage cannot be assigned with TX or NX when M0.");
  if (n === "N3") return "IIIC";
  const node = n === "N1mi" && ["T2", "T3", "T4"].includes(t) ? "N1" : n;
  const groups = {
    "Tis:N0": "0", "T1:N0": "IA",
    "T0:N1mi": "IB", "T1:N1mi": "IB",
    "T0:N1": "IIA", "T1:N1": "IIA", "T2:N0": "IIA",
    "T2:N1": "IIB", "T3:N0": "IIB",
    "T0:N2": "IIIA", "T1:N2": "IIIA", "T2:N2": "IIIA",
    "T3:N1": "IIIA", "T3:N2": "IIIA",
    "T4:N0": "IIIB", "T4:N1": "IIIB", "T4:N2": "IIIB"
  };
  const value = groups[t + ":" + node];
  if (!value) throw new Error("No AJCC8 anatomical group for this combination. Verify TNM categories.");
  return value;
}

if (typeof module !== "undefined" && module.exports) module.exports = { stageAnatomic };

if (typeof document !== "undefined") {
  const form = document.getElementById("stage-form");
  const result = document.getElementById("result");
  const message = document.getElementById("message");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const t = document.getElementById("t").value;
    const n = document.getElementById("n").value;
    const m = document.getElementById("m").value;
    try {
      const stage = stageAnatomic(t, n, m);
      result.textContent = "Stage " + stage;
      message.textContent = t + " " + n + " " + m + " · AJCC 8 anatomic stage only. Prognostic stage not calculated.";
      result.classList.remove("error");
    } catch (err) {
      result.textContent = "Not assignable";
      result.classList.add("error");
      message.textContent = err.message;
    }
  });
  form.addEventListener("reset", () => {
    result.textContent = "—";
    message.textContent = "Enter a TNM combination and select Calculate.";
    result.classList.remove("error");
  });
}
