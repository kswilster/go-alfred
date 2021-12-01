# encoding: utf-8

import sys
from workflow import Workflow, ICON_WEB, web

API_KEY = 'GO_LINKS_API_KEY_HERE'

def main(wf):
    url = 'https://api.golinks.io/golinks'
    params = dict(limit=100)
    headers = dict(Authorization="Bearer %s" %(API_KEY))
    r = web.get(url, params, headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by go and extract the links
    response = r.json()
    links = response['results']

    # Loop through the returned links and add an item for each to
    # the list of results for Alfred
    for link in links:
        wf.add_item(title=link['name'],
                    subtitle=link['url'],
                    arg=link['name'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))