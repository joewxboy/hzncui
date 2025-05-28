"""Main TUI implementation for Open Horizon Management Hub CUI.

This module provides a Text User Interface (TUI) for managing Open Horizon Management Hub.
It allows users to view and manage nodes, services, patterns, policies, organizations, and users
through an interactive command-line interface.

Author: Joe Pearson  
Created: 2022-02-19
"""

from curses import wrapper
import py_cui, requests, json
import logging
from typing import List, Dict, Any, Optional
from .config import load_config, get_config, ConfigError

__version__ = '0.0.1'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class hzncuiApp:
    """Main application class for the Open Horizon CUI.
    
    This class handles the TUI interface and interaction with the Open Horizon API.
    It provides menus for navigating different aspects of the Open Horizon Management Hub
    and displays detailed information about selected items.
    
    Attributes:
        parent: The parent PyCUI instance
        primary_menu: Menu for selecting main categories
        secondary_menu: Menu for selecting specific items
        tertiary_menu: Menu for displaying item details
        nodeArray: Dictionary mapping node IDs to their details
    """

    def __init__(self, parent: py_cui.PyCUI) -> None:
        """Initialize the CUI application.
        
        Args:
            parent: The parent PyCUI instance that manages the TUI
        """
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
            
            # Validate credentials before proceeding
            logger.info("Validating credentials...")
            try:
                r = requests.get(
                    f'{hzn_exchange_url}/orgs/{hzn_org_id}/users/admin',
                    auth=(f'{hzn_org_id}/admin', exchange_user_admin_pw)
                )
                r.raise_for_status()
                logger.info("Credentials validated successfully")
            except requests.exceptions.RequestException as e:
                logger.error(f"Credential validation failed: {str(e)}")
                raise ValueError(f"Invalid credentials: {str(e)}")
            
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
                
                # Check for error response
                if isinstance(data, dict) and ('code' in data or 'msg' in data):
                    error_msg = data.get('msg', 'Unknown error')
                    logger.error(f"API Error: {error_msg}")
                    raise ValueError(f"API Error: {error_msg}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise
            
            if not isinstance(data, list):
                logger.error(f"Expected list of nodes, got {type(data)}")
                raise ValueError("Invalid response format: expected list of nodes")

            # Initialize main menu
            li = ['Nodes', 'Services', 'Patterns', 'Policies', 'Orgs', 'Users']
            self.primary_menu = self.parent.add_scroll_menu('1. Choose an item', 0, 0, row_span=1, column_span=1)
            self.primary_menu.set_selected_color(py_cui.BLACK_ON_YELLOW)
            self.primary_menu.add_item_list(li)
            self.primary_menu.set_on_selection_change_event(self.on_primary_menu_selection)

            # Initialize node details menu
            self.secondary_menu = self.parent.add_scroll_menu('2. Choose a node to see details', 0, 1, row_span=1, column_span=2)
            self.secondary_menu.set_selected_color(py_cui.BLACK_ON_YELLOW)
            self.secondary_menu.set_on_selection_change_event(hzncuiApp.drawThirdMenu)

            # Process node data
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

            # Initialize node list
            self.secondary_menu.add_item_list(lid)

            # Initialize details display
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

    @staticmethod
    def drawThirdMenu(current_node: str) -> None:
        """Display detailed information about the selected node.
        
        Args:
            current_node: The ID of the node to display details for
        """
        self = hzncuiApp.self
        
        try:
            # Get node details
            node = self.nodeArray.get(current_node)
            if not node:
                logger.error(f"Node {current_node} not found in nodeArray")
                return
                
            # Format node details
            nid = [
                f'   node type: {node.get("nodeType", "N/A")}',
                f'architecture: {node.get("arch", "N/A")}',
                f'    services: {node.get("runningServices", "N/A")}',
                f'   heartbeat: {node.get("lastHeartbeat", "N/A")}',
                f'      owner: {node.get("owner", "N/A")}',
                f'       name: {node.get("name", "N/A")}'
            ]

            # Update display
            self.tertiary_menu.set_title(f'3. Details for node {current_node}')
            self.tertiary_menu.clear()
            self.tertiary_menu.add_item_list(nid)
        except Exception as e:
            logger.error(f"Error drawing third menu: {e}", exc_info=True)
            self.tertiary_menu.clear()
            self.tertiary_menu.add_item_list([f"Error displaying node details: {str(e)}"])

    def fetch_services(self) -> None:
        """Fetch services from the Open Horizon Exchange and display them in the TUI.
        If the API returns an empty list, it is treated as a valid response.
        """
        try:
            r = requests.get(
                f'{get_config("HZN_EXCHANGE_URL")}/orgs/{get_config("HZN_ORG_ID")}/services',
                auth=(f'{get_config("HZN_ORG_ID")}/admin', get_config('EXCHANGE_USER_ADMIN_PW'))
            )
            r.raise_for_status()
            response = r.json()
            services = response.get('services', {})
            if not services:
                logger.info("No services found.")
                self.secondary_menu.clear()
                self.secondary_menu.add_item_list(["No services available."])
                return
            service_ids = list(services.keys())
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list(service_ids)
            self.serviceArray = services
        except Exception as e:
            logger.error(f"Error fetching services: {e}")
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list([f"Error fetching services: {str(e)}"])

    def draw_service_details(self, service_id: str) -> None:
        """Display detailed information about the selected service.
        
        Args:
            service_id: The ID of the service to display details for
        """
        service = self.serviceArray.get(service_id)
        if not service:
            logger.error(f"Service {service_id} not found in serviceArray")
            return
        details = [
            f'   service type: {service.get("serviceType", "N/A")}',
            f'   version: {service.get("version", "N/A")}',
            f'   owner: {service.get("owner", "N/A")}',
            f'   name: {service.get("name", "N/A")}'
        ]
        self.tertiary_menu.set_title(f'3. Details for service {service_id}')
        self.tertiary_menu.clear()
        self.tertiary_menu.add_item_list(details)

    def fetch_patterns(self) -> None:
        """Fetch patterns from the Open Horizon Exchange and display them in the TUI.
        If the API returns an empty list, it is treated as a valid response.
        """
        try:
            r = requests.get(
                f'{get_config("HZN_EXCHANGE_URL")}/orgs/{get_config("HZN_ORG_ID")}/patterns',
                auth=(f'{get_config("HZN_ORG_ID")}/admin', get_config('EXCHANGE_USER_ADMIN_PW'))
            )
            r.raise_for_status()
            response = r.json()
            patterns = response.get('patterns', {})
            if not patterns:
                logger.info("No patterns found.")
                self.secondary_menu.clear()
                self.secondary_menu.add_item_list(["No patterns available."])
                return
            pattern_ids = list(patterns.keys())
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list(pattern_ids)
            self.patternArray = patterns
        except Exception as e:
            logger.error(f"Error fetching patterns: {e}")
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list([f"Error fetching patterns: {str(e)}"])

    def draw_pattern_details(self, pattern_id: str) -> None:
        """Display detailed information about the selected pattern.
        
        Args:
            pattern_id: The ID of the pattern to display details for
        """
        pattern = self.patternArray.get(pattern_id)
        if not pattern:
            logger.error(f"Pattern {pattern_id} not found in patternArray")
            return
        details = [
            f'   label: {pattern.get("label", "N/A")}',
            f'   description: {pattern.get("description", "N/A")}',
            f'   owner: {pattern.get("owner", "N/A")}',
            f'   public: {pattern.get("public", "N/A")}',
            f'   lastUpdated: {pattern.get("lastUpdated", "N/A")}'
        ]
        self.tertiary_menu.set_title(f'3. Details for pattern {pattern_id}')
        self.tertiary_menu.clear()
        self.tertiary_menu.add_item_list(details)

    def on_primary_menu_selection(self, selected_item: str) -> None:
        """Handle selection change in the primary menu.
        
        Args:
            selected_item: The selected item from the primary menu
        """
        if selected_item == 'Services':
            self.secondary_menu.set_title('2. Choose a service to see details')
            self.tertiary_menu.set_title('3. Details for service')
            self.tertiary_menu.clear()
            self.fetch_services()
            # Automatically show details for the first service if available
            if self.serviceArray:
                first_service_id = next(iter(self.serviceArray))
                self.draw_service_details(first_service_id)
        elif selected_item == 'Nodes':
            self.secondary_menu.set_title('2. Choose a node to see details')
            self.tertiary_menu.set_title('3. Details for node')
            self.tertiary_menu.clear()
            self.fetch_nodes()
            if self.nodeArray:
                first_node_id = next(iter(self.nodeArray))
                self.draw_node_details(first_node_id)
        elif selected_item == 'Patterns':
            self.secondary_menu.set_title('2. Choose a pattern to see details')
            self.tertiary_menu.set_title('3. Details for pattern')
            self.tertiary_menu.clear()
            self.fetch_patterns()
            if self.patternArray:
                first_pattern_id = next(iter(self.patternArray))
                self.draw_pattern_details(first_pattern_id)

    def fetch_nodes(self) -> None:
        """Fetch nodes from the Open Horizon Exchange and display them in the TUI.
        If the API returns an empty list, it is treated as a valid response.
        """
        try:
            r = requests.get(
                f'{get_config("HZN_EXCHANGE_URL")}/orgs/{get_config("HZN_ORG_ID")}/node-details',
                auth=(f'{get_config("HZN_ORG_ID")}/admin', get_config('EXCHANGE_USER_ADMIN_PW'))
            )
            r.raise_for_status()
            nodes = r.json()
            if not nodes:
                logger.info("No nodes found.")
                self.secondary_menu.clear()
                self.secondary_menu.add_item_list(["No nodes available."])
                return
            node_ids = [node.get("id", "Unknown") for node in nodes]
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list(node_ids)
            self.nodeArray = {node.get("id"): node for node in nodes}
        except Exception as e:
            logger.error(f"Error fetching nodes: {e}")
            self.secondary_menu.clear()
            self.secondary_menu.add_item_list([f"Error fetching nodes: {str(e)}"])

    def draw_node_details(self, node_id: str) -> None:
        """Display detailed information about the selected node.
        
        Args:
            node_id: The ID of the node to display details for
        """
        node = self.nodeArray.get(node_id)
        if not node:
            logger.error(f"Node {node_id} not found in nodeArray")
            return
        details = [
            f'   node type: {node.get("nodeType", "N/A")}',
            f'architecture: {node.get("arch", "N/A")}',
            f'    services: {node.get("runningServices", "N/A")}',
            f'   heartbeat: {node.get("lastHeartbeat", "N/A")}',
            f'      owner: {node.get("owner", "N/A")}',
            f'       name: {node.get("name", "N/A")}'
        ]
        self.tertiary_menu.set_title(f'3. Details for node {node_id}')
        self.tertiary_menu.clear()
        self.tertiary_menu.add_item_list(details)

def main() -> None:
    """Initialize and start the CUI application."""
    root = py_cui.PyCUI(2, 3)
    root.set_title(f'Open Horizon Management Hub CUI v{__version__}')
    wrapper = hzncuiApp(root)
    root.start()
