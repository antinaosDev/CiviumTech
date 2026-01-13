import argparse
import sys
import toml
from supabase import create_client, Client

# Load Secrets
try:
    secrets = toml.load(".streamlit/secrets.toml")
    URL = secrets["SUPABASE_URL"]
    SERVICE_KEY = secrets.get("SUPABASE_SERVICE_KEY")
    if not SERVICE_KEY:
        print("Error: SUPABASE_SERVICE_KEY no encontrada en .streamlit/secrets.toml")
        sys.exit(1)
except Exception as e:
    print(f"Error cargando secretos: {e}")
    sys.exit(1)

# Init Admin Client
supabase: Client = create_client(URL, SERVICE_KEY)

def get_department_id(code):
    if not code:
        return None
    resp = supabase.table("departments").select("id").eq("code", code).single().execute()
    if resp.data:
        return resp.data["id"]
    return None

def create_admin_user(email, password, role, dept_code):
    print(f"Creando usuario {email} con rol {role} en departamento {dept_code}...")
    
    # 1. Create User in Auth
    user_id = None
    try:
        attributes = {
            "email": email,
            "password": password,
            "email_confirm": True
        }
        user = supabase.auth.admin.create_user(attributes)
        user_id = user.user.id
        print(f"Usuario Auth creado: {user_id}")
    except Exception as e:
        print(f"Error creando usuario Auth (puede que ya exista): {e}")
        return

    # 2. Link in public.users
    link_user_profile(user_id, email, role, dept_code)

def link_user_profile(user_id, email, role, dept_code):
    try:
        dept_id = get_department_id(dept_code)
        
        data = {
            "id": user_id,
            "email": email,
            "full_name": email.split("@")[0],
            "role": role,
            "department_id": dept_id
        }
        
        print(f"Intentando insertar: {data}")
        res = supabase.table("users").upsert(data).execute()
        print(f"Perfil de usuario actualizado en public.users: {email} -> {role}")
        
    except Exception as e:
        print(f"Error creando perfil en tabla users: {e}")
        if hasattr(e, 'code'):
             print(f"Code: {e.code}")
        if hasattr(e, 'details'):
             print(f"Details: {e.details}")
        if hasattr(e, 'hint'):
             print(f"Hint: {e.hint}")

def main():
    parser = argparse.ArgumentParser(description="Admin Tool for GovTech CRM")
    subparsers = parser.add_subparsers(dest="command")
    
    # Create User Command
    user_parser = subparsers.add_parser("create-user", help="Create a new user")
    user_parser.add_argument("--email", required=True)
    user_parser.add_argument("--password", required=True)
    user_parser.add_argument("--role", default="USER_CIUDADANO", choices=["PROGRAMADOR", "ADMIN", "USER_FUNCIONARIO", "USER_CIUDADANO"])
    user_parser.add_argument("--dept", help="Department Code (e.g., ALC, DIDECO)")

    # Link Existing User Command
    link_parser = subparsers.add_parser("link-user", help="Link an existing Auth UID to a profile")
    link_parser.add_argument("--uid", required=True)
    link_parser.add_argument("--email", required=True)
    link_parser.add_argument("--role", default="USER_CIUDADANO", choices=["PROGRAMADOR", "ADMIN", "USER_FUNCIONARIO", "USER_CIUDADANO"])
    link_parser.add_argument("--dept", help="Department Code (e.g., ALC, DIDECO)")

    # List Users Command
    subparsers.add_parser("list-users", help="List all Auth users")

    # Reset Password Command
    reset_parser = subparsers.add_parser("reset-password", help="Reset user password")
    reset_parser.add_argument("--uid", required=True)
    reset_parser.add_argument("--newpass", required=True)

    args = parser.parse_args()

    if args.command == "create-user":
        create_admin_user(args.email, args.password, args.role, args.dept)
    elif args.command == "link-user":
        print(f"Vinculando usuario existente {args.uid}...")
        link_user_profile(args.uid, args.email, args.role, args.dept)
    elif args.command == "list-users":
        try:
            users = supabase.auth.admin.list_users()
            print("Usuarios en Auth:")
            for u in users:
                print(f" - {u.email} [UID: {u.id}]")
        except Exception as e:
            print(f"Error listando usuarios: {e}")
    elif args.command == "reset-password":
        try:
            print(f"Reseteando clave y confirmando email para UID: {args.uid}...")
            supabase.auth.admin.update_user_by_id(
                args.uid, 
                {"password": args.newpass, "email_confirm": True}
            )
            print("¡Contraseña actualizada y Email confirmado exitosamente!")
        except Exception as e:
            print(f"Error actualizando contraseña: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
