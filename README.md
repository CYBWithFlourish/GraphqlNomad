<h1 align="center">GraphQLNomad</h1>

<div align="center">

```
  ________                    .__     ________   .____     _______                             .___
 /  _____/___________  ______ |  |__  \_____  \  |    |    \      \   ____   _____ _____     __| _/
/   \  __\_  __ \__  \ \____ \|  |  \  /   / \  \|    |    /  |    \ /  _ \ /     \\__  \   / __ |
\    \_\  \  | \// __ \|  |_> >   Y  \/    \_/.  \    |___/   |     (  <_> )  Y Y  \/ __ \_/ /_/ |
 \______  /__|  (____  /   __/|___|  /\_____\ \_/_______  \____|__  /\____/|__|_|  (____  /\____ |
        \/           \/|__|        \/        \__>       \/       \/             \/     \/      \/
```
**v1.0.0 - An integrated tool to detect, fingerprint, and explore GraphQL endpoints.**

</div>

<div align="center">

[![PyPI Version](https://img.shields.io/pypi/v/graphqlnomad.svg)](https://pypi.org/project/graphqlnomad/)
[![Build Status](https://github.com/CYBWithFlourish/GraphQLNomad/actions/workflows/ci-workflow.yml/badge.svg)](https://github.com/YOUR_USERNAME/GraphQLNomad/actions/workflows/ci-workflow.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/graphqlnomad.svg)](https://pypi.org/project/graphqlnomad/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

</div>

**GraphQLNomad** is a powerful command-line tool designed for security researchers, bug bounty hunters, and developers to streamline the process of testing GraphQL endpoints. It automates reconnaissance and provides a feature-rich interactive shell to explore schemas and craft custom queries.

## ✨ Key Features

*   **Endpoint Detection**: Automatically discovers GraphQL endpoints using a built-in and customizable wordlist.
*   **Engine Fingerprinting**: Identifies the underlying GraphQL engine (e.g., Apollo, Hot Chocolate, Hasura) based on its behavior.
*   **Schema Introspection**: Fetches the entire GraphQL schema and parses it for queries, mutations, and types.
*   **Interactive Shell**: A user-friendly interactive console to explore the schema, view object details, and build queries on the fly.
*   **Non-Interactive Mode**: Run scans and output results to a CSV file for automation and scripting.
*   **Connection Options**: Full support for custom headers, HTTP/S proxies, and request timeouts.

## 🎬 Demo

[![asciicast](https://asciinema.org/a/P8PtBGYs64JgghVvkxVC1dRs9.svg)](https://asciinema.org/a/P8PtBGYs64JgghVvkxVC1dRs9)

## 🛠️ Installation

You can install GraphQLNomad from multiple sources.

#### From PyPI (Recommended)
This is the easiest and fastest way to get started.

```bash
pip install pipx
```

```bash
pipx install graphqlnomad
```

#### From NPM
For users in the JavaScript ecosystem, an npm wrapper is available.
*(Note: Python and pipx are still required.)*

```bash
npm install -g graphqlnomad
```

#### From Source
To get the latest development version, you can install directly from this repository.

```bash
git clone https://github.com/CYBWithFlourish/GraphQLNomad.git
cd GraphQLNomad
pip install .
```

## 🚀 Usage

GraphQLNomad is simple to run. At its most basic, just provide a base URL to scan.

```bash
graphqlnomad [URL] [OPTIONS]
```

The tool will then attempt to find the endpoint, fingerprint it, and if successful, will drop you into an interactive shell.

#### Command-line Options

```
usage: graphqlnomad [-h] [-v] [--no-detect] [--no-fingerprint] [-w WORDLIST] [-l] [-H HEADER] [-p PROXY] [-T TIMEOUT] [--no-redirect] [--non-interactive] [-o OUTPUT_FILE] url

GraphQLNomad v1.0.0: An integrated tool to detect, fingerprint, and explore GraphQL endpoints.

positional arguments:
  url                   The target base URL or specific GraphQL endpoint URL.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Reconnaissance Options:
  --no-detect           Do not attempt to find the endpoint automatically.
  --no-fingerprint      Do not attempt to fingerprint the engine.
  -w WORDLIST, --wordlist WORDLIST
                        Path to a custom wordlist file for endpoint detection.
  -l, --list-engines    List all fingerprintable GraphQL engines and exit.

Connection Options:
  -H HEADER, --header HEADER
                        Add a custom header. Format: 'Header-Name: Header-Value'
  -p PROXY, --proxy PROXY
                        HTTP(S) proxy URL. Format: http://user:pass@host:port
  -T TIMEOUT, --timeout TIMEOUT
                        Request timeout in seconds (default: 15).
  --no-redirect         Do not follow 3xx redirection.

Execution Options:
  --non-interactive     Exit after reconnaissance is complete.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output reconnaissance results to a CSV file.
```

## 💡 Examples

#### 1. Basic Reconnaissance on a Domain
Scan a target URL, find the endpoint, and start an interactive session.
```bash
graphqlnomad https://rickandmortyapi.com/graphql
```

#### 2. Non-Interactive Scan with Output
Scan a known endpoint, disable fingerprinting, and save the results to a CSV file.
```bash
graphqlnomad https://api.spacex.land/graphql --no-detect -o spacex.csv --non-interactive
```

#### 3. Using the Interactive Shell
Once in the shell, you can use these commands:
*   `help`: Show the list of available commands.
*   `queries`: List all available queries from the schema.
*   `mutations`: List all available mutations.
*   `info <TypeName>`: Show detailed information about a specific query, mutation, or type.
*   `run query <QueryName>`: Start the interactive query builder to craft and execute a request.
*   `exit`: Close the interactive session.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/CYBWithFlourish/GraphQLNomad/issues).

1.  **Fork** the project.
2.  Create your **Feature Branch** (`git checkout -b feature/AmazingFeature`).
3.  **Commit** your Changes (`git commit -m 'feat: Add some AmazingFeature'`).
4.  **Push** to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a **Pull Request**.

## 📜 License

This project is licensed under the **Apache 2.0 License**. See the [LICENSE](https://github.com/CYBWithFlourish/GraphqlNomad/blob/main/LICENSE) file for more details.

## 🙏 Acknowledgments

*   [Colorama](https://github.com/tartley/colorama) for making terminal output beautiful.
*   The entire open-source security community.
