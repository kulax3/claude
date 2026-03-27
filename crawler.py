"""
URL Crawler - URLリストから情報を収集するシンプルなクローラー
"""

import time
import urllib.request
import urllib.error
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    """HTMLからテキストを抽出するパーサー"""

    SKIP_TAGS = {"script", "style", "noscript", "head"}

    def __init__(self):
        super().__init__()
        self._skip = False
        self._skip_depth = 0
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip = True
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip:
            self._skip_depth -= 1
            if self._skip_depth == 0:
                self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.texts.append(text)

    def get_text(self):
        return " ".join(self.texts)


def fetch_page(url: str, timeout: int = 10) -> dict:
    """
    URLからページ情報を取得する。

    Args:
        url: 取得するURL
        timeout: タイムアウト秒数

    Returns:
        dict: url, status, title, text, error のキーを持つ辞書
    """
    result = {"url": url, "status": None, "title": None, "text": None, "error": None}

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SimpleCrawler/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result["status"] = response.status
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                result["error"] = f"Unsupported content type: {content_type}"
                return result

            html = response.read().decode("utf-8", errors="replace")

        # テキスト抽出
        parser = TextExtractor()
        parser.feed(html)
        full_text = parser.get_text()
        result["text"] = full_text[:2000]  # 先頭2000文字に制限

        # タイトル抽出
        title_start = html.lower().find("<title>")
        title_end = html.lower().find("</title>")
        if title_start != -1 and title_end != -1:
            result["title"] = html[title_start + 7 : title_end].strip()

    except urllib.error.HTTPError as e:
        result["status"] = e.code
        result["error"] = str(e)
    except urllib.error.URLError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)

    return result


def crawl(urls: list[str], delay: float = 1.0) -> list[dict]:
    """
    URLリストをクロールして情報を収集する。

    Args:
        urls: クロールするURLのリスト
        delay: リクエスト間の待機時間（秒）

    Returns:
        list[dict]: 各URLの取得結果リスト
    """
    results = []
    for i, url in enumerate(urls):
        print(f"[{i + 1}/{len(urls)}] Fetching: {url}")
        result = fetch_page(url)
        results.append(result)

        if result["error"]:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  OK ({result['status']}): {result['title']}")

        if i < len(urls) - 1:
            time.sleep(delay)

    return results


if __name__ == "__main__":
    sample_urls = [
        "https://example.com",
        "https://example.org",
    ]

    results = crawl(sample_urls, delay=1.0)

    print("\n===== 収集結果 =====")
    for r in results:
        print(f"\nURL: {r['url']}")
        print(f"  タイトル : {r['title']}")
        print(f"  テキスト : {r['text'][:100] if r['text'] else None}")
        if r["error"]:
            print(f"  エラー   : {r['error']}")
