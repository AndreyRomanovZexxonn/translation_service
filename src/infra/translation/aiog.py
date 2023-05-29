import asyncio
import json
import pprint

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from google.cloud import translate_v3
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("./service-account.json")
creds = ServiceAccountCreds(scopes=["https://www.googleapis.com/auth/cloud-platform"], **json.load(open('service-account.json')))


async def translate_to_latin(words):
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        language = await aiogoogle.discover('translate', 'v2')
        words = dict(q=[words], target='la')
        result = await aiogoogle.as_service_account(
            language.translations.translate(json=words)
        )
    """
    {'data': {'translations': [{'detectedSourceLanguage': 'en',
                            'translatedText': 'terribilis'}]}}
    """
    pprint.pprint(result)


def translate():
    asyncio.run(translate_to_latin('awesome'))
from google.cloud.translate_v3.types import TranslateDocumentResponse, TranslateTextResponse

async def sample_delete_glossary():
    # Create a client
    client = translate_v3.TranslationServiceAsyncClient(credentials=credentials)

    # Initialize request argument(s)
    request = translate_v3.TranslateTextRequest(
        contents=['прикольный',],
        source_language_code="ru",
        target_language_code="en-US",
        parent="projects/dh-adtech"
    )

    # Make the request
    operation = client.translate_text(request=request)

    print("Waiting for operation to complete...")

    response = (await operation).result()

    # Handle the response
    print(response)

from googletrans.models import Translated
from googletrans.models import TranslatedPart

def translate2():
    asyncio.run(sample_delete_glossary())


from googletrans import Translator
translator = Translator()
translator.translate('привет')
