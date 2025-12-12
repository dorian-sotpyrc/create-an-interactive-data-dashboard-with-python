(function () {
  const config = window.DASHBOARD_CONFIG || {};

  const cardsContainer = document.getElementById("cards");
  const chartsContainer = document.getElementById("charts");
  const tableHead = document.getElementById("table-head");
  const tableBody = document.getElementById("table-body");

  const startDateInput = document.getElementById("start-date");
  const endDateInput = document.getElementById("end-date");
  const resetFiltersBtn = document.getElementById("reset-filters");

  function getFilters() {
    const params = new URLSearchParams();
    if (startDateInput.value) params.set("start_date", startDateInput.value);
    if (endDateInput.value) params.set("end_date", endDateInput.value);
    return params;
  }

  async function fetchJSON(url, params) {
    const fullUrl = params && params.toString() ? `${url}?${params.toString()}` : url;
    const res = await fetch(fullUrl);
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }
    return res.json();
  }

  function renderCards(metrics) {
    cardsContainer.innerHTML = "";
    metrics.forEach((m) => {
      const card = document.createElement("div");
      card.className = "card";

      const label = document.createElement("div");
      label.className = "card-label";
      label.textContent = m.label;

      const value = document.createElement("div");
      value.className = "card-value";
      value.textContent = m.formatted ?? m.value;

      card.appendChild(label);
      card.appendChild(value);
      cardsContainer.appendChild(card);
    });
  }

  function renderTable(rows) {
    tableHead.innerHTML = "";
    tableBody.innerHTML = "";

    if (!rows || rows.length === 0) {
      return;
    }

    const columns = Object.keys(rows[0]);

    const trHead = document.createElement("tr");
    columns.forEach((col) => {
      const th = document.createElement("th");
      th.textContent = col;
      trHead.appendChild(th);
    });
    tableHead.appendChild(trHead);

    rows.forEach((row) => {
      const tr = document.createElement("tr");
      columns.forEach((col) => {
        const td = document.createElement("td");
        td.textContent = row[col];
        tr.appendChild(td);
      });
      tableBody.appendChild(tr);
    });
  }

  function createSVG(width, height) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    return svg;
  }

  function renderLineChart(container, chart) {
    const width = 400;
    const height = 220;
    const padding = 30;

    const svg = createSVG(width, height);

    const points = chart.points || [];
    if (points.length === 0) {
      container.textContent = "No data";
      return;
    }

    const xs = points.map((p, i) => i);
    const ys = points.map((p) => p.y);

    const xMin = 0;
    const xMax = xs.length - 1 || 1;
    const yMin = 0;
    const yMax = Math.max(...ys) || 1;

    function xScale(x) {
      return padding + ((width - 2 * padding) * (x - xMin)) / (xMax - xMin || 1);
    }

    function yScale(y) {
      return height - padding - ((height - 2 * padding) * (y - yMin)) / (yMax - yMin || 1);
    }

    const svgNS = "http://www.w3.org/2000/svg";

    // Axes
    const xAxis = document.createElementNS(svgNS, "line");
    xAxis.setAttribute("x1", padding);
    xAxis.setAttribute("y1", height - padding);
    xAxis.setAttribute("x2", width - padding);
    xAxis.setAttribute("y2", height - padding);
    xAxis.setAttribute("stroke", "#4b5563");
    xAxis.setAttribute("stroke-width", "1");
    svg.appendChild(xAxis);

    const yAxis = document.createElementNS(svgNS, "line");
    yAxis.setAttribute("x1", padding);
    yAxis.setAttribute("y1", padding);
    yAxis.setAttribute("x2", padding);
    yAxis.setAttribute("y2", height - padding);
    yAxis.setAttribute("stroke", "#4b5563");
    yAxis.setAttribute("stroke-width", "1");
    svg.appendChild(yAxis);

    // Line path
    let d = "";
    points.forEach((p, i) => {
      const x = xScale(xs[i]);
      const y = yScale(p.y);
      d += i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`;
    });

    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#60a5fa");
    path.setAttribute("stroke-width", "2");
    svg.appendChild(path);

    // Dots
    points.forEach((p, i) => {
      const cx = xScale(xs[i]);
      const cy = yScale(p.y);
      const circle = document.createElementNS(svgNS, "circle");
      circle.setAttribute("cx", cx);
      circle.setAttribute("cy", cy);
      circle.setAttribute("r", "3");
      circle.setAttribute("fill", "#93c5fd");
      svg.appendChild(circle);
    });

    container.innerHTML = "";
    container.appendChild(svg);
  }

  function renderBarChart(container, chart) {
    const width = 400;
    const height = 220;
    const padding = 30;

    const svg = createSVG(width, height);

    const points = chart.points || [];
    if (points.length === 0) {
      container.textContent = "No data";
      return;
    }

    const ys = points.map((p) => p.y);
    const yMin = 0;
    const yMax = Math.max(...ys) || 1;

    const svgNS = "http://www.w3.org/2000/svg";

    const xAxis = document.createElementNS(svgNS, "line");
    xAxis.setAttribute("x1", padding);
    xAxis.setAttribute("y1", height - padding);
    xAxis.setAttribute("x2", width - padding);
    xAxis.setAttribute("y2", height - padding);
    xAxis.setAttribute("stroke", "#4b5563");
    xAxis.setAttribute("stroke-width", "1");
    svg.appendChild(xAxis);

    const yAxis = document.createElementNS(svgNS, "line");
    yAxis.setAttribute("x1", padding);
    yAxis.setAttribute("y1", padding);
    yAxis.setAttribute("x2", padding);
    yAxis.setAttribute("y2", height - padding);
    yAxis.setAttribute("stroke", "#4b5563");
    yAxis.setAttribute("stroke-width", "1");
    svg.appendChild(yAxis);

    const barAreaWidth = width - 2 * padding;
    const barWidth = barAreaWidth / points.length * 0.7;

    points.forEach((p, i) => {
      const xCenter = padding + (barAreaWidth * (i + 0.5)) / points.length;
      const barHeight = ((height - 2 * padding) * (p.y - yMin)) / (yMax - yMin || 1);
      const x = xCenter - barWidth / 2;
      const y = height - padding - barHeight;

      const rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("x", x);
      rect.setAttribute("y", y);
      rect.setAttribute("width", barWidth);
      rect.setAttribute("height", barHeight);
      rect.setAttribute("fill", "#34d399");
      svg.appendChild(rect);

      // X labels
      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", xCenter);
      label.setAttribute("y", height - padding + 12);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("font-size", "9");
      label.setAttribute("fill", "#9ca3af");
      label.textContent = p.x;
      svg.appendChild(label);
    });

    container.innerHTML = "";
    container.appendChild(svg);
  }

  function renderCharts(charts) {
    chartsContainer.innerHTML = "";

    charts.forEach((chartCfg) => {
      const wrapper = document.createElement("div");
      wrapper.className = "chart";

      const title = document.createElement("h2");
      title.className = "chart-title";
      title.textContent = chartCfg.label;

      const canvas = document.createElement("div");
      canvas.className = "chart-canvas";
      canvas.dataset.chartId = chartCfg.id;

      wrapper.appendChild(title);
      wrapper.appendChild(canvas);
      chartsContainer.appendChild(wrapper);
    });
  }

  async function updateData() {
    const params = getFilters();

    try {
      const [metricsRes, tableRes] = await Promise.all([
        fetchJSON("/api/metrics", params),
        fetchJSON("/api/table", params),
      ]);

      renderCards(metricsRes.metrics || []);
      renderTable(tableRes.rows || []);

      // Fetch each chart individually
      const charts = (config.charts || []).slice();
      for (const chartCfg of charts) {
        const data = await fetchJSON(`/api/charts/${encodeURIComponent(chartCfg.id)}`, params);
        const canvas = chartsContainer.querySelector(`.chart-canvas[data-chart-id="${chartCfg.id}"]`);
        if (!canvas) continue;
        if (data.type === "line") {
          renderLineChart(canvas, data);
        } else {
          renderBarChart(canvas, data);
        }
      }
    } catch (err) {
      console.error(err);
    }
  }

  function initFilters() {
    const dateFilterCfg = (config.filters || []).find((f) => f.id === "date_range");
    if (!dateFilterCfg) return;

    function onChange() {
      updateData();
    }

    startDateInput.addEventListener("change", onChange);
    endDateInput.addEventListener("change", onChange);

    resetFiltersBtn.addEventListener("click", () => {
      startDateInput.value = "";
      endDateInput.value = "";
      updateData();
    });
  }

  function init() {
    renderCharts(config.charts || []);
    initFilters();
    updateData();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
