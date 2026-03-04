# 🗓️ OpenClaw Google Calendar Integration

OpenClawで複数のGoogleアカウントのカレンダー・タスクを**自然言語**で管理するシステム。

> 「明日14時にA社と打ち合わせ、1時間」→ 自動でカレンダー登録 + 通知送信 🎉

---

## ✨ 主な機能

### 📅 基本機能
- ✅ **複数アカウント対応** - 複数のGoogleアカウントを統合管理
- ✅ **自然言語入力** - 「明日14時にMTG、1時間」で自動登録
- ✅ **アカウント自動判定** - キーワードから自動でアカウントを判定
- ✅ **確認フロー** - 自動判定時は確認、明示的指定時は即登録
- ✅ **通知機能** - iMessage + Chatwork に自動通知
- ✅ **カレンダー監視** - 新しいイベントを自動検出して通知

### 🚀 高度な機能
- ✅ **統合カレンダー表示** - 複数アカウントの予定を統合表示、空き時間検索
- ✅ **予定の編集・削除** - タイトル検索で簡単に編集・削除
- ✅ **定期予定の管理** - 「毎週水曜10時にMTG」で繰り返し予定を作成
- ✅ **リマインダー機能** - 予定の事前通知、今日の予定サマリー
- ✅ **スマート提案** - 空き時間提案、ダブルブッキング検出、スケジュール最適化
- ✅ **Google Tasks 連携** - カレンダーとタスクを統合管理
- ✅ **予定のテンプレート** - よく使う予定をワンコマンドで作成

---

## 🚀 クイックスタート

### 1. セットアップ

```bash
git clone https://github.com/masaki-sigoto/openclaw-calendar.git
cd openclaw-calendar
./setup.sh
```

### 2. Google Cloud 設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Google Calendar API と Google Tasks API を有効化
3. OAuth 2.0 クライアントIDを作成
4. `credentials.json` をダウンロードして配置

### 3. 初回認証

```bash
source venv/bin/activate
python server.py
> auth crosslink
> auth programming_school
```

---

## 📖 使い方

### OpenClaw からの使用

```
真熙さん: 「明日14時にA社と打ち合わせ、1時間」
OpenClaw: → カレンダーに登録 + 通知送信 ✅
```

### コマンドライン

```bash
# 予定を作成
python calendar_tools.py add "明日14時にMTG、1時間"

# 今日の予定を確認
python calendar_view.py today

# 空き時間を検索
python calendar_view.py free 7

# 予定を削除
python calendar_edit.py delete "テスト会議"

# 定期予定を作成
python calendar_recurring.py from-text "毎週水曜10時にチームMTG、1時間"

# スマート提案
python calendar_smart.py suggest 60 7

# Google Tasks 統合
python calendar_tasks.py unified

# テンプレートを使用
python calendar_templates.py use "A社MTG" "2026-03-05T14:00:00+09:00"
```

---

## 📁 ファイル構成

| ファイル | 説明 |
|---------|------|
| `server.py` | メインサーバー（OAuth認証、カレンダー・タスク操作） |
| `calendar_tools.py` | 自然言語パーサー、イベント作成 |
| `calendar_view.py` | 統合カレンダー表示、空き時間検索 |
| `calendar_edit.py` | 予定の編集・削除 |
| `calendar_recurring.py` | 定期予定の管理 |
| `calendar_reminder.py` | リマインダー機能 |
| `calendar_smart.py` | スマート提案 |
| `calendar_tasks.py` | Google Tasks 連携 |
| `calendar_templates.py` | 予定のテンプレート |
| `calendar_monitor.py` | カレンダー監視（新しいイベント検出） |
| `openclaw_helper.py` | ヘルパー関数 |
| `openclaw_integration.py` | OpenClaw 統合（iMessage, Chatwork通知） |
| `notifications.py` | 通知サービス |

---

## 🔧 カスタマイズ

### アカウント判定ルール

`openclaw_helper.py` の `determine_account()` 関数でキーワードを編集：

```python
crosslink_keywords = [
    'a社', 'b社', '営業', '商談', '提案',
    'ラーニング', 'seo', 'ブログ'
]

programming_keywords = [
    '体験会', 'ココグラム', '座席表', 'シフト',
    '名古屋', '関西', '東海'
]
```

### 通知設定

`.env` ファイルで Chatwork 通知を設定：

```bash
CHATWORK_API_TOKEN=your_token_here
CHATWORK_ROOM_ID=your_room_id_here
```

---

## 📚 詳細ドキュメント

- [📖 詳細な使い方](README_FULL.md)
- [📝 Changelog](CHANGELOG.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🤝 貢献

プルリクエスト歓迎！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

---

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

---

## 🙏 謝辞

- [OpenClaw](https://openclaw.ai) - AIアシスタントフレームワーク
- [Google Calendar API](https://developers.google.com/calendar)
- [Google Tasks API](https://developers.google.com/tasks)

---

**作成日**: 2026年3月4日

🌟 **Star** をつけてくれると嬉しいです！
