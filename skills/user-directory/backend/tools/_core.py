"""Shared backend for user-directory tools."""

import json

def _db():
    from models.db import db
    return db


def lookup_user(agent, args):
    q = args.get('query', '').strip()
    uid = args.get('user_id', '').strip()
    if uid:
        user = _db().get_user(uid)
        if user:
            return {'status': 'success', 'user': user}
        return {'status': 'not_found', 'message': 'User not found'}
    if q:
        results = _db().search_users(query=q)
        return {'status': 'success', 'users': results, 'count': len(results)}
    return {'status': 'error', 'message': 'Provide query or user_id'}


def get_user_summary(agent, args):
    uid = args.get('user_id', '').strip()
    if not uid:
        return {'status': 'error', 'message': 'user_id is required'}
    user = _db().get_user(uid)
    if not user:
        return {'status': 'not_found', 'message': 'User not found'}
    contacts = _db().get_contacts(uid)
    tags = _db().get_tags(uid)
    groups = _db().get_user_groups(uid)
    linked_agents = _db().get_user_agents(uid)
    agent_id = agent.get('id', '')
    access = _db().get_access_control_info(agent_id, uid)
    audit = _db().get_audit_log(uid, limit=5)
    return {
        'status': 'success',
        'user': user,
        'contacts': contacts,
        'tags': tags,
        'groups': groups,
        'linked_agents': linked_agents,
        'access_control': access,
        'recent_audit_entries': audit
    }


def list_users(agent, args):
    q = args.get('query', '')
    tags = args.get('tags', '')
    group_id = args.get('group_id', '')
    limit = min(args.get('limit', 20), 100)
    offset = args.get('offset', 0)
    tag_list = tags.split(',') if tags else None
    users = _db().search_users(
        query=q, tags=tag_list,
        group_id=group_id or None,
        limit=limit, offset=offset
    )
    return {'status': 'success', 'users': users, 'count': len(users)}


def add_user_contact(agent, args):
    uid = args.get('user_id', '').strip()
    channel_type = args.get('channel_type', '').strip()
    ext_uid = args.get('external_user_id', '').strip()
    value = args.get('value', ext_uid)
    if not uid or not channel_type or not ext_uid:
        return {'status': 'error', 'message': 'user_id, channel_type, and external_user_id are required'}
    contact = _db().add_contact(
        uid, channel_type, ext_uid, value=value,
        actor_type='agent', actor_id=agent.get('id', '')
    )
    if not contact:
        return {'status': 'error', 'message': 'Failed to add contact (may already exist)'}
    return {'status': 'success', 'contact': contact}


def manage_user_tags(agent, args):
    uid = args.get('user_id', '').strip()
    action = args.get('action', '').strip()
    tag = args.get('tag', '').strip()
    if not uid or not action or not tag:
        return {'status': 'error', 'message': 'user_id, action, and tag are required'}
    if action == 'add':
        ok = _db().add_tag(uid, tag, actor_type='agent', actor_id=agent.get('id', ''))
    elif action == 'remove':
        ok = _db().remove_tag(uid, tag, actor_type='agent', actor_id=agent.get('id', ''))
    else:
        return {'status': 'error', 'message': f'Invalid action: {action}. Use "add" or "remove".'}
    if not ok:
        return {'status': 'error', 'message': f'Failed to {action} tag "{tag}"'}
    current_tags = _db().get_tags(uid)
    return {'status': 'success', 'tags': current_tags}


def list_groups(agent, args):
    groups = _db().list_groups()
    result = []
    for g in groups:
        users, group_agents = _db().get_group_members(g['id'])
        result.append({
            'id': g['id'],
            'name': g['name'],
            'description': g.get('description', ''),
            'user_count': len(users),
            'agent_count': len(group_agents)
        })
    return {'status': 'success', 'groups': result, 'count': len(result)}


def create_group(agent, args):
    name = args.get('name', '').strip()
    description = args.get('description', '').strip()
    if not name:
        return {'status': 'error', 'message': 'Group name is required'}
    group = _db().create_group(name=name, description=description, created_by=agent.get('id', ''))
    if not group:
        return {'status': 'error', 'message': 'Failed to create group'}
    return {'status': 'success', 'group': group}


def manage_user_groups(agent, args):
    uid = args.get('user_id', '').strip()
    group_id = args.get('group_id', '').strip()
    action = args.get('action', '').strip()
    if not uid or not group_id or not action:
        return {'status': 'error', 'message': 'user_id, group_id, and action are required'}
    if action == 'add':
        ok = _db().add_group_member(group_id, 'user', uid)
    elif action == 'remove':
        ok = _db().remove_group_member(group_id, 'user', uid)
    else:
        return {'status': 'error', 'message': f'Invalid action: {action}'}
    if not ok:
        return {'status': 'error', 'message': f'Failed to {action} user from group'}
    return {'status': 'success', 'message': f'User {action}ed from group'}


def get_access_control_info(agent, args):
    uid = args.get('user_id', '').strip()
    if not uid:
        return {'status': 'error', 'message': 'user_id is required'}
    agent_id = agent.get('id', '')
    info = _db().get_access_control_info(agent_id, uid)
    return {'status': 'success', 'access_control': info}


def block_user(agent, args):
    uid = args.get('user_id', '').strip()
    blocked = args.get('blocked', True)
    reason = args.get('reason', '')
    if not uid:
        return {'status': 'error', 'message': 'user_id is required'}
    agent_id = agent.get('id', '')
    if not _db().can_block_user(agent_id, uid):
        return {'status': 'error', 'message': 'Permission denied: only admin agents can block users'}
    if blocked:
        ok = _db().block_user(uid, reason=reason, actor_type='agent', actor_id=agent_id)
    else:
        ok = _db().unblock_user(uid, actor_type='agent', actor_id=agent_id)
    if not ok:
        return {'status': 'error', 'message': 'Failed to update block status'}
    return {'status': 'success', 'blocked': blocked}


def merge_users(agent, args):
    source = args.get('source_id', '').strip()
    target = args.get('target_id', '').strip()
    if not source or not target:
        return {'status': 'error', 'message': 'source_id and target_id are required'}
    agent_id = agent.get('id', '')
    if not _db().can_merge_users(agent_id):
        return {'status': 'error', 'message': 'Permission denied: only admin agents can merge users'}
    ok = _db().merge_users(source, target, actor_type='agent', actor_id=agent_id)
    if not ok:
        return {'status': 'error', 'message': 'Merge failed'}
    return {'status': 'success', 'message': f'User {source} merged into {target}'}


# Map function names to implementations
HANDLERS = {
    'lookup_user': lookup_user,
    'get_user_summary': get_user_summary,
    'list_users': list_users,
    'add_user_contact': add_user_contact,
    'manage_user_tags': manage_user_tags,
    'list_groups': list_groups,
    'create_group': create_group,
    'manage_user_groups': manage_user_groups,
    'get_access_control_info': get_access_control_info,
    'block_user': block_user,
    'merge_users': merge_users,
}
