from mcp_server.config import mcp

# Import tools
from mcp_server.tools.list_emails import list_emails
from mcp_server.tools.send_email import send_email

# Import resources
from mcp_server.resources.email_profile import get_profile

if __name__ == "__main__":
    mcp.run()
