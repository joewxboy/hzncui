"""Main TUI implementation for Open Horizon Management Hub CUI

Author: Joe Pearson  
Created: 2022-02-19
"""

from curses import wrapper
import py_cui, requests, json
import logging
from .config import load_config, get_config, ConfigError

__version__ = '0.0.1'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class hzncuiApp:

    def __init__(self, parent):
        hzncuiApp.self = self
        self.parent = parent

        try:
            # Load and validate configuration
            logger.info("Loading configuration...")
            load_config()
            
            # Get configuration values
            logger.info("Retrieving configuration values...")
            hzn_org_id = get_config('HZN_ORG_ID')
            exchange_user_admin_pw = get_config('EXCHANGE_USER_ADMIN_PW')
            hzn_exchange_url = get_config('HZN_EXCHANGE_URL')
            
            logger.info(f"Using Exchange URL: {hzn_exchange_url}")
            logger.info(f"Using Organization ID: {hzn_org_id}")
            
            # retrieve data from the configured Open Horizon Exchange
            r = requests.get(
                f'{hzn_exchange_url}/orgs/{hzn_org_id}/node-details',
                auth=(f'{hzn_org_id}/admin', exchange_user_admin_pw)
            )
            
            # Log the raw response for debugging
            logger.debug(f"Raw response: {r.text}")
            
            try:
                data = json.loads(r.text)
                logger.debug(f"Parsed data type: {type(data)}")
                logger.debug(f"Parsed data: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise
            
            if not isinstance(data, list):
                logger.error(f"Expected list of nodes, got {type(data)}")
                raise ValueError("Invalid response format: expected list of nodes")

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
            
            for node in data:
                try:
                    if not isinstance(node, dict):
                        logger.error(f"Expected node to be a dictionary, got {type(node)}")
                        continue
                        
                    node_id = node.get("id")
                    if not node_id:
                        logger.error(f"Node missing 'id' field: {node}")
                        continue
                        
                    lid.append(node_id)
                    self.nodeArray[node_id] = node
                    logger.debug(f"Added node {node_id} to list")
                except Exception as e:
                    logger.error(f"Error processing node: {e}")
                    continue

            if not lid:
                raise ValueError("No valid nodes found in response")

            # put the list of IDs into the node details CUI widget
            self.secondary_menu.add_item_list(lid)

            # initialize the detail box
            current_node = self.secondary_menu.get()
            self.tertiary_menu = self.parent.add_scroll_menu('placeholder', 1, 0, row_span=1, column_span=3)

            hzncuiApp.drawThirdMenu(current_node)
            
        except ConfigError as e:
            # Display configuration error in the UI
            logger.error(f"Configuration error: {e}")
            self.primary_menu = self.parent.add_scroll_menu('Error', 0, 0, row_span=2, column_span=3)
            self.primary_menu.add_item_list([str(e)])
            self.primary_menu.set_selected_color(py_cui.RED_ON_BLACK)
        except Exception as e:
            # Display any other errors in the UI
            logger.error(f"Application error: {e}", exc_info=True)
            self.primary_menu = self.parent.add_scroll_menu('Error', 0, 0, row_span=2, column_span=3)
            self.primary_menu.add_item_list([f"Error: {str(e)}"])
            self.primary_menu.set_selected_color(py_cui.RED_ON_BLACK)

    def drawThirdMenu(current_node):
        self = hzncuiApp.self
        
        try:
            # create the detail box
            node = self.nodeArray.get(current_node)
            if not node:
                logger.error(f"Node {current_node} not found in nodeArray")
                return
                
            nid = [
                f'   node type: {node.get("nodeType", "N/A")}',
                f'architecture: {node.get("arch", "N/A")}',
                f'    services: {node.get("runningServices", "N/A")}',
                f'   heartbeat: {node.get("lastHeartbeat", "N/A")}',
                f'      owner: {node.get("owner", "N/A")}',
                f'       name: {node.get("name", "N/A")}'
            ]

            self.tertiary_menu.set_title(f'3. Details for node {current_node}')
            self.tertiary_menu.clear()
            self.tertiary_menu.add_item_list(nid)
        except Exception as e:
            logger.error(f"Error drawing third menu: {e}", exc_info=True)
            self.tertiary_menu.clear()
            self.tertiary_menu.add_item_list([f"Error displaying node details: {str(e)}"])

def main():
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon Management Hub CUI v{__version__}')
    wrapper = hzncuiApp(root)
    root.start()
