# Geospatial Project
**Title: Geospatial Analysis for Infrastructure Planning in Nairobi**

---

## **1. Introduction**

Geospatial analysis has become an essential tool in urban planning, disaster management, and infrastructure development. This project aims to leverage geospatial data and interactive maps to provide a comprehensive visualization of essential services such as **hospitals, schools, water points, and road networks** within Nairobi, Kenya. By integrating **Flask, Leaflet.js, OSMnx, and GeoJSON**, we built an interactive web application to analyze and visualize these critical locations effectively.

---

## **2. Project Objectives**

- **To visualize Nairobi’s infrastructure (hospitals, schools, water sources, and roads) using an interactive web map.**
- **To analyze road networks for accessibility and urban planning.**
- **To integrate geospatial data from OpenStreetMap (OSM) for enhanced decision-making.**
- **To provide a user-friendly interface for viewing essential service locations.**
- **To optimize geospatial data rendering for performance and usability.**

---

## **3. Tools and Technologies Used**

This project was developed using a combination of backend and frontend technologies:

### **Backend (Flask & Python Libraries)**

- **Flask** - Used to build the web application and serve the interactive map.
- **OSMnx** - To retrieve and manipulate road network data from OpenStreetMap.
- **GeoJSON** - To store and serve geospatial data.
- **SQLite** - Used for lightweight data storage.

### **Frontend (Leaflet.js & JavaScript)**

- **Leaflet.js** - Used for map rendering and interactive layers.
- **HTML, CSS, JavaScript** - For the web interface.
- **Bootstrap & Google Fonts** - Used for better UI design.

---

## **4. Methodology and Implementation**

### **Step 1: Setting Up the Development Environment**

We started by setting up a **virtual environment** to manage dependencies efficiently:

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install flask osmnx networkx folium
```

### **Step 2: Retrieving Geospatial Data**

Using **OSMnx**, we fetched road network data for **Nairobi, Kenya**:

```python
import osmnx as ox
import networkx as nx
from flask import Flask, jsonify, render_template

# Fetch road network of Nairobi
place_name = "Nairobi, Kenya"
G = ox.graph_from_place(place_name, network_type="drive", simplify=True)
```

We also stored important **points of interest (POIs)** such as **schools, hospitals, and water points** as JSON data for easy retrieval:

```python
schools = [
    {"name": "University of Nairobi", "lat": -1.279818, "lng": 36.822839},
    {"name": "Strathmore University", "lat": -1.309829, "lng": 36.814758},
]

hospitals = [
    {"name": "Kenyatta National Hospital", "lat": -1.3032, "lng": 36.8065},
    {"name": "Aga Khan Hospital", "lat": -1.2674, "lng": 36.8176},
]
```

### **Step 3: Creating Flask API Endpoints**

Flask was used to serve geospatial data to the frontend:

```python
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify({"schools": schools, "hospitals": hospitals})
```

### **Step 4: Integrating with Leaflet.js**

On the frontend, we loaded the map and added layers dynamically:

```javascript
var map = L.map('map').setView([-1.279818, 36.822839], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

fetch('/data')
    .then(response => response.json())
    .then(data => {
        data.schools.forEach(school => {
            L.marker([school.lat, school.lng])
                .addTo(map)
                .bindPopup(`<b>${school.name}</b>`);
        });
    });
```

### **Step 5: Performance Optimization**

- **Used a smaller dataset** by focusing only on Nairobi instead of fetching an entire country’s road network.
- **Implemented caching** to reduce redundant API calls.
- **Used simplified GeoJSON data** to reduce load time.

---

## **5. Challenges and Solutions**

### **Challenge 1: Performance Issues with Large OSM Data**

- **Solution**: Limited the road network extraction to **only driveable roads** and simplified the geometries to reduce computational load.

### **Challenge 2: Overlapping Map Layers**

- **Solution**: Adjusted the **z-index** of road layers so that **labels and markers remained visible**.

### **Challenge 3: Flask Debugging Issues**

- **Solution**: Used proper **debugging tools and logging** to track errors efficiently.

---

## **6. Applications and Future Enhancements**

This geospatial analysis tool has potential applications in:

- **Urban Planning** - Assisting government authorities in planning infrastructure development.
- **Disaster Management** - Mapping out emergency service locations for crisis response.
- **Traffic Optimization** - Future integration with real-time traffic data to suggest optimal routes.
- **Public Awareness** - Providing citizens with an easy way to locate essential services.

### **Future Enhancements:**

- **Route Optimization**: Implement **Dijkstra’s Algorithm** for finding the shortest path between locations.
- **Live Data Integration**: Fetch real-time data on road conditions and service availability.
- **User Authentication**: Allowing users to log in and save custom locations.
- **Data Analytics Dashboard**: Providing statistical insights on service accessibility.

---

## **7. Conclusion**

This project successfully demonstrated how **Flask, OSMnx, and Leaflet.js** can be combined to visualize geospatial data in a meaningful way. Through interactive maps, users can explore critical infrastructure in Nairobi, improving planning and decision-making. By overcoming various technical challenges, the project achieved a **functional, optimized, and visually appealing** geospatial mapping system.

With further improvements, this system could be expanded for **nationwide infrastructure analysis, disaster response planning, and urban development research**, making it a valuable tool for both policymakers and researchers.

---

## **8. References**

- OpenStreetMap API: [https://www.openstreetmap.org](https://www.openstreetmap.org)
- OSMnx Documentation: [https://osmnx.readthedocs.io](https://osmnx.readthedocs.io)
- Flask Framework: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- Leaflet.js: [https://leafletjs.com](https://leafletjs.com)

