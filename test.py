import requests
import json


response = requests.get(
        'https://prod.pkf-m.ru/parser-api/v1/parser/intormet/suppliers/',
        headers={
            'accept': 'application/json',
            'apikey': 'qDas8ppyF4Hrw2ZRbrBXWSkuNbO0gL'
        }
    )
supplier_id = response.json()[0]['id']
print(supplier_id)