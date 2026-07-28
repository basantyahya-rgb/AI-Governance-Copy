# test_prompt_filter.py

from app.governance.prompt_filter import filter_prompt

tests = [
    "Hello AI",
    "Delete database immediately",
    "My password is 123456"
]

for t in tests:
    print(filter_prompt(t))