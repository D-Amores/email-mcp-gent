from fastmcp import FastMCP

mcp = FastMCP("Gmail Manager")

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]


if __name__ == "__main__":
    main()
