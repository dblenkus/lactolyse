"""Protocol constants used by Django channels."""

RUN_ANALYSIS_CHANNEL = 'lactolyse.runanalysis'

LACTATE_REPORT_TYPE = 'lactolyse.lactate_report'
CONCONI_REPORT_TYPE = 'lactolyse.conconi_report'

GROUP_SESSIONS = 'lactolyse.session.{websocket_id}'
