
import re


def parse_command(command: str):
    """Convert a simple natural-language command into an MCP tool call."""

    text = command.casefold().strip()
    text = re.sub(r"[?!.,]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    if not text:
        return None

    # Exit commands
    if text in {"exit", "quit", "bye", "goodbye"}:
        return ("exit", {})

    # Help commands
    if text in {"help", "commands", "what can you do"}:
        return ("help", {})

    # Commands that request all events
    list_patterns = [
        r"show (me )?(all )?(the )?(upcoming )?events",
        r"list (all )?(the )?(upcoming )?events",
        r"display (all )?(the )?events",
        r"what events (are )?(available|there)",
        r"all events",
    ]

    if any(re.fullmatch(pattern, text) for pattern in list_patterns):
        return ("list_events", {})

    # Commands that request a particular event by ID
    id_patterns = [
        r"(?:get|show|find|open|view) (?:me )?"
        r"(?:the )?(?:details|information|info) "
        r"(?:for|of|about) (?:event )?#?(\d+)",

        r"(?:get|show|find|open|view) "
        r"(?:event )?#?(\d+)",

        r"event (?:id )?#?(\d+)",
    ]

    for pattern in id_patterns:
        match = re.fullmatch(pattern, text)

        if match:
            return (
                "get_event",
                {"event_id": int(match.group(1))},
            )

    # Search commands
    search_prefix = re.match(
        r"^(?:please )?(?:find|search for|search|look for)"
        r"(?: me)?\s+(.+)$",
        text,
    )

    if search_prefix:
        query = search_prefix.group(1)

        # Remove words that describe the request rather than
        # the event we want to find.
        query = re.sub(
            r"\b(events?|all|the|upcoming|available|"
            r"please|in|at|near|for|me|that|are|is|"
            r"located|happening)\b",
            " ",
            query,
        )

        query = re.sub(r"\s+", " ", query).strip()

        if query:
            return ("search_events", {"query": query})

    return None


if __name__ == "__main__":
    while True:
        command = input("Try a command (or quit): ")
        print("Parsed:", parse_command(command))
