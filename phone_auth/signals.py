from django.dispatch import Signal

reset_pass_mail = Signal()
reset_pass_phone = Signal()
verify_email = Signal()
verify_phone = Signal()
