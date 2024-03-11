import csv
import io
import urllib.request
from urllib.parse import urlencode

token = "YnVybHV1ZGF5c2FudG9zaGt1bWFyM0BnbWFpbC5jb206ZjBjZmYxNjIwYWMwZWUyMGNmNzhjYmUwNzQ5MTAzYzE1NTYxYjk5Yw=="

headers = {
    'Accept': 'text/csv',
    'Authorization': f'Basic {token}'
}
base_url = 'https://epc.opendatacommunities.org/api/v1/domestic/search'
query_params = {'postcode': 'PO167GZ','from-month':1, 'from-year':2022, 'to-month':1, 'to-year':2024}

encoded_params = urlencode(query_params)

full_url = f"{base_url}?{encoded_params}"

with urllib.request.urlopen(urllib.request.Request(full_url, headers=headers)) as response:
    response_body = response.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(response_body))
    for row in csv_reader:
        energy_rating = row['current-energy-rating']
        building_reference_number = row['building-reference-number']
        certificate_link = f"https://epc.opendatacommunities.org/domestic/certificate/{row['lmk-key']}"
        print(f"Energy Rating: {energy_rating}, Certificate Link: {certificate_link}")
