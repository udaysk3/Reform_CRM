import hmac
from hashlib import sha1
import urllib.request
import json
import base64

token = "CAPtZUnRJQitAkvDqHBGNgYEogkjgoKRUaQRTIEf"

headers = {"Accept": "application/json", "Authorization": f"Basic {token}"}


def sign_url(url, key, secret):
    url += f"ApplicationKey={key}"
    signature = base64.b64encode(
        hmac.new(secret.encode(), url.encode(), sha1).digest()
    ).decode()
    url += f"&Signature={signature}"
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ) as response:
            response_body = response.read().decode()
            json_response = json.loads(response_body)
            if "area-array" in json_response and json_response["area-array"]:
                first_area = json_response["area-array"][0]
                short_label = first_area.get("shortLabel", None)
                if short_label:
                    print(f"Short Label: {short_label}")
                    return short_label
                else:
                    print("Short Label not found in the response.")
                    return None
            else:
                print("Invalid or empty response.")
                return None

    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response: {e.read().decode()}")
        return None
    except urllib.error.URLError as e:
        print(f"URLError: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def getLA(searchText):
    searchText = searchText.replace(" ", "")
    return sign_url(
        f"http://webservices.esd.org.uk/areas?searchText={searchText}&",
        "OxbQLXXqwAwghwvmycrbHtIgHGdFPhZlbvakqHyW",
        "WPgIAQmXypXmKckAEdhf",
    )


# Test the function
short_label = sign_url(
    "http://webservices.esd.org.uk/areas?searchText=sw11&",
    "OxbQLXXqwAwghwvmycrbHtIgHGdFPhZlbvakqHyW",
    "WPgIAQmXypXmKckAEdhf",
)
print(f"Short label obtained: {short_label}")