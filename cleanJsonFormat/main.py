import random
import json
# Ejemplo de lista de objetos con diferentes categorías
objetos_con_categorias =[{
  "_id": "0UpMGVwAdG",
  "secondary_images": [
    "diving_gear.jpg",
    "diving_underwater.jpg"
  ],
  "contact": {
    "address": "789 Dive Center Street",
    "document": "VWX789",
    "phone": "+654-789-0123"
  },
  "details": {
    "features": [
      "Underwater exploration",
      "Certified instructors"
    ],
    "description": "Experience the thrill of underwater exploration with our scuba diving expedition. Dive into vibrant marine ecosystems and discover a world of wonders beneath the surface.",
    "schedule": "schedule",
    "location": "location"
  },
  "reservation022": [
    {
      "qty": 1,
      "date": {
        "startDate": {
          "year": 2024,
          "month": 6,
          "day": 5
        },
        "endDate": {
          "year": 2024,
          "month": 6,
          "day": 5
        }
      }
    }
  ],
  "_p_userId": "_User$tDrKkyBCPE",
  "category": "Deportes",
  "activity": "Atletismo",
  "provider": "LLC",
  "main_image": "diving_main.jpg",
  "price": 80,
  "title": "Scuba Diving Expedition",
  "qty": 500,
  "status": "accepted",
  "_created_at": {
    "$date": "2024-07-08T21:55:16.046Z"
  },
  "_updated_at": {
    "$date": "2024-10-14T14:58:02.160Z"
  }
},
{
  "_id": "vVVg1hUhYR",
  "secondary_images": [
    "diving_gear.jpg",
    "diving_underwater.jpg"
  ],
  "contact": {
    "address": "789 Dive Center Street",
    "document": "VWX789",
    "phone": "+654-789-0123"
  },
  "details": {
    "features": [
      "Underwater exploration",
      "Certified instructors"
    ],
    "description": "Experience the thrill of underwater exploration with our scuba diving expedition. Dive into vibrant marine ecosystems and discover a world of wonders beneath the surface.",
    "schedule": "schedule",
    "location": "location"
  },
  "reservation022": [
    {
      "qty": 1,
      "date": {
        "startDate": {
          "year": 2024,
          "month": 6,
          "day": 5
        },
        "endDate": {
          "year": 2024,
          "month": 6,
          "day": 5
        }
      }
    }
  ],
  "_p_userId": "_User$SYVSM6Cc7v",
  "category": "Deportes",
  "activity": "Atletismo",
  "provider": "LLC",
  "main_image": "diving_main.jpg",
  "price": 80,
  "title": "Scuba Diving Expedition",
  "qty": 500,
  "status": "accepted",
  "_created_at": {
    "$date": "2024-07-08T22:30:26.219Z"
  },
  "_updated_at": {
    "$date": "2024-10-14T14:52:51.749Z"
  }
},
{
  "_id": "a0RVKlQa16",
  "secondary_images": [
    "https://res.cloudinary.com/dge3tzzsh/image/upload/v1720801093/gravitad_general/qoetwcsx0t0ebynwdo3w.png"
  ],
  "contact": {
    "address": "asdsadsadsad",
    "document": "2654554545",
    "phone": "0424-747-2652"
  },
  "details": {
    "features": [
      "comodo"
    ],
    "description": "adasdasdasd"
  },
  "_p_userId": "_User$GSx4UdErFL",
  "category": "Hospedaje",
  "activity": "Cabaña",
  "provider": "Autónomo",
  "main_image": "https://res.cloudinary.com/dge3tzzsh/image/upload/v1720801078/gravitad_general/epngd0je7tmk7omhmalw.png",
  "price": 33,
  "title": "wqweeqwe",
  "qty": 499,
  "status": "accepted",
  "_created_at": {
    "$date": "2024-07-12T16:18:35.142Z"
  },
  "_updated_at": {
    "$date": "2024-10-14T14:57:21.174Z"
  },
  "reservation022": [
    {
      "qty": 1,
      "date": {
        "startDate": {
          "year": 2024,
          "month": 10,
          "day": 11
        },
        "endDate": {
          "year": 2024,
          "month": 10,
          "day": 18
        }
      }
    }
  ]
},
{
  "_id": "AlcceBBg7F",
  "secondary_images": [
    "https://res.cloudinary.com/dge3tzzsh/image/upload/v1720817287/gravitad_general/gohqouqsv2um9xzbassl.png"
  ],
  "contact": {
    "address": "sdfdf",
    "document": "2654554545",
    "phone": "+5804247472652"
  },
  "details": {
    "features": [
      "adsadsadad"
    ],
    "description": "adasdasdasd"
  },
  "_p_userId": "_User$GSx4UdErFL",
  "category": "Transporte",
  "activity": "Hotel",
  "provider": "Autónomo",
  "main_image": "https://res.cloudinary.com/dge3tzzsh/image/upload/v1720817294/gravitad_general/wk04vcue4zdqdee0jnj0.png",
  "price": 80,
  "title": "jjjjjj",
  "qty": 500,
  "status": "accepted",
  "_created_at": {
    "$date": "2024-07-12T20:48:33.265Z"
  },
  "_updated_at": {
    "$date": "2024-10-16T18:59:49.185Z"
  }
},
{
  "_id": "R7vjXneQd7",
  "secondary_images": [
    "diving_gear.jpg",
    "diving_underwater.jpg"
  ],
  "contact": {
    "address": "789 Dive Center Street",
    "document": "VWX789",
    "phone": "+654-789-0123"
  },
  "details": {
    "features": [
      "Underwater exploration",
      "Certified instructors"
    ],
    "description": "Experience the thrill of underwater exploration with our scuba diving expedition. Dive into vibrant marine ecosystems and discover a world of wonders beneath the surface."
  },
  "category": "Deportes",
  "activity": "Atletismo",
  "provider": "LLC",
  "main_image": "diving_main.jpg",
  "price": 80,
  "title": "Scuba Diving Expedition",
  "qty": 500,
  "status": "pending",
  "_created_at": {
    "$date": "2024-10-14T15:03:28.188Z"
  },
  "_updated_at": {
    "$date": "2024-10-14T15:03:28.188Z"
  }
},
{
  "_id": "lHsEa4IjdZ",
  "secondary_images": [
    "diving_gear.jpg",
    "diving_underwater.jpg"
  ],
  "contact": {
    "address": "789 Dive Center Street",
    "document": "VWX789",
    "phone": "+654-789-0123"
  },
  "details": {
    "features": [
      "Underwater exploration",
      "Certified instructors"
    ],
    "description": "Experience the thrill of underwater exploration with our scuba diving expedition. Dive into vibrant marine ecosystems and discover a world of wonders beneath the surface."
  },
  "category": "Hoteleria",
  "activity": "Atletismo",
  "provider": "LLC",
  "main_image": "diving_main.jpg",
  "price": 80,
  "title": "Scuba Diving Expedition",
  "qty": 500,
  "status": "rejected",
  "_created_at": {
    "$date": "2024-10-14T15:03:48.377Z"
  },
  "_updated_at": {
    "$date": "2024-10-14T15:04:10.895Z"
  }
},
{
  "_id": "jbs2a1GHOr",
  "secondary_images": [
    "diving_gear.jpg",
    "diving_underwater.jpg"
  ],
  "contact": {
    "address": "789 Dive Center Street",
    "document": "VWX789",
    "phone": "+654-789-0123"
  },
  "details": {
    "features": [
      "Underwater exploration",
      "Certified instructors"
    ],
    "description": "Experience the thrill of underwater exploration with our scuba diving expedition. Dive into vibrant marine ecosystems and discover a world of wonders beneath the surface."
  },
  "category": "Deporte",
  "activity": "Atletismo",
  "provider": "LLC",
  "main_image": "diving_main.jpg",
  "price": 100,
  "title": "Atletismo 1",
  "qty": 500,
  "status": "accepted",
  "_created_at": {
    "$date": "2024-10-14T15:20:54.198Z"
  },
  "_updated_at": {
    "$date": "2024-10-16T18:58:17.951Z"
  }
}]

# Lista para almacenar los nuevos objetos
nuevos_objetos = []
# Recorrer cada objeto en la lista original
for objeto in objetos_con_categorias:
    # Crear 10 nuevos elementos por cada objeto
    for _ in range(10):
        # Crear un nuevo objeto con las propiedades originales y el nuevo parámetro 'price'
        nuevo_objeto = {
            "_id": objeto["_id"],
            "category": objeto["category"],
            "activity": objeto["activity"],
            "price": random.randint(0, 1000)  # Generar un valor aleatorio entre 0 y 1000
        }
        
        # Agregar el nuevo objeto a la lista de nuevos objetos
        nuevos_objetos.append(nuevo_objeto)

# Imprimir la lista de nuevos objetos
print(nuevos_objetos)
# Guardar la lista de nuevos objetos en un archivo JSON
with open('nuevos_objetos.json', 'w') as file:
    json.dump(nuevos_objetos, file, indent=4)

# Contar los elementos en la lista de nuevos objetos
cantidad_nuevos_objetos = len(nuevos_objetos)

# Imprimir la cantidad de nuevos objetos
print("Cantidad de nuevos objetos:", cantidad_nuevos_objetos)