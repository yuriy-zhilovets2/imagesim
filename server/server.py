#!/home/space/prog/imagededup/bin/python3
import weaviate

from imagededup.methods import CNN
from weaviate.util import generate_uuid5
from flask import Flask, request
from ext import CNNext

collection = "PastVu"

hasher = CNNext()

client = weaviate.Client(
    url = "http://weaviate:8080",
)

app = Flask(__name__)

###

@app.put("/fingerprint/<name>")
def add_fingerprint(name):
  try:
    if 'image' not in request.files:
      return ("No image uploaded", 400)

    region = request.form.get("region", "")
    
    if not region:
      return ("region is missing", 400)  
    
    uuid = uuid_by_name(name)
    
    rec = client.data_object.get_by_id(uuid, class_name=collection)
    if (rec is not None):
      return (f"Image '{name}' already exists", 409)

    fp = hasher.cnn_encode_stream(request.files['image'].stream)

    client.data_object.create(
      data_object={
        "name": name,
        "region": region,
      },
      class_name=collection,
      uuid=uuid,
      vector=fp,
    )
    
    return {
        "name": name,
        "region": region,
    }
    
  except Exception as e:
    return (str(e), 500)
  
###  

@app.patch("/fingerprint/<name>")
def update_fingerprint(name):
  try:
    uuid = uuid_by_name(name)
    rec = client.data_object.get_by_id(uuid, class_name=collection)
    if (rec is None):
      return (f"Image '{name}' not found", 404)

    region = request.form.get("region", "")

    fp = None
    if 'image' in request.files:
      fp = hasher.cnn_encode_stream(request.files['image'].stream)
      
    if fp is not None or region:
      args = {
        "uuid": uuid,
        "class_name": collection,
        "data_object": {},
      }

      if region:
        args["data_object"]["region"] = region
        
      if fp is not None:
        args["vector"] = fp

      client.data_object.update(**args)

    rec = client.data_object.get_by_id(uuid, class_name=collection)
    return rec["properties"]

  except Exception as e:
    return (str(e), 500)
  
###  
  
@app.delete("/fingerprint/<name>")
def del_fingerprint(name):
  try:
    uuid = uuid_by_name(name)

    rec = client.data_object.get_by_id(uuid, class_name=collection)
    if (rec is None):
      return (f"Image '{name}' not found", 404)
    
    client.data_object.delete(
      uuid=uuid,
      class_name=collection,
    )
    
    return ("", 204)

  except Exception as e:
    return (str(e), 500)

###  

@app.post("/match")
def match():
  try:
    limit = request.form.get('limit', 10, int)
    distance = request.form.get('distance', 0.1, float)
    region = request.form.get('region', '')
    
    if 'image' not in request.files:
      return ("No image uploaded", 400)

    fp = hasher.cnn_encode_stream(request.files['image'].stream)
    query = make_query(region, limit, distance).with_near_vector({
        "vector": fp,
        "distance": distance,
    })
  
    return decorate(query.do(), "")

  except Exception as e:
    return (str(e), 500)

###    

@app.get("/match/<name>")
def match_id(name):
  try:
    uuid = uuid_by_name(name)
    limit = request.args.get('limit', 10, int)
    distance = request.args.get('distance', 0.1, float)
    region = request.args.get('region', '')
    
    rec = client.data_object.get_by_id(uuid, class_name=collection)
    if (rec is None):
      return (f"Image '{name}' is not found", 404)
  
    # limit+1, потому что мы убираем из вывода этот же самый объект
    query = make_query(region, limit+1, distance).with_near_object({
        "id": uuid_by_name(name),
        "distance": distance,
    })
  
    return decorate(query.do(), name)

  except Exception as e:
    return (str(e), 500)
  
######################################

def make_query(region, limit, distance):
  query = (
    client.query
    .get(collection, ["name", "region"])
    .with_limit(limit)
    .with_additional(["distance"])
  )

  if region:
    query = query.with_where({
        "path": ["region"],
        "operator": "Equal",
        "valueText": region,
    })

  return query

# {"data":{"Get":{"PastVu":[{"_additional":{"distance":-7.1525574e-07},"name":"buda2.jpg","region":"1"},{"_additional":{"distance":0.0067709684},"name":"buda.jpg","region":"1"}]}}}  
# {'data': {'Get': {'PastVu': None}}, 'errors': [{'locations': [{'column': 6, 'line': 1}], 'message': 'explorer: get class: vectorize params: nearObject params: vector not found', 'path': ['Get', 'PastVu']}]}
def decorate(response, name):
  if "errors" in response:
    return ("\n".join(list(
      map(lambda rec: rec["message"], response["errors"])
    )), 500)
  else:
    l = response["data"]["Get"]["PastVu"]
    return list(
      filter(lambda rec: rec["name"] != name,
        map(lambda rec: {"name": rec["name"], "distance": rec["_additional"]["distance"], "region": rec["region"]}, l)
      )
    )

#PUT  /fingerprint/name image, region -> {...}
#PATCH /fingerprint/name image,region
#DELETE /fingerprint/name

#GET /match image, region, distance, limit
#GET /match/id region, distance, limit

def uuid_by_name(name) -> str:
  return generate_uuid5(name)
