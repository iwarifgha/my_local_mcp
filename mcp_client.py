import asyncio
from pathlib import Path
import sys

from mcp import Client, StdioServerParameters


async def main():
    # Locate server.py relative to this file.
    server_path = Path(__file__).with_name("mcp_server.py")

    # Tell the MCP client how to launch the server.
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    # Launch the server and establish the MCP connection.
    async with Client(server) as client:

        print("\nConnected to the MCP server.")

        # Discover the server's available tools.
        response = await client.list_tools()

        tools = response.tools

        print("\nAvailable tools:")

        for index, tool in enumerate(tools, start=1):
            print(f"{index}. {tool.name} - {tool.description}")

        while True:
            print("\nSelect a tool:")
            print("1. List events")
            print("2. Get event by ID")
            print("3. Search events")
            print("0. Exit")

            choice = input("\nYour choice: ").strip()

            if choice == "0":
                print("Disconnecting...")
                break

            elif choice == "1":
                tool_name = "list_events"
                arguments = {}

            elif choice == "2":
                try:
                    event_id = int(input("Enter event ID: "))
                except ValueError:
                    print("Please enter a valid integer.")
                    continue

                tool_name = "get_event"
                arguments = {"event_id": event_id}

            elif choice == "3":
                query = input("Enter a search term: ").strip()

                tool_name = "search_events"
                arguments = {"query": query}

            else:
                print("Invalid choice.")
                continue

            # Send the tool request through MCP.
            result = await client.call_tool(
                tool_name,
                arguments,
            )

            # Display the result.
            if result.is_error:
                print("\nThe server reported an error.")
            else:
                print("\nResult:")

                if result.structured_content is not None:
                    print(result.structured_content)
                else:
                    for content in result.content:
                        if hasattr(content, "text"):
                            print(content.text)
                        else:
                            print(content)


if __name__ == "__main__":
    asyncio.run(main())
