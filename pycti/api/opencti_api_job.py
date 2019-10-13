import logging


class OpenCTIApiJob:

    def __init__(self, api):
        self.api = api

    def report_status(self, job_id, status, message):
        logging.info('Reporting job ' + job_id + ' with status ' + status + '...')
        query = """
            mutation ReportJobStatus($id: ID!, $status: Status!, $message: String) {
                reportJobStatus(id: $id, status: $status, message: $message) {
                    id
                }
            }
           """
        self.api.query(query, {'id': job_id, 'status': status, 'message': message})

    def report_error(self, job_id, message):
        self.report_status(job_id, 'error', message)

    def report_success(self, job_id, message):
        self.report_status(job_id, 'complete', message)
