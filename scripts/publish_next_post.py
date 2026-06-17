#!/usr/bin/env python3
"""
Publishes the next queued blog post.

How it works:
- Looks in content-queue/ for folders named like "01-slug", "02-slug", etc.
- Takes the lowest-numbered one.
- Reads its post.html, which starts with a metadata comment:
      <!-- CARD {"slug":"...","banner":"b1","category":"...","title":"...","blurb":"..."} -->
- Writes the page to blog/<slug>/index.html (with the CARD comment stripped).
- Adds a card to the top of blog/index.html.
- Adds a <url> to sitemap.xml.
- Deletes the queue folder.

Run with --dry-run to see what it would publish without changing anything.
"""
import os, re, json, sys, datetime, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "content-queue")
BLOG_INDEX = os.path.join(ROOT, "blog", "index.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
DRY = "--dry-run" in sys.argv

def find_next():
    if not os.path.isdir(QUEUE):
        return None
    items = []
    for name in sorted(os.listdir(QUEUE)):
        d = os.path.join(QUEUE, name)
        if os.path.isdir(d) and re.match(r"^\d+", name) and os.path.isfile(os.path.join(d, "post.html")):
            items.append(name)
    return items[0] if items else None

def main():
    nxt = find_next()
    if not nxt:
        print("Queue is empty. Nothing to publish.")
        return 0

    folder = os.path.join(QUEUE, nxt)
    html = open(os.path.join(folder, "post.html"), encoding="utf-8").read()

    m = re.search(r"<!--\s*CARD\s*(\{.*?\})\s*-->", html, re.DOTALL)
    if not m:
        print(f"ERROR: no CARD metadata comment found in {nxt}/post.html")
        return 1
    meta = json.loads(m.group(1))
    for key in ("slug", "title", "blurb"):
        if not meta.get(key):
            print(f"ERROR: CARD metadata missing '{key}' in {nxt}")
            return 1
    slug = meta["slug"]
    banner = meta.get("banner", "b1")
    category = meta.get("category", "")

    page = re.sub(r"<!--\s*CARD\s*\{.*?\}\s*-->\s*", "", html, count=1, flags=re.DOTALL)
    today = datetime.date.today().isoformat()

    print(f"Next in queue: {nxt}")
    print(f"  -> publishing to /blog/{slug}/")
    if DRY:
        print("DRY RUN, no files changed. Metadata:", json.dumps(meta))
        return 0

    # 1. Write the live post
    dest_dir = os.path.join(ROOT, "blog", slug)
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

    # 2. Add a card to the top of the blog index grid
    idx = open(BLOG_INDEX, encoding="utf-8").read()
    card = (
        f'      <a class="post-card" href="/blog/{slug}/">\n'
        f'        <div class="banner {banner}">{category}</div>\n'
        f'        <div class="pc-body">\n'
        f'          <h2>{meta["title"]}</h2>\n'
        f'          <p>{meta["blurb"]}</p>\n'
        f'          <span class="read">Read more &rarr;</span>\n'
        f'        </div>\n'
        f'      </a>\n\n'
    )
    grid_anchor = '<div class="blog-grid">\n'
    if grid_anchor in idx:
        idx = idx.replace(grid_anchor, grid_anchor + card, 1)
        open(BLOG_INDEX, "w", encoding="utf-8").write(idx)
    else:
        print("WARNING: could not find blog-grid anchor; card not added.")

    # 3. Add a sitemap entry
    sm = open(SITEMAP, encoding="utf-8").read()
    url = (
        f'  <url><loc>https://www.bresosaasy.com/blog/{slug}/</loc>'
        f'<lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
        f'</urlset>'
    )
    if "</urlset>" in sm and f"/blog/{slug}/" not in sm:
        sm = sm.replace("</urlset>", url, 1)
        open(SITEMAP, "w", encoding="utf-8").write(sm)

    # 4. Remove the published item from the queue
    shutil.rmtree(folder)
    print(f"Done. Published {slug} and removed queue item {nxt}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
