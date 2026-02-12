import os
import re
from datetime import datetime, timezone
import pandas as pd
from operator import itemgetter
from jira import JIRA
import requests
import concurrent.futures

# Set the float format
pd.options.display.float_format = "{:.4f}".format

user = 'naveenkumar.govindappa@lumen.com'
apikey = 'ATATT3xFfGF0FScTklJ84F9Gw0FfLwEJOjcXxr-XFtNJ2GjnSk-Jm_jeGNPSBbMsW5VF67SprJyVnBDecf7F73tZGn7drwNZE1sC_ZiNkLEH3rd5YcAXRlqrPMX-XmLejw-CYVq2hhJBDPAT10bajwBby9YYfzJ02d86nOtoBQDdU9J4kTiN8NU=E0B60B45'
server = 'http://lumen.atlassian.net/'
rest_base_url = 'https://lumen.atlassian.net/rest/api/3/jql/'

options = {
 'server': server
}

def pipc_sort(s):
    match = re.match(r"([a-z]+)([0-9]+)", s, re.I)
    if match:
        items = match.groups()
        # Reverse the items for sorting, so 'PI' comes before 'PC'
        return (items[0], int(items[1]))
    return (s, float('inf'))  # Return the string with a high sorting value

def calculate_cycle_time(issue_key, created_date, resolution_date):
    # Start at the first page
    start_at = 0
    # Variables to store the timestamps
    start_time = None
    end_time = resolution_date  # Set end_time as resolution_date

    while True:
        # Construct the API endpoint URL
        url = f"{rest_base_url}issue/{issue_key}/changelog?startAt={start_at}"

        # Make a GET request to the Jira API
        response = requests.get(url, auth=(user, apikey))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            changelog = response.json()

            # Process the change history
            for history in changelog['values']:
                # Iterate over items in the history
                for item in history['items']:
                    if item['field'] == 'status':
                        histtime = datetime.strptime(history['created'], "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(
                            timezone.utc).replace(tzinfo=None)
                        if item['toString'] == 'In Progress':
                            if start_time is None or histtime < start_time:
                                start_time = histtime

            # If this is the last page, break the loop
            if changelog['isLast']:
                break

            # Otherwise, move on to the next page
            start_at += len(changelog['values'])
        else:
            print(f"Failed to retrieve change history for {issue_key}. Status code: {response.status_code}")
            return None

    # If start_time is still None after processing all the change history,
    # set it to the creation time of the issue
    if start_time is None:
        start_time = created_date

    print(issue_key, "Start Time:", start_time, "End Time:", end_time)

    # Calculate and return the cycle time
    if start_time is not None and end_time is not None:
        return start_time, end_time, end_time - start_time
    else:
        return start_time, end_time, None

jira = JIRA(options, basic_auth=(user,apikey) )

directory = 'C:\\JIRA_DATA'
if not os.path.exists(directory):
    os.makedirs(directory)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'{directory}\\JIRA_METRICS_{timestamp}.xlsx'

data = []
total_issues = 0
for r in range(0,50000,100):
    # Swift Team 5375
    # VM 5139
    # OES 5253
    # SPEO 5254
    issues = jira.enhanced_search_issues('"Team[Team]" in (5375) AND issue type in (Story,Bug)', maxResults=100)

    if len(issues) == 0:
        break
    total_issues += len(issues)
    print(f'Fetched {total_issues} issues so far...')
    for issue in issues:
        fix_versions = '| '.join([v.name for v in issue.fields.fixVersions])
        summary = issue.fields.summary.replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace('\r\n', ' ')
        story_points = issue.raw['fields']["customfield_10028"] if issue.raw['fields']["customfield_10028"] is not None else 0
        created_date = datetime.strptime(issue.raw['fields']["created"], "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(
            timezone.utc).replace(tzinfo=None)

        if issue.raw['fields']["resolutiondate"] is not None:
            resolved_date = datetime.strptime(issue.raw['fields']["resolutiondate"],"%Y-%m-%dT%H:%M:%S.%f%z").astimezone(timezone.utc).replace(tzinfo=None)
            lead_time = resolved_date - created_date
        else:
            resolved_date = None
            lead_time = None
        if issue.raw['fields']["customfield_10021"] is not None:
            # some sprints missing End date
            # This problem was introduced after the ctl to Lumen migration
            # sprints = sorted(issue.raw['fields']["customfield_10021"],key=itemgetter('endDate'), reverse=True)
            sprints = [sprint for sprint in issue.raw['fields']["customfield_10021"] if 'endDate' in sprint]
            sprints = sorted(sprints, key=itemgetter('endDate'), reverse=True)
            #sprints = sorted(issue.raw['fields']["customfield_10021"],key=itemgetter('endDate'), reverse=True)
            sprint = [sub['name'] for sub in sprints ]
            prev_sprints = '| '.join(str(i) for i in sprint[1:])
            if sprint:
                current_sprint = sprint[0]
            else:
                current_sprint = "Null"
            data.append(
                [issue.key, issue.fields.issuetype, summary, issue.raw['fields']["description"], issue.fields.priority,
                 fix_versions, issue.fields.assignee, issue.fields.status, current_sprint, prev_sprints, len(sprint),
                 story_points, issue.raw['fields']["customfield_10014"],
                 issue.raw['fields']["customfield_10001"]["name"], created_date, resolved_date, lead_time])
            # Sprint details are coming as null for some items , Bug introduced after ctl to lumen migration
            #data.append([issue.key, issue.fields.issuetype,summary,issue.raw['fields']["description"],issue.fields.priority,fix_versions,issue.fields.assignee,issue.fields.status,sprint[0],prev_sprints,len(sprint),story_points,issue.raw['fields']["customfield_10014"],issue.raw['fields']["customfield_10001"]["name"],created_date,resolved_date,lead_time])
        else:
            data.append([issue.key, issue.fields.issuetype,summary,issue.raw['fields']["description"],issue.fields.priority,fix_versions,issue.fields.assignee,issue.fields.status,"Null","Null",0,story_points,issue.raw['fields']["customfield_10014"],issue.raw['fields']["customfield_10001"]["name"],created_date,resolved_date,lead_time])

df = pd.DataFrame(data, columns=["ID","IssueType","Summary","Description","Priority","FixVersion","Assignee","Status","CurrentSprint","PrevSprints","SprintCount","StoryPoint","Epic","TeamName","created","resolutiondate","LeadTime"])
print(f'Finished fetching issues. Total issues fetched: {total_issues}')

# Filter out rows where LeadTime or ResolutionTime is None
df_filtered = df.dropna(subset=['LeadTime', 'resolutiondate'])
df_filtered = df.dropna(subset=['LeadTime', 'resolutiondate'])

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    future_to_issue = {executor.submit(calculate_cycle_time, row['ID'], row['created'], row['resolutiondate']): row for _, row in df_filtered.iterrows()}
    for future in concurrent.futures.as_completed(future_to_issue):
        row = future_to_issue[future]
        try:
            start_time, end_time, cycle_time = future.result()
            # Append the start time, end time and cycle time to the corresponding row in the DataFrame
            df.loc[df['ID'] == row['ID'], 'WorkStart'] = start_time
            df.loc[df['ID'] == row['ID'], 'WorkEnd'] = end_time
            df.loc[df['ID'] == row['ID'], 'CycleTime'] = cycle_time
            #print(f"Updated work start, work end and cycle time for issue {row['ID']}")
        except Exception as exc:
            print(f'An error occurred while processing issue {row["ID"]}: {exc}')
# Extract the planning cycle name from the CurrentSprint column
df.loc[:, 'Latest_PC'] = df['CurrentSprint'].apply(lambda x: re.search(r'(PC\d+|PI\d+)', x).group(0) if re.search(r'(PC\d+|PI\d+)', x) else None)
df.to_excel(filename, sheet_name='JiraData', index=False)
print(f'Finished fetching Cycle time')

# Filter out rows where CurrentSprint is Null
df_filtered = df[df['CurrentSprint'] != 'Null'].copy()

# Extract the planning cycle name from the CurrentSprint column
# Planning Cycle is populated from Sprint as most of the issues does not have fix version
#df_filtered.loc[:, 'PlanningCycle'] = df_filtered['CurrentSprint'].apply(lambda x: re.search(r'(PC\d+|PI\d+)', x).group(0) if re.search(r'(PC\d+|PI\d+)', x) else x)
# EGW team sprint names does not have PI or PC in the name for support stories
df_filtered.loc[:, 'PlanningCycle'] = df_filtered['CurrentSprint'].apply(lambda x: re.search(r'(PC\d+|PI\d+)', x).group(0) if re.search(r'(PC\d+|PI\d+)', x) else None)

# Drop rows where PlanningCycle is None
df_filtered.dropna(subset=['PlanningCycle'], inplace=True)

# Group the data by the extracted planning cycle
grouped = df_filtered.groupby(['PlanningCycle', 'TeamName'])

# Calculate the defect density for each group
def calculate_defect_density(group):
    bug_count = group[group['IssueType'].apply(lambda x: x.name) == 'Bug'].shape[0]
    story_points_delivered = group['StoryPoint'].sum()
    return bug_count / story_points_delivered if story_points_delivered != 0 else 0

df_defect_density = grouped.apply(calculate_defect_density).reset_index()
df_defect_density.columns = ['PlanningCycle', 'TeamName', 'DefectDensity']

# Pivot the DataFrame
df_pivot = df_defect_density.pivot(index='TeamName', columns='PlanningCycle', values='DefectDensity')

# Reset the index
df_pivot.reset_index(inplace=True)

# Sort the columns (excluding the first column 'TeamName') using the pipc_sort function
sorted_columns = ['TeamName'] + sorted(df_pivot.columns[1:], key=pipc_sort)
df_pivot = df_pivot[sorted_columns]

# Write the DataFrame to the second sheet of the Excel file
with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
    df_pivot.to_excel(writer, sheet_name='DefectDensity', index=False)

# Group the data by the extracted planning cycle
grouped = df_filtered.groupby(['PlanningCycle', 'TeamName'])
# Calculate the number of defects and total story points for each group
def calculate_defects_and_story_points(group):
    bug_count = group[group['IssueType'].apply(lambda x: x.name) == 'Bug'].shape[0]
    story_points_delivered = group['StoryPoint'].sum()
    return pd.Series([bug_count, story_points_delivered], index=['DefectCount', 'TotalStoryPoints'])

df_defects_and_story_points = grouped.apply(calculate_defects_and_story_points).reset_index()

# Write the DataFrame to the third sheet of the Excel file
with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
    df_defects_and_story_points.to_excel(writer, sheet_name='DefectDensiyData', index=False)

#Calculate Average story point for each team per PC
# Group the data by 'PlanningCycle' and 'TeamName'
grouped = df_filtered.groupby(['PlanningCycle', 'TeamName'])
# Calculate the team size for each group
df_team_size = grouped['Assignee'].nunique().reset_index()

# Rename the 'Assignee' column to 'TeamSize'
df_team_size.rename(columns={'Assignee': 'TeamSize'}, inplace=True)

# Merge df_defects_and_story_points with df_team_size
df_merged = pd.merge(df_defects_and_story_points, df_team_size, on=['PlanningCycle', 'TeamName'])

# Calculate the average story points per person
df_merged['AvgStoryPointsPerPerson'] = df_merged['TotalStoryPoints'] / df_merged['TeamSize']

# Pivot the DataFrame
df_pivot = df_merged.pivot(index='TeamName', columns='PlanningCycle', values='AvgStoryPointsPerPerson')

# Reset the index
df_pivot.reset_index(inplace=True)

# Sort the columns (excluding the first column 'TeamName') using the pipc_sort function
sorted_columns = ['TeamName'] + sorted(df_pivot.columns[1:], key=pipc_sort)
df_pivot = df_pivot[sorted_columns]

# Write the DataFrame to a new sheet in the Excel file
with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
    df_pivot.to_excel(writer, sheet_name='AvgStoryPoint', index=False)

# calculate the Average Lead time per PC per Team

# Group the data by 'PlanningCycle' and 'TeamName'
grouped = df_filtered.groupby(['PlanningCycle', 'TeamName'])

# Calculate the average lead time for each group
df_lead_time = grouped['LeadTime'].mean().reset_index()

# Rename the 'LeadTime' column to 'AvgLeadTime'
df_lead_time.rename(columns={'LeadTime': 'AvgLeadTime'}, inplace=True)

# Pivot the DataFrame
df_pivot = df_lead_time.pivot(index='TeamName', columns='PlanningCycle', values='AvgLeadTime')

# Reset the index
df_pivot.reset_index(inplace=True)

# Sort the columns (excluding the first column 'TeamName') using the pipc_sort function
sorted_columns = ['TeamName'] + sorted(df_pivot.columns[1:], key=pipc_sort)
df_pivot = df_pivot[sorted_columns]

# Write the DataFrame to a new sheet in the Excel file
with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
    df_pivot.to_excel(writer, sheet_name='AvgLeadTime', index=False)

# calculate the Average Cycle time per PC per Team

# Group the data by 'PlanningCycle' and 'TeamName'
grouped = df_filtered.groupby(['PlanningCycle', 'TeamName'])

# Calculate the average Cycle time for each group
df_lead_time = grouped['CycleTime'].mean().reset_index()

# Rename the 'CycleTime' column to 'AvgCycleTime'
df_lead_time.rename(columns={'CycleTime': 'AvgCycleTime'}, inplace=True)

# Pivot the DataFrame
df_pivot = df_lead_time.pivot(index='TeamName', columns='PlanningCycle', values='AvgCycleTime')

# Reset the index
df_pivot.reset_index(inplace=True)

# Sort the columns (excluding the first column 'TeamName') using the pipc_sort function
sorted_columns = ['TeamName'] + sorted(df_pivot.columns[1:], key=pipc_sort)
df_pivot = df_pivot[sorted_columns]

# Write the DataFrame to a new sheet in the Excel file
with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
    df_pivot.to_excel(writer, sheet_name='AvgCycleTime', index=False)