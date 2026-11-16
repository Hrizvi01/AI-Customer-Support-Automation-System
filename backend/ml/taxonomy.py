"""Reviewed operational grouping of BANKING77 intents, not original support labels."""
ACCOUNT = {
    'card_linking', 'lost_or_stolen_card', 'pin_blocked', 'edit_personal_details',
    'why_verify_identity', 'unable_to_verify_identity', 'compromised_card',
    'passcode_forgotten', 'lost_or_stolen_phone', 'terminate_account',
    'verify_source_of_funds', 'change_pin', 'verify_top_up', 'activate_my_card',
    'verify_my_identity', 'beneficiary_not_allowed',
}
TECHNICAL = {
    'card_not_working', 'contactless_not_working', 'virtual_card_not_working',
    'top_up_failed', 'failed_transfer', 'declined_card_payment', 'declined_transfer',
    'declined_cash_withdrawal', 'balance_not_updated_after_bank_transfer',
    'balance_not_updated_after_cheque_or_cash_deposit', 'automatic_top_up',
    'apple_pay_or_google_pay',
}
BILLING = {
    'exchange_rate', 'card_payment_wrong_exchange_rate', 'extra_charge_on_statement',
    'pending_cash_withdrawal', 'top_up_by_bank_transfer_charge', 'pending_top_up',
    'cancel_transfer', 'wrong_amount_of_cash_received', 'card_payment_fee_charged',
    'transfer_not_received_by_recipient', 'top_up_reverted', 'card_payment_not_recognised',
    'direct_debit_payment_not_recognised', 'pending_card_payment', 'request_refund',
    'Refund_not_showing_up', 'pending_transfer', 'transaction_charged_twice',
    'reverted_card_payment?', 'transfer_fee_charged', 'wrong_exchange_rate_for_cash_withdrawal',
    'cash_withdrawal_not_recognised', 'exchange_charge', 'top_up_by_card_charge', 'cash_withdrawal_charge',
}


def category(intent: str) -> str:
    if intent in ACCOUNT:
        return 'account'
    if intent in TECHNICAL:
        return 'technical'
    if intent in BILLING:
        return 'billing'
    return 'general'
