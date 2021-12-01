# encoding: utf-8

import sys
import argparse
from workflow import Workflow, ICON_WEB, ICON_WARNING, web

def get_all_go_links(api_key):
    """Retrieve all Go Links in JSON format
    """
    url = 'https://api.golinks.io/golinks'
    params = dict(limit=100)
    headers = dict(Authorization="Bearer %s" %(api_key))

    r = web.get(url, params, headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by go and extract the links
    response = r.json()
    links = response['results']

    return links

# Generate a string search key for a link
def search_key_for_link(link):
     elements = []
     elements.append(link['name'])  # name
     return u' '.join(elements)

def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --setkey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided API key
    ####################################################################

    # decide what to do based on arguments
    if args.apikey:  # Script was passed an API key
        # save the key
        wf.settings['api_key'] = args.apikey
        return 0  # 0 means script exited cleanly

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

    query = args.query
    links = get_all_go_links(api_key)

    # If script was passed a query, use it to filter links
    if query:
        links = wf.filter(query, links, key=search_key_for_link, min_score=20)

    # Loop through the returned links and adds an item for each to
    # the list of results for Alfred
    for link in links:
        wf.add_item(title=link['name'],
                    subtitle=link['url'],
                    arg=link['name'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))