from flask import Flask, request, jsonify
from flask_cors import CORS
from mapquadlib import HereQuad

app = Flask(__name__)
CORS(app)

def polygon_geojson(west, south, east, north, props=None):
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": props or {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [west, south],
                    [west, north],
                    [east, north],
                    [east, south],
                    [west, south]
                ]]
            }
        }]
    }

@app.route("/api/tile", methods=["POST"])
def api_tile():
    try:
        data = request.get_json(force=True) or {}
        tile_id = int(str(data.get("tile_id", "")).strip())
        # Correct HERE package usage: construct from long key (tile id)
        qb = HereQuad.from_long_key(tile_id)
        bb = qb.bounding_box
        resp = {
            "ok": True,
            "tile": {
                "id": tile_id,
                "level": qb.level
            },
            "bbox": [bb.west, bb.south, bb.east, bb.north],
            "geojson": polygon_geojson(bb.west, bb.south, bb.east, bb.north, {"level": qb.level})
        }
        return jsonify(resp)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)