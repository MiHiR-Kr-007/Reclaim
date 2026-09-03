from datetime import datetime, timedelta
from models import RecoveryCase, DecisionRecord

class ComplianceGuard:

    @staticmethod
    def check_pre_debit_notice(case: RecoveryCase, action_type: str) -> tuple[bool, str]:
        # Only retry-type debit actions require pre-debit notice
        if action_type in ["silent_retry", "retry_debit"]:
            if not case.pre_debit_notice_sent or not case.pre_debit_notice_time:
                return False, "PreDebitNoticeRule: RBI requires pre-debit notice >=24h before debit attempt."
            
            hours_since_notice = (datetime.utcnow() - case.pre_debit_notice_time).total_seconds() / 3600
            if hours_since_notice < 24:
                return False, f"PreDebitNoticeRule: Only {hours_since_notice:.1f}h elapsed since notice. 24h notice window not met."
        
        return True, "PreDebitNoticeRule: Notice window satisfied or not applicable."

    @staticmethod
    def check_afa_threshold(case: RecoveryCase, action_type: str) -> tuple[bool, str]:
        AFA_LIMIT_PAISE = 1500000
        if case.amount_paise > AFA_LIMIT_PAISE and action_type in ["silent_retry", "retry_debit"]:
            return False, "AFAThresholdRule: Amount exceeds ₹15,000. Fresh AFA required; silent retry blocked."
        return True, "AFAThresholdRule: Within ₹15,000 standing consent limit."

    @staticmethod
    def check_max_attempts(case: RecoveryCase, max_allowed: int = 3) -> tuple[bool, str]:
        if case.attempts >= max_allowed:
            return False, f"MaxAttemptsRule: Case has reached max allowed attempts ({case.attempts}/{max_allowed})."
        return True, f"MaxAttemptsRule: Attempt count {case.attempts} within allowed limit."

    @staticmethod
    def check_cooldown(case: RecoveryCase, cooldown_hours: int = 12) -> tuple[bool, str]:
        if case.last_attempt_at:
            hours_since = (datetime.utcnow() - case.last_attempt_at).total_seconds() / 3600
            if hours_since < cooldown_hours:
                return False, f"CooldownRule: Only {hours_since:.1f}h since last attempt. Required cooldown is {cooldown_hours}h."
        return True, "CooldownRule: Cooldown window satisfied."

    @staticmethod
    def check_quiet_hours(start_hour: int = 9, end_hour: int = 20) -> tuple[bool, str]:
        current_hour = datetime.utcnow().hour + 5.5
        current_hour = current_hour % 24
        if not (start_hour <= current_hour <= end_hour):
            return False, f"QuietHoursRule: Outreach blocked outside 9am-8pm window (current local hour ~{int(current_hour)})."
        return True, "QuietHoursRule: Within compliant communication hours."

    @classmethod
    def evaluate_all(cls, case: RecoveryCase, action_type: str) -> list[DecisionRecord]:
        evaluations = [
            ("PreDebitNoticeRule", cls.check_pre_debit_notice(case, action_type)),
            ("AFAThresholdRule", cls.check_afa_threshold(case, action_type)),
            ("MaxAttemptsRule", cls.check_max_attempts(case)),
            ("CooldownRule", cls.check_cooldown(case)),
            ("QuietHoursRule", cls.check_quiet_hours()),
        ]

        records = []
        for rule_name, (allowed, reason) in evaluations:
            record = DecisionRecord(
                case_id=case.id,
                actor="compliance_guard",
                rule_name=rule_name,
                allowed=allowed,
                reason=reason
            )
            records.append(record)
        return records