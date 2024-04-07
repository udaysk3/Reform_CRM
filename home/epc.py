import csv
import io
import urllib.request
from io import StringIO
import json
from urllib.parse import urlencode

def parse_recommendations(recommendations_url, headers):
    with urllib.request.urlopen(urllib.request.Request(recommendations_url, headers=headers)) as response:
        csv_data = response.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_data))
        print(csv_data)
        recommendations_list = []
        for row in csv_reader:
            indicative_cost = row['indicative-cost'].replace('£', '').replace(',', '')
            text = row['improvement-descr-text']
            if row['improvement-descr-text'] == '':
                try:
                    with open('home/unique_records.json', 'r') as json_file:
                        json_data = json.load(json_file)
                        text = json_data[row['improvement-id']]['improvement_summary_text']
                except FileNotFoundError:
                    text = None
            recommendation_text = f"{text} , £({indicative_cost})"
            print(text, indicative_cost)
            print(recommendation_text)
            recommendations_list.append(recommendation_text)
        recommendations_str = '<br>'.join(recommendations_list)
        
        return recommendations_str

def getEPC(postcode, house_name, street_name):
    customer_address = f"{house_name} {street_name}".lower()
    token = "YnVybHV1ZGF5c2FudG9zaGt1bWFyM0BnbWFpbC5jb206ZjBjZmYxNjIwYWMwZWUyMGNmNzhjYmUwNzQ5MTAzYzE1NTYxYjk5Yw=="

    headers = {
        'Accept': 'text/csv',
        'Authorization': f'Basic {token}'
    }
    postcode = postcode.replace(' ', '')
    base_url = 'https://epc.opendatacommunities.org/api/v1/domestic/search'
    recommendations_url = "https://epc.opendatacommunities.org/api/v1/domestic/recommendations/"
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
            # print(row)
            dataset_address_cleaned = row['address'].replace(' ', '').strip(',').lower().replace(',', '')
            address_dataset  = row['address'].split(',')[0].replace(' ', '').lower()
            cleaned_house_name = house_name.replace(' ', '').lower()
            if address_dataset[:len(cleaned_house_name)]==cleaned_house_name and customer_address_cleaned in dataset_address_cleaned:
                most_similar_data = row
                break
        parsed_recommendations = []
        if most_similar_data:
            energy_rating = most_similar_data['current-energy-rating']
            certificate_link = f"https://epc.opendatacommunities.org/domestic/certificate/{most_similar_data['lmk-key']}"
            recommendations_url += most_similar_data['lmk-key']
            parsed_recommendations = parse_recommendations(recommendations_url, headers)
            print(parsed_recommendations)
            return {'energy_rating': energy_rating, 'energy_certificate_link': certificate_link, "county" : row['county'], "local_authority"  : row['local-authority-label'], "constituency" : row['constituency-label'], "town" : row['posttown'], "address" : row['address'], "recommendations" : parsed_recommendations}
        else:
            return {'energy_rating': None, 'energy_certificate_link': None, "county" : None, "local_authority"  : None, "constituency" : None, "town" : None, "address" : None, "recommendations" : parsed_recommendations}