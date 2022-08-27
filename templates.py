from db import DB
import json


elements = []
for category in DB['categories'].values():
  title = category['title']
  description = category['description']
  elements.append(
           {
      "title": title,
      "description": description,
      "buttons": [
        {
          "action": {
            "type": "text",
            "label": title
          }
        }
      ]
      } 
    )

data = {
  "type": "carousel",
  "elements": elements
}

CATEGORIES_TEMPLATE= json.dumps(data)
