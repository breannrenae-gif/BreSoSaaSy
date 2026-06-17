# Blog content queue (auto-publish)

Posts in this folder are published automatically, **one per week, every Tuesday morning**,
by the GitHub Action in `.github/workflows/weekly-blog.yml`.

## How it works
- Each queued post lives in a folder named `NN-name/` (for example `01-concierge/`) and contains a single `post.html`.
- The lowest number publishes first. So `01-` goes out before `02-`, and so on.
- The very first line of each `post.html` is a metadata comment the publisher reads:
  ```
  <!-- CARD {"slug":"my-post-url","banner":"b1","category":"Topic","title":"Card title","blurb":"One-sentence summary."} -->
  ```
- When a post is published, the script:
  1. Writes it to `blog/<slug>/index.html` (with the CARD comment removed)
  2. Adds a card to the top of `blog/index.html`
  3. Adds the URL to `sitemap.xml`
  4. Deletes the queue folder

## To add more posts
Drop a new `NN-name/post.html` in here with a CARD comment at the top. Use the next number
(or any number higher than what is left). That is it. They will keep publishing weekly.

## To publish one right now
Go to the repo on GitHub, open the **Actions** tab, choose **Weekly Blog Publish**, and click
**Run workflow**. It will publish the next queued post immediately.

## To change the schedule
Edit the `cron` line in `.github/workflows/weekly-blog.yml`. The time is in UTC.
`0 16 * * 2` means Tuesdays at 16:00 UTC (about 9 AM in Las Vegas during PDT).
