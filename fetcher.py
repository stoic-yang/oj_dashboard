import requests
import json
import time
from datetime import datetime, date

def timestamp_to_date(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

# 获取 AtCoder 难度评级字典的全局缓存
ATCODER_MODELS = None

def fetch_atcoder_models():
    global ATCODER_MODELS
    if ATCODER_MODELS is not None:
        return ATCODER_MODELS
    try:
        res = requests.get("https://kenkoooo.com/atcoder/resources/problem-models.json", timeout=10)
        ATCODER_MODELS = res.json()
    except:
        ATCODER_MODELS = {}
    return ATCODER_MODELS

def fetch_codeforces(config):
    handle = config.get('handle')
    if not handle:
        return {"platform": "Codeforces", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": "No handle"}
    
    try:
        url = f"https://codeforces.com/api/user.status?handle={handle}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['status'] != 'OK':
            return {"platform": "Codeforces", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": data.get('comment', 'API Error')}
        
        daily_subs = {}
        daily_diff = {}
        solved_problems = set()
        today_str = date.today().strftime('%Y-%m-%d')
        today_solved = []
        today_seen = set()
        
        for sub in data['result']:
            date_str = timestamp_to_date(sub['creationTimeSeconds'])
            daily_subs[date_str] = daily_subs.get(date_str, 0) + 1
            if sub.get('verdict') == 'OK':
                problem_id = f"{sub['problem']['contestId']}{sub['problem']['index']}"
                solved_problems.add(problem_id)
                rating = sub['problem'].get('rating', 0)
                if rating > 0:
                    daily_diff[date_str] = max(daily_diff.get(date_str, 0), rating)
                # 收集今日 AC 题目
                if date_str == today_str and problem_id not in today_seen:
                    today_seen.add(problem_id)
                    name = sub['problem'].get('name', problem_id)
                    today_solved.append(name)
                
        return {
            "platform": "Codeforces",
            "daily_submissions": daily_subs,
            "daily_max_difficulty": daily_diff,
            "solved_count": len(solved_problems),
            "today_solved": today_solved
        }
    except Exception as e:
        return {"platform": "Codeforces", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": str(e)}

def fetch_leetcode(config):
    username = config.get('username')
    site = config.get('site', 'cn')
    if not username:
        return {"platform": "LeetCode", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": "No username"}
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if site == 'cn':
            url = "https://leetcode.cn/graphql"
            calendar_query = {
                "query": "query userProfileCalendar($userSlug: String!) { userCalendar(userSlug: $userSlug) { submissionCalendar } }",
                "variables": {"userSlug": username}
            }
            stats_query = {
                "query": "query userProfileUserQuestionProgress($userSlug: String!) { userProfileUserQuestionProgress(userSlug: $userSlug) { numAcceptedQuestions { count } } }",
                "variables": {"userSlug": username}
            }
            
            cal_res = requests.post(url, json=calendar_query, headers=headers, timeout=10).json()
            stats_res = requests.post(url, json=stats_query, headers=headers, timeout=10).json()
            
            daily_subs = {}
            if 'data' in cal_res and 'userCalendar' in cal_res['data']:
                calendar_str = cal_res['data']['userCalendar']['submissionCalendar']
                calendar_data = json.loads(calendar_str) if calendar_str else {}
                for ts_str, count in calendar_data.items():
                    date_str = timestamp_to_date(int(ts_str))
                    daily_subs[date_str] = daily_subs.get(date_str, 0) + count
                    
            solved_count = 0
            if 'data' in stats_res and 'userProfileUserQuestionProgress' in stats_res['data']:
                solved_data = stats_res['data']['userProfileUserQuestionProgress']['numAcceptedQuestions']
                solved_count = sum(item['count'] for item in solved_data)
                
        else:
            url = "https://leetcode.com/graphql"
            query = {
                "query": "query userCalendar($username: String!) { matchedUser(username: $username) { userCalendar { submissionCalendar } submitStats: submitStatsGlobal { acSubmissionNum { count } } } }",
                "variables": {"username": username}
            }
            res = requests.post(url, json=query, headers=headers, timeout=10).json()
            
            daily_subs = {}
            solved_count = 0
            if 'data' in res and 'matchedUser' in res['data']:
                user_data = res['data']['matchedUser']
                calendar_str = user_data['userCalendar']['submissionCalendar']
                calendar_data = json.loads(calendar_str) if calendar_str else {}
                for ts_str, count in calendar_data.items():
                    date_str = timestamp_to_date(int(ts_str))
                    daily_subs[date_str] = daily_subs.get(date_str, 0) + count
                    
                solved_count = user_data['submitStats']['acSubmissionNum'][0]['count']
                
        # LeetCode 日历 API 无法获取每日具体题目名称和难度
        return {
            "platform": "LeetCode",
            "daily_submissions": daily_subs,
            "daily_max_difficulty": {}, 
            "solved_count": solved_count,
            "today_solved": []
        }
    except Exception as e:
        return {"platform": "LeetCode", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": str(e)}

def fetch_atcoder(config):
    username = config.get('username')
    if not username:
        return {"platform": "AtCoder", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": "No username"}
    
    try:
        url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second=0"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return {"platform": "AtCoder", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": f"HTTP {response.status_code}"}
        
        subs = response.json()
        daily_subs = {}
        daily_diff = {}
        solved_problems = set()
        models = dict(fetch_atcoder_models())
        today_str = date.today().strftime('%Y-%m-%d')
        today_solved = []
        today_seen = set()
        
        for sub in subs:
            date_str = timestamp_to_date(sub['epoch_second'])
            daily_subs[date_str] = daily_subs.get(date_str, 0) + 1
            if sub.get('result') == 'AC':
                p_id = sub['problem_id']
                solved_problems.add(p_id)
                
                diff = models.get(p_id, {}).get('difficulty', 0)
                if diff > 0:
                    daily_diff[date_str] = max(daily_diff.get(date_str, 0), diff)
                
                if date_str == today_str and p_id not in today_seen:
                    today_seen.add(p_id)
                    today_solved.append(p_id)
                
        return {
            "platform": "AtCoder",
            "daily_submissions": daily_subs,
            "daily_max_difficulty": daily_diff,
            "solved_count": len(solved_problems),
            "today_solved": today_solved
        }
    except Exception as e:
        return {"platform": "AtCoder", "daily_submissions": {}, "daily_max_difficulty": {}, "solved_count": 0, "error": str(e)}

def fetch_all(configs):
    results = {}
    if 'codeforces' in configs:
        results['codeforces'] = fetch_codeforces(configs['codeforces'])
    if 'leetcode' in configs:
        results['leetcode'] = fetch_leetcode(configs['leetcode'])
    if 'atcoder' in configs:
        results['atcoder'] = fetch_atcoder(configs['atcoder'])
    return results

if __name__ == '__main__':
    pass
