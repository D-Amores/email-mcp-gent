from mcp_server.config import mcp

# Import tools so mcp registers them
from mcp_server.tools.list_emails import list_emails
from mcp_server.tools.send_email import send_email

if __name__ == "__main__":
    mcp.run()
