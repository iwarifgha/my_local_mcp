# Events MCP

A small local [Model Context Protocol](https://modelcontextprotocol.io) (MCP) client and server for an imaginary events catalog. The server stores three sample events and exposes them as tools. The client starts that server, connects over standard input and output, and lets you call the tools from a menu.

A separate command parser turns short English phrases into the same tool calls. A language model is not connected. Nothing in the running program calls an API or needs an API key.

## What you can do

- List every event
- Look up one event by numeric ID
- Search by a word in the name, location, or category

## How it fits together

```text
mcp_client.py                         mcp_server.py
numbered menu                         EVENTS catalog
      |                                     |
      |  stdio (JSON-RPC / MCP)             |
      +------------ spawns and calls -------+
                    list_events
                    get_event
                    search_events

parser.py
English phrase  -->  ("tool_name", {arguments})
```

`mcp_client.py` launches `mcp_server.py` with the same Python interpreter and keeps the connection open until you exit. You do not start the server yourself for normal use.

`parser.py` only decides which tool and arguments a phrase maps to. It does not open an MCP connection or read the catalog.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (recommended), or `pip`

## Setup

From the project root:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

On Windows, activate with `.venv\Scripts\activate`.

Without uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

`pyproject.toml` also lists `anthropic`, `prompt-toolkit`, and `python-dotenv`. The events client, server, and parser do not import them.

## Run the client

```bash
uv run mcp_client.py
```

Or, with the virtual environment already active:

```bash
python mcp_client.py
```

The client prints the tools it discovered, then shows this menu:

```text
1. List events
2. Get event by ID
3. Search events
0. Exit
```

- **1** calls `list_events` with no arguments.
- **2** asks for an integer ID and calls `get_event`. A non-integer is rejected before the call. An unknown ID comes back from the server as `{"error": "No event found with ID N"}`.
- **3** asks for a search term and calls `search_events`.
- **0** closes the connection.

Results are printed from the tool's structured content when the server provides it, and from text content otherwise.

Running `mcp_server.py` on its own starts an MCP process that waits for protocol messages on stdin. Use the client, which starts the server for you.

## Try the command parser

```bash
uv run parser.py
```

Type a phrase and press Enter. Each line prints the parsed tool call, or `None` when the phrase is not recognized. `quit` ends the loop.

The parser lowercases the text, strips `?` `!` `.` and `,`, and matches the whole line.

| You type | Parsed call |
| --- | --- |
| `show me all the upcoming events` | `("list_events", {})` |
| `list events` | `("list_events", {})` |
| `what events are available?` | `("list_events", {})` |
| `get the details for event #2` | `("get_event", {"event_id": 2})` |
| `show event 1` | `("get_event", {"event_id": 1})` |
| `event id 3` | `("get_event", {"event_id": 3})` |
| `search for music` | `("search_events", {"query": "music"})` |
| `find events in Lagos` | `("search_events", {"query": "lagos"})` |
| `look for technology` | `("search_events", {"query": "technology"})` |
| `help` | `("help", {})` |
| `quit` | `("exit", {})` |

List phrases that match include `show`, `list`, and `display` with optional words such as `me`, `all`, `the`, and `upcoming`, plus `what events are available`, `what events are there`, and `all events`.

Lookup phrases start with `get`, `show`, `find`, `open`, or `view`, and include an event number. `event id 2` and `event #2` also match. A leading `#` is allowed on the number.

Search phrases start with `find`, `search`, `search for`, or `look for`, optionally after `please`. Filler words (`event`, `events`, `in`, `at`, `near`, `the`, and similar) are removed from the remainder, and what is left becomes `query`.

`help`, `commands`, and `what can you do` map to `help`. `exit`, `quit`, `bye`, and `goodbye` map to `exit`. Those two names are parser results only. The server does not implement them.

`parse_command` in `parser.py` is the function to call if you later connect this parser to the client.

## Tools

Defined in `mcp_server.py` with `@mcp.tool()`.

| Tool | Arguments | Returns |
| --- | --- | --- |
| `list_events` | none | Every event |
| `get_event` | `event_id: int` | That event, or `{"error": "No event found with ID N"}` |
| `search_events` | `query: str` | Events whose name, location, or category contains `query`, case-insensitive. A blank query returns `[]` |

Each event is a dict with `id`, `name`, `location`, and `category`.

## Sample events

| ID | Name | Location | Category |
| --- | --- | --- | --- |
| 1 | Port Harcourt Music Festival | Port Harcourt | Music |
| 2 | Lagos Tech Conference | Lagos | Technology |
| 3 | Port Harcourt Startup Meetup | Port Harcourt | Technology |

The list lives in `EVENTS` in `mcp_server.py`. Edit that list to add or change events. Restart the client so it launches a server with the new data.

To add a tool, write a function, decorate it with `@mcp.tool()`, and give it a docstring. The docstring is the description the client prints at startup. A new tool is callable with `client.call_tool` once the menu (or a parser rule) knows its name and arguments.

## Project layout

```text
mcp_server.py     Event catalog and MCP tools. Speaks MCP on stdin/stdout.
mcp_client.py     Menu client. Spawns the server and calls tools.
parser.py         Rule-based phrases -> tool name and arguments.
pyproject.toml    Package metadata and dependencies.
uv.lock           Locked dependency versions.
core/             Unused chat scaffolding. Not imported by the events program.
```

## Protocol

The client uses `StdioServerParameters` and `mcp.Client` from the Python MCP SDK (`mcp>=1.8`). The server is `mcp.server.MCPServer`, named `Local Event Server`, and `mcp.run()` serves it on stdio. Tool discovery is `list_tools()`. Calls go through `call_tool(name, arguments)`.
