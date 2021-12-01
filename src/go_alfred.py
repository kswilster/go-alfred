# encoding: utf-8

import sys
import argparse
from workflow import Workflow, ICON_WEB, ICON_WARNING, web

# Retrieve all Go Links in JSON format
def get_all_go_links(api_key):
    url = 'https://api.golinks.io/golinks'
    limit = 100
    offset = 0
    last_page = False
    headers = dict(Authorization="Bearer %s" %(api_key))
    links = []

    while not last_page:
      params = dict(limit=limit, offset=offset)

      r = web.get(url, params, headers)

      # throw an error if request failed
      # Workflow will catch this and show it to the user
      r.raise_for_status()

      # Parse the JSON returned by go and extract the links
      response = r.json()
      total_results = response['metadata']['total_results']
      links += response['results']
      if (limit + offset >= total_results):
        last_page = True
      offset += limit

    return links

# Generate a string search key for a link
def search_key_for_link(link):
     elements = []
     elements.append(link['name'])  # name
     elements.append(link['description']) # description
     return u' '.join(elements)

def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --setkey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    # arg for clearing api key
    parser.add_argument('--clearkey', dest='clearkey', nargs='?', const=True)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save or Clear an API key
    #####################################################################

    # clear key
    if args.clearkey:
      wf.settings['api_key'] = False
      return 0

    # save key
    if args.apikey:
        wf.settings['api_key'] = args.apikey
        return 0

    ####################################################################
    # Check that we have an API key saved
    ####################################################################

    api_key = wf.settings.get('api_key', None)

    if not api_key:  # API key has not yet been set
        wf.add_item('No API key set.',
                    'Please use gosetkey to set your GoLinks API key.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # View GO Links
    ####################################################################

    # Retrieve links from cache if available
    # Cache is invalidated after 24 hours
    def get_go_links_with_api_key():
        return get_all_go_links(api_key)

    links = wf.cached_data('links', get_go_links_with_api_key, max_age=60*60*24)
    query = args.query

    # If script was passed a query, use it to filter links
    if query:
        links = wf.filter(query, links, key=search_key_for_link, min_score=20)

    # Loop through the returned links and adds an item for each to
    # the list of results for Alfred
    for link in links:
        wf.add_item(title=link['name'],
                    subtitle=link['description'],
                    arg=link['name'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))