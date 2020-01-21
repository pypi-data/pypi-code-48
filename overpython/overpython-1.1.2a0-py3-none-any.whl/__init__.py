from .overpython import *

msg_enabled = False
logs        = [
    "What's new in Overpython 1.1.2? (spoiler alert: not much)",
    "Added openf(), tolower(), toupper(), equals(), notequal()",
    "New example code in README.md (unrelated)"
]

if msg_enabled == True:
    print("Overcomplicating Python for masochists since 420 AD")

def changelogs():
    for i in logs:
        print(i)
