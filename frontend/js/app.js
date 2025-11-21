window.addEventListener("DOMContentLoaded", async () => {
  // initialize map
  const map = L.map('map').setView([40.73, -73.93], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  let hotspotLayerGroup = L.layerGroup().addTo(map);
  let anomalyLayerGroup = L.layerGroup().addTo(map);

  // helper to draw hotspots
  function drawHotspots(rows) {
    hotspotLayerGroup.clearLayers();
    if (!rows || rows.length === 0) {
      alert("No hotspots found for this hour.");
      return;
    }
    let maxCount = Math.max(...rows.map(r => r.count || 0));
    rows.forEach(r => {
      // grid_x and grid_y are already in proper coordinate format (multiplied by 100)
      // Properly convert back: longitude = grid_x / 100, latitude = grid_y / 100
      const longitude = r.grid_x / 100.0;
      const latitude = r.grid_y / 100.0;
      
      // Scale radius based on hotspot intensity (count)
      const radius = 80 + (r.count / Math.max(1, maxCount)) * 400;
      
      // Leaflet expects [latitude, longitude]
      L.circle([latitude, longitude], {
        radius: radius,
        color: 'orange',
        fillColor: 'orange',
        fillOpacity: 0.4,
        weight: 1
      })
      .bindPopup(`<b>Grid: ${r.grid_key}</b><br>Trips: ${r.count}<br>Avg Fare: $${r.avg_fare?.toFixed(2)}<br>Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`)
      .addTo(hotspotLayerGroup);
    });
  }

  // helper to draw anomalies
  function drawAnomalies(rows) {
    anomalyLayerGroup.clearLayers();
    if (!rows || rows.length === 0) return;
    rows.forEach(a => {
      // Parse grid_key to get grid_x and grid_y
      const [gx, gy] = a.grid_key.split("_").map(Number);
      
      // Convert back to latitude and longitude
      const latitude = gy / 100.0;
      const longitude = gx / 100.0;
      
      // Leaflet expects [latitude, longitude]
      L.circleMarker([latitude, longitude], { 
        radius: 8, 
        color: "red", 
        fill: true, 
        fillOpacity: 0.9,
        weight: 2
      })
      .bindPopup(`<b>Anomaly</b><br>Grid: ${a.grid_key}<br>Trips: ${a.count}<br>Z-Score: ${(a.z || a.zscore || 'n/a').toFixed(2)}<br>Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`)
      .addTo(anomalyLayerGroup);
    });
  }

  // function to fetch hotspots for a specific hour
  async function loadHotspots(hour) {
    try {
      const resp = await fetch(`/api/hotspots?hour=${hour}`);
      if (!resp.ok) throw new Error(`hotspots API failed: ${resp.status}`);
      const hotspots = await resp.json();
      drawHotspots(hotspots);
    } catch (err) {
      console.error("Failed to load hotspots:", err);
    }
  }

  // fetch anomalies once (they’re usually global)
  try {
    const resp2 = await fetch(`/api/anomalies`);
    if (resp2.ok) {
      const anomalies = await resp2.json();
      drawAnomalies(anomalies);
    }
  } catch (err) {
    console.error("Failed to load anomalies:", err);
  }

  // button event handler
  document.getElementById("loadBtn").addEventListener("click", async () => {
    const hour = parseInt(document.getElementById("hourInput").value);
    if (isNaN(hour) || hour < 0 || hour > 23) {
      alert("Please enter a valid hour (0–23).");
      return;
    }
    await loadHotspots(hour);
  });

  // initial load for hour 0
  await loadHotspots(0);
});
