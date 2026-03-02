# OJ Dashboard

English | [中文](README.md)

**Aggregate submission records from Codeforces, LeetCode, and AtCoder into a single unified heatmap.**

You might grind contests on Codeforces, practice problems on LeetCode, and sharpen your skills on AtCoder — but there's no single place to see your **combined** training activity across all platforms. OJ Dashboard solves this: a unified GitHub-style contribution heatmap that gives you a clear picture of your overall progress.

## ✨ Features

- 🔥 **Unified Heatmap** — Submissions from all three platforms merged into one calendar heatmap, fully reflecting your training rhythm
- 🏆 **Difficulty Heatmap** — Shows the highest-rated problem you solved each day (CF / AtCoder rating)
- 📊 **Problem Stats** — Summarizes AC count across platforms with a pie chart breakdown
- 🎯 **Interactive Setup** — Just enter your usernames on the page, no config files needed

## Preview
![Dashboard Preview](preview.png)

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/stoic-yang/oj_dashboard.git
cd oj_dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python server.py
```

### 4. Open

Visit [http://localhost:8080](http://localhost:8080), enter your usernames for each platform, and click "Generate Dashboard".

> First load may take 5–15 seconds as data is fetched from all three platforms.

## 🎨 Platform Colors

| Platform | Color |
|----------|-------|
| Codeforces | 🔵 Blue `#4A90D9` |
| LeetCode | 🟡 Yellow `#F5A623` |
| AtCoder | 🟢 Green `#4CAF50` |

## 📁 Project Structure

```
oj_dashboard/
├── server.py          # Flask backend
├── fetcher.py         # API fetchers for each platform
├── config.json        # Optional default config
├── requirements.txt   # Python dependencies
└── static/
    ├── index.html     # Frontend page
    ├── style.css      # Styles
    └── app.js         # Frontend logic
```

## ⚙️ Optional: Preset Config

Instead of entering usernames on the web page, you can edit `config.json` to preset them (used when no URL parameters are provided):

```json
{
  "codeforces": { "handle": "your_cf_handle" },
  "leetcode": { "username": "your_lc_username", "site": "cn" },
  "atcoder": { "username": "your_atcoder_username" }
}
```

Set `site` to `"cn"` for LeetCode China, or `"com"` for the global site.

## 🔧 Tech Stack

Python Flask + ECharts. Data sourced from Codeforces Official API, LeetCode GraphQL API, and AtCoder via [kenkoooo's API](https://github.com/kenkoooo/AtCoderProblems).
