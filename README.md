# Web App Challenge — mock interview kit #2 (Stacks)

| Folder | Who sees it |
| --- | --- |
| `candidate/` | **Give this to your friend.** Starter Flask + Pony ORM app and the task brief (`candidate/README.md`). |
| `interviewer/` | **You only.** `INTERVIEWER_GUIDE.md`, the reference `solution/`, and hidden acceptance tests (`test_tasks.py`). |

`stacks.zip` is `candidate/` ready to send. To rebuild it:

```bash
rm -f stacks.zip
zip -r stacks.zip candidate -x 'candidate/venv/*' -x '*.sqlite' -x '*__pycache__*' -x '*.pytest_cache*' -x '*.DS_Store'
```
