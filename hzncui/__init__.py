"""Main TUI implementation for Open Horizon Management Hub CUI

Author: Joe Pearson  
Created: 2022-02-19
"""


from curses import wrapper
import py_cui, requests, json, os

__version__ = '0.0.1'

class hzncuiApp:

    def __init__(self, parent):

        hzncuiApp.self = self

        self.parent = parent

        # read Open Horizon configuration from environment variables

        hzn_org_id = os.environ['HZN_ORG_ID']
        exchange_user_admin_pw = os.environ['EXCHANGE_USER_ADMIN_PW']
        hzn_exchange_url = os.environ['HZN_EXCHANGE_URL']

        # retrieve data from the configured Open Horizon Exchange

        r = requests.get(f'{hzn_exchange_url}/orgs/{hzn_org_id}/node-details', auth=(f'{hzn_org_id}/admin', exchange_user_admin_pw))
        data = json.loads(r.text)

        li = ['Nodes', 'Services', 'Patterns', 'Policies', 'Orgs', 'Users']
        self.primary_menu = self.parent.add_scroll_menu('1. Choose an item', 0, 0, row_span=1, column_span=1)
        self.primary_menu.set_selected_color(py_cui.BLACK_ON_YELLOW)
        self.primary_menu.add_item_list(li)

        # create the CUI widget for displaying node details

        self.secondary_menu = self.parent.add_scroll_menu('2. Choose a node to see details', 0, 1, row_span=1, column_span=2)
        self.secondary_menu.set_selected_color(py_cui.BLACK_ON_YELLOW)
        self.secondary_menu.set_on_selection_change_event(hzncuiApp.drawThirdMenu)

        # create a list of IDs from the list of edge node dicts

        lid = []
        self.nodeArray = {}
        for d in data:
            lid.append(d["id"])
            self.nodeArray[d["id"]] = d

        # put the list of IDs into the node details CUI widget

        self.secondary_menu.add_item_list(lid)

        # initialize the detail box

        current_node = self.secondary_menu.get()
        self.tertiary_menu = self.parent.add_scroll_menu('placeholder', 1, 0, row_span=1, column_span=3)

        hzncuiApp.drawThirdMenu(current_node)


    def drawThirdMenu(current_node):

        self = hzncuiApp.self
        
        # create the detail box

        nid = [f'   node type: {self.nodeArray[current_node]["nodeType"]}']
        nid.append(f'architecture: {self.nodeArray[current_node]["arch"]}')
        nid.append(f'    services: {self.nodeArray[current_node]["runningServices"]}')
        nid.append(f'   heartbeat: {self.nodeArray[current_node]["lastHeartbeat"]}')

        self.tertiary_menu.set_title(f'3. Details for node {current_node}')
        self.tertiary_menu.clear()
        self.tertiary_menu.add_item_list(nid)

def main():
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon Management Hub CUI v{__version__}')
    wrapper =  hzncuiApp(root)
    root.start()
