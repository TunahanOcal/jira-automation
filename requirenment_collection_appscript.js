function onOpen(e) {
  SpreadsheetApp.getUi()
      .createMenu("TGO")
      .addItem('Get New Requests', 'getFormResponses')
      .addItem("Move Completed Requests",'moveCompletedRequests')
      .addToUi();
}

function onInstall(e) {
  onOpen(e);
}

function getFormResponses() {
  var form = FormApp.openById('1rMEsJd8gHm3nfpp62qqoJ16_T0sJid_-Ef4brkQp_bc');
  var spreadSheet = SpreadsheetApp.openById('1wVeh5NUCFhdUh3Kk2eQvycrTQam6RgGwTF8V-DrtrgU');
  var sheet = spreadSheet.getSheetByName("Requests");
  var lastRow = sheet.getLastRow();
  var range = sheet.getRange('A:I');
  var targetValues = range.getValues();
  var formResponses = form.getResponses();
  var lastResponseTime = Utilities.parseDate(targetValues[lastRow-1][2].toString(),"GMT+3","dd.MM.yyyy HH:mm:ss");
  if(lastResponseTime=="" || lastResponseTime =='Requirement Date'){
    lastResponseTime= new Date("1990-01-01 00:00:00");
  }
  Logger.log(lastResponseTime.getTime())
  var newResponses = formResponses.filter(rsp => rsp.getTimestamp().getTime()>lastResponseTime.getTime());
  Logger.log(formResponses[formResponses.length-1].getTimestamp());
  Logger.log(formResponses[formResponses.length-1].getRespondentEmail());
  var description = "";
  var newRequestCount = newResponses.length;
  var requestTime=new Date();
  for (var i = 0; i < newResponses.length; i++) {
    var formResponse = newResponses[i];
    
    var itemResponses = formResponse.getItemResponses();
    targetValues[lastRow+i][0] = 'TGO'
    targetValues[lastRow+i][1] = itemResponses[0].getResponse().toString();
    requestTime = Utilities.formatDate(formResponse.getTimestamp(),"GMT+3","dd.MM.yyyy HH:mm:ss");
    targetValues[lastRow+i][2] = requestTime; 
    targetValues[lastRow+i][3] = formResponse.getRespondentEmail();
    targetValues[lastRow+i][4] = itemResponses[4].getResponse().toString();
    targetValues[lastRow+i][5] = itemResponses[1].getResponse().toString();
    targetValues[lastRow+i][6] = itemResponses[2].getResponse().toString();
    targetValues[lastRow+i][7] = itemResponses[3].getResponse().toString();
    
    for(var a=5; a<itemResponses.length;a++){
      description += (itemResponses[a].getResponse().toString()+"\n");
    }
    targetValues[lastRow+i][8] = description;
    description = ""
    range.setValues(targetValues);
    
  }
  SpreadsheetApp.getUi().prompt(newRequestCount + " new requests have been added!")
}

function moveCompletedRequests(){
  var spreadSheet = SpreadsheetApp.openById('1wVeh5NUCFhdUh3Kk2eQvycrTQam6RgGwTF8V-DrtrgU');
  var requestSheet = spreadSheet.getSheetByName("Requests");
  var completedSheet = spreadSheet.getSheetByName("Completed Requests");
  var range = requestSheet.getRange('A:AH');
  var requstValues = range.getValues();
  var completedRequests = requstValues.filter(r => (r[11] =='Done' && r[33] == 'Done') || r[11]=='Cancelled' || r[11]=='Talep Reddedildi' )
  var lastRow = completedSheet.getLastRow();
  var range2 = completedSheet.getRange('A:AH');
  var targetCompletedValues = range2.getValues();
  var movedRequests = 0
  for(var i = 0; i<completedRequests.length;i++){
    targetCompletedValues[lastRow+i] = completedRequests[i];
    range2.setValues(targetCompletedValues);
  }
  

  for(var j=requestSheet.getLastRow(); j>0;j--){
    if((requstValues[j][11].toString().trim()=='Done' && requstValues[j][33].toString().trim()=='Done')|| requstValues[j][11]=='Cancelled' || requstValues[j][11]=='Talep Reddedildi' ){
      requestSheet.deleteRow(j+1);
      movedRequests++;
    }
  }
  SpreadsheetApp.getUi().prompt(movedRequests +" completed request have been moved!");
}
