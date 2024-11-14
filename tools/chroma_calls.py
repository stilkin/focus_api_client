import json
import sys

import chromadb

sys.path.append('../')

from fooocus.fc_settings import all_fc_styles

chroma_client = chromadb.PersistentClient('../tools/chroma/chroma.sqlite')
DEFAULT_STYLES = '["Fooocus V2", "Fooocus Photograph", "Fooocus Negative"]'


def cdb_insert():
    keys = []
    for i in range(len(all_fc_styles)):
        keys.append(f'{i}')

    collection = chroma_client.get_or_create_collection(name='all_fc_styles')
    collection.upsert(
        documents=all_fc_styles,
        ids=keys
    )


def cdb_query(prompt, n_results=3):
    collection = chroma_client.get_or_create_collection(name='all_fc_styles')
    results = collection.query(
        query_texts=[prompt],  # Chroma will embed this for you
        n_results=n_results  # how many results to return
    )
    return results


def get_style_guess(prompt):
    cdb_results = cdb_query(prompt, n_results=3)
    if cdb_results is not None and 'documents' in cdb_results:
        style_array = cdb_results['documents'][0]
        return json.dumps(style_array)
    return DEFAULT_STYLES

# cdb_insert()  # TODO: RUN ONCE AFTER INSTALLATION
# print(get_style_guess('an impressionist painting of megatron'))
