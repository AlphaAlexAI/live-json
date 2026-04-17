# Live JSON

A CLI tool to fetch live follower counts from Instagram.

## Overview

This project provides a command-line interface (CLI) utility written in Python to retrieve the follower count of specified Instagram users. It interacts with a userinfo HTTP API to fetch real-time data, offering flexibility in how the results are presented. The tool is designed to be simple to use and configure for quick access to follower metrics.

## Features

*   Fetches follower counts for one or multiple Instagram users.
*   Outputs total follower count when multiple users are specified.
*   Saves fetched data to a `data/instagram.json` file upon successful retrieval.
*   Provides JSON output for programmatic integration.
*   Configurable API host and key for flexible deployment. 
## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Live-json.git
    cd Live-json
    ```

2.  Install dependencies:
    This project primarily uses Python's built-in libraries. You will need Python 3.x installed on your system.

    ```bash
    pip install -r requirements.txt # If a requirements.txt file exists
    ```
    *(Note: Based on the provided code, specific external libraries are not explicitly listed. If `requirements.txt` is not present, ensure you have Python 3.x installed.)*

## Usage

The primary script for fetching Instagram follower counts is `scripts/instagram_followers.py`.

Environment Variables:

Before running, ensure the following environment variables are set:

*   `API_HOST`: The hostname of the Instagram userinfo API.
*   `API_KEY`: Your subscription key for the API.
*   `USERS`: A comma-separated string of Instagram usernames (e.g., `"instagram,facebook,tiktok"`).

Example Command:

```bash
export API_HOST="api.example.com"
export API_KEY="your_api_key_here"
export USERS="instagram,facebook"
python3 ./scripts/instagram_followers.py
```

This command will fetch the follower counts for "instagram" and "facebook", print the total, and save the detailed JSON data to `./data/instagram.json`.

## Dependencies

*   Python 3.x: The primary programming language.
*   Instagram Userinfo HTTP API: An external API is required to fetch follower data. Details regarding the specific API endpoint, authentication, and rate limits should be obtained from the API provider.

## Configuration

Configuration is managed via environment variables:

*   `API_HOST`: Specifies the target API server.
*   `API_KEY`: Your authentication key for the API service.
*   `USERS`: A list of Instagram usernames to query.

## Running Tests

This project currently has no explicit testing framework or test files indicated. To ensure the project's health, it is recommended to implement a testing suite (e.g., using `unittest` or `pytest`).

## Folder Structure Overview

*   `./scripts/`: Contains executable Python scripts, including `instagram_followers.py`.
*   `./data/`: Stores output data, such as `instagram.json`.
*   `./new-data/`: An empty directory, possibly for future use.
*   `./.github/`: Contains GitHub-specific configurations (e.g., workflows).
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

## Security Considerations

*   API Key Management: API keys should be treated as sensitive credentials. Avoid hardcoding them directly into scripts. Use environment variables or a secure secrets management system.
*   Input Sanitization: If user inputs were to be directly used in API requests without proper sanitization, it could lead to injection vulnerabilities. Ensure all user-provided data is validated and escaped before being used in external requests.
*   HTTPS Usage: Always ensure that API requests are made over HTTPS to encrypt data in transit.

## Error Handling & Troubleshooting

*   API Connection Errors: If the `API_HOST` is incorrect or the API is unavailable, `urllib.error` exceptions may occur. Ensure the `API_HOST` is correctly configured and the API service is operational.
*   Authentication Failures: An invalid `API_KEY` will likely result in an API error response, which the script should handle gracefully.
*   User Not Found: If a specified username does not exist or is private, the API might return an error or specific data. The script's current implementation doesn't explicitly detail handling for individual user errors beyond overall request success/failure.
*   File Write Permissions: Ensure the script has write permissions to the `./data/` directory if you expect `instagram.json` to be created or updated.

## Contributing

Contributions are welcome! Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure they are well-documented.
4.  Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details. *(Placeholder - ensure a LICENSE.md file is created or update this section with the actual license information.)*
