# Open Horizon CUI API Documentation

## Overview

The Open Horizon CUI provides a Text User Interface (TUI) for managing Open Horizon Management Hub. This document describes the API endpoints used by the application and how to interact with them.

## Configuration

The application requires the following configuration:

### Required Environment Variables

- `HZN_ORG_ID`: Your Open Horizon organization ID
- `HZN_EXCHANGE_URL`: The URL of your Open Horizon Exchange
- `EXCHANGE_USER_ADMIN_PW`: The admin password for the exchange user

### Optional Environment Variables

- `HZN_API_TIMEOUT`: API request timeout in seconds (default: 30)
- `HZN_DEBUG`: Enable debug logging (default: false)

## API Endpoints

### Node Management

#### Get Node Details
```http
GET {HZN_EXCHANGE_URL}/orgs/{HZN_ORG_ID}/node-details
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of nodes with their details.

Response format:
```json
[
  {
    "id": "string",
    "nodeType": "string",
    "arch": "string",
    "runningServices": "string",
    "lastHeartbeat": "string",
    "owner": "string",
    "name": "string",
    "properties": [
      {
        "name": "string",
        "type": "string",
        "value": "string"
      }
    ]
  }
]
```

### Services

#### Get Services
```http
GET {HZN_EXCHANGE_URL}/orgs/{HZN_ORG_ID}/services
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of services.

### Patterns

#### Get Patterns
```http
GET {HZN_EXCHANGE_URL}/orgs/{HZN_ORG_ID}/patterns
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of patterns.

### Policies

#### Get Policies
```http
GET {HZN_EXCHANGE_URL}/orgs/{HZN_ORG_ID}/policies
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of policies.

### Organizations

#### Get Organizations
```http
GET {HZN_EXCHANGE_URL}/orgs
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of organizations.

### Users

#### Get Users
```http
GET {HZN_EXCHANGE_URL}/orgs/{HZN_ORG_ID}/users
Authorization: Basic {HZN_ORG_ID}/admin:{EXCHANGE_USER_ADMIN_PW}
```

Returns a list of users.

## Error Handling

The application handles the following error cases:

1. Configuration Errors
   - Missing required environment variables
   - Invalid configuration values

2. API Errors
   - Network connectivity issues
   - Authentication failures
   - Invalid response formats
   - Missing or malformed data

3. UI Errors
   - Invalid user input
   - Display rendering issues

## Logging

The application uses Python's logging module with the following levels:

- DEBUG: Detailed information for debugging
- INFO: General operational information
- WARNING: Warning messages for potentially problematic situations
- ERROR: Error messages for serious problems
- CRITICAL: Critical errors that may prevent the application from running

## Development

### Adding New Endpoints

To add support for a new API endpoint:

1. Add the endpoint URL to the configuration if needed
2. Create a new method in the `hzncuiApp` class to handle the endpoint
3. Add appropriate error handling and logging
4. Update the UI to display the new data
5. Add tests for the new functionality

### Testing

The application includes tests for:
- Configuration loading
- API endpoint responses
- UI rendering
- Error handling

Run tests with:
```bash
pytest
``` 