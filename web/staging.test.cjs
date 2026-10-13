const { test } = require("node:test");
const assert = require("node:assert/strict");
const { stageAnatomic } = require("./app.js");

test("AJCC8 table coverage and N1mi exceptions", () => {
  const rows = [
    ["Tis","N0","0"], ["T1","N0","IA"], ["T0","N1mi","IB"], ["T1","N1mi","IB"],
    ["T0","N1","IIA"], ["T1","N1","IIA"], ["T2","N0","IIA"],
    ["T2","N1","IIB"], ["T3","N0","IIB"], ["T2","N1mi","IIB"],
    ["T0","N2","IIIA"], ["T1","N2","IIIA"], ["T2","N2","IIIA"],
    ["T3","N1","IIIA"], ["T3","N2","IIIA"], ["T3","N1mi","IIIA"],
    ["T4","N0","IIIB"], ["T4","N1","IIIB"], ["T4","N2","IIIB"],
    ["T4","N1mi","IIIB"], ["T1","N3","IIIC"]
  ];
  for (const [t,n,expected] of rows) {
    assert.equal(stageAnatomic(t,n,"M0"), expected, t+" "+n);
  }
  assert.equal(stageAnatomic("TX","NX","M1"), "IV");
});
test("Unsupported and unknown TNM categories never receive a stage", () => {
  for (const [t,n,m] of [["T0","N0","M0"],["Tis","N1","M0"],["TX","N0","M0"],["T1","NX","M0"],["T5","N1","M0"]]) {
    assert.throws(() => stageAnatomic(t,n,m), Error);
  }
});
