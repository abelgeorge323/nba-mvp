#!/usr/bin/env python
import os, csv
from jira import JIRA

SERVER  = "https://foodtrx.atlassian.net"
EMAIL   = "abelgeorge323@gmail.com"
TOKEN   = "ATATT3xFfGF0HCmIC8B3J0ROIr8REP7M2m2l5pfut18-9udCgu7y96okT-b3NZIZ60QsfwjZ95tLBzr9FGXGFc36fnCgHcWccq5mn8mOeK-GPJQC_79QTu9VfOG3vHxyZEXMGvkpqYJpLNHxiKMu1lSQCrY3-7Ht7FHrn4JXW7FaCCxj1DX_2VA=54BB5C8F"
PROJECT = "PRAC"
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