"""Protocol constants used by Django channels."""

RUN_ANALYSIS_CHANNEL = 'lactolyse.runanalysis'

LACTATE_REPORT_TYPE = 'lactolyse.lactate_report'
LACTATE_REPORT_RUN_TYPE = 'lactolyse.lactate_run_report'
CONCONI_REPORT_TYPE = 'lactolyse.conconi_report'

GROUP_SESSIONS = 'lactolyse.session.{websocket_id}'
