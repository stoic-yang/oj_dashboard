import os
import json
from flask import Flask, jsonify, request, send_from_directory
from fetcher import fetch_all

app = Flask(__name__, static_folder='static', template_folder='static')

def load_config():
    if not os.path.exists('config.json'):
        return {}
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/data')
def get_data():
    # 优先从查询参数获取用户名，否则回退到 config.json
    cf_handle = request.args.get('cf', '').strip()
    lc_username = request.args.get('lc', '').strip()
    lc_site = request.args.get('lc_site', 'cn').strip()
    ac_username = request.args.get('ac', '').strip()

    if cf_handle or lc_username or ac_username:
        config = {}
        if cf_handle:
            config['codeforces'] = {'handle': cf_handle}
        if lc_username:
            config['leetcode'] = {'username': lc_username, 'site': lc_site}
        if ac_username:
            config['atcoder'] = {'username': ac_username}
    else:
        config = load_config()

    raw_results = fetch_all(config)
    
    aggregated_daily_submissions = {}
    aggregated_max_difficulty = {}
    platform_stats = []
    total_solved = 0
    
    for key, data in raw_results.items():
        if "error" in data:
            print(f"[{data['platform']}] Error: {data['error']}")
            
        solved = data.get('solved_count', 0)
        total_solved += solved
        
        platform_stats.append({
            "name": data['platform'],
            "solved": solved,
            "error": data.get('error', None)
        })
        
        for date_str, count in data.get('daily_submissions', {}).items():
            aggregated_daily_submissions[date_str] = aggregated_daily_submissions.get(date_str, 0) + count
            
        for date_str, diff in data.get('daily_max_difficulty', {}).items():
            aggregated_max_difficulty[date_str] = max(aggregated_max_difficulty.get(date_str, 0), diff)
            
    response_data = {
        "platforms": platform_stats,
        "total_solved": total_solved,
        "heatmap": aggregated_daily_submissions,
        "difficulty_heatmap": aggregated_max_difficulty
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
