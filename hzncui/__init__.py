"""Main TUI implementation for Open Horizon Management Hub CUI

Author: Joe Pearson  
Created: 2022-02-19
"""

from curses import wrapper
import py_cui, requests, json
from .config import load_config, get_config, ConfigError

__version__ = '0.0.1'

class hzncuiApp:

    def __init__(self, parent):
        hzncuiApp.self = self
        self.parent = parent

        try:
            # Load and validate configuration
            load_config()
            
            # Get configuration values
            hzn_org_id = get_config('HZN_ORG_ID')
            exchange_user_admin_pw = get_config('EXCHANGE_USER_ADMIN_PW')
            hzn_exchange_url = get_config('HZN_EXCHANGE_URL')
            
            # retrieve data from the configured Open Horizon Exchange
            r = requests.get(
                f'{hzn_exchange_url}/orgs/{hzn_org_id}/node-details',
                auth=(f'{hzn_org_id}/admin', exchange_user_admin_pw)
            )
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
            for node in data:  # data is a list of node dictionaries
                node_id = node["id"]
                lid.append(node_id)
                self.nodeArray[node_id] = node

            # put the list of IDs into the node details CUI widget
            self.secondary_menu.add_item_list(lid)

            # initialize the detail box
            current_node = self.secondary_menu.get()
            self.tertiary_menu = self.parent.add_scroll_menu('placeholder', 1, 0, row_span=1, column_span=3)

            hzncuiApp.drawThirdMenu(current_node)
            
        except ConfigError as e:
            # Display configuration error in the UI
            self.primary_menu = self.parent.add_scroll_menu('Error', 0, 0, row_span=2, column_span=3)
            self.primary_menu.add_item_list([str(e)])
            self.primary_menu.set_selected_color(py_cui.RED_ON_BLACK)
        except Exception as e:
            # Display any other errors in the UI
            self.primary_menu = self.parent.add_scroll_menu('Error', 0, 0, row_span=2, column_span=3)
            self.primary_menu.add_item_list([f"Error: {str(e)}"])
            self.primary_menu.set_selected_color(py_cui.RED_ON_BLACK)

    def drawThirdMenu(current_node):
        self = hzncuiApp.self
        
        # create the detail box
        node = self.nodeArray[current_node]
        nid = [
            f'   node type: {node["nodeType"]}',
            f'architecture: {node["arch"]}',
            f'    services: {node["runningServices"]}',
            f'   heartbeat: {node["lastHeartbeat"]}',
            f'      owner: {node["owner"]}',
            f'       name: {node["name"]}'
        ]

        self.tertiary_menu.set_title(f'3. Details for node {current_node}')
        self.tertiary_menu.clear()
        self.tertiary_menu.add_item_list(nid)

def main():
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon Management Hub CUI v{__version__}')
    wrapper = hzncuiApp(root)
    root.start()
