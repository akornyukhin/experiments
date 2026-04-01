import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STORE_MCP_URL = "http://127.0.0.1:8001/mcp"
PRODUCT_WIDGET_PATH = BASE_DIR / "app/widgets/simple_product.widget"
