#!/bin/bash
#
# OpenClaw Google Calendar Integration - セットアップスクリプト
#

set -e

echo "🚀 OpenClaw Google Calendar Integration - セットアップ開始"
echo ""

# Pythonバージョンチェック
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python 3.10以上が必要です（現在: $PYTHON_VERSION）"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION"

# 仮想環境の作成
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
else
    echo "✅ 仮想環境は既に存在します"
fi

# 仮想環境をアクティベート
source venv/bin/activate

# pipのアップグレード
echo "📦 pip をアップグレード中..."
pip install --upgrade pip > /dev/null 2>&1

# 依存パッケージのインストール
echo "📦 依存パッケージをインストール中..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ 依存パッケージをインストールしました"

# credentials.json の確認
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "⚠️ credentials.json が見つかりません"
    echo ""
    echo "次の手順で Google Cloud プロジェクトを設定してください："
    echo "1. https://console.cloud.google.com/ でプロジェクトを作成"
    echo "2. Google Calendar API と Google Tasks API を有効化"
    echo "3. OAuth 2.0 クライアントIDを作成"
    echo "4. credentials.json をダウンロードして、このフォルダに配置"
    echo ""
    echo "詳細は README.md を参照してください"
    exit 1
fi

echo "✅ credentials.json が見つかりました"

# .env ファイルの確認
if [ ! -f ".env" ]; then
    echo ""
    echo "💡 .env ファイルが見つかりません（オプション）"
    echo ""
    echo "Chatwork通知を有効にする場合は .env を作成してください："
    echo "  cp .env.example .env"
    echo "  # .env を編集して CHATWORK_API_TOKEN を設定"
    echo ""
fi

# 初回認証
echo ""
echo "🔐 Google Calendar API の認証"
echo ""
echo "次のコマンドで認証を開始してください："
echo "  source venv/bin/activate"
echo "  python server.py"
echo "  > auth crosslink"
echo "  > auth programming_school"
echo ""

echo "✅ セットアップ完了！"
echo ""
echo "📖 使い方："
echo "  python calendar_tools.py add \"明日14時にMTG、1時間\""
echo "  python calendar_view.py today"
echo "  python calendar_templates.py list"
echo ""
echo "詳細は README_FULL.md を参照してください"
