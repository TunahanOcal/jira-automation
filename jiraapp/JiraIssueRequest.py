from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from typing import List
from jira import JIRA, Issue
from numpy.typing import ArrayLike
import pandas as pd
from jiraapp.ParentIssue import ParentIssue

from jiraapp.JiraField import JiraField


JIRA_SERVER = {"server": "jira-server-link"}
JIRA_CREDENTIALS = os.getenv("JIRA_CREDENTIALS")
with open(JIRA_CREDENTIALS) as f:
    credentials = json.load(f)
    JIRA_API_TOKEN = credentials["jiraApiToken"]
    JIRA_USER = credentials["jiraUser"]


class JiraIssueRequest:
    summary: str
    parent: str
    description: str
    assignee: str
    dueDate: str
    customfield_13403: str  # Requirement Date
    customfield_11301: int  # estimated story point
    customfield_13200: int  # actual story point
    customfield_13106: int  # DWH Reviewer
    customfield_10005: str  # Epic Link
    reporter: str
    issueType: JiraField
    components: List
    labels: List
    project: str
    priority: JiraField
    issueType: JiraField
    parent: ParentIssue

    def __init__(
        self,
        row: ArrayLike,
        columns: pd.Index,
        components: List,
        isDev: bool,
        isLooker: bool,
        parent: str,
    ):
        self.components = []
        self.labels = []
        self.project = "DWH"
        self.priority = JiraField(name="Medium")
        self.reporter = JiraField(name=row[columns.get_loc("DWH Owner")])
        if row[columns.get_loc("Due Date")] == "":
            self.duedate = None
        else:
            self.duedate = str(
                datetime.strptime(row[columns.get_loc("Due Date")], "%d.%m.%Y %H:%M:%S")
            )
        self.customfield_13403 = str(
            datetime.strptime(
                row[columns.get_loc("Requirement Date")], "%d.%m.%Y %H:%M:%S"
            )
        )
        for component in components:
            self.components.append(JiraField(name=component))
        
        epicLink = ''

        if parent == None:
            notes = ''
            requestor = ''
            if("Notes" in columns):
                notes = row[columns.get_loc("Notes")]
            if('Label' in columns):
                labels = str(row[columns.get_loc("Label")]).strip().split(',') 
                for label in labels:
                    self.labels.append(label)
            if("Request Owner" in columns):
                requestor = row[columns.get_loc("Request Owner")]
            
            if('Epic Link' in columns):
                epicLink = str(row[columns.get_loc("Epic Link")])
                if(epicLink !=""):
                    self.customfield_10005 = epicLink
            
            
            if "TGO" in components:
                self.summary = "TGO - " + row[columns.get_loc("Summary")]
            else:
                self.summary = row[columns.get_loc("Summary")]
            self.description = (
                "Request Owner: "
                + requestor
                + " \n"
                + "Description:"
                + row[columns.get_loc("Description")]
                + " \n"
                + "Notes: "
                + notes
            )
            self.issuetype = JiraField(name="Task")
            self.parent = ParentIssue(key=None)
            self.assignee = JiraField(name=row[columns.get_loc("DWH Owner")])
        elif isDev:
            if "TGO" in components:
                self.summary = "TGO Dev- " + row[columns.get_loc("Summary")]
            else:
                self.summary = "Dev - " + row[columns.get_loc("Summary")]
            self.issuetype = JiraField(name="Sub-task")
            self.customfield_11301 = None
            self.customfield_13200 = None
            self.assignee = None
            self.parent = ParentIssue(key=parent)
            if row[columns.get_loc("Dev Story Point")] == "":
                self.customfield_11301 = None
            else:
                self.customfield_11301 = row[columns.get_loc("Dev Story Point")]
        elif isLooker:
            if('Label' in columns):
                labels = str(row[columns.get_loc("Label")]).strip().split(',') 
                for label in labels:
                    self.labels.append(label)   
            if "TGO" in components:
                self.summary = "TGO Looker- " + row[columns.get_loc("Summary")]
            else:
                self.summary = "Dev-Looker - " + row[columns.get_loc("Summary")]
            self.issuetype = JiraField(name="Sub-task")
            if row[columns.get_loc("Looker Story Point")] == "":
                self.customfield_11301 = None
                self.customfield_13200 = None
            else:
                self.customfield_11301 = row[columns.get_loc("Looker Story Point")]
                self.customfield_13200 = row[columns.get_loc("Looker Story Point")]
            self.assignee = JiraField(name=row[columns.get_loc("DWH Owner")])
            self.parent = ParentIssue(key=parent)
        else:
            if('Label' in columns):
                labels = str(row[columns.get_loc("Label")]).strip().split(',') 
                for label in labels:
                    self.labels.append(label)
            if "TGO" in components:
                self.summary = "TGO Analysis- " + row[columns.get_loc("Summary")]
            else:
                self.summary = "Analysis - " + row[columns.get_loc("Summary")]
            self.issuetype = JiraField(name="Sub-task")
            if row[columns.get_loc("Story Point")] == "":
                self.customfield_11301 = None
                self.customfield_13200 = None
            else:
                self.customfield_11301 = row[columns.get_loc("Story Point")]
                self.customfield_13200 = row[columns.get_loc("Story Point")]
            self.assignee = JiraField(name=row[columns.get_loc("DWH Owner")])
            self.parent = ParentIssue(key=parent)
            if 'Reviewer' in columns:
                reviewer = row[columns.get_loc("Reviewer")]
                self.customfield_13106 = [JiraField(name=reviewer)]
        pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def getJiraAPI() -> JIRA:
        return JIRA(
            options=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_API_TOKEN)
        )

    def createJiraTask(self, jira: JIRA) -> Issue:
        return jira.create_issue(json.loads(self.toJSON()), jira)
