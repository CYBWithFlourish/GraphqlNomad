#!/bin/python
import requests
import json
import sys
import shlex
import argparse
from urllib.parse import urlparse, urljoin
from time import strftime, gmtime

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ImportError:
    print("Warning: 'colorama' library not found. Output will be uncolored.")
    print("For a better experience, please install it: pip install colorama")
    class Fore: RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    class Style: RESET_ALL = BRIGHT = ""

# --- CPRINT HELPER FUNCTION START ---
# cprint helper function to handle colored output.
def cprint(color, text, bright=False):
    """Helper function to print colored text."""
    style = Style.BRIGHT if bright else ""
    print(f"{style}{color}{text}{Style.RESET_ALL}")
# --- CPRINT HELPER FUNCTION END ---

# --- graphw00f -----------------------------------------------------------------------------------------------------------------------------------------------
DEFAULT_PATHS = ["/graphql", "/api/graphql", "/graphiql", "/graphql/console", "/v1/graphql", "/v2/graphql", "/graphql/api", "/api"]
ENGINES = {
    'apollo-server': {'name': 'Apollo Server', 'url': 'https://www.apollographql.com/docs/apollo-server/', 'ref': 'https://github.com/apollographql/apollo-server', 'technology': ['Node.js', 'JavaScript'], 'fingerprints': [{'type': 'header', 'value': 'x-apollo-tracing'}, {'type': 'error_text', 'value': 'Syntax Error: Unexpected Name'}, {'type': 'error_code', 'path': ['errors', 0, 'extensions', 'code'], 'value': 'GRAPHQL_PARSE_FAILED'}]},
    'graphene': {'name': 'Graphene', 'url': 'https://graphene-python.org/', 'ref': 'https://github.com/graphql-python/graphene', 'technology': ['Python', 'Django', 'Flask'], 'fingerprints': [{'type': 'error_text', 'value': 'Did you mean'}, {'type': 'error_text', 'value': '"errors":'}]},
    'hot-chocolate': {'name': 'Hot Chocolate', 'url': 'https://chillicream.com/docs/hotchocolate', 'ref': 'https://github.com/ChilliCream/hotchocolate', 'technology': ['.NET', 'C#'], 'fingerprints': [{'type': 'error_code', 'path': ['errors', 0, 'extensions', 'code'], 'value': 'HC0001'}]},
    'hasura': {'name': 'Hasura', 'url': 'https://hasura.io/', 'ref': 'https://github.com/hasura/graphql-engine', 'technology': ['Go', 'Haskell'], 'fingerprints': [{'type': 'error_code', 'path': ['errors', 0, 'extensions', 'code'], 'value': 'validation-failed'}, {'type': 'error_code', 'path': ['errors', 0, 'extensions', 'path'], 'value': '$'}]}
}
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
BANNER = r"""
  ________                    .__     ________   .____     _______                             .___
 /  _____/___________  ______ |  |__  \_____  \  |    |    \      \   ____   _____ _____     __| _/
/   \  __\_  __ \__  \ \____ \|  |  \  /   / \  \|    |    /  |    \ /  _ \ /     \\__  \   / __ | 
\    \_\  \  | \// __ \|  |_> >   Y  \/    \_/.  \    |___/   |     (  <_> )  Y Y  \/ __ \_/ /_/ | 
 \______  /__|  (____  /   __/|___|  /\_____\ \_/_______  \____|__  /\____/|__|_|  (____  /\____ | 
        \/           \/|__|        \/        \__>       \/       \/             \/     \/      \/ 
                          v0.0.0 - @CYBWithFlourish | https://x.com/0xCYBFlourish
"""
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
INTROSPECTION_QUERIES = [
    """
    query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }
    """,
    """query IntrospectionQuery { __schema { types { name kind description fields { name } } } }""",
    """query IntrospectionQuery { schema: __schema { types { name } } }""",
    """{ __schema { types { name } } }"""
]
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
MANUAL_PAGES = {
    "queries": {"description": "Lists all available top-level queries.", "usage": "queries", "example": "GraphQLNomad> queries"},
    "mutations": {"description": "Lists all available top-level mutations.", "usage": "mutations", "example": "GraphQLNomad> mutations"},
    "info": {"description": "Displays schema info for a specific query, mutation, or type.", "usage": "info <name>", "example": "GraphQLNomad> info user"},
    "run": {"description": "Interactively build and execute a GraphQL request.", "usage": "run <query|mutation> <name>", "example": "GraphQLNomad> run query user"},
    "help": {"description": "Displays help information for commands.", "usage": "help [command]", "example": "GraphQLNomad> help run"},
    "exit": {"description": "Exits the interactive shell.", "usage": "exit", "example": "GraphQLNomad> exit"}
}
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
class GraphQLNomad:
    def __init__(self, url, headers=None, proxy=None, timeout=15, follow_redirects=True):
        self.base_url = url
        self.endpoint_url = url
        self.headers = headers or {}
        self.proxies = {'http': proxy, 'https' : proxy} if proxy else None
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.schema = None
        self.queries = {}
        self.mutations = {}
        self.types = {}

    def _print_banner(self):
        lines = BANNER.strip('\n').split('\n')
        split_point = len(lines) // 2
        for i in range(split_point): cprint(Fore.MAGENTA, lines[i])
        for i in range(split_point, len(lines)): cprint(Fore.WHITE, lines[i])

    def _send_request(self, url, query, variables=None):
        payload = {'query': query}
        if variables: payload['variables'] = variables
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
                proxies=self.proxies,
                allow_redirects=self.follow_redirects
            )
            return response
        except requests.exceptions.RequestException as e:
            return None

    def _check_endpoint(self, url):
        test_query = "{__typename}"
        response = self._send_request(url, test_query)
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if 'data' in json_data and '__typename' in json_data['data']:
                    return True
            except json.JSONDecodeError:
                return False
        return False

    def detect_endpoint(self, wordlist=None):
        cprint(Fore.CYAN, "[*] Starting detection phase...", bright=True)
        paths_to_check = wordlist or DEFAULT_PATHS
        for path in paths_to_check:
            target_url = urljoin(self.base_url, path)
            print(f"  -> Checking {target_url}")
            if self._check_endpoint(target_url):
                cprint(Fore.GREEN, f"[!] Found GraphQL endpoint at: {target_url}", bright=True)
                self.endpoint_url = target_url
                return True
        cprint(Fore.RED, "[x] Could not find GraphQL endpoint automatically.", bright=True)
        return False

    def fingerprint_engine(self):
        cprint(Fore.CYAN, "\n[*] Attempting to fingerprint engine...", bright=True)
        malformed_query = "queryy {__typename}"
        response = self._send_request(self.endpoint_url, malformed_query)

        if response is None:
            cprint(Fore.YELLOW, "[?] Fingerprinting failed: Could not get a response from the endpoint.")
            return None

        response_headers = {k.lower(): v for k,v in response.headers.items()}
        response_json = {}
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            pass

        for engine_key, engine_data in ENGINES.items():
            for fingerprint in engine_data['fingerprints']:
                if fingerprint['type'] == 'header' and fingerprint['value'] in response_headers:
                    return engine_key
                if fingerprint['type'] == 'error_text' and fingerprint['value'] in response.text:
                    return engine_key
                if fingerprint['type'] == 'error_code' and response_json:
                    try:
                        current = response_json
                        for key in fingerprint['path']:
                            current = current[key]
                        if current == fingerprint['value']:
                            return engine_key
                    except (KeyError, IndexError):
                        continue

        cprint(Fore.YELLOW, "[?] No specific engine fingerprint matched. It might be a custom or unknown engine.")
        return None

    def fetch_schema(self):
        cprint(Fore.CYAN, f"\n[*] Attempting to fetch schema from {self.endpoint_url}...", bright=True)
        if self.headers: print(f"{Fore.WHITE}    Using custom headers for requests.")

        for i, query in enumerate(INTROSPECTION_QUERIES):
            print(f"  -> Trying introspection method #{i+1}...")
            response = self._send_request(self.endpoint_url, query.strip())
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data and 'data' in data and data['data'].get('__schema'):
                        self.schema = data['data']['__schema']
                        cprint(Fore.GREEN, f"    Success! Schema fetched using method #{i+1}.", bright=True)
                        self._parse_schema()
                        return True
                except json.JSONDecodeError:
                    cprint(Fore.YELLOW, f"    Method #{i+1} returned a non-JSON response.")
                    continue

        cprint(Fore.RED, "[x] Fatal: All introspection methods failed. Endpoint may be hardened or invalid.", bright=True)
        return False

    def _parse_schema(self):
        for type_info in self.schema.get('types', []):
            if type_info and type_info.get('name'): self.types[type_info['name']] = type_info
        query_type_name = self.schema.get('queryType', {}).get('name')
        if query_type_name and self.types.get(query_type_name):
            for field in self.types[query_type_name].get('fields', []):
                self.queries[field['name']] = field
        mutation_type_name = self.schema.get('mutationType', {}).get('name')
        if mutation_type_name and self.types.get(mutation_type_name):
            for field in self.types[mutation_type_name].get('fields', []):
                self.mutations[field['name']] = field
        print(f"    Found {Style.BRIGHT}{Fore.YELLOW}{len(self.queries)}{Style.RESET_ALL} queries and {Style.BRIGHT}{Fore.YELLOW}{len(self.mutations)}{Style.RESET_ALL} mutations.")

    def run_interactive_shell(self):
        cprint(Fore.GREEN, "\n--- Starting Interactive Session ---", bright=True)
        print("Type 'help' for a list of commands.")
        while True:
            try:
                prompt = f"{Style.BRIGHT}{Fore.MAGENTA}GraphQLNomad> {Style.RESET_ALL}"
                cmd_input = input(prompt).strip()
                if not cmd_input: continue
                parts = shlex.split(cmd_input)
                command, args = parts[0].lower(), parts[1:]
                if command in ["exit", "quit"]: break
                elif command == "help": self._handle_help(args)
                elif command == "queries": self._list_items(self.queries, "Available Queries")
                elif command == "mutations": self._list_items(self.mutations, "Available Mutations")
                elif command == "info" and args: self._show_info(args[0])
                elif command == "run" and len(args) >= 2: self._interactive_runner(args[0], args[1])
                else: cprint(Fore.RED, "Unknown or invalid command. Type 'help'.")
            except (KeyboardInterrupt, EOFError): break
            except Exception as e: cprint(Fore.RED, f"An unexpected error occurred: {e}", bright=True)
        print(f"\n{Style.BRIGHT}Goodbye!{Style.RESET_ALL}")

    def _print_table(self, title, rows, headers):
        if not rows: return
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row): widths[i] = max(widths[i], len(str(cell)))
        cprint(Fore.GREEN, f"\n--- {title} ---", bright=True)
        header_line = "  ".join(f"{h:<{widths[i]}}" for i, h in enumerate(headers))
        print(f"{Style.BRIGHT}{Fore.WHITE}{header_line}")
        print(f"{Fore.WHITE}{'-' * (sum(widths) + 2 * (len(headers) -1))}")
        for row in rows:
            first_col = f"{Fore.YELLOW}{str(row[0]):<{widths[0]}}"
            rest_cols = "  ".join(f"{str(cell):<{widths[i+1]}}" for i, cell in enumerate(row[1:]))
            print(f"{first_col}{Style.RESET_ALL}  {rest_cols}")
        print()

    def _handle_help(self, args):
        if not args:
            rows = [("queries", "List all available queries."), ("mutations", "List all available mutations."), ("info <name>", "Show details about a query, mutation, or type."), ("run <query|mutation> <name>", "Interactively build and execute a request."), ("help [command]", "Show this help table or a detailed manual."), ("exit / quit", "Exit the shell.")]
            self._print_table("GraphQLNomad Command Reference", rows, headers=["Command", "Description"])
        else:
            command = args[0].lower()
            if command == "quit": command = "exit"
            page = MANUAL_PAGES.get(command)
            if not page:
                cprint(Fore.RED, f"No manual page found for '{command}'.")
                return
            print(f"\n{Style.BRIGHT}{Fore.GREEN}--- MANUAL: {command} ---{Style.RESET_ALL}")
            print(f"{page['description']}\n")
            print(f"  {Style.BRIGHT}{Fore.YELLOW}Usage:{Style.RESET_ALL} {page['usage']}")
            if "arguments" in page: print(f"  {Style.BRIGHT}{Fore.YELLOW}Arguments:{Style.RESET_ALL}\n    {page['arguments']}")
            print(f"  {Style.BRIGHT}{Fore.YELLOW}Example:{Style.RESET_ALL} {page['example']}")
            print(f"{Style.BRIGHT}{Fore.GREEN}{'-' * (len(command) + 14)}{Style.RESET_ALL}\n")

    def _list_items(self, items, title):
        if not items:
            cprint(Fore.YELLOW, f"No {title.lower().replace('available ', '')} found.")
            return
        rows = [(name, details.get('description', 'No description')) for name, details in sorted(items.items())]
        self._print_table(title, rows, headers=["Name", "Description"])

    def _show_info(self, name):
        item = self.queries.get(name) or self.mutations.get(name) or self.types.get(name)
        if not item:
            cprint(Fore.RED, f"'{name}' not found.")
            return
        info_json = json.dumps(item, indent=2)
        print(f"\n{Style.BRIGHT}{Fore.GREEN}--- Details for '{name}' ---{Style.RESET_ALL}")
        print(info_json)
        print(f"{Style.BRIGHT}{Fore.GREEN}{'-' * (len(name) + 18)}{Style.RESET_ALL}\n")

    def _get_base_type(self, type_info):
        current_type = type_info
        while current_type.get('ofType'): current_type = current_type['ofType']
        return current_type

    def _build_query_recursively(self, type_name, indent="  "):
        type_info = self.types.get(type_name)
        if not type_info or type_info.get('kind') not in ('OBJECT', 'INTERFACE') or not type_info.get('fields'): return ""
        cprint(Fore.CYAN, f"\nSelect fields for type '{type_name}':", bright=True)
        fields_str, available_fields = "", {field['name']: field for field in type_info['fields']}
        field_names = list(available_fields.keys())
        for i, name in enumerate(field_names):
            base_type = self._get_base_type(available_fields[name]['type'])['name']
            print(f"  {Fore.YELLOW}{i+1}{Style.RESET_ALL}: {name} ({Fore.WHITE}{base_type}{Style.RESET_ALL})")
        try:
            prompt = f"{Style.BRIGHT}{Fore.MAGENTA}Enter field numbers (e.g., 1 3 4), or '*' for all: {Style.RESET_ALL}"
            selection = input(prompt)
            selected_indices = []
            if selection.strip() == '*':
                selected_indices = range(1, len(field_names) + 1)
            else:
                for item in selection.split():
                    try:
                        selected_indices.append(int(item))
                    except ValueError:
                        cprint(Fore.YELLOW, f"Warning: '{item}' is not a valid number, skipping.")

            for i in selected_indices:
                if 1 <= i <= len(field_names):
                    field_name, field_info = field_names[i-1], available_fields[field_names[i-1]]
                    base_type_info = self._get_base_type(field_info['type'])
                    fields_str += f"{indent}{field_name}"
                    if base_type_info.get('kind') in ('OBJECT', 'INTERFACE'):
                        sub_fields = self._build_query_recursively(base_type_info['name'], indent + "  ")
                        fields_str += f" {{\n{sub_fields}{indent}}}\n" if sub_fields else "\n"
                    else: fields_str += "\n"
                else: cprint(Fore.RED, f"Warning: Field number {i} is out of range, skipping.")
        except (ValueError, IndexError):
            cprint(Fore.RED, "Invalid selection. Please enter space-separated numbers.")
            return self._build_query_recursively(type_name, indent)
        return fields_str

    def _interactive_runner(self, op_type, op_name):
        op_type = op_type.lower()
        op_map = self.queries if op_type == 'query' else self.mutations
        if op_name not in op_map:
            cprint(Fore.RED, f"{op_type.capitalize()} '{op_name}' not found."); return
        op_info, arg_str, args_to_add = op_map[op_name], "", []

        if op_info.get('args'):
            cprint(Fore.CYAN, f"\nEnter arguments for '{op_name}':", bright=True)
            print("(Press Enter to skip optional args)")
            for arg in op_info['args']:
                base_type = self._get_base_type(arg['type'])
                base_type_name = base_type['name']
                type_details = self.types.get(base_type_name)
                is_non_null = 'NON_NULL' in str(arg['type'])

                prompt_text = f"  {Fore.YELLOW}{arg['name']}{Style.RESET_ALL} ({Fore.WHITE}{base_type_name}{Style.RESET_ALL}){'*' if is_non_null else ''}: "
                if type_details and type_details.get('kind') == 'ENUM':
                    enum_values = [v['name'] for v in type_details.get('enumValues', [])]
                    prompt_text += f"\n    (Options: {', '.join(enum_values)}) -> "

                val = input(prompt_text)
                if val:
                    formatted_val = ""
                    if base_type_name in ('Int', 'Float'):
                        formatted_val = val
                    elif base_type_name == 'Boolean':
                        if val.lower() in ['true', 't', '1', 'yes']:
                            formatted_val = 'true'
                        else:
                            formatted_val = 'false'
                    elif type_details and type_details.get('kind') == 'ENUM':
                        formatted_val = val
                    else:
                        formatted_val = json.dumps(val)

                    args_to_add.append(f"{arg['name']}: {formatted_val}")

            if args_to_add:
                arg_str = f"({', '.join(args_to_add)})"

        selection_set = self._build_query_recursively(self._get_base_type(op_info['type'])['name'])
        if not selection_set:
            cprint(Fore.RED, "No fields selected. Aborting execution."); return
        final_query = f"{op_type} {{\n  {op_name}{arg_str} {{\n{selection_set}  }}\n}}"
        cprint(Fore.GREEN, "\n--- Executing Query ---", bright=True)
        cprint(Fore.CYAN, final_query)
        response = self._send_request(self.endpoint_url, final_query)
        if response and response.status_code == 200:
            cprint(Fore.BLUE, "\n--- Response ---", bright=True)
            print(json.dumps(response.json(), indent=2))
            print()
        elif response:
            cprint(Fore.RED, f"\n--- Request Failed (Status: {response.status_code}) ---", bright=True)
            print(response.text)
        else:
            cprint(Fore.RED, "\n--- Request Failed (No Response) ---", bright=True)

class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'usage: '
        # Print banner first
        lines = BANNER.strip('\n').split('\n')
        split_point = len(lines) // 2
        for i in range(split_point): print(f"{Fore.MAGENTA}{lines[i]}")
        for i in range(split_point, len(lines)): print(f"{Fore.WHITE}{lines[i]}")
        # Then call the original usage
        return super(CustomHelpFormatter, self).add_usage(usage, actions, groups, prefix)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GraphQLNomad v0.0.0: An integrated tool to detect, fingerprint, and explore GraphQL endpoints.",
        formatter_class=CustomHelpFormatter,
        epilog="""Examples:\n  # Detect, fingerprint, and start interactive session on a base URL\n  python graphqlnomad.py https://rickandmortyapi.com/\n\n  # Provide a specific endpoint and skip detection\n  python graphqlnomad.py https://rickandmortyapi.com/graphql --no-detect\n\n  # Run non-interactively, saving fingerprint result to a file\n  python graphqlnomad.py https://api.example.com/ -o results.csv --non-interactive\n\n  # Use a proxy and custom headers\n  python graphqlnomad.py https://api.example.com/ --proxy http://127.0.0.1:8080 -H "Authorization: Bearer <token>" """
    )
    parser.add_argument("url", help="The target base URL or specific GraphQL endpoint URL.")
    parser.add_argument("-v", "--version", action="version", version="GraphQLNomad v0.0.0")

    recon_group = parser.add_argument_group('Reconnaissance Options')
    recon_group.add_argument("--detect", action="store_true", default=True, help=argparse.SUPPRESS)
    recon_group.add_argument("--no-detect", action="store_false", dest="detect", help="Do not attempt to find the endpoint automatically.")
    recon_group.add_argument("--fingerprint", action="store_true", default=True, help=argparse.SUPPRESS)
    recon_group.add_argument("--no-fingerprint", action="store_false", dest="fingerprint", help="Do not attempt to fingerprint the engine.")
    recon_group.add_argument("-w", "--wordlist", help="Path to a custom wordlist file for endpoint detection.")
    recon_group.add_argument("-l", "--list-engines", action="store_true", help="List all fingerprintable GraphQL engines and exit.")

    conn_group = parser.add_argument_group('Connection Options')
    conn_group.add_argument("-H", "--header", action="append", help="Add a custom header. Format: 'Header-Name: Header-Value'")
    conn_group.add_argument("-p", "--proxy", help="HTTP(S) proxy URL. Format: http://user:pass@host:port")
    conn_group.add_argument("-T", "--timeout", type=int, default=15, help="Request timeout in seconds (default: 15).")
    conn_group.add_argument("--no-redirect", action="store_false", dest="follow_redirects", help="Do not follow 3xx redirection.")

    exec_group = parser.add_argument_group('Execution Options')
    exec_group.add_argument("--interactive", action="store_true", default=True, help=argparse.SUPPRESS)
    exec_group.add_argument("--non-interactive", action="store_false", dest="interactive", help="Exit after reconnaissance is complete.")
    exec_group.add_argument("-o", "--output-file", help="Output reconnaissance results to a CSV file.")
    args = parser.parse_args()

    if args.list_engines:
        dummy_nomad = GraphQLNomad("")
        dummy_nomad._print_banner()
        cprint(Fore.CYAN, "\n[*] Listing all known engines for fingerprinting...", bright=True)
        rows = []
        for key, data in ENGINES.items(): rows.append((data['name'], ", ".join(data['technology']), data['url']))
        dummy_nomad._print_table("Fingerprintable Engines", rows, ["Name", "Technology", "Homepage"])
        sys.exit(0)

    headers = {'User-Agent': 'GraphQLNomad/0.0.0'}
    if args.header:
        for h in args.header:
            try:
                name, value = h.split(":", 1)
                headers[name.strip()] = value.strip()
            except ValueError:
                cprint(Fore.RED, f"Invalid header format: '{h}'. Use 'Name: Value'.", bright=True)
                sys.exit(1)

    nomad = GraphQLNomad(url=args.url, headers=headers, proxy=args.proxy, timeout=args.timeout, follow_redirects=args.follow_redirects)
    nomad._print_banner()

    try:
        if args.detect:
            wordlist = None
            if args.wordlist:
                try:
                    with open(args.wordlist, 'r') as f: wordlist = [line.strip() for line in f if line.strip()]
                    cprint(Fore.WHITE, f"[*] Using custom wordlist from: {args.wordlist}")
                except FileNotFoundError:
                    cprint(Fore.RED, f"[x] Error: Wordlist file not found at '{args.wordlist}'", bright=True)
                    sys.exit(1)
            if not nomad.detect_endpoint(wordlist): sys.exit(1)
        else:
            cprint(Fore.CYAN, "[*] Skipping detection phase as requested.", bright=True)
            print(f"  -> Verifying provided endpoint: {args.url}")
            if not nomad._check_endpoint(args.url):
                cprint(Fore.YELLOW, "[?] Warning: Provided URL does not seem to be a valid GraphQL endpoint.", bright=True)
                if input("    Continue anyway? (y/n): ").lower() not in ['y', 'yes']:
                    cprint(Fore.RED, "Aborting.")
                    sys.exit(1)

        fingerprint_result = None
        if args.fingerprint:
            fingerprint_result = nomad.fingerprint_engine()
            if fingerprint_result:
                engine = ENGINES[fingerprint_result]
                cprint(Fore.GREEN, f"[!] Discovered GraphQL Engine: {engine['name']}", bright=True)
                print(f"    Technologies: {', '.join(engine['technology'])}")
                print(f"    Homepage: {engine['url']}")
            else:
                fingerprint_result = "Generic/Unknown"

        if args.output_file:
            cprint(Fore.CYAN, f"\n[*] Writing results to {args.output_file}...", bright=True)
            try:
                with open(args.output_file, 'w', newline='') as f:
                    import csv
                    writer = csv.writer(f)
                    writer.writerow(['url', 'detected_endpoint', 'detected_engine', 'timestamp_utc'])
                    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    engine_name = ENGINES.get(fingerprint_result, {}).get('name', fingerprint_result or 'N/A')
                    writer.writerow([nomad.base_url, nomad.endpoint_url, engine_name, timestamp])
            except IOError as e:
                cprint(Fore.RED, f"[x] Error writing to file: {e}", bright=True)

        if args.interactive:
            if nomad.fetch_schema():
                nomad.run_interactive_shell()
            else:
                cprint(Fore.YELLOW, "\nCould not fetch schema. The interactive shell requires a working introspection query.", bright=True)
        else:
            cprint(Fore.BLUE, "\n[*] Reconnaissance complete. Exiting as requested.", bright=True)

    except KeyboardInterrupt:
        cprint(Fore.YELLOW, "\n\n[*] User interrupted process. Exiting.", bright=True)
        sys.exit(0)
    except Exception as main_exception:
        cprint(Fore.RED, f"\nA critical error occurred: {main_exception}", bright=True)
        sys.exit(1)
