"""
Instagram 日本酒トレンドクローラー
Instagramから #日本酒 の投稿を収集し、Markdownレポートを生成する

使い方:
  python instagram_sake_crawler.py           # 実際にInstagramからデータ収集
  python instagram_sake_crawler.py --demo    # デモデータでレポート生成
"""

import datetime
import sys
from pathlib import Path


# ---- 設定 ----
HASHTAGS = ["日本酒"]      # 収集するハッシュタグ（#不要）
MAX_POSTS = 100             # 取得する最大投稿数
TOP_N = 20                  # レポートに掲載する投稿数
HOURS_BACK = 24             # 過去何時間を対象にするか


# ---- デモデータ ----
_now = datetime.datetime.now(datetime.timezone.utc)

DEMO_POSTS = [
    {"shortcode": "ABC001", "url": "https://www.instagram.com/p/ABC001/",
     "owner": "sake_lover_jp", "timestamp": _now - datetime.timedelta(hours=1),
     "caption": "獺祭 純米大吟醸 磨き二割三分🍶 フルーティな香りが最高！今夜のお供に。\n#日本酒 #獺祭 #純米大吟醸 #山口 #旭酒造",
     "likes": 892, "comments": 47, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC001/media/"},
    {"shortcode": "ABC002", "url": "https://www.instagram.com/p/ABC002/",
     "owner": "nihonshu_bar_tokyo", "timestamp": _now - datetime.timedelta(hours=3),
     "caption": "本日入荷✨ 新政 No.6 X-type 限定本数あり。ご来店お早めに！\n#日本酒 #新政 #秋田 #自然派日本酒 #日本酒バー",
     "likes": 1243, "comments": 89, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC002/media/"},
    {"shortcode": "ABC003", "url": "https://www.instagram.com/p/ABC003/",
     "owner": "kyoto_fushimi_sake", "timestamp": _now - datetime.timedelta(hours=5),
     "caption": "伏見の酒蔵めぐり🍶 月桂冠 黄桜 佐々木酒造を一日で回れる観光ルートをブログに書きました！\n#日本酒 #京都 #伏見 #酒蔵 #観光",
     "likes": 2105, "comments": 134, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC003/media/"},
    {"shortcode": "ABC004", "url": "https://www.instagram.com/p/ABC004/",
     "owner": "sake_and_food", "timestamp": _now - datetime.timedelta(hours=2),
     "caption": "日本酒×お刺身の最強ペアリング🐟🍶 白身魚には淡麗辛口、マグロ赤身には旨口純米酒が鉄板！\n#日本酒 #ペアリング #刺身 #グルメ #おつまみ",
     "likes": 3412, "comments": 201, "has_video": True,
     "thumbnail": "https://instagram.com/p/ABC004/media/"},
    {"shortcode": "ABC005", "url": "https://www.instagram.com/p/ABC005/",
     "owner": "sake_festival_info", "timestamp": _now - datetime.timedelta(hours=4),
     "caption": "【告知】東京日本酒フェスティバル2026🎉 来週末開催！100以上の蔵元が集結。チケット残りわずか。\n#日本酒 #イベント #フェスティバル #東京 #蔵元",
     "likes": 4567, "comments": 312, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC005/media/"},
    {"shortcode": "ABC006", "url": "https://www.instagram.com/p/ABC006/",
     "owner": "tohoku_sake_brewery", "timestamp": _now - datetime.timedelta(hours=8),
     "caption": "春の新酒できました🌸 今年の出来は例年より旨みが強め。ぜひ蔵元直送でお取り寄せを！\n#日本酒 #新酒 #東北 #山形 #蔵元直送",
     "likes": 1876, "comments": 98, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC006/media/"},
    {"shortcode": "ABC007", "url": "https://www.instagram.com/p/ABC007/",
     "owner": "sake_world_export", "timestamp": _now - datetime.timedelta(hours=6),
     "caption": "NYでも日本酒ブーム🗽🍶 現地のSakeバーで獺祭・久保田が大人気。海外需要が急拡大中！\n#日本酒 #海外 #ニューヨーク #sake #輸出",
     "likes": 2234, "comments": 156, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC007/media/"},
    {"shortcode": "ABC008", "url": "https://www.instagram.com/p/ABC008/",
     "owner": "craft_nihonshu", "timestamp": _now - datetime.timedelta(hours=10),
     "caption": "自然派日本酒（ナチュール）飲み比べ🍶 無添加・野生酵母の個性的な味わいにハマってます。\n#日本酒 #ナチュール #自然派 #クラフト酒 #無添加",
     "likes": 987, "comments": 67, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC008/media/"},
    {"shortcode": "ABC009", "url": "https://www.instagram.com/p/ABC009/",
     "owner": "sake_beauty_tips", "timestamp": _now - datetime.timedelta(hours=14),
     "caption": "日本酒で肌ケア✨ 酒粕パックを週2回続けて3ヶ月。透明感が上がった気がする！成分解説もブログで。\n#日本酒 #美容 #酒粕 #スキンケア #美白",
     "likes": 5123, "comments": 423, "has_video": True,
     "thumbnail": "https://instagram.com/p/ABC009/media/"},
    {"shortcode": "ABC010", "url": "https://www.instagram.com/p/ABC010/",
     "owner": "kubota_fan_club", "timestamp": _now - datetime.timedelta(hours=7),
     "caption": "久保田 千寿 vs 万寿 飲み比べ🆚 千寿のキレと万寿の深み、あなたはどっち派？\n#日本酒 #久保田 #新潟 #朝日酒造 #飲み比べ",
     "likes": 1654, "comments": 211, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC010/media/"},
    {"shortcode": "ABC011", "url": "https://www.instagram.com/p/ABC011/",
     "owner": "izakaya_shibuya_new", "timestamp": _now - datetime.timedelta(hours=3),
     "caption": "【新店情報】渋谷に47都道府県の日本酒が揃うお店がオープン🏪 利き酒セット¥2,000が人気！\n#日本酒 #居酒屋 #渋谷 #新店 #利き酒",
     "likes": 3789, "comments": 267, "has_video": True,
     "thumbnail": "https://instagram.com/p/ABC011/media/"},
    {"shortcode": "ABC012", "url": "https://www.instagram.com/p/ABC012/",
     "owner": "sake_brewing_diary", "timestamp": _now - datetime.timedelta(hours=16),
     "caption": "仕込み水が命💧 軟水と硬水では味が全然違う。今日は蔵元さんに取材させていただきました！\n#日本酒 #酒造り #蔵元 #仕込み水 #醸造",
     "likes": 1123, "comments": 78, "has_video": False,
     "thumbnail": "https://instagram.com/p/ABC012/media/"},
]


def fetch_posts(hashtags: list[str], max_results: int, since: datetime.datetime) -> list[dict]:
    """instaloaderでハッシュタグ投稿を取得する"""
    try:
        import instaloader
    except ImportError:
        raise RuntimeError("instaloaderがインストールされていません: pip install instaloader")

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    posts = []
    for tag in hashtags:
        print(f"#{tag} を収集中...")
        try:
            hashtag = instaloader.Hashtag.from_name(L.context, tag)
            for i, post in enumerate(hashtag.get_posts()):
                if i >= max_results:
                    break
                if post.date_utc < since.replace(tzinfo=None):
                    print(f"  {since} 以前の投稿に到達。収集終了。")
                    break
                posts.append({
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "owner": post.owner_username,
                    "timestamp": post.date_utc.replace(tzinfo=datetime.timezone.utc),
                    "caption": post.caption or "",
                    "likes": post.likes,
                    "comments": post.comments,
                    "has_video": post.is_video,
                    "thumbnail": post.url,
                })
                if (i + 1) % 20 == 0:
                    print(f"  {i + 1}件取得済み...")
        except Exception as e:
            raise RuntimeError(f"Instagram接続エラー (#{tag}): {e}\n\n"
                               "ヒント: Instagramはログインなしだと取得数が制限されます。\n"
                               "--demo オプションでデモレポートを確認できます。")

    print(f"合計 {len(posts)} 件取得")
    return posts


def score_post(post: dict) -> float:
    """エンゲージメントスコア（動画はボーナス）"""
    score = post["likes"] * 1.0 + post["comments"] * 3.0
    if post["has_video"]:
        score *= 1.3
    return score


def extract_hashtags(posts: list[dict], top_n: int = 15) -> list[tuple[str, int]]:
    """キャプションから頻出ハッシュタグを集計する"""
    import re
    tag_count: dict[str, int] = {}
    pattern = re.compile(r"#([^\s#]+)")
    exclude = {"日本酒", "nihonshu", "sake", "日本", "酒"}
    for post in posts:
        for tag in pattern.findall(post["caption"]):
            if tag.lower() not in exclude:
                tag_count[tag] = tag_count.get(tag, 0) + 1
    return sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:top_n]


def generate_report(posts: list[dict], top_n: int, since: datetime.datetime, is_demo: bool = False) -> str:
    """Markdownレポートを生成する"""
    now = datetime.datetime.now(datetime.timezone.utc)
    jst = datetime.timezone(datetime.timedelta(hours=9))
    now_jst = now.astimezone(jst)

    ranked = sorted(posts, key=score_post, reverse=True)[:top_n]

    total = len(posts)
    with_video = sum(1 for p in posts if p["has_video"])
    avg_likes = sum(p["likes"] for p in posts) / total if total else 0
    avg_comments = sum(p["comments"] for p in posts) / total if total else 0

    top_hashtags = extract_hashtags(posts)

    hashtag_str = " ".join(f"#{t}" for t in HASHTAGS)
    demo_notice = "\n> ⚠️ **これはデモデータです。実際のInstagramデータではありません。**\n" if is_demo else ""

    lines = [
        f"# Instagram 日本酒トレンドレポート",
        f"",
        f"> 生成日時: {now_jst.strftime('%Y年%m月%d日 %H:%M')} JST  ",
        f"> 収集期間: 過去{HOURS_BACK}時間 ({since.astimezone(jst).strftime('%m/%d %H:%M')} 〜 {now_jst.strftime('%m/%d %H:%M')} JST)  ",
        f"> 検索ハッシュタグ: `{hashtag_str}`",
        demo_notice,
        f"---",
        f"",
        f"## 概要統計",
        f"",
        f"| 項目 | 値 |",
        f"|------|-----|",
        f"| 収集投稿数 | {total} 件 |",
        f"| 動画投稿 | {with_video} 件 ({with_video/total*100:.1f}%) |",
        f"| 平均いいね数 | {avg_likes:.1f} |",
        f"| 平均コメント数 | {avg_comments:.1f} |",
        f"",
        f"---",
        f"",
        f"## 共起ハッシュタグ TOP 15",
        f"",
    ]

    if top_hashtags:
        lines.append("| ハッシュタグ | 出現数 |")
        lines.append("|-------------|--------|")
        for tag, count in top_hashtags:
            lines.append(f"| #{tag} | {count} |")
    else:
        lines.append("_ハッシュタグデータなし_")

    lines += [
        f"",
        f"---",
        f"",
        f"## トレンド投稿 TOP {len(ranked)}",
        f"",
        f"> エンゲージメント（いいね×1 + コメント×3、動画×1.3倍）でランキング",
        f"",
    ]

    for rank, post in enumerate(ranked, 1):
        date_jst = post["timestamp"].astimezone(jst).strftime("%Y/%m/%d %H:%M")
        media_badge = " [動画]" if post["has_video"] else " [画像]"
        score = score_post(post)
        caption_preview = post["caption"].replace("\n", "  ")[:200]
        if len(post["caption"]) > 200:
            caption_preview += "..."

        lines += [
            f"### {rank}. @{post['owner']}{media_badge}",
            f"",
            f"投稿日時: {date_jst}  ",
            f"いいね {post['likes']}  コメント {post['comments']}  _(スコア: {score:.0f})_",
            f"",
            f"> {caption_preview}",
            f"",
            f"リンク: {post['url']}",
            f"",
            f"---",
            f"",
        ]

    lines.append("_このレポートは instagram_sake_crawler.py によって自動生成されました_")
    return "\n".join(lines)


def main():
    is_demo = "--demo" in sys.argv

    now = datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(hours=HOURS_BACK)

    if is_demo:
        print("[デモモード] サンプルデータでレポートを生成します")
        posts = DEMO_POSTS
    else:
        print("Instagramからデータを収集します...")
        try:
            posts = fetch_posts(HASHTAGS, MAX_POSTS, since)
        except RuntimeError as e:
            print(f"\nエラー: {e}", file=sys.stderr)
            print("\n--demo オプションでデモレポートを生成できます:", file=sys.stderr)
            print("  python instagram_sake_crawler.py --demo", file=sys.stderr)
            sys.exit(1)

    if not posts:
        print("投稿が取得できませんでした。")
        return

    report = generate_report(posts, TOP_N, since, is_demo=is_demo)

    jst = datetime.timezone(datetime.timedelta(hours=9))
    suffix = "_demo" if is_demo else ""
    filename = f"instagram_sake_report_{now.astimezone(jst).strftime('%Y%m%d_%H%M')}{suffix}.md"
    output_path = Path(__file__).parent / filename

    output_path.write_text(report, encoding="utf-8")
    print(f"\nレポートを保存しました: {output_path}")
    print(f"  収集投稿数: {len(posts)}")
    print(f"  掲載投稿数: {min(TOP_N, len(posts))}")


if __name__ == "__main__":
    main()
