"""
Prompt Security Layer
First line of defense before AI processing.
"""

import re
from rapidfuzz import fuzz

# --------------------------------------------------
# Configuration
# --------------------------------------------------

FUZZY_THRESHOLD = 90


BLOCKED_PATTERNS = {

    "SYSTEM_COMMAND": [

        r"\brm\s+-rf\b",
        r"\bsudo\b",
        r"\bsu\b",
        r"\bchmod\b",
        r"\bchown\b",
        r"\bmkfs\b",
        r"\bformat\b",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bpoweroff\b",
        r"\bhalt\b",
        r"\bkillall\b",
        r"\btaskkill\b",
        r"\btaskmgr\b",
        r"\bdel\b",
        r"\berase\b",
        r"\bwipe\b",
        r"\bdestroy\b",
        r"\buninstall\b",

        r"\bdrop\b.*\bdatabase\b",
        r"\bdelete\b.*\bdatabase\b",
        r"\btruncate\b.*\btable\b",
        r"\bdrop\b.*\btable\b",
        r"\bdrop\b.*\bschema\b",
    ],

    "MALWARE":[

        r"\bmalware\b",
        r"\bvirus\b",
        r"\bworm\b",
        r"\btrojan\b",
        r"\btrojan\s*horse\b",
        r"\bransomware\b",
        r"\bspyware\b",
        r"\badware\b",
        r"\brootkit\b",
        r"\bbootkit\b",
        r"\bkey\s*logger\b",
        r"\bkeylogger\b",
        r"\bbackdoor\b",
        r"\bbotnet\b",
        r"\bexploit\b",
        r"\bpayload\b",
        r"\bshellcode\b",
        r"\breverse\s*shell\b",
        r"\bremote\s*shell\b",
    ],

    "SECRETS":[

        r"\bpassword\b",
        r"\bpasswd\b",
        r"\bpasscode\b",
        r"\bcredential\b",
        r"\bcredentials\b",

        r"\bapi\s*key\b",
        r"\bapikey\b",

        r"\bsecret\b",
        r"\bsecret\s*key\b",

        r"\bprivate\s*key\b",
        r"\bpublic\s*key\b",

        r"\btoken\b",
        r"\baccess\s*token\b",
        r"\brefresh\s*token\b",

        r"\bssh\s*key\b",
        r"\bpem\b",
        r"\boauth\b",
        r"\bbearer\b",
    ],

    "DATA_EXFILTRATION":[

        r"dump\s+database",
        r"extract\s+data",
        r"download\s+database",
        r"steal\s+data",
        r"copy\s+database",
        r"leak\s+data",
        r"export\s+database",
        r"retrieve\s+credentials",
        r"show\s+passwords",

    ],

    "SOCIAL_ENGINEERING":[

        r"phishing",
        r"social\s+engineering",
        r"impersonate",
        r"spoof",
        r"fake\s+identity",
        r"credential\s+harvesting",

    ],

    "HARMFUL":[

        r"make\s+a\s+virus",
        r"write\s+malware",
        r"create\s+ransomware",
        r"bypass\s+authentication",
        r"privilege\s+escalation",
        r"sql\s+injection",
        r"xss",
        r"cross\s+site\s+scripting",
        r"csrf",
        r"ddos",

    ],
}


# --------------------------------------------------
# Plain keywords used by RapidFuzz
# --------------------------------------------------

DANGEROUS_KEYWORDS = {

    "SYSTEM_COMMAND":[
        "shutdown",
        "reboot",
        "poweroff",
        "halt",
        "format",
        "delete",
        "erase",
        "wipe",
        "destroy",
        "rm rf",
        "drop database",
        "truncate table",
        "drop table",
        "drop schema",
    ],

    "MALWARE":[
        "malware",
        "virus",
        "worm",
        "trojan",
        "trojan horse",
        "ransomware",
        "spyware",
        "adware",
        "rootkit",
        "bootkit",
        "keylogger",
        "backdoor",
        "botnet",
        "shellcode",
        "reverse shell",
    ],

    "SECRETS":[
        "password",
        "passwd",
        "passcode",
        "credential",
        "credentials",
        "api key",
        "secret key",
        "private key",
        "public key",
        "token",
        "access token",
        "refresh token",
        "oauth",
        "bearer token",
    ],

    "DATA_EXFILTRATION":[
        "dump database",
        "extract data",
        "steal data",
        "leak data",
        "copy database",
    ],

    "SOCIAL_ENGINEERING":[
        "phishing",
        "impersonate",
        "spoof",
        "fake identity",
    ],

    "HARMFUL":[
        "sql injection",
        "cross site scripting",
        "csrf",
        "ddos",
        "bypass authentication",
        "privilege escalation",
    ]
}

def normalize(text: str) -> str:

    text = text.lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^\w\s]", " ", text)

    text = re.sub(r"(.)\1{2,}", r"\1", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

def fuzzy_scan(prompt: str):

    prompt = normalize(prompt)

    words = prompt.split()

    for category, keywords in DANGEROUS_KEYWORDS.items():

        for keyword in keywords:

            # Exact match
            if keyword in prompt:
                return False, keyword, category

            # Phrase similarity
            phrase_score = fuzz.partial_ratio(prompt, keyword)

            if phrase_score >= FUZZY_THRESHOLD:
                return False, keyword, category

            # Single-word similarity
            for word in words:

                score = fuzz.ratio(word, keyword)

                if score >= FUZZY_THRESHOLD:
                    return False, keyword, category

    return True, None, "SAFE"

def filter_prompt(prompt: str):

    prompt = normalize(prompt)

    # ----------------------------
    # 1. Regex (fast & precise)
    # ----------------------------

    for category, patterns in BLOCKED_PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, prompt):

                return (
                    False,
                    f"Regex matched: {pattern}",
                    category,
                )

    # ----------------------------
    # 2. RapidFuzz
    # ----------------------------

    allowed, keyword, category = fuzzy_scan(prompt)

    if not allowed:

        return (
            False,
            f"Fuzzy matched keyword: '{keyword}'",
            category,
        )

    # ----------------------------
    # Safe
    # ----------------------------

    return (
        True,
        "Prompt passed security filter.",
        "SAFE",
    )