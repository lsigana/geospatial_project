let map = L.map("map").setView([-1.286389, 36.817223], 12);

// Add OpenStreetMap tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
}).addTo(map);

// Store blocked roads
let blockedEdges = [];
let blockedLayers = [];

// Fetch and display routes
function fetchRoutes() {
    fetch("/api/routes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
    })
    .then((response) => response.json())
    .then((routes) => {
        // Remove previous routes
        map.eachLayer((layer) => {
            if (layer instanceof L.Polyline && !blockedLayers.includes(layer)) {
                map.removeLayer(layer);
            }
        });

        // Draw primary and alternative routes
        Object.keys(routes).forEach((town) => {
            let primary = routes[town].primary;
            let alternative = routes[town].alternative;

            if (primary.length > 0) {
                L.polyline(primary, { color: "blue", weight: 4 }).addTo(map)
                    .bindPopup(`Primary route to ${town}`);
            }

            if (alternative.length > 0) {
                L.polyline(alternative, { color: "red", weight: 4, dashArray: "5, 10" }).addTo(map)
                    .bindPopup(`Alternative route to ${town}`);
            }
        });

        // Fetch and draw blocked roads
        fetchBlockedRoads();
    });
}
// Define a custom roadblock icon
const roadblockIcon = L.divIcon({
    className: "roadblock-icon",
    html: `<div class="roadblock-marker"></div>`,
    iconSize: [32, 32],  // Size of the icon
    iconAnchor: [16, 16],  // Center the icon
    popupAnchor: [0, -16]  // Position popup above the icon
});

let blockedMarkers = [];  // Store blocked road markers
document.head.appendChild(style);

// Function to fetch and animate blocked roads
function fetchBlockedRoads() {
    fetch("/api/blocked_roads")
        .then(response => response.json())
        .then(data => {
            // Remove previous markers with fade-out animation
            blockedMarkers.forEach(marker => {
                marker._icon.classList.add("fade-out");
                setTimeout(() => map.removeLayer(marker), 500);
            });
            blockedMarkers = [];

            data.blocked_edges.forEach(edge => {
                let coords = edge.map(node => [node.lat, node.lon]);

                let marker = L.marker(coords[0], { icon: roadblockIcon })
                    .addTo(map)
                    .bindPopup("Blocked Road - Click to Unblock")
                    .on("click", function () {
                        unblockRoad(edge);
                    });

                // Add fade-in animation
                marker._icon.classList.add("fade-in");
                blockedMarkers.push(marker);
            });
        });
}
// Ensure map supports touch gestures smoothly
map.doubleClickZoom.disable(); // Prevent accidental zooming

// Click event to block roads
map.on("click", function (e) {
    let lat = e.latlng.lat;
    let lon = e.latlng.lng;

    fetch(`/api/nearest_node?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(node => {
            let nearestNode = node.node;
            if (blockedEdges.includes(nearestNode)) return;

            blockedEdges.push(nearestNode);

            // Send blocked road to backend
            fetch("/api/block_road", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ node1: blockedEdges[0], node2: blockedEdges[1] }),
            })
            .then(() => fetchBlockedRoads());
        });
});
// Make popups close with a tap outside
map.on("click", function () {
    map.closePopup();
});
// Function to unblock roads
function unblockRoad(edge) {
    fetch("/api/unblock_road", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node1: edge[0], node2: edge[1] }),
    })
    .then(() => {
        fetchRoutes(); // Refresh routes
    });
}

// Initial route display
fetchRoutes();
