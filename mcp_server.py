
from mcp.server import MCPServer

# Create the MCP server.
mcp = MCPServer("Local Event Server")

# Sample event database.
EVENTS = [
    {
        "id": 1,
        "name": "Port Harcourt Music Festival",
        "location": "Port Harcourt",
        "category": "Music",
    },
    {
        "id": 2,
        "name": "Lagos Tech Conference",
        "location": "Lagos",
        "category": "Technology",
    },
    {
        "id": 3,
        "name": "Port Harcourt Startup Meetup",
        "location": "Port Harcourt",
        "category": "Technology",
    },
]


@mcp.tool()
def list_events() -> list[dict]:
    """Return all available events."""
    return EVENTS


@mcp.tool()
def get_event(event_id: int) -> dict:
    """Get an event by its unique ID."""

    for event in EVENTS:
        if event["id"] == event_id:
            return event

    return {"error": f"No event found with ID {event_id}"}


@mcp.tool()
def search_events(query: str) -> list[dict]:
    """Search events by name, location, or category."""

    query = query.strip().casefold()

    if not query:
        return []

    return [
        event
        for event in EVENTS
        if query in event["name"].casefold()
        or query in event["location"].casefold()
        or query in event["category"].casefold()
    ]


if __name__ == "__main__":
    mcp.run()
