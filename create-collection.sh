curl \
-X POST \
-H "Content-Type: application/json" \
-d '{
    "class": "PastVu",
    "description": "Vectors of Pastvu photo fingerprints",
    "vectorIndexType": "hnsw",
    "vectorIndexConfig": {
        "distance": "cosine"
    },
    "vectorizer": "none",
    "properties": [
        {
            "dataType": [
                "text"
            ],
            "description": "Name of a photo (e.g. numeric id)",
            "name": "title",
            "indexFilterable": false,
            "indexSearchable": false
        },
        {
            "dataType": [
                "text"
            ],
            "description": "Region of a photo",
            "name": "region",
            "indexFilterable": true,
            "indexSearchable": false
        }
    ]
}' \
http://localhost:8080/v1/schema
