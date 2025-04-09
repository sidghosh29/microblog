import requests
from flask_babel import _
from app import app

# Read Documentation: https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/reference/v3/translate
def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
            not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'southeastasia',
    }

    endpoint = "https://api.cognitive.microsofttranslator.com"
    path='/translate'
    constructed_url = endpoint+path
    params = {
    'api-version': '3.0',
    'from': source_language,
    'to': dest_language
    }

    # request = requests.post(constructed_url, params=params, headers=headers, json=body)
    r = requests.post(constructed_url, params=params, headers=auth, json=[{'Text': text}])

    # r is the response object
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return r.json()[0]['translations'][0]['text']