import json
import subprocess

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

with open('threads.json') as f:
    data = json.load(f)

threads = data['data']['repository']['pullRequest']['reviewThreads']['nodes']

responses = {
    "PRRT_kwDORVMCOM5v_2SX": "✅ Solved: The `/config` endpoint now redacts the `discord_webhook` URL to prevent credential leakage.",
    "PRRT_kwDORVMCOM5wAj9P": "❌ Not solved: As discussed in the overall review, this has been deferred to task #20 on the roadmap.",
    "PRRT_kwDORVMCOM5wAj9V": "❌ Not solved: As discussed, exposing the backend directly is an intentional shortcut for paper trading and we will add a reverse proxy in the future.",
    "PRRT_kwDORVMCOM5wBZz2": "✅ Solved: Added the required `ReactNode` import from `'react'` in the affected files.",
    "PRRT_kwDORVMCOM5wBZ0D": "✅ Solved: The response payload now uses the resolved `ws_clients` variable instead of trying to access the nonexistent `client_count` property."
}

for t in threads:
    tid = t['id']
    if not t['isResolved'] or tid in responses:
        if tid in responses:
            body = responses[tid]
            mutation = f'''
            mutation {{
              addPullRequestReviewThreadReply(input: {{pullRequestReviewThreadId: "{tid}", body: "{body}"}}) {{
                clientMutationId
              }}
            }}
            '''
            print(f"Replying to {tid}...")
            res = run_cmd(f'''gh api graphql -f query='{mutation}' ''')
            if res.returncode == 0:
                print(f"Successfully replied to {tid}")
            else:
                print(f"Failed to reply to {tid}: {res.stderr}")
