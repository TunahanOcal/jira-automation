from typing import Union
from google.GoogleApp import GoogleApp
from jiraapp.JiraIssueRequest import JiraIssueRequest
import json
import pandas as pd
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import traceback
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"]
)



@app.get("/addJiraTasks/{document_key}/")
async def addJiraTasks(document_key: str, sheet_id: int):
    mandatory_fields = ["Jira Link", "Summary", "Requirement Date"]
    result = {"result": "", "content": []}
    try:
        gapp = GoogleApp()
        sheet = gapp.getGoogleSpreadSheet(document_key=document_key, sheet_id=sheet_id)
        jira = JiraIssueRequest.getJiraAPI()
        tasks = pd.DataFrame(sheet.get_all_records())
        if all(elem in mandatory_fields for elem in tasks.columns.values.tolist()):
            raise Exception(
                {"description": "Missing mandatory field/fileds!", "code": 200}
            )
        jiraLinkColInd = tasks.columns.get_loc("Jira Link")
        tasksNotCreated = tasks[
            (tasks["Jira Link"] == "") & (tasks["Status"] == "To-Do")
        ]
        # componentName = str(sheet.spreadsheet.title).split(" ")[0]
        createdJiraTasks = []
        print(tasks.columns.values.tolist())
        componentColInd = tasksNotCreated.columns.get_loc("Components")
        devRequiredCol = tasksNotCreated.columns.get_loc("Dev Required")
        lookerRequiredCol = None
        if('Looker Required' in tasksNotCreated.columns):
            lookerRequiredCol = tasks.columns.get_loc("Looker Required")
        if tasksNotCreated.empty:
            print("There is no new task")
        else:
            for row, i in zip(tasksNotCreated.values, tasksNotCreated.index.values):
                try:
                    components = str(row[componentColInd]).strip().split(",")
                    issueRequest = JiraIssueRequest(
                        row,
                        tasksNotCreated.columns,
                        components,
                        isDev=False,
                        isLooker=False,
                        parent=None,
                    )
                    newTask = issueRequest.createJiraTask(jira)
                    sheet.update_cell(
                        i + 2,
                        jiraLinkColInd + 1,
                        "https://jtracker.trendyol.com/browse/" + newTask.key,
                    )
                    createdJiraTasks.append(json.loads(issueRequest.toJSON()))
                    analysisTask = JiraIssueRequest(
                        row,
                        tasksNotCreated.columns,
                        components,
                        False,
                        False,
                        newTask.key,
                    )
                    analysisTask.createJiraTask(jira)
                    createdJiraTasks.append(json.loads(analysisTask.toJSON()))
                    if row[devRequiredCol] == "Yes":
                        devTask = JiraIssueRequest(
                            row,
                            tasksNotCreated.columns,
                            components,
                            True,
                            False,
                            newTask.key,
                        )
                        devTask.createJiraTask(jira)
                        createdJiraTasks.append(json.loads(devTask.toJSON()))
                    if lookerRequiredCol != None and row[lookerRequiredCol]  == "Yes":
                        lookertask = JiraIssueRequest(
                            row,
                            tasksNotCreated.columns,
                            components,
                            False,
                            True,
                            newTask.key,
                        )
                        lookertask.createJiraTask(jira)
                        createdJiraTasks.append(json.loads(lookertask.toJSON()))
                except Exception as err:
                    traceback.print_exc()
                    createdJiraTasks.append(str(err))
        result["result"] = "Success"
        result["content"] = createdJiraTasks

    except KeyError as kerr:
        traceback.print_exc()
        result["result"] = "An Error Occured"
        result["content"].append(str(kerr) + " column not found on the document!")
    except Exception as err:
        traceback.print_exc()
        result["result"] = "An Error Occured"
        result["content"].append(str(err))
    finally:
        return JSONResponse(
            content=result, status_code=200, media_type="application/json"
        )


@app.get("/updateJiraTaskStatusOnSheet/{document_key}/")
async def updateJiraTaskStatusOnSheet(document_key: str, sheet_id: int):
    result = {"result": "", "content": []}
    try:
        gapp = GoogleApp()
        sheet = gapp.getGoogleSpreadSheet(document_key=document_key, sheet_id=sheet_id)
        jira = JiraIssueRequest.getJiraAPI()
        tasks = pd.DataFrame(sheet.get_all_records())
        statusColInd = tasks.columns.get_loc("Status")
        jiraLinkColInd = tasks.columns.get_loc("Jira Link")
        tasksInProgress = tasks[
            (tasks["Status"] != "Done") & (tasks["Jira Link"] != "")
        ]

        for row, i in zip(tasksInProgress.values, tasksInProgress.index.values):
            try:
                jiraKey = str(row[jiraLinkColInd]).split("/")[-1]
                jiraIssue = jira.issue(jiraKey)
                jiraIssueStatus = jiraIssue.get_field("status")
                sheet.update_cell(i + 2, statusColInd + 1, str(jiraIssueStatus))
                issueStatus = {
                    "issue": "https://jtracker.trendyol.com/browse/" + jiraIssue.key,
                    "status": str(jiraIssueStatus),
                }

                result["content"].append(issueStatus)
            except Exception as err:
                traceback.print_exc()
                result["content"].append(str(err))

        result["result"] = "Success"

    except KeyError as kerr:
        traceback.print_exc()
        result["result"] = "An Error Occured"
        result["content"].append(str(kerr) + " column not found on the document!")
    except Exception as err:
        traceback.print_exc()
        result["result"] = "An Error Occured"
        result["content"].append(str(err))
    finally:
        return JSONResponse(
            content=result, status_code=200, media_type="application/json"
        )
    
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=2000)