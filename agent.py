#@title Code from Gemini
import os
from google.adk.agents import Agent
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from datetime import date

from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
import google.auth
from google.adk.tools.bigquery.config import WriteMode
from .tools import call_ds_agent


date_today = date.today()
STATE_QUERY_RESULTS="query_result"


CREDENTIALS_VALUE = None

# Write modes define BigQuery access control of agent:
tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED,
)


application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
      credentials=application_default_credentials)

# Instantiate a BigQuery toolset
bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config,
	tool_filter=[
        'list_table_ids',
        'get_table_info',
        'execute_sql',
    ]
)

root_agent = Agent(
   model="gemini-2.0-flash",
   name="bigquery_agent",
   description=(
       "Agent that answers questions about BigQuery data by executing SQL queries"
   ),

   # --- THIS IS THE NEW PROMPT ---
   instruction=f"""You are a very smart BigQuery Cost analysis agent.

   **Workflow for Cost Analysis:**
   * The user's project is: `vertexsearch-447722`
   * The dataset is: `BillingExport`
   * When the user asks for costs (e.g., "get me costs across projects"):
       1.  First, call the `list_table_ids` tool to find the tables in the `argolis-project-340214.BillingExport` dataset.
       2.  Identify the main billing table (it usually starts with `gcp_billing_`).
       3.  Call `execute_sql` with a query to get the costs.
       4.  Return the results of the query to the user.

   **Workflow for data science type questions including charting:**
   * When the user asks for a data science query or a chart:
       1.  Follow the full **Workflow for Cost Analysis** to get the data from `execute_sql`.
       2.  **Immediately** call the `call_ds_agent` tool. Pass the `query_result` and the user's `question`.
       3. Share the output of the call_ds_agent tool with the user  .
       # ------------------------------------------

   Understand the user's question and use this workflow to answer it.
   """,

   tools=[bigquery_toolset, call_ds_agent],
)
