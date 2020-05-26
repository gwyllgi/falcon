from googleapiclient.discovery import build

import settings as discord_settings


def search_google(search_term, **kwargs):
    """
    search_google
        method to return google search result in formatted data
    :param search_term: Search keyword
    :param kwargs:
    :return: Search results
    """
    service = build("customsearch", "v1", developerKey=discord_settings.GOOGLE_API_KEY)
    results = service.cse().list(
        q=search_term,
        cx=discord_settings.GOOGLE_CSE_KEY,
        **kwargs,
    ).execute()
    results = results.get('items', [])

    # create formatted search results from the above results
    search_result = []
    for result in results[:discord_settings.MAX_SEARCH_RESULT_COUNT]:
        search_result.append({
            'title': result.get('title'),
            'link': result.get('link'),
            'description': result.get('snippet')
        })
    return search_result
