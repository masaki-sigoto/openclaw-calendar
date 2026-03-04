# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-04

### Added
- 🎉 初回リリース
- 複数Googleアカウントの統合管理（OAuth認証）
- 自然言語での予定作成（「明日14時にMTG、1時間」）
- アカウント自動判定（キーワードベース + 明示的指定）
- 確認フロー（キーワード判定時は確認、明示的指定時は即登録）
- iMessage + Chatwork 通知機能
- カレンダー監視（30分ごとに新しいイベントを自動検出）
- 統合カレンダー表示（今日・今週・空き時間検索）
- 予定の編集・削除機能
- 定期予定の管理（「毎週水曜10時にMTG」）
- リマインダー機能（事前通知 + 今日の予定サマリー）
- スマート提案（空き時間提案、ダブルブッキング検出、スケジュール最適化）
- Google Tasks 連携（カレンダーとタスクの統合管理）
- 予定のテンプレート機能

### Technical Details
- Python 3.14+ 対応
- Google Calendar API v3
- Google Tasks API v1
- AppleScript経由のiMessage送信
- Chatwork API連携
- OpenClaw統合

## [Unreleased]

### Planned
- LINE Notify対応（サービス終了のためMessaging API検討中）
- Slack通知対応
- Discord通知対応
- 音声入力対応（Siri shortcuts）
- カレンダービュー画像生成
- DASH（タスク管理システム）との深い統合
- Web UI

---

フィードバック・機能要望は [Issues](https://github.com/masaki-sigoto/openclaw-calendar/issues) まで！
