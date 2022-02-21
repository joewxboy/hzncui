"""Main TUI implementation for Open Horizon Management Hub CUI

Author: Joe Pearson  
Created: 2022-02-19
"""


import py_cui, requests, json, os

__version__ = '0.0.1'

class hzncuiApp:

    def __init__(self, parent):

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

        # create a list of IDs from the list of edge node dicts

        lid = []
        for d in data:
            lid.append(d["id"])

        # put the list of IDs into the node details CUI widget

        self.secondary_menu.add_item_list(lid)

        # create the detail box

        current_node = self.secondary_menu.get()
        self.detail_box = self.parent.add_block_label(f'3. Details for node {current_node}', 1, 0, row_span=1, column_span=3, padx=0, pady=0)

def main():
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon Management Hub CUI v{__version__}')
    wrapper =  hzncuiApp(root)
    root.start()
