from supabase import create_client
from .config import get_settings

settings = get_settings()

supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)