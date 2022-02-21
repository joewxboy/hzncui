"""Main TUI implementation for Open Horizon CUI

Author: Joe Pearson  
Created: 2022-02-19
"""


import py_cui, requests, json, os

__version__ = 'v0.0.1'

class hzncuiApp:

    def __init__(self, master):

        self.master = master
        hzn_org_id = os.environ['HZN_ORG_ID']
        exchange_user_admin_pw = os.environ['EXCHANGE_USER_ADMIN_PW']
        hzn_exchange_url = os.environ['HZN_EXCHANGE_URL']

        r = requests.get(f'{hzn_exchange_url}/orgs/{hzn_org_id}/node-details', auth=(f'{hzn_org_id}/admin', exchange_user_admin_pw))
        data = json.loads(r.text)

        self.edge_nodes_menu = self.master.add_scroll_menu('Select edge node', 0, 0, row_span=1, column_span=3)
        self.edge_nodes_menu.set_selected_color(py_cui.BLACK_ON_YELLOW)
        
        lid = []
        for d in data:
            lid.append(d["id"])

        self.edge_nodes_menu.add_item_list(lid)

def main():
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon CUI {__version__}')
    wrapper =  hzncuiApp(root)
    root.start()
