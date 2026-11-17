"""Publish today's carousel (Asia/Bangkok date) to Instagram.

Picks the oldest folder in posts/ that has not been posted yet (folders are named by
planned date, which only sets the order), publishes its *.jpg + caption.txt as one carousel
via the Instagram API with Instagram Login (graph.instagram.com), then writes .posted in it.
Never posts more than one carousel per Bangkok day unless POST_DATE is given.

Env:
  IG_TOKEN    long-lived Instagram user access token (required)
  GITHUB_REPOSITORY, GITHUB_REF_NAME   set by GitHub Actions; used to build public image URLs
  POST_DATE   optional override, e.g. 2026-11-18
  DRY_RUN=1   print what would be posted, publish nothing
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://graph.instagram.com"
BKK = timezone(timedelta(hours=7))


def call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"Instagram API error on {method} {path}: {e.code} {body}")


def wait_ready(container_id, label):
    for _ in range(30):
        status = call("GET", container_id, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            sys.exit(f"{label} container {container_id} failed: {status}")
        time.sleep(5)
    sys.exit(f"{label} container {container_id} not ready after 150s")


def main():
    today = datetime.now(BKK).strftime("%Y-%m-%d")
    folders = sorted(p for p in Path("posts").iterdir() if p.is_dir())
    if os.environ.get("POST_DATE"):
        folder = Path("posts") / os.environ["POST_DATE"]
    else:
        if any((p / ".posted").exists() and (p / ".posted").read_text().startswith(today) for p in folders):
            print(f"Already posted today ({today}), nothing to do")
            return
        pending = [p for p in folders if not (p / ".posted").exists()]
        if not pending:
            sys.exit("The queue is empty: every folder in posts/ has been posted. Add new posts to keep going.")
        folder = pending[0]
    date = folder.name
    if (folder / ".posted").exists():
        print(f"{date} already posted, nothing to do")
        return
    images = sorted(folder.glob("*.jpg"))
    if not images:
        sys.exit(f"No content for {date}: the queue is empty. Add posts/{date}/ to keep posting.")
    if not 2 <= len(images) <= 10:
        sys.exit(f"{date}: a carousel needs 2-10 images, found {len(images)}")
    caption = (folder / "caption.txt").read_text(encoding="utf-8").strip()

    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    urls = [f"https://raw.githubusercontent.com/{repo}/{branch}/{p.as_posix()}" for p in images]

    if os.environ.get("DRY_RUN") == "1":
        print("DRY RUN", date, *urls, "---", caption, sep="\n")
        return

    me = call("GET", "me", fields="user_id,username")
    ig_id = me["user_id"]
    print(f"Posting {len(urls)} slides for {date} to @{me.get('username')}")

    children = []
    for i, u in enumerate(urls, 1):
        c = call("POST", f"{ig_id}/media", image_url=u, is_carousel_item="true")
        wait_ready(c["id"], f"slide {i}")
        children.append(c["id"])

    carousel = call("POST", f"{ig_id}/media", media_type="CAROUSEL",
                    children=",".join(children), caption=caption)
    wait_ready(carousel["id"], "carousel")
    published = call("POST", f"{ig_id}/media_publish", creation_id=carousel["id"])
    link = call("GET", published["id"], fields="permalink").get("permalink", "")
    print("Published:", published["id"], link)
    (folder / ".posted").write_text(f"{today}\n{published['id']}\n{link}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
