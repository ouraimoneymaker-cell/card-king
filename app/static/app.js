const $ = (id) => document.getElementById(id);

function setText(id, text){ $(id).textContent = text; }
function money(x){ return `$${Number(x).toFixed(2)}`; }

function chipRisk(risk){
  const el = $("risk");
  el.classList.remove("chip--green","chip--amber","chip--red");
  if(risk === "Low") el.classList.add("chip--green");
  else if(risk === "Medium") el.classList.add("chip--amber");
  else el.classList.add("chip--red");
  setText("risk", `Risk: ${risk}`);
}

function decisionColor(decision){
  const el = $("decision");
  el.style.color = "var(--text)";
  if(decision === "GRADE" || decision === "BUY") el.style.color = "var(--good)";
  if(decision === "PASS") el.style.color = "var(--bad)";
  if(decision === "SELL") el.style.color = "var(--warn)";
}

function bindSlider(sliderId, valId){
  const s = $(sliderId);
  const v = $(valId);
  const update = () => v.textContent = Number(s.value).toFixed(1);
  s.addEventListener("input", update);
  update();
}

async function postJSON(url, payload){
  const res = await fetch(url, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  if(!res.ok){
    const t = await res.text();
    throw new Error(`HTTP ${res.status}: ${t}`);
  }
  return res.json();
}

async function onDecide(){
  const query = $("query").value.trim();
  if(!query){
    setText("status","Enter a card to analyze.");
    return;
  }
  setText("status","Computing decision…");
  $("decideBtn").disabled = true;

  const listed = $("listedPrice").value.trim();
  const listed_price = listed ? Number(listed) : null;

  const payload = {
    query,
    listed_price: listed_price && !Number.isNaN(listed_price) ? listed_price : null,
    metrics: {
      centering: Number($("centering").value),
      corners: Number($("corners").value),
      edges: Number($("edges").value),
      surface: Number($("surface").value),
      issue_flag: $("issueFlag").checked
    }
  };

  try{
    const out = await postJSON("/api/decision", payload);

    setText("decision", out.decision);
    decisionColor(out.decision);

    setText("confidence", `Confidence: ${out.confidence}/100`);
    chipRisk(out.risk);

    setText("market", `${money(out.market_value.p25)} – ${money(out.market_value.p75)}`);
    setText("marketMeta", `Median ${money(out.market_value.median)}`);

    setText("roi", `${money(out.roi.expected_net)} net`);
    setText("breakeven", `Breakeven: ${out.roi.breakeven_grade} • ROI ${out.roi.roi_pct.toFixed(0)}%`);

    const probs = $("probs");
    probs.innerHTML = "";
    const order = ["PSA10","PSA9","PSA8","PSA7","LT7"];
    for(const k of order){
      const p = out.grade_probabilities[k] ?? 0;
      const div = document.createElement("div");
      div.className = "prob";
      div.textContent = `${k}: ${(p*100).toFixed(0)}%`;
      probs.appendChild(div);
    }

    const why = $("why");
    why.innerHTML = "";
    for(const line of out.explanation){
      const li = document.createElement("li");
      li.textContent = line;
      why.appendChild(li);
    }

    setText("status","Done.");
  }catch(err){
    setText("status", `Error: ${err.message}`);
  }finally{
    $("decideBtn").disabled = false;
  }
}

function init(){
  bindSlider("centering","centeringVal");
  bindSlider("corners","cornersVal");
  bindSlider("edges","edgesVal");
  bindSlider("surface","surfaceVal");

  $("decideBtn").addEventListener("click", onDecide);
  $("scanBtn").addEventListener("click", () => {
    setText("status","Scan is a placeholder in MVP (manual input required).");
  });
}
document.addEventListener("DOMContentLoaded", init);
