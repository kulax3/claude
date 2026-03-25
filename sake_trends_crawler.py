"""
日本酒トレンドクローラー
Xから日本酒に関するトレンドポストを収集し、Markdownレポートを生成する

使い方:
  python sake_trends_crawler.py           # 実際にXからデータ収集
  python sake_trends_crawler.py --demo    # デモデータでレポート生成
"""

import datetime
import re
import sys
from pathlib import Path


# ---- 設定 ----
SEARCH_QUERY = "日本酒 lang:ja"
MAX_POSTS = 100          # 取得する最大ポスト数
TOP_N = 20               # レポートに掲載するポスト数
HOURS_BACK = 24          # 過去何時間を対象にするか


# ---- デモデータ ----
DEMO_POSTS = [
    {"id": 1, "url": "https://x.com/sake_lover/status/1", "user": "sake_lover", "display_name": "日本酒好き",
     "content": "今日は獺祭を飲んだ！フルーティで飲みやすい純米大吟醸。最高 #日本酒 #獺祭 https://t.co/xxx",
     "likes": 312, "retweets": 45, "replies": 18, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example1.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)},
    {"id": 2, "url": "https://x.com/nihonshu_bar/status/2", "user": "nihonshu_bar", "display_name": "日本酒バー",
     "content": "本日のおすすめ！新政No.6 X-type 入荷しました。数量限定です。#日本酒 #新政 #秋田",
     "likes": 287, "retweets": 62, "replies": 31, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example2.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)},
    {"id": 3, "url": "https://x.com/sake_nerd/status/3", "user": "sake_nerd", "display_name": "酒オタク",
     "content": "久保田 千寿と万寿の飲み比べ。熟成感と旨みの深さが全然違う。万寿の複雑さがたまらない！ #日本酒 #久保田",
     "likes": 198, "retweets": 29, "replies": 14, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example3.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=8)},
    {"id": 4, "url": "https://x.com/izakaya_tokyo/status/4", "user": "izakaya_tokyo", "display_name": "東京居酒屋情報",
     "content": "渋谷の新店舗！全国47都道府県の日本酒が揃う居酒屋がオープン。利き酒セットが人気 #居酒屋 #日本酒",
     "likes": 445, "retweets": 134, "replies": 27, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example4.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)},
    {"id": 5, "url": "https://x.com/sake_food/status/5", "user": "sake_food", "display_name": "日本酒×料理",
     "content": "日本酒と刺身の合わせ方。白身魚には淡麗辛口、赤身には純米酒が鉄板。今夜試してみて！ #日本酒 #グルメ",
     "likes": 521, "retweets": 89, "replies": 43, "has_media": False, "media_urls": [],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)},
    {"id": 6, "url": "https://x.com/tohoku_sake/status/6", "user": "tohoku_sake", "display_name": "東北の酒蔵",
     "content": "春の新酒祭り開催！山形・宮城・福島の蔵元が一堂に集まります。試飲チケット好評発売中 #日本酒 #東北",
     "likes": 367, "retweets": 98, "replies": 55, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example6.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)},
    {"id": 7, "url": "https://x.com/craft_sake/status/7", "user": "craft_sake", "display_name": "クラフト日本酒",
     "content": "自然派日本酒（ナチュール）が面白い。添加物なし、野生酵母だけで醸した個性的な味わい。クセになる #日本酒",
     "likes": 156, "retweets": 38, "replies": 22, "has_media": False, "media_urls": [],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)},
    {"id": 8, "url": "https://x.com/sake_export/status/8", "user": "sake_export", "display_name": "日本酒輸出情報",
     "content": "海外での日本酒ブーム続く。ニューヨークの日本酒バーが急増中。NYでの人気銘柄は獺祭・久保田・賀茂鶴 #日本酒 #海外",
     "likes": 289, "retweets": 77, "replies": 19, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example8.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=7)},
    {"id": 9, "url": "https://x.com/sake_brewing/status/9", "user": "sake_brewing", "display_name": "酒造り情報",
     "content": "今年の新米使用の純米酒、搾りたてが各地で出荷開始。新酒のフレッシュな味わいは今だけ！ #日本酒 #新酒",
     "likes": 203, "retweets": 51, "replies": 16, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example9.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=15)},
    {"id": 10, "url": "https://x.com/sake_event/status/10", "user": "sake_event", "display_name": "日本酒イベント",
     "content": "来週末「東京日本酒フェスティバル2026」開催！100以上の蔵元が参加。チケット残りわずか #日本酒 #イベント",
     "likes": 678, "retweets": 201, "replies": 87, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example10.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4)},
    {"id": 11, "url": "https://x.com/sake_health/status/11", "user": "sake_health", "display_name": "健康×日本酒",
     "content": "日本酒に含まれるアミノ酸と美容効果が話題。適量飲酒でグルタミン酸・アスパラギン酸が摂れる #日本酒",
     "likes": 134, "retweets": 42, "replies": 28, "has_media": False, "media_urls": [],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=18)},
    {"id": 12, "url": "https://x.com/kyoto_sake/status/12", "user": "kyoto_sake", "display_name": "京都の酒",
     "content": "伏見の酒蔵めぐりしてきた！月桂冠・黄桜・佐々木酒造を巡るルートが最高だった #日本酒 #京都 #伏見",
     "likes": 412, "retweets": 88, "replies": 34, "has_media": True,
     "media_urls": ["https://pbs.twimg.com/media/example12.jpg"],
     "date": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=9)},
]


def fetch_posts(query: str, max_results: int, since: datetime.datetime) -> list[dict]:
    """snscrapeでポストを取得する"""
    try:
        import snscrape.modules.twitter as sntwitter
    except ImportError:
        raise RuntimeError("snscrapeがインストールされていません: pip install snscrape")

    posts = []
    since_str = since.strftime("%Y-%m-%d_%H:%M:%S_UTC")
    full_query = f"{query} since:{since_str}"

    print(f"検索クエリ: {full_query}")
    print("収集中...")

    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(full_query).get_items()):
            if i >= max_results:
                break
            has_media = bool(tweet.media)
            posts.append({
                "id": tweet.id,
                "url": tweet.url,
                "date": tweet.date,
                "user": tweet.user.username,
                "display_name": tweet.user.displayname,
                "content": tweet.rawContent,
                "likes": tweet.likeCount or 0,
                "retweets": tweet.retweetCount or 0,
                "replies": tweet.replyCount or 0,
                "has_media": has_media,
                "media_urls": [m.fullUrl for m in (tweet.media or []) if hasattr(m, "fullUrl")],
            })
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}件取得済み...")
    except Exception as e:
        raise RuntimeError(f"X接続エラー: {e}\n\nヒント: X APIキーが必要な場合は公式API(Bearer Token)の利用を検討してください。")

    print(f"合計 {len(posts)} 件取得")
    return posts


def score_post(post: dict) -> float:
    """エンゲージメントスコアを計算する（画像付きはボーナス）"""
    score = post["likes"] * 1.0 + post["retweets"] * 2.0 + post["replies"] * 0.5
    if post["has_media"]:
        score *= 1.5
    return score


def extract_keywords(posts: list[dict]) -> list[tuple[str, int]]:
    """頻出キーワードを抽出する（簡易版）"""
    stop_words = {
        "日本酒", "を", "に", "は", "が", "の", "で", "と", "た", "て",
        "し", "も", "な", "RT", "https", "co", "amp", "です", "ます",
        "ない", "から", "より", "まで", "など", "これ", "それ", "あの",
        "この", "その", "いる", "ある", "する", "いう", "こと", "もの",
    }
    word_count: dict[str, int] = {}
    pattern = re.compile(r"[一-龯ぁ-んァ-ヶ]{2,}")
    for post in posts:
        words = pattern.findall(post["content"])
        for w in words:
            if w not in stop_words:
                word_count[w] = word_count.get(w, 0) + 1
    return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:15]


def generate_report(posts: list[dict], top_n: int, since: datetime.datetime, is_demo: bool = False) -> str:
    """Markdownレポートを生成する"""
    now = datetime.datetime.now(datetime.timezone.utc)
    jst = datetime.timezone(datetime.timedelta(hours=9))
    now_jst = now.astimezone(jst)

    # スコアでソート（画像付き優先）
    ranked = sorted(posts, key=score_post, reverse=True)[:top_n]

    # 統計
    total = len(posts)
    with_media = sum(1 for p in posts if p["has_media"])
    avg_likes = sum(p["likes"] for p in posts) / total if total else 0
    avg_rt = sum(p["retweets"] for p in posts) / total if total else 0

    # キーワード
    keywords = extract_keywords(posts)

    demo_notice = "\n> ⚠️ **これはデモデータです。実際のXデータではありません。**\n" if is_demo else ""

    lines = [
        f"# 日本酒トレンドレポート",
        f"",
        f"> 生成日時: {now_jst.strftime('%Y年%m月%d日 %H:%M')} JST  ",
        f"> 収集期間: 過去{HOURS_BACK}時間 ({since.astimezone(jst).strftime('%m/%d %H:%M')} 〜 {now_jst.strftime('%m/%d %H:%M')} JST)  ",
        f"> 検索クエリ: `{SEARCH_QUERY}`",
        demo_notice,
        f"---",
        f"",
        f"## 概要統計",
        f"",
        f"| 項目 | 値 |",
        f"|------|-----|",
        f"| 収集ポスト数 | {total} 件 |",
        f"| 画像付きポスト | {with_media} 件 ({with_media/total*100:.1f}%) |",
        f"| 平均いいね数 | {avg_likes:.1f} |",
        f"| 平均RT数 | {avg_rt:.1f} |",
        f"",
        f"---",
        f"",
        f"## 頻出キーワード TOP 15",
        f"",
    ]

    if keywords:
        lines.append("| キーワード | 出現数 |")
        lines.append("|-----------|--------|")
        for word, count in keywords:
            lines.append(f"| {word} | {count} |")
    else:
        lines.append("_キーワードデータなし_")

    lines += [
        f"",
        f"---",
        f"",
        f"## トレンドポスト TOP {len(ranked)}",
        f"",
        f"> エンゲージメント（いいね×1 + RT×2 + 返信×0.5、画像付き1.5倍）でランキング",
        f"",
    ]

    for rank, post in enumerate(ranked, 1):
        date_jst = post["date"].astimezone(jst).strftime("%Y/%m/%d %H:%M")
        media_badge = " [画像あり]" if post["has_media"] else ""
        score = score_post(post)

        lines += [
            f"### {rank}. @{post['user']}{media_badge}",
            f"",
            f"**{post['display_name']}** · {date_jst}  ",
            f"いいね {post['likes']}  RT {post['retweets']}  返信 {post['replies']}  "
            f"_(スコア: {score:.0f})_",
            f"",
            f"> {post['content'].replace(chr(10), '  ')}",
            f"",
            f"リンク: {post['url']}",
            f"",
        ]

        if post["media_urls"]:
            lines.append("**メディアURL:**")
            for url in post["media_urls"][:3]:
                lines.append(f"- {url}")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines += [
        f"_このレポートは sake_trends_crawler.py によって自動生成されました_",
    ]

    return "\n".join(lines)


def main():
    is_demo = "--demo" in sys.argv

    now = datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(hours=HOURS_BACK)

    if is_demo:
        print("[デモモード] サンプルデータでレポートを生成します")
        posts = DEMO_POSTS
    else:
        print("Xからデータを収集します...")
        try:
            posts = fetch_posts(SEARCH_QUERY, MAX_POSTS, since)
        except RuntimeError as e:
            print(f"\nエラー: {e}", file=sys.stderr)
            print("\n--demo オプションでデモレポートを生成できます:", file=sys.stderr)
            print("  python sake_trends_crawler.py --demo", file=sys.stderr)
            sys.exit(1)

    if not posts:
        print("ポストが取得できませんでした。")
        return

    report = generate_report(posts, TOP_N, since, is_demo=is_demo)

    jst = datetime.timezone(datetime.timedelta(hours=9))
    suffix = "_demo" if is_demo else ""
    filename = f"sake_trends_report_{now.astimezone(jst).strftime('%Y%m%d_%H%M')}{suffix}.md"
    output_path = Path(__file__).parent / filename

    output_path.write_text(report, encoding="utf-8")
    print(f"\nレポートを保存しました: {output_path}")
    print(f"  収集ポスト数: {len(posts)}")
    print(f"  掲載ポスト数: {min(TOP_N, len(posts))}")


if __name__ == "__main__":
    main()
