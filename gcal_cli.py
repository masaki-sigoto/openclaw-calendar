#!/usr/bin/env python3
"""
Google Calendar CLI for OpenClaw
OpenClawから直接呼び出せるCLIツール
"""

import sys
import json
import argparse
from server import GoogleCalendarMCP


def main():
    parser = argparse.ArgumentParser(description='Google Calendar CLI for OpenClaw')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate account')
    auth_parser.add_argument('account', help='Account name (crosslink/programming_school)')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List upcoming events')
    list_parser.add_argument('account', help='Account name')
    list_parser.add_argument('--max', type=int, default=10, help='Maximum number of events')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create calendar event')
    create_parser.add_argument('account', help='Account name')
    create_parser.add_argument('title', help='Event title')
    create_parser.add_argument('start', help='Start time (ISO 8601)')
    create_parser.add_argument('end', help='End time (ISO 8601)')
    create_parser.add_argument('--description', help='Event description')
    create_parser.add_argument('--location', help='Event location')
    create_parser.add_argument('--no-notify', action='store_true', help='Disable notifications')
    
    # parse command
    create_parser = subparsers.add_parser('parse', help='Parse natural language to create event')
    create_parser.add_argument('text', help='Natural language text')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # MCPサーバー初期化
    mcp = GoogleCalendarMCP(enable_notifications=not getattr(args, 'no_notify', False))
    
    try:
        if args.command == 'auth':
            print(f"Authenticating {args.account}...")
            mcp.authenticate(args.account)
            print(f"✅ {args.account} authenticated!")
            return 0
        
        elif args.command == 'list':
            # 自動認証
            if args.account not in mcp.services:
                print(f"Authenticating {args.account}...")
                mcp.authenticate(args.account)
            
            events = mcp.list_events(args.account, max_results=args.max)
            print(f"📅 Upcoming events for {args.account}:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  - {start}: {event['summary']}")
            return 0
        
        elif args.command == 'create':
            # 自動認証
            if args.account not in mcp.services:
                print(f"Authenticating {args.account}...")
                mcp.authenticate(args.account)
            
            event = mcp.create_event(
                account=args.account,
                summary=args.title,
                start_time=args.start,
                end_time=args.end,
                description=args.description,
                location=args.location
            )
            print(f"✅ Event created: {event['htmlLink']}")
            return 0
        
        elif args.command == 'parse':
            # TODO: 自然言語パース機能（AIで日時とタイトルを抽出）
            print("⚠️  Natural language parsing not yet implemented")
            print("Use the 'create' command with explicit parameters instead")
            return 1
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
