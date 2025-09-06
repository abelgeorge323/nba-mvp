#!/usr/bin/env python
import os, csv
from jira import JIRA

SERVER  = "https://foodtrx.atlassian.net"
EMAIL   = "abelgeorge323@gmail.com"
TOKEN   = "ATATT3xFfGF0giZcU1HvZX03U-xCDoj2K4wocpGl40TlrSLICgisBwODCOL8lEHYUgyFYID-XGWMXMkJMmnRHVfhvfmhRpbloUMIfS9MUGZJeJeweH-gABVqLeFAKE-wPb4pfah-rpyjFiqEGN-Wbc10yjnMA55fohizdpsENKVCpCE_6-rmiug=DD4E2363"
PROJECT = "KAN"

jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

with open("quick_test.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fields = {
            "project": {"key": PROJECT},
            "summary": row["Summary"],
            "issuetype": {"name": "Task"},
            "description": f"h3. Preconditions\n{row['Preconditions']}\n\nh3. Steps\n{row['Steps']}\n\nh3. Expected\n{row['ExpectedResult']}",
            "priority": {"name": row.get("Priority", "Medium")}
        }
        issue = jira.create_issue(fields=fields)
        print(f"✅ {issue.key}  –  {row['Summary']}")
