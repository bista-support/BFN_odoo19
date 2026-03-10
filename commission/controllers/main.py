from odoo import http
from odoo.http import request
import io
import csv

class SettlementReportController(http.Controller):

    @http.route('/commission/settlement/csv/<int:settlement_id>', type='http', auth='user')
    def export_settlement_csv(self, settlement_id, **kwargs):
        settlement = request.env['commission.settlement'].browse(settlement_id)
        if not settlement.exists():
            return request.not_found()

        # Prepare CSV
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Date','Agent','Customer', 'Invoice Line', 'Invoice Number', 'Commission', 'Settled Amount'])  # headers

        # Example: export related lines
        for line in settlement.line_ids:
            customer = (
                line.invoice_line_id.move_id.partner_id.display_name
                if line.invoice_line_id and line.invoice_line_id.move_id and line.invoice_line_id.move_id.partner_id
                else ''
            )
            writer.writerow([
                line.date or '', # Date
                line.agent_id.display_name if line.agent_id else '', #Agent name
                customer,                                           #customer name
                line.invoice_line_id.name if line.invoice_line_id else '', # Invoice Line (or use display_name if preferred)
                line.invoice_number if line.invoice_number else '',         # Invoice Number
                line.commission_id.name if line.commission_id else '',   # Commission
                line.settled_amount or 0.0                               # Settled Amount
            ])

        csv_data = buffer.getvalue()
        buffer.close()
        
        agent_name = settlement.agent_id.name.replace(' ', '_') if settlement.agent_id else 'NoAgent'
        date_to = settlement.date_to.strftime('%Y-%m-%d') if settlement.date_to else 'NoDate'

        filename = f"Commission_Lines_{agent_name}_{date_to}.csv"

        # Send as downloadable CSV
        return request.make_response(
            csv_data,
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', f'attachment; filename={filename}')
            ]
        )
