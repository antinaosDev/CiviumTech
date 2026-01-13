-- Drop problematic policies
drop policy if exists "Admins/Programmers can view all profiles" on public.users;
drop policy if exists "Programmer can manage departments" on public.departments;

-- Fix User visibility policy
-- Instead of querying the table recursively, allow users to see their own profile
-- AND allow users with 'PROGRAMADOR' or 'ADMIN' role to see everyone.
-- Crucial: To avoid recursion, we rely on the fact that checking your OWN record is cheap/safe
-- BUT "select role from public.users where id = auth.uid()" inside a policy on public.users IS recursive.

-- SOLUTION 1: Create a secure function (SECURITY DEFINER) to get role, bypassing RLS for the check.
CREATE OR REPLACE FUNCTION public.get_my_role()
RETURNS user_role AS $$
BEGIN
  RETURN (SELECT role FROM public.users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Re-create User Policy using the function
create policy "Admins/Programmers can view all profiles"
on public.users for select
using ( 
  auth.uid() = id -- Can always see self
  OR
  get_my_role() in ('ADMIN', 'PROGRAMADOR') -- Can see others if admin
);

-- Fix Department Policy
create policy "Programmer can manage departments" 
on public.departments for all 
using ( get_my_role() = 'PROGRAMADOR' );
