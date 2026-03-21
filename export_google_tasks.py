"""
Google Tasks を CSV にエクスポートするスクリプト

事前準備:
1. Google Cloud Console で Tasks API を有効化
2. OAuth 2.0 クライアントID (デスクトップアプリ) を作成
3. credentials.json をこのスクリプトと同じディレクトリに配置
4. 必要なパッケージをインストール:
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import csv
import os
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
OUTPUT_FILE = f"google_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def authenticate():
    """Google OAuth2 認証を行い、credentialsを返す"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} が見つかりません。\n"
                    "Google Cloud Console から OAuth 2.0 クライアントID を作成し、\n"
                    f"{CREDENTIALS_FILE} としてこのディレクトリに配置してください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def fetch_all_tasks(service):
    """全タスクリストからすべてのタスクを取得する"""
    all_tasks = []

    # タスクリスト一覧を取得
    tasklists_result = service.tasklists().list().execute()
    tasklists = tasklists_result.get("items", [])

    if not tasklists:
        print("タスクリストが見つかりませんでした。")
        return all_tasks

    for tasklist in tasklists:
        list_id = tasklist["id"]
        list_title = tasklist["title"]
        print(f"取得中: {list_title}")

        # タスクを取得（完了済み・非表示も含む）
        page_token = None
        while True:
            tasks_result = service.tasks().list(
                tasklist=list_id,
                showCompleted=True,
                showHidden=True,
                pageToken=page_token,
            ).execute()

            tasks = tasks_result.get("items", [])
            for task in tasks:
                all_tasks.append({
                    "list_title": list_title,
                    "task_id": task.get("id", ""),
                    "title": task.get("title", ""),
                    "notes": task.get("notes", ""),
                    "status": "完了" if task.get("status") == "completed" else "未完了",
                    "due": task.get("due", ""),
                    "completed": task.get("completed", ""),
                    "updated": task.get("updated", ""),
                    "parent": task.get("parent", ""),
                    "position": task.get("position", ""),
                })

            page_token = tasks_result.get("nextPageToken")
            if not page_token:
                break

    return all_tasks


def export_to_csv(tasks, output_file):
    """タスクをCSVファイルに書き出す"""
    fieldnames = [
        "list_title",
        "title",
        "status",
        "due",
        "completed",
        "notes",
        "updated",
        "parent",
        "position",
        "task_id",
    ]

    headers = {
        "list_title": "タスクリスト",
        "title": "タスク名",
        "status": "ステータス",
        "due": "期限",
        "completed": "完了日時",
        "notes": "メモ",
        "updated": "更新日時",
        "parent": "親タスクID",
        "position": "並び順",
        "task_id": "タスクID",
    }

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        # 日本語ヘッダーを書き込む
        writer.writerow(headers)
        writer.writerows(tasks)

    print(f"\n{len(tasks)} 件のタスクを {output_file} に書き出しました。")


def main():
    print("Google Tasks CSV エクスポート")
    print("=" * 40)

    try:
        creds = authenticate()
        service = build("tasks", "v1", credentials=creds)

        tasks = fetch_all_tasks(service)

        if tasks:
            export_to_csv(tasks, OUTPUT_FILE)
        else:
            print("エクスポートするタスクがありませんでした。")

    except FileNotFoundError as e:
        print(f"\nエラー: {e}")
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
