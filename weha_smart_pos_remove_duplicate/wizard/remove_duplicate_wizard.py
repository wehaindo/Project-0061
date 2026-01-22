import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class RemoveDuplicateWizard(models.TransientModel):
    _name = 'remove.duplicate.wizard'
    _description = 'Remove Duplicate POS Order Lines Wizard'

    # Selection fields
    session_ids = fields.Many2many(
        'pos.session',
        string='POS Sessions',
        help='Select POS sessions to process all orders within. Leave empty to process all sessions.'
    )
    
    # State management
    state = fields.Selection([
        ('scan', 'Scan Results'),
        ('confirm', 'Confirm Deletion'),
        ('done', 'Completed')
    ], default='scan', string='State')
    
    # Scan results
    scanned_session_count = fields.Integer(string='Sessions Scanned', readonly=True)
    scanned_order_count = fields.Integer(string='Orders Scanned', readonly=True)
    total_duplicate_orders = fields.Integer(string='Total Duplicate Orders', readonly=True)
    unique_orders_count = fields.Integer(string='Unique Orders', readonly=True)
    
    # Duplicate order details
    duplicate_order_ids = fields.One2many(
        'remove.duplicate.order',
        'wizard_id',
        string='Duplicate Orders',
        readonly=True
    )
    
    # Summary by order
    order_summary_ids = fields.One2many(
        'remove.duplicate.order.summary',
        'wizard_id',
        string='Order Summary by Access Token',
        readonly=True
    )
    
    # Session summary
    session_summary_ids = fields.One2many(
        'remove.duplicate.session.summary',
        'wizard_id',
        string='Session Summary',
        readonly=True
    )
    
    # Removal results
    removed_orders_count = fields.Integer(string='Orders Removed', readonly=True)
    error_messages = fields.Text(string='Errors', readonly=True)

    # Auto-scan functionality disabled per user request
    # Sessions are not automatically loaded on wizard open
    # User must manually select sessions and click scan button

    def action_scan_duplicates(self):
        """Scan selected sessions for duplicate orders"""
        # Clear previous results
        if self.duplicate_order_ids:
            self.duplicate_order_ids.unlink()
        if self.order_summary_ids:
            self.order_summary_ids.unlink()
        if self.session_summary_ids:
            self.session_summary_ids.unlink()
        
        # Get sessions to process
        sessions = self._get_sessions_to_process()
        
        if not sessions:
            raise UserError(_('No POS sessions found to process.'))
        
        _logger.info(f"Scanning {len(sessions)} sessions for duplicate orders")
        
        # Collect all orders from selected sessions
        all_orders = self.env['pos.order']
        for session in sessions:
            all_orders |= self._get_orders_in_session(session)
        
        _logger.info(f"Total orders to scan: {len(all_orders)}")
        
        # Find duplicates based on access_token
        duplicate_info = self._find_duplicate_orders(all_orders)
        
        total_duplicates = len(duplicate_info['duplicate_orders'])
        unique_count = len(duplicate_info['unique_tokens'])
        duplicate_order_records = []
        order_summaries = []
        session_summaries = {}
        
        # Create duplicate order records
        for dup_order in duplicate_info['duplicate_orders']:
            duplicate_order_records.append((0, 0, {
                'session_id': dup_order.session_id.id,
                'session_name': dup_order.session_id.name,
                'order_id': dup_order.id,
                'order_name': dup_order.name,
                'access_token': dup_order.access_token or '',
                'date_order': dup_order.date_order,
                'amount_total': dup_order.amount_total,
                'partner_id': dup_order.partner_id.id if dup_order.partner_id else False,
                'partner_name': dup_order.partner_id.name if dup_order.partner_id else '',
            }))
            
            # Track session summary
            session_id = dup_order.session_id.id
            if session_id not in session_summaries:
                session_summaries[session_id] = {
                    'session': dup_order.session_id,
                    'duplicate_count': 0
                }
            session_summaries[session_id]['duplicate_count'] += 1
        
        # Create order summaries grouped by access_token
        for token, orders in duplicate_info['orders_by_token'].items():
            if len(orders) > 1:  # Only show tokens with duplicates
                order_summaries.append((0, 0, {
                    'access_token': token or 'No Token',
                    'total_orders': len(orders),
                    'duplicate_count': len(orders) - 1,
                    'first_order_id': orders[0].id,
                    'first_order_name': orders[0].name,
                }))
        
        # Create session summaries
        session_summary_records = []
        for session in sessions:
            session_id = session.id
            session_orders = all_orders.filtered(lambda o: o.session_id.id == session_id)
            duplicate_count = session_summaries.get(session_id, {}).get('duplicate_count', 0)
            
            session_summary_records.append((0, 0, {
                'session_id': session.id,
                'session_name': session.name,
                'total_orders': len(session_orders),
                'duplicate_orders': duplicate_count,
                'unique_orders': len(session_orders) - duplicate_count,
            }))
        
        # Update wizard with results
        self.write({
            'state': 'scan',
            'scanned_session_count': len(sessions),
            'scanned_order_count': len(all_orders),
            'total_duplicate_orders': total_duplicates,
            'unique_orders_count': unique_count,
            'duplicate_order_ids': duplicate_order_records,
            'order_summary_ids': order_summaries,
            'session_summary_ids': session_summary_records,
        })
        
        _logger.info(f"Scan complete: {total_duplicates} duplicate orders found across {len(sessions)} sessions")
        
        # Only return action if called directly, not from onchange
        if not self.env.context.get('from_onchange'):
            return self._return_wizard_action()

    def action_confirm_removal(self):
        """Move to confirmation state"""
        self.ensure_one()
        
        if not self.duplicate_order_ids:
            raise UserError(_('No duplicate orders found to remove.'))
        
        self.state = 'confirm'
        return self._return_wizard_action()

    def action_remove_duplicates(self):
        """Remove the duplicate orders"""
        self.ensure_one()
        
        if not self.duplicate_order_ids:
            raise UserError(_('No duplicate orders to remove.'))
        
        _logger.info(f"Removing {len(self.duplicate_order_ids)} duplicate orders")
        
        removed_count = 0
        errors = []
        
        # Process each duplicate order
        def action_remove_duplicates(self):
            for dup_order in self.duplicate_order_ids:
                order = dup_order.order_id
                
                if order.state == 'draft':
                    order.unlink()  # Delete draft orders
                    
                elif order.state in ['paid', 'done', 'invoiced']:
                    order.action_pos_order_cancel()  # Cancel paid orders
                    
                elif order.state == 'cancel':
                    try:
                        order.unlink()  # Try to delete cancelled
                    except:
                        pass  # Already cancelled, that's okay
        
        # Update wizard with results
        self.write({
            'state': 'done',
            'removed_orders_count': removed_count,
            'error_messages': '\n'.join(errors) if errors else 'All duplicate orders removed successfully!',
        })
        
        _logger.info(f"Removal complete: {removed_count} duplicate orders removed")
        
        return self._return_wizard_action()

    def action_back_to_scan(self):
        """Go back to scan results"""
        self.ensure_one()
        self.state = 'scan'
        return self._return_wizard_action()

    def action_reset(self):
        """Reset wizard and rescan"""
        self.ensure_one()
        
        self.duplicate_order_ids.unlink()
        self.order_summary_ids.unlink()
        self.session_summary_ids.unlink()
        
        self.write({
            'state': 'scan',
            'scanned_session_count': 0,
            'scanned_order_count': 0,
            'total_duplicate_orders': 0,
            'unique_orders_count': 0,
            'removed_orders_count': 0,
            'error_messages': False,
        })
        
        # Rescan with current sessions
        self.action_scan_duplicates()
        
        return self._return_wizard_action()

    def _get_sessions_to_process(self):
        """Get sessions based on selection criteria"""
        if self.session_ids:
            return self.session_ids
        
        # If no specific sessions selected, get all sessions
        # You can add additional filters here (e.g., by date, state, etc.)
        return self.env['pos.session'].search([])

    def _get_orders_in_session(self, session):
        """Get all orders in a session"""
        domain = [('session_id', '=', session.id)]
        return self.env['pos.order'].search(domain)

    def _find_duplicate_orders(self, orders):
        """Find duplicate orders based on access_token"""
        orders_by_token = {}
        unique_tokens = set()
        duplicate_orders = []
        
        for order in orders:
            token = order.access_token or ''
            
            if not token:
                # Skip orders without access token
                continue
                
            if token not in orders_by_token:
                orders_by_token[token] = []
                unique_tokens.add(token)
            
            orders_by_token[token].append(order)
        
        # Identify duplicates (keep first, mark rest as duplicates)
        for token, token_orders in orders_by_token.items():
            if len(token_orders) > 1:
                # Keep the first order (usually oldest), mark rest as duplicates
                sorted_orders = sorted(token_orders, key=lambda o: o.date_order)
                duplicate_orders.extend(sorted_orders[1:])  # Skip first, add rest
        
        return {
            'orders_by_token': orders_by_token,
            'unique_tokens': unique_tokens,
            'duplicate_orders': duplicate_orders
        }

    def _return_wizard_action(self):
        """Return action to keep wizard open"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'remove.duplicate.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class RemoveDuplicateOrder(models.TransientModel):
    _name = 'remove.duplicate.order'
    _description = 'Duplicate Order Detail'
    _order = 'session_name, date_order desc'

    wizard_id = fields.Many2one('remove.duplicate.wizard', required=True, ondelete='cascade')
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    session_name = fields.Char(string='Session', readonly=True)
    order_id = fields.Many2one('pos.order', string='Order', readonly=True)
    order_name = fields.Char(string='Order Reference', readonly=True)
    access_token = fields.Char(string='Access Token', readonly=True)
    date_order = fields.Datetime(string='Order Date', readonly=True)
    amount_total = fields.Float(string='Total Amount', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    partner_name = fields.Char(string='Customer Name', readonly=True)


class RemoveDuplicateOrderSummary(models.TransientModel):
    _name = 'remove.duplicate.order.summary'
    _description = 'Order Summary Grouped by Access Token'
    _order = 'total_orders desc'

    wizard_id = fields.Many2one('remove.duplicate.wizard', required=True, ondelete='cascade')
    access_token = fields.Char(string='Access Token', readonly=True)
    total_orders = fields.Integer(string='Total Orders', readonly=True)
    duplicate_count = fields.Integer(string='Duplicate Count', readonly=True)
    first_order_id = fields.Many2one('pos.order', string='First Order', readonly=True)
    first_order_name = fields.Char(string='First Order Reference', readonly=True)


class RemoveDuplicateSessionSummary(models.TransientModel):
    _name = 'remove.duplicate.session.summary'
    _description = 'Session Summary with Duplicate Orders'
    _order = 'session_name'

    wizard_id = fields.Many2one('remove.duplicate.wizard', required=True, ondelete='cascade')
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    session_name = fields.Char(string='Session Name', readonly=True)
    total_orders = fields.Integer(string='Total Orders', readonly=True)
    duplicate_orders = fields.Integer(string='Duplicate Orders', readonly=True)
    unique_orders = fields.Integer(string='Unique Orders', readonly=True)
