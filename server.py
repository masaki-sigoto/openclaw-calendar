#!/usr/bin/env python3
"""
Google Calendar MCP Server
複数Googleアカウントのカレンダー・タスクを管理するMCPサーバー
"""

import os
import json
import sys
import shlex
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Google API Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 通知サービス
from notifications import NotificationService

# MCP SDK (これは後でインストール)
# from mcp import Server, Tool

# OAuth2 スコープ
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

class GoogleCalendarMCP:
    """Google Calendar MCP Server"""
    
    def __init__(self, credentials_file: str = 'credentials.json', enable_notifications: bool = True):
        self.credentials_file = credentials_file
        self.tokens = {}  # {account_name: credentials}
        self.services = {}  # {account_name: {calendar: service, tasks: service}}
        self.enable_notifications = enable_notifications
        self.notifier = NotificationService() if enable_notifications else None
        
    def authenticate(self, account_name: str) -> Credentials:
        """
        OAuth認証フロー
        account_name: 'crosslink' or 'programming_school'
        """
        token_file = f'token_{account_name}.json'
        creds = None
        
        # 既存のトークンがあれば読み込み
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # トークンが無効なら再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.tokens[account_name] = creds
        
        # サービス初期化
        self.services[account_name] = {
            'calendar': build('calendar', 'v3', credentials=creds),
            'tasks': build('tasks', 'v1', credentials=creds)
        }
        
        return creds
    
    def create_event(
        self,
        account: str,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        カレンダーイベントを作成
        
        Args:
            account: 'crosslink' or 'programming_school'
            summary: イベントのタイトル
            start_time: 開始時刻 (ISO 8601形式: '2026-03-05T14:00:00+09:00')
            end_time: 終了時刻
            description: 説明（オプション）
            location: 場所（オプション）
        
        Returns:
            作成されたイベントの情報
        """
        if account not in self.services:
            raise ValueError(f"Account '{account}' not authenticated")
        
        # 終日イベントかどうかを判定（日付のみで時刻がない場合）
        is_all_day = 'T' not in start_time
        
        if is_all_day:
            # 終日イベント
            event = {
                'summary': summary,
                'start': {'date': start_time},
                'end': {'date': end_time},
            }
        else:
            # 時刻指定のイベント
            event = {
                'summary': summary,
                'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
                'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
            }
        
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        
        calendar_service = self.services[account]['calendar']
        event = calendar_service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        # 通知は calendar_tools.py で送信する
        
        return event
    
    def list_events(
        self,
        account: str,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        カレンダーイベント一覧を取得
        
        Args:
            account: 'crosslink' or 'programming_school'
            time_min: 開始時刻（ISO 8601形式）
            time_max: 終了時刻（ISO 8601形式）
            max_results: 最大取得件数
        
        Returns:
            イベントのリスト
        """
        if account not in self.services:
            raise ValueError(f"Account '{account}' not authenticated")
        
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        calendar_service = self.services[account]['calendar']
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    
    def create_task(
        self,
        account: str,
        title: str,
        due: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Google Tasksにタスクを作成
        
        Args:
            account: 'crosslink' or 'programming_school'
            title: タスクのタイトル
            due: 期限（RFC 3339形式: '2026-03-05T00:00:00Z'）
            notes: メモ（オプション）
        
        Returns:
            作成されたタスクの情報
        """
        if account not in self.services:
            raise ValueError(f"Account '{account}' not authenticated")
        
        task = {'title': title}
        
        if due:
            task['due'] = due
        if notes:
            task['notes'] = notes
        
        tasks_service = self.services[account]['tasks']
        task = tasks_service.tasks().insert(
            tasklist='@default',
            body=task
        ).execute()
        
        return task
    
    def list_tasks(
        self,
        account: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Google Tasksのタスク一覧を取得
        
        Args:
            account: 'crosslink' or 'programming_school'
            max_results: 最大取得件数
        
        Returns:
            タスクのリスト
        """
        if account not in self.services:
            raise ValueError(f"Account '{account}' not authenticated")
        
        tasks_service = self.services[account]['tasks']
        results = tasks_service.tasks().list(
            tasklist='@default',
            maxResults=max_results
        ).execute()
        
        return results.get('items', [])


def main():
    """MCP Server起動"""
    print("Google Calendar MCP Server starting...")
    
    # 作業ディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # MCPサーバー初期化
    mcp = GoogleCalendarMCP()
    
    # TODO: MCPプロトコルの実装
    # とりあえずテスト用のCLI
    print("Available commands:")
    print("  auth <account>  - Authenticate account (crosslink/programming_school)")
    print("  list <account>  - List upcoming events")
    print("  create <account> <title> <start> <end>  - Create event")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            cmd = shlex.split(user_input)
            
            if cmd[0] == 'auth':
                account = cmd[1]
                print(f"Authenticating {account}...")
                mcp.authenticate(account)
                print(f"✅ {account} authenticated!")
            
            elif cmd[0] == 'list':
                account = cmd[1]
                events = mcp.list_events(account)
                print(f"\n📅 Upcoming events for {account}:")
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(f"  - {start}: {event['summary']}")
            
            elif cmd[0] == 'create':
                account = cmd[1]
                title = cmd[2]
                start = cmd[3]
                end = cmd[4]
                event = mcp.create_event(account, title, start, end)
                print(f"✅ Event created: {event['htmlLink']}")
            
            elif cmd[0] == 'quit' or cmd[0] == 'exit':
                break
            
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
