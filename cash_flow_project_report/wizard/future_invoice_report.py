
class FutureInvoiceReport(object):

    def __init__(self, partner, column, period, report_type, qty, rate):
        self.partner = partner
        self.column = column
        self.period = period
        self.report_type = report_type
        self.qty = qty
        self.rate = rate
