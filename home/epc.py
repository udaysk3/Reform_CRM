import csv
import io
import urllib.request
from urllib.parse import urlencode

def getEPC(postcode, house_name, street_name):
    customer_address = f"{house_name} {street_name}".lower()
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
            print(row['address'])
            dataset_address_cleaned = row['address'].replace(' ', '').strip(',').lower().replace(',', '')
            address_dataset  = row['address'].split(',')[0].replace(' ', '').lower()
            cleaned_house_name = house_name.replace(' ', '').lower()
            print(dataset_address_cleaned, customer_address_cleaned, address_dataset)
            print(address_dataset[:len(house_name)], house_name)
            if address_dataset[:len(cleaned_house_name)]==cleaned_house_name and customer_address_cleaned in dataset_address_cleaned:
                most_similar_data = row
                break

        if most_similar_data:
            energy_rating = most_similar_data['current-energy-rating']
            certificate_link = f"https://epc.opendatacommunities.org/domestic/certificate/{most_similar_data['lmk-key']}"
            print(row)
            return {'energy_rating': energy_rating, 'energy_certificate_link': certificate_link, "county" : row['county'], "local_authority"  : row['local-authority-label'], "constituency" : row['constituency-label'], "town" : row['posttown'], "address" : row['address']}
        else:
            return {'energy_rating': None, 'energy_certificate_link': None, "county" : None, "local_authority"  : None, "constituency" : None, "town" : None, "address" : None}