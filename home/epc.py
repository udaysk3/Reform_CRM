import csv
import io
import urllib.request
from urllib.parse import urlencode
from fuzzywuzzy import fuzz

def getEPC(postcode, customer_address):
    token = "YnVybHV1ZGF5c2FudG9zaGt1bWFyM0BnbWFpbC5jb206ZjBjZmYxNjIwYWMwZWUyMGNmNzhjYmUwNzQ5MTAzYzE1NTYxYjk5Yw=="

    headers = {
        'Accept': 'text/csv',
        'Authorization': f'Basic {token}'
    }
    postcode = postcode.replace(' ', '')
    base_url = 'https://epc.opendatacommunities.org/api/v1/domestic/search'
    query_params = {'postcode': postcode,'from-month':1, 'from-year':2008, 'to-month':1, 'to-year':2024}

    encoded_params = urlencode(query_params)

    full_url = f"{base_url}?{encoded_params}"

    with urllib.request.urlopen(urllib.request.Request(full_url, headers=headers)) as response:
        response_body = response.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(response_body))
        most_similar_data = None
        max_similarity_score = 0
        
        # Remove spaces and trailing commas from customer address
        customer_address_cleaned = customer_address.replace(' ', '').strip(',').lower()
        
        for row in csv_reader:
            dataset_address_cleaned = row['address'].replace(' ', '').strip(',').lower()
            address_dataset  = row['address'].split(',')[0].replace(' ', '').lower()
            print(dataset_address_cleaned, customer_address_cleaned)
            print(row['address'])
            if address_dataset == customer_address_cleaned:
                most_similar_data = row
                break

        if most_similar_data:
            energy_rating = most_similar_data['current-energy-rating']
            certificate_link = f"https://epc.opendatacommunities.org/domestic/certificate/{most_similar_data['lmk-key']}"
            return {'energy_rating': energy_rating, 'energy_certificate_link': certificate_link}
        else:
            return {'energy_rating': None, 'energy_certificate_link': None}