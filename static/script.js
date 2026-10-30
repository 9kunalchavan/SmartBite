// SmartBite front-end: talks to the Flask API using fetch().
const $ = (id) => document.getElementById(id);

async function api(url, method = "GET", body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function toast(message, bad = false) {
  const t = $("toast");
  t.textContent = message;
  t.className = "toast" + (bad ? " bad" : "");
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 2600);
}

// Run an action and show any error as a message
async function safely(action) {
  try { await action(); } catch (err) { toast(err.message, true); }
}

// ---------- Profile ----------
async function loadProfile() {
  const { profile } = await api("/api/profile");
  if (!profile) return;
  $("name").value = profile.name;
  $("age").value = profile.age;
  $("preference").value = profile.preference;
  $("budget").value = profile.budget;
  $("goal").value = profile.goal;
}

$("profileForm").addEventListener("submit", (e) => {
  e.preventDefault();
  safely(async () => {
    await api("/api/profile", "POST", {
      name: $("name").value,
      age: $("age").value,
      preference: $("preference").value,
      budget: $("budget").value,
      goal: $("goal").value,
    });
    toast("Profile saved!");
    await Promise.all([loadPlan(), loadFoods(), loadDashboard()]);
    $("planner").scrollIntoView();
  });
});

// ---------- Meal planner ----------
async function loadPlan() {
  const grid = $("planGrid");
  try {
    const { plan, reason } = await api("/api/meal-plan");
    $("planNote").textContent = "Suggestions are chosen by simple rules: your food preference, goal and budget. Focus: " + reason.toLowerCase() + ".";
    grid.innerHTML = "";
    for (const meal in plan) {
      const options = plan[meal].options.map((f) => `
        <div class="option">
          <strong>${f.emoji} ${f.name}</strong>
          <small>${f.unit} · ${f.calories} kcal · ${f.protein} g protein · ₹${f.price}</small>
        </div>`).join("");
      grid.insertAdjacentHTML("beforeend", `
        <div class="card meal"><h3>${meal}</h3>
        <p class="limit">Budget for this meal: about ₹${plan[meal].budget}</p>${options}</div>`);
    }
  } catch (err) {
    grid.innerHTML = "";
    $("planNote").textContent = "Save your profile to see your meal plan.";
  }
}

// ---------- Food tracker ----------
async function loadFoods() {
  const { foods } = await api("/api/foods");
  $("foodSelect").innerHTML = foods
    .map((f) => `<option value="${f.id}">${f.emoji} ${f.name} (${f.unit})</option>`).join("");
}

function showLog({ log, totals }) {
  $("logBody").innerHTML = log.map((e) => `
    <tr><td>${e.emoji} ${e.name}</td><td>${e.quantity}</td><td>${e.calories}</td>
    <td>${e.protein}</td><td>${e.cost}</td>
    <td><button class="del" data-id="${e.id}" aria-label="Delete">✕</button></td></tr>`).join("");
  $("totCal").textContent = totals.calories;
  $("totPro").textContent = totals.protein;
  $("totCost").textContent = totals.cost;
  $("logEmpty").style.display = log.length ? "none" : "block";
  $("clearLog").style.display = log.length ? "inline-block" : "none";
}

$("logForm").addEventListener("submit", (e) => {
  e.preventDefault();
  safely(async () => {
    const data = await api("/api/log", "POST", {
      food_id: Number($("foodSelect").value),
      quantity: $("quantity").value,
    });
    showLog(data);
    $("quantity").value = 1;
    toast("Food added!");
    loadDashboard();
  });
});

$("logBody").addEventListener("click", (e) => {
  const id = e.target.dataset.id;
  if (!id) return;
  safely(async () => {
    showLog(await api("/api/log?id=" + id, "DELETE"));
    loadDashboard();
  });
});

$("clearLog").addEventListener("click", () => {
  safely(async () => {
    showLog(await api("/api/log", "DELETE"));
    loadDashboard();
  });
});

// ---------- Water ----------
function showWater(count, target) {
  $("waterCount").textContent = count;
  $("waterTarget").textContent = target;
  $("glasses").innerHTML = Array.from({ length: target }, (_, i) =>
    `<span class="${i < count ? "full" : ""}">🥛</span>`).join("");
}

function changeWater(action) {
  safely(async () => {
    const { water, target } = await api("/api/water", "POST", { action });
    showWater(water, target);
    loadDashboard();
  });
}
$("waterPlus").addEventListener("click", () => changeWater("add"));
$("waterMinus").addEventListener("click", () => changeWater("remove"));

// ---------- Dashboard ----------
function setBar(id, value, target) {
  const bar = $(id);
  const percent = target ? Math.min((value / target) * 100, 100) : 0;
  bar.style.width = percent + "%";
  bar.classList.toggle("over", target && value > target);
}

async function loadDashboard() {
  const d = await api("/api/dashboard");
  $("greeting").textContent = d.name ? `Today's progress for ${d.name}` : "Save your profile to see personal targets.";
  $("dCal").textContent = d.calories;   $("dCalT").textContent = d.calorie_target;
  $("dPro").textContent = d.protein;    $("dProT").textContent = d.protein_target;
  $("dExp").textContent = d.expense;    $("dBud").textContent = d.budget ?? "–";
  $("dWat").textContent = d.water;      $("dWatT").textContent = d.water_target;
  setBar("bCal", d.calories, d.calorie_target);
  setBar("bPro", d.protein, d.protein_target);
  setBar("bExp", d.expense, d.budget);
  setBar("bWat", d.water, d.water_target);
  $("tip").textContent = d.tip;
  showWater(d.water, d.water_target);
}

// ---------- Mobile menu ----------
$("menuBtn").addEventListener("click", () => $("menu").classList.toggle("open"));
$("menu").addEventListener("click", () => $("menu").classList.remove("open"));

// ---------- Start ----------
safely(async () => {
  await loadProfile();
  await Promise.all([loadPlan(), loadFoods(), loadDashboard()]);
  showLog(await api("/api/log"));
});
