from supabase import create_client, Client

SUPABASE_URL = "https://hereajktyvuktkwrbtev.supabase.co"
SUPABASE_KEY = "sb_publishable_DXBiPAUNP2j0LdN4YYl1qA_WDP8ssrm"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)