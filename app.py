import osmnx as ox
import networkx as nx
import sqlite3 
import json
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Load a smaller road network (e.g., Nairobi only)
place_name = "Nairobi, Kenya"
G = ox.graph_from_place(
    place_name, 
    network_type="drive", 
    simplify=True,
    retain_all=False  # Remove isolated subgraphs (saves memory)
)
# Convert graph to GeoJSON
edges_gdf = ox.graph_to_gdfs(G, nodes=False)
roads_geojson = edges_gdf.to_json()

# Example water points (replace with real data if available)
water_points = [
    {"name": "City Park Water Point", "lat": -1.265746, "lng": 36.822295},
    {"name": "Kibera Water Kiosk", "lat": -1.316452, "lng": 36.782667},
    {"name": "Gikambura Public Water Tap", "lat": -1.289976, "lng": 36.886562},
    {"name": "Kasarani Water Supply", "lat": -1.214946, "lng": 36.893347},
    {"name": "Dandora Water Project", "lat": -1.266282, "lng": 36.879742},
    {"name": "Karen Water Distribution", "lat": -1.354986, "lng": 36.722081},
    {"name": "Mathare Community Water Tap", "lat": -1.264895, "lng": 36.855479}
]
hospitals = [
    {"name": "Kenyatta National Hospital", "lat": -1.300355, "lng": 36.806681},
    {"name": "Aga Khan University Hospital", "lat": -1.264938, "lng": 36.818165},
    {"name": "The Nairobi Hospital", "lat": -1.292140, "lng": 36.812468},
    {"name": "Mater Hospital", "lat": -1.308846, "lng": 36.845972},
    {"name": "MP Shah Hospital", "lat": -1.267862, "lng": 36.823133},
    {"name": "Coptic Hospital", "lat": -1.300215, "lng": 36.797357},
    {"name": "Karen Hospital", "lat": -1.343042, "lng": 36.714172},
    {"name": "Gertrude's Children's Hospital", "lat": -1.245153, "lng": 36.827014},
    {"name": "M.P. Shah Hospital", "lat": -1.267978, "lng": 36.823086},
    {"name": "Nairobi Women’s Hospital", "lat": -1.298153, "lng": 36.792071}
]
schools = [
    {"name": "University of Nairobi", "lat": -1.279818, "lng": 36.822839},
    {"name": "Strathmore University", "lat": -1.309829, "lng": 36.814758},
    {"name": "Kenyatta University", "lat": -1.182622, "lng": 36.927304},
    {"name": "Jomo Kenyatta University", "lat": -1.099628, "lng": 37.015061},
    {"name": "Mount Kenya University", "lat": -1.047014, "lng": 37.072460},
    {"name": "USIU Africa", "lat": -1.224088, "lng": 36.886353},
    {"name": "Daystar University", "lat": -1.413850, "lng": 36.962583},
    {"name": "Technical University of Kenya", "lat": -1.285618, "lng": 36.821289},
    {"name": "Catholic University of East Africa", "lat": -1.310441, "lng": 36.812813},
    {"name": "Multimedia University of Kenya", "lat": -1.392245, "lng": 36.747429},
    {"name": "Africa Nazarene University", "lat": -1.426741, "lng": 36.956270}
]

# Define a simple homepage route
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/road_network")
def road_network():
    return jsonify(json.loads(edges_geojson))  # Convert GeoJSON to JSON format

@app.route("/data")
def data():
    return jsonify({
        "water_points": water_points,  
        "hospitals": hospitals, 
        "schools": schools, 
        "roads": roads_geojson
        })
    
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response

# Store manually blocked roads
blocked_edges = set()

# Get nearest road node
def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, lon, lat)

# Get town data
def get_towns():
    conn = sqlite3.connect("resource_allocation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Town, Latitude, Longitude FROM WaterAccess")
    rows = cursor.fetchall()
    conn.close()
    return [{"town": row[0], "lat": row[1], "lon": row[2]} for row in rows]

# Function to compute routes
def find_routes(destination_lat, destination_lon):
    nairobi_lat, nairobi_lon = -1.286389, 36.817223
    start_node = get_nearest_node(nairobi_lat, nairobi_lon)
    end_node = get_nearest_node(destination_lat, destination_lon)

    # Create a modified graph
    G_modified = G.copy()
    for u, v in blocked_edges:
        if G_modified.has_edge(u, v):
            G_modified.remove_edge(u, v)

    # Compute primary and alternative routes
    try:
        primary_route = nx.shortest_path(G_modified, start_node, end_node, weight="length")
    except nx.NetworkXNoPath:
        primary_route = []

    try:
        alternative_route = list(nx.shortest_simple_paths(G_modified, start_node, end_node, weight="length"))[1]
    except (nx.NetworkXNoPath, IndexError):
        alternative_route = []

    # Convert nodes to lat/lon
    primary_coords = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in primary_route]
    alternative_coords = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in alternative_route]

    return primary_coords, alternative_coords

# API Endpoint: Fetch routes considering blocked roads
@app.route("/api/routes", methods=["POST"])
def get_routes():
    towns = get_towns()
    routes = {}

    for town in towns:
        primary, alternative = find_routes(town["lat"], town["lon"])
        routes[town["town"]] = {"primary": primary, "alternative": alternative}

    return jsonify(routes)

# API Endpoint: Add blocked road
@app.route("/api/block_road", methods=["POST"])
def block_road():
    data = request.json
    node1, node2 = data["node1"], data["node2"]
    blocked_edges.add((node1, node2))
    return jsonify({"message": "Road blocked", "blocked_edges": list(blocked_edges)})

# API Endpoint: Unblock a road
@app.route("/api/unblock_road", methods=["POST"])
def unblock_road():
    data = request.json
    node1, node2 = data["node1"], data["node2"]
    blocked_edges.discard((node1, node2))  # Remove road from blocked list
    return jsonify({"message": "Road unblocked", "blocked_edges": list(blocked_edges)})

# API Endpoint: Fetch blocked roads
@app.route("/api/blocked_roads", methods=["GET"])
def get_blocked_roads():
    return jsonify({"blocked_edges": list(blocked_edges)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
