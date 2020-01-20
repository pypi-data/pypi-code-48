#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class IntrastatStatementPurchaseSection(models.AbstractModel):
    _inherit = 'account.intrastat.statement.section'
    _name = 'account.intrastat.statement.purchase.section'
    _description = "Fields and methods " \
                   "common to all Intrastat purchase sections"

    amount_currency = fields.Integer(
        string="Amount in Currency",
        digits=dp.get_precision('Account'))

    @api.model
    def _prepare_statement_line(self, inv_intra_line, statement_id=None):
        res = super(IntrastatStatementPurchaseSection, self) \
            ._prepare_statement_line(inv_intra_line, statement_id)
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id)
        invoice_id = inv_intra_line.invoice_id

        # Amounts
        dp_model = self.env['decimal.precision']
        amount_currency = statement_id.round_min_amount(
            inv_intra_line.amount_currency,
            statement_id.company_id or company_id,
            dp_model.precision_get('Account'))

        res.update({
            # Only for non-Euro countries
            'amount_currency':
                amount_currency
                if not invoice_id.company_id.currency_id.id
                and invoice_id.currency_id.id
                else 0,
        })
        return res


class IntrastatStatementPurchaseSection1(models.Model):
    _inherit = 'account.intrastat.statement.purchase.section'
    _name = 'account.intrastat.statement.purchase.section1'
    _description = "Intrastat Statement - Purchases Section 1"

    transaction_nature_id = fields.Many2one(
        comodel_name='account.intrastat.transaction.nature',
        string="Transaction Nature")
    weight_kg = fields.Integer(
        string="Net Mass (kg)")
    additional_units = fields.Integer(
        string="Additional Units")
    additional_units_required = fields.Boolean(
        string="Additional Unit Required",
        store=True,
        related='intrastat_code_id.additional_unit_required')
    additional_units_uom = fields.Char(
        string="Additional Unit of Measure",
        readonly=True,
        related='intrastat_code_id.additional_unit_uom_id.name')
    statistic_amount_euro = fields.Integer(
        string="Statistic Value in Euro",
        digits=dp.get_precision('Account'))
    delivery_code_id = fields.Many2one(
        comodel_name='account.incoterms',
        string="Delivery Terms")
    transport_code_id = fields.Many2one(
        comodel_name='account.intrastat.transport',
        string="Transport Mode")
    country_origin_id = fields.Many2one(
        comodel_name='res.country',
        string="Provenance Country")
    country_good_origin_id = fields.Many2one(
        comodel_name='res.country',
        string="Goods Origin Country")
    province_destination_id = fields.Many2one(
        comodel_name='res.country.state',
        string="Destination Province")

    @api.onchange('weight_kg')
    def change_weight_kg(self):
        if self.statement_id.company_id.intrastat_additional_unit_from == \
                'weight':
            self.additional_units = self.weight_kg

    @api.multi
    def apply_partner_data(self, partner_data):
        res = super(IntrastatStatementPurchaseSection1, self) \
            .apply_partner_data(partner_data)
        if 'country_origin_id' in partner_data:
            self.country_origin_id = partner_data['country_origin_id']
        if 'country_good_origin_id' in partner_data:
            self.country_good_origin_id = \
                partner_data['country_good_origin_id']
        return res

    @api.model
    def _prepare_statement_line(self, inv_intra_line, statement_id=None):
        res = super(IntrastatStatementPurchaseSection1, self) \
            ._prepare_statement_line(inv_intra_line, statement_id)
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id)

        # Company defaults
        delivery_code_id = \
            inv_intra_line.delivery_code_id \
            or company_id.intrastat_purchase_delivery_code_id
        province_destination_id = \
            inv_intra_line.province_destination_id \
            or company_id.intrastat_purchase_province_destination_id
        statistic_amount = \
            inv_intra_line.statistic_amount_euro \
            or company_id.intrastat_purchase_statistic_amount
        transaction_nature_id = \
            inv_intra_line.transaction_nature_id \
            or company_id.intrastat_purchase_transaction_nature_id
        transport_code_id = \
            inv_intra_line.transport_code_id \
            or company_id.intrastat_purchase_transport_code_id

        # Amounts
        dp_model = self.env['decimal.precision']
        statistic_amount = statement_id.round_min_amount(
            statistic_amount,
            statement_id.company_id or company_id,
            dp_model.precision_get('Account'))

        res.update({
            'transaction_nature_id': transaction_nature_id.id,
            'weight_kg': round(inv_intra_line.weight_kg) or 0,
            'additional_units': round(inv_intra_line.additional_units) or 0,
            'statistic_amount_euro': statistic_amount,
            'delivery_code_id': delivery_code_id.id,
            'transport_code_id': transport_code_id,
            'country_origin_id': inv_intra_line.country_origin_id.id,
            'country_good_origin_id': inv_intra_line.country_good_origin_id.id,
            'province_destination_id': province_destination_id.id
        })
        return res

    @api.multi
    def _prepare_export_line(self):
        self.ensure_one()
        self._export_line_checks(_("Purchase"), 1)

        rcd = ''
        # Codice dello Stato membro del fornitore
        country_id = self.country_partner_id or self.partner_id.country_id
        rcd += '{:2s}'.format(country_id.code or '')
        #  Codice IVA del fornitore
        rcd += '{:12s}'.format(self.vat_code.replace(' ', '') or '')
        # Ammontare delle operazioni in euro
        rcd += '{:13s}'.format(str(self.amount_euro).zfill(13))
        # Ammontare delle operazioni in valuta
        rcd += '{:13s}'.format(str(self.amount_currency).zfill(13))
        # Codice della natura della transazione
        rcd += '{:1s}'.format(self.transaction_nature_id.code or '')
        # Codice della nomenclatura combinata della merce
        rcd += '{:8s}'.format(self.intrastat_code_id.name or '')
        #  Massa netta in chilogrammi
        rcd += '{:10s}'.format(str(self.weight_kg).zfill(10))
        #  Quantità espressa nell'unità di misura supplementare
        rcd += '{:10s}'.format(str(self.additional_units).zfill(10))
        #  Valore statistico in euro
        rcd += '{:13s}'.format(str(self.statistic_amount_euro).zfill(13))
        #  Codice delle condizioni di consegna
        rcd += '{:1s}'.format(
            self.delivery_code_id and self.delivery_code_id.code[:1] or '')
        #  Codice del modo di trasporto
        rcd += '{:1s}'.format(
            self.transport_code_id and str(self.transport_code_id.code) or '')
        #  Codice del paese di provenienza
        rcd += '{:2s}'.format(self.country_origin_id.code or '')
        #  Codice del paese di origine della merce
        rcd += '{:2s}'.format(self.country_good_origin_id.code or '')
        # Codice della provincia di destinazione della merce
        rcd += '{:2s}'.format(self.province_destination_id.code or '')

        rcd += "\r\n"
        return rcd


class IntrastatStatementPurchaseSection2(models.Model):
    _inherit = 'account.intrastat.statement.purchase.section'
    _name = 'account.intrastat.statement.purchase.section2'
    _description = "Intrastat Statement - Purchases Section 2"

    month = fields.Integer(
        string="Ref. Month")
    quarterly = fields.Integer(
        string="Ref. Quarter")
    year_id = fields.Integer(
        string="Ref. Year")
    sign_variation = fields.Selection(
        selection=[
            ('+', "+"),
            ('-', "-")],
        string="Adjustment Sign")
    transaction_nature_id = fields.Many2one(
        comodel_name='account.intrastat.transaction.nature',
        string="Transaction Nature")
    statistic_amount_euro = fields.Integer(
        string='Statistic Value in Euro',
        digits=dp.get_precision('Account'))

    @api.model
    def _prepare_statement_line(self, inv_intra_line, statement_id=None):
        res = super(IntrastatStatementPurchaseSection2, self) \
            ._prepare_statement_line(inv_intra_line, statement_id)
        company_id = self._context.get(
            'company_id', self.env.user.company_id)

        # Company defaults
        statistic_amount = \
            inv_intra_line.statistic_amount_euro \
            or company_id.intrastat_purchase_statistic_amount
        transaction_nature_id = \
            inv_intra_line.transaction_nature_id \
            or company_id.intrastat_purchase_transaction_nature_id

        # Amounts
        dp_model = self.env['decimal.precision']
        statistic_amount = statement_id.round_min_amount(
            statistic_amount,
            statement_id.company_id or company_id,
            dp_model.precision_get('Account'))

        # Period Ref
        ref_period = statement_id._get_period_ref()

        # Sign variation
        sign_variation = False
        if inv_intra_line.invoice_id.type == 'in_refund':
            sign_variation = '-'

        res.update({
            'month': ref_period.get('month'),
            'quarterly': ref_period.get('quarterly'),
            'year_id': ref_period.get('year_id'),
            'sign_variation': sign_variation,
            'transaction_nature_id': transaction_nature_id,
            'statistic_amount_euro': statistic_amount,
        })
        return res

    @api.multi
    def _export_line_checks(self, section_label, section_number):
        super(IntrastatStatementPurchaseSection2, self) \
            ._export_line_checks(section_label, section_number)
        if not self.year_id:
            raise ValidationError(
                _("Missing reference year on 'Purchases - Section 2'"))
        if not self.sign_variation:
            raise ValidationError(
                _("Missing adjustment sign on 'Purchases - Section 2'"))
        if self.statement_id.period_type == 'M':
            if not self.month:
                raise ValidationError(
                    _("Missing reference month "
                        "on 'Purchases - Section 2' adjustment"))
        elif self.statement_id.period_type == 'T':
            if not self.quarterly:
                raise ValidationError(
                    _("Missing reference quarter "
                        "on 'Purchases - Section 2' adjustment"))

    @api.multi
    def _prepare_export_line(self):
        self._export_line_checks(_("Purchase"), 2)

        rcd = ''
        # Mese di riferimento del riepilogo da rettificare
        rcd += '{:2s}'.format(str(self.month).zfill(2))
        #  Trimestre di riferimento del riepilogo da rettificare
        rcd += '{:1s}'.format(str(self.quarterly).zfill(1))
        # Anno periodo di ref da modificare
        rcd += '{:2s}'.format(self.year_id and str(self.year_id)[2:] or '')
        # Codice dello Stato membro del fornitore
        country_id = self.country_partner_id or self.partner_id.country_id
        rcd += '{:2s}'.format(country_id.code or '')
        #  Codice IVA del fornitore
        rcd += '{:12s}'.format(self.vat_code.replace(' ', '') or '')
        #  Segno da attribuire alle variazioni da X(1) apportare
        rcd += '{:1s}'.format(self.sign_variation or '')
        # Ammontare delle operazioni in euro
        rcd += '{:13s}'.format(str(self.amount_euro).zfill(13))
        # Ammontare delle operazioni in valuta
        # >> da valorizzare solo per operazione Paesi non Euro
        if not (
                self.invoice_id.company_id.currency_id.id ==
                self.invoice_id.currency_id.id
        ):
            rcd += '{:13s}'.format(str(self.amount_currency).zfill(13))
        else:
            rcd += '{:13s}'.format(str(0).zfill(13))
        # Codice della natura della transazione
        rcd += '{:1s}'.format(
            self.transaction_nature_id and self.transaction_nature_id.code or '')
        # Codice della nomenclatura combinata della merce
        rcd += '{:8s}'.format(
            self.intrastat_code_id and self.intrastat_code_id.name or '')
        #  Valore statistico in euro
        rcd += '{:13s}'.format(str(self.statistic_amount_euro).zfill(13))

        rcd += "\r\n"
        return rcd

    @api.multi
    def get_amount_euro(self):
        amount = 0
        for section in self:
            if section.sign_variation == '-':
                amount -= section.amount_euro
            else:
                amount += section.amount_euro
        return amount


class IntrastatStatementPurchaseSection3(models.Model):
    _inherit = 'account.intrastat.statement.purchase.section'
    _name = 'account.intrastat.statement.purchase.section3'
    _description = "Intrastat Statement - Purchases Section 3"

    invoice_number = fields.Char(
        string="Invoice Number")
    invoice_date = fields.Date(
        string="Invoice Date")
    supply_method = fields.Selection(
        selection=[
            ('I', "Instant"),
            ('R', "Repeated")],
        string="Supply Method")
    payment_method = fields.Selection(
        selection=[
            ('B', "Bank Transfer"),
            ('A', "Credit"),
            ('X', "Other")],
        string="Payment Method")
    country_payment_id = fields.Many2one(
        comodel_name='res.country',
        string="Payment Country")

    @api.model
    def _prepare_statement_line(self, inv_intra_line, statement_id=None):
        res = super(IntrastatStatementPurchaseSection3, self) \
            ._prepare_statement_line(inv_intra_line, statement_id)
        res.update({
            'invoice_number': inv_intra_line.invoice_number,
            'invoice_date': inv_intra_line.invoice_date,
            'supply_method': inv_intra_line.supply_method,
            'payment_method': inv_intra_line.payment_method,
            'country_payment_id': inv_intra_line.country_payment_id.id,
        })
        return res

    @api.multi
    def _prepare_export_line(self):
        self._export_line_checks(_("Purchase"), 3)

        rcd = ''
        # Codice dello Stato membro del fornitore
        country_id = self.country_partner_id or self.partner_id.country_id
        rcd += '{:2s}'.format(country_id.code or '')
        #  Codice IVA del fornitore
        rcd += '{:12s}'.format(self.vat_code.replace(' ', '') or '')
        # Ammontare delle operazioni in euro
        rcd += '{:13s}'.format(str(self.amount_euro).zfill(13))
        # Ammontare delle operazioni in valuta
        rcd += '{:13s}'.format(str(self.amount_currency).zfill(13))
        # Numero Fattura
        invoice_number = self.invoice_number or ''
        if len(invoice_number) > 15:
            invoice_number = invoice_number[-15:]
        rcd += '{:15s}'.format(str(invoice_number).zfill(15))
        # Data Fattura
        invoice_date_ddmmyy = False
        if self.invoice_date:
            invoice_date_ddmmyy = self.invoice_date.strftime('%d%m%y')
        rcd += '{:2s}'.format(invoice_date_ddmmyy or '')
        # Codice del servizio
        rcd += '{:6s}'.format(self.intrastat_code_id.name or '')
        # Modalità di erogazione
        rcd += '{:1s}'.format(self.supply_method or '')
        # Modalità di incasso
        rcd += '{:1s}'.format(self.payment_method or '')
        # Codice del paese di pagamento
        rcd += '{:2s}'.format(self.country_payment_id.code or '')

        rcd += "\r\n"
        return rcd


class IntrastatStatementPurchaseSection4(models.Model):
    _inherit = 'account.intrastat.statement.purchase.section'
    _name = 'account.intrastat.statement.purchase.section4'
    _description = "Intrastat Statement - Purchases Section 4"

    intrastat_custom_id = fields.Many2one(
        comodel_name='account.intrastat.custom',
        string="Customs Section")
    month = fields.Integer(
        string="Ref. Month")
    quarterly = fields.Integer(
        string="Ref. Quarter")
    year_id = fields.Integer(
        string="Ref. Year")
    protocol = fields.Integer(
        string="Protocol Number",
        size=6)
    progressive_to_modify_id = fields.Many2one(
        comodel_name='account.intrastat.statement.purchase.section1',
        string="Progressive to Adjust ID")
    progressive_to_modify = fields.Integer(
        string="Progressive to Adjust")
    invoice_number = fields.Char(
        string="Invoice Number")
    invoice_date = fields.Date(
        string="Invoice Date")
    supply_method = fields.Selection(
        selection=[
            ('I', "Instant"),
            ('R', "Repeated")],
        string="Supply Method")
    payment_method = fields.Selection(
        selection=[
            ('B', "Bank Transfer"),
            ('A', "Credit"),
            ('X', "Other")],
        string="Payment Method")
    country_payment_id = fields.Many2one(
        comodel_name='res.country',
        string="Payment Country")

    @api.model
    def _prepare_statement_line(self, inv_intra_line, statement_id=None):
        res = super(IntrastatStatementPurchaseSection4, self) \
            ._prepare_statement_line(inv_intra_line, statement_id)
        # Period Ref
        ref_period = statement_id._get_period_ref()

        res.update({
            'month': ref_period.get('month'),
            'quarterly': ref_period.get('quarterly'),
            'year_id': ref_period.get('year_id'),
            'invoice_number': inv_intra_line.invoice_number,
            'invoice_date': inv_intra_line.invoice_date,
            'supply_method': inv_intra_line.supply_method,
            'payment_method': inv_intra_line.payment_method,
            'country_payment_id': inv_intra_line.country_payment_id.id,
            'intrastat_custom_id': statement_id.intrastat_custom_id.id
        })
        return res

    @api.multi
    def _export_line_checks(self, section_label, section_number):
        super(IntrastatStatementPurchaseSection4, self) \
            ._export_line_checks(section_label, section_number)
        if not self.year_id:
            raise ValidationError(
                _("Missing reference year on 'Purchases - Section 4'"))
        if not self.intrastat_custom_id:
            raise ValidationError(
                _("Missing customs section on 'Purchases - Section 4'"))
        if not self.protocol:
            raise ValidationError(
                _("Missing protocol number on 'Purchases - Section 4'"))
        if not self.progressive_to_modify:
            raise ValidationError(
                _("Missing progressive to adjust on 'Purchases - Section 4'"))
        if (not self.invoice_number) or (not self.invoice_date):
            raise ValidationError(
                _("Missing invoice data on 'Purchases - Section 4'"))
        if not self.supply_method:
            raise ValidationError(
                _("Missing supply method on 'Purchases - Section 4'"))
        if not self.payment_method:
            raise ValidationError(
                _("Missing payment method on 'Purchases - Section 4'"))
        if not self.country_payment_id:
            raise ValidationError(
                _("Missing payment country on 'Purchases - Section 4'"))

    @api.multi
    def _prepare_export_line(self):
        self._export_line_checks(_("Purchase"), 4)

        rcd = ''
        # Codice della sezione doganale in cui è stato registrata la
        # dichiarazione da rettificare
        rcd += '{:6s}'.format(self.intrastat_custom_id.code or '')
        # Anno di registrazione della dichiarazione da rettificare
        rcd += '{:2s}'.format(self.year_id and str(self.year_id)[2:] or '')
        # Protocollo della dichiarazione da rettificare
        rcd += '{:6s}'.format(
            self.protocol and str(self.protocol).zfill(6) or '')
        # Progressivo della sezione 3 da rettificare
        rcd += '{:5s}'.format(
            self.progressive_to_modify_id and
            str(self.progressive_to_modify_id.sequence).zfill(5)
            or '')
        # Codice dello Stato membro dell’acquirente
        country_id = self.country_partner_id or self.partner_id.country_id
        rcd += '{:2s}'.format(country_id.code or '')
        # Codice IVA dell’acquirente
        rcd += '{:12s}'.format(self.vat_code.replace(' ', '') or '')
        # Ammontare delle operazioni in euro
        rcd += '{:13s}'.format(str(self.amount_euro).zfill(13))
        # Ammontare delle operazioni in valuta
        # >> da valorizzare solo per operazione Paesi non Euro
        if not (
                self.invoice_id.company_id.currency_id.id ==
                self.invoice_id.currency_id.id
        ):
            rcd += '{:13s}'.format(str(self.amount_currency).zfill(13))
        else:
            rcd += '{:13s}'.format(str(0).zfill(13))
        # Numero Fattura
        rcd += '{:15s}'.format(str(self.invoice_number).zfill(15))
        # Data Fattura
        invoice_date_ddmmyy = False
        if self.invoice_date:
            invoice_date_ddmmyy = self.invoice_date.strftime('%d%m%y')
        rcd += '{:2s}'.format(invoice_date_ddmmyy or '')
        # Codice del servizio
        rcd += '{:6s}'.format(self.intrastat_code_id.name or '')
        # Modalità di erogazione
        rcd += '{:1s}'.format(self.supply_method or '')
        # Modalità di incasso
        rcd += '{:1s}'.format(self.payment_method or '')
        # Codice del paese di pagamento
        rcd += '{:2s}'.format(self.country_payment_id.code or '')

        rcd += "\r\n"
        return rcd
