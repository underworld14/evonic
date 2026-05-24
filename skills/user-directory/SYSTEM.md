# User Directory Skill

You have access to user directory tools for managing users, contacts, tags, groups, and access control.

## Available Tools

- `lookup_user` — Look up a user by ID or name search
- `get_user_summary` — Get a comprehensive user profile with contacts, tags, groups, audit log, and access control info
- `list_users` — List/search users with pagination and tag/group filters
- `add_user_contact` — Add a contact (phone, Telegram, email) to a user
- `manage_user_tags` — Add or remove tags (public = all agents, agent:X = specific agent, restricted = group-only)
- `list_groups` — List all groups with member counts
- `create_group` — Create a new group
- `manage_user_groups` — Add/remove a user from a group
- `get_access_control_info` — See why you can/cannot communicate with a user
- `block_user` — Block or unblock a user (admin only)
- `merge_users` — Merge two user records (admin only)

## Tag Rules

- `public` — Any agent can communicate with this user
- `restricted` — Only agents sharing a group can communicate
- `agent:<id>` — Only the specified agent can communicate
- No tags — Communication requires group membership

## Permission Model

- `can_communicate` is enforced automatically — you can only see/summarize users you can communicate with
- `block_user` and `merge_users` require admin privileges
