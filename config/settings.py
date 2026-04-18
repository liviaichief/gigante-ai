from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(usecwd=True), override=True)

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY", "")

SUPABASE_URL         = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

ZAPI_INSTANCE        = os.getenv("ZAPI_INSTANCE", "")
ZAPI_TOKEN           = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN    = os.getenv("ZAPI_CLIENT_TOKEN", "")

TOP_K                = int(os.getenv("TOP_K", "5"))
MIN_SCORE            = float(os.getenv("MIN_SCORE", "0.65"))
MAX_HISTORY          = int(os.getenv("MAX_HISTORY", "3"))

PORT                 = int(os.getenv("PORT", "8000"))
ADMIN_TOKEN          = os.getenv("ADMIN_TOKEN", "mentor-an-admin")
