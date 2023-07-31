import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    json_data = json.loads(response.text)
    return json_data
    
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, json=json_payload, **kwargs)
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    results = []
    if dealer_id:
        json_result = get_request(url, id = dealer_id)
    else:
        json_result = get_request(url)
    if json_result:
        rev = json_result
        reviews = rev["data"]["docs"]
        for view in reviews:
            review_obj = DealerReview(dealership=view["dealership"], name=view["name"], purchase=view["purchase"],
            review=view['review'], purchase_date=view["purchase_date"], car_make=view["car_make"],
            car_model=view["car_model"], car_year=view["car_year"],sentiment=analyze_review_sentiments(view["review"]), id=view["id"])
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/c8f7cc29-a2a4-40f6-86e6-54fbb981f338"
    api_key = "api_key"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(text=dealerreview, language='en',
         features=Features(sentiment=SentimentOptions(targets=[dealerreview]))).get_result()
    label = response["sentiment"]["document"]["label"]
    return label.capitalize

def get_single_dealers(**kwargs):
    results = {}
    # Call get_request with a URL parameter
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/ad3ea32e-d99c-4d84-ac0e-58b0030eb458/dealership-package/get-dealership"
    if 'dealer_id' in kwargs:
        json_result = get_request(url, id=kwargs["dealer_id"])
    else:
        json_result = get_request(url)
    if json_result:
        dealers = json_result[0]
        # Creates a dealer Object from the JSON result
        dealer_obj = CarDealer(address=dealers["address"], city=dealers["city"], full_name=dealers["full_name"],
                                id=dealers["id"], lat=dealers["lat"], long=dealers["long"],
                                short_name=dealers["short_name"],
                                st=dealers["st"], zip=dealers["zip"])
        results["dealer"] = dealer_obj
    return results
