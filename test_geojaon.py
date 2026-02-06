import json

input_file = "maurya1.geojson"
output_file = "maurya_shifted.geojson"

# Adjust this value until the polygons align properly over India
SHIFT_LON = 35.0  # degrees east

def shift_coords(obj):
    """Recursively shift longitudes in coordinate lists."""
    if isinstance(obj, list):
        if len(obj) == 2 and all(isinstance(c, (int, float)) for c in obj):
            lon, lat = obj
            return [lon + SHIFT_LON, lat]
        return [shift_coords(sub) for sub in obj]
    return obj

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for feature in data.get("features", []):
    geom = feature.get("geometry", {})
    if "coordinates" in geom:
        geom["coordinates"] = shift_coords(geom["coordinates"])

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Shifted GeoJSON saved to {output_file}")
