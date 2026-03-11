import os
import PyPDF2
from mcp_server.config import mcp

# Constants
MANUALS_DIR = os.path.join(os.path.dirname(__file__), "manuals")
VERSION_MAP = {
    "latest": "manual_v3.pdf",
    "v1": "manual_v1.pdf",
    "v2": "manual_v2.pdf",
    "v3": "manual_v3.pdf",
}


def _resolve_filename(version: str) -> str | None:
    """Resolve version string to filename."""
    return VERSION_MAP.get(version.lower())


def _get_pdf_path(filename: str) -> str:
    """Build full path to PDF file."""
    return os.path.join(MANUALS_DIR, filename)


def _extract_pdf_text(pdf_path: str) -> tuple[int, str]:
    """Extract text and page count from a PDF file."""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        pages_text = [reader.pages[i].extract_text() for i in range(len(reader.pages))]
        return len(reader.pages), "\n\n".join(pages_text)


def _format_manual(
    version: str, filename: str, pdf_path: str, num_pages: int, text: str
) -> str:
    """Format manual content as readable markdown."""
    return (
        f"# Setup Manual - {version.upper()}\n\n"
        f"**File:** {filename}\n"
        f"**Pages:** {num_pages}\n"
        f"**Location:** {pdf_path}\n"
        f"---\n\n"
        f"{text}"
    )


@mcp.resource("docs://setup-manual/{version}")
def get_setup_manual(version: str = "latest") -> str:
    """
    Resource Template: Setup manual from local PDF files.
    Valid URIs:
    - docs://setup-manual/latest  → Most recent version (v3)
    - docs://setup-manual/v1      → First version
    - docs://setup-manual/v2      → Second version
    - docs://setup-manual/v3      → Third version
    """
    try:
        filename = _resolve_filename(version)
        if not filename:
            return f"Version '{version}' not found. Valid versions: {list(VERSION_MAP.keys())}"

        pdf_path = _get_pdf_path(filename)
        if not os.path.exists(pdf_path):
            return f"File not found: {pdf_path}"

        num_pages, text = _extract_pdf_text(pdf_path)
        return _format_manual(version, filename, pdf_path, num_pages, text)

    except Exception as e:
        raise RuntimeError(f"Failed to read manual: {str(e)}")
