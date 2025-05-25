# Open Horizon CUI

A Text User Interface (TUI) for managing Open Horizon Management Hub.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

The application can be configured using either a `.env` file or environment variables. The `.env` file is the preferred method.

### Using .env file

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in your configuration values:
   ```
   HZN_ORG_ID=your-org-id
   HZN_EXCHANGE_URL=https://your-exchange-url
   EXCHANGE_USER_ADMIN_PW=your-admin-password
   ```

### Using Environment Variables

You can also set the configuration using environment variables:

```bash
export HZN_ORG_ID=your-org-id
export HZN_EXCHANGE_URL=https://your-exchange-url
export EXCHANGE_USER_ADMIN_PW=your-admin-password
```

### Required Configuration

The following configuration values are required:

- `HZN_ORG_ID`: Your Open Horizon organization ID
- `HZN_EXCHANGE_URL`: The URL of your Open Horizon Exchange
- `EXCHANGE_USER_ADMIN_PW`: The admin password for the exchange user

### Optional Configuration

- `HZN_API_TIMEOUT`: API request timeout in seconds (default: 30)
- `HZN_DEBUG`: Enable debug logging (default: false)

## Usage

Run the application:

```bash
python -m hzncui
```

## Development

For development, install the development requirements:

```bash
pip install -r requirements_dev.txt
```