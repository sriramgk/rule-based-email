from datetime import datetime, timedelta
from models.email import Email


class EmailRuleProcessor:
    def __init__(self, rules: dict, google_email_provider):
        self.rules = rules
        self.google_email_provider = google_email_provider

    def apply_rules_to_emails(self, emails):
        results = []
        for email in emails:
            actions_to_apply = []
            for rule_set in self.rules["rule_sets"]:
                if self.evaluate_rule_set(rule_set, email):
                    actions_to_apply.extend(rule_set["actions"])

            if actions_to_apply:
                self.apply_actions(actions_to_apply, email)

            results.append({"email": email.subject, "actions": actions_to_apply})

        return results

    def evaluate_rule_set(self, rule_set, email: Email):
        """
        Function to evaluate if an email matches a rule set
        """
        rule_match = rule_set["rule_match"]
        rules = rule_set["rules"]

        if rule_match == "any":
            return any(self.evaluate_rule(rule, email.to_dict()) for rule in rules)
        elif rule_match == "all":
            return all(self.evaluate_rule(rule, email.to_dict()) for rule in rules)
        else:
            return False

    # Function to evaluate if an email matches a rule
    def evaluate_rule(self, rule, email):
        field = rule["field"]
        predicate = rule["predicate"]
        value = rule["value"]
        result = False

        if field in email:
            if field == "received_at":
                # Get X days before date
                value = datetime.now() - timedelta(days=int(value))

            if predicate == "contains":
                result = value.lower() in email[field].lower()
            elif predicate == "does_not_contain":
                result = value.lower() not in email[field].lower()
            elif predicate == "equals":
                result = email[field].lower() == value.lower()
            elif predicate == "does_not_equal":
                result = email[field].lower() != value.lower()
            elif predicate == "greater_than":
                result = email[field] < value
            elif predicate == "less_than":
                result = email[field] > value
        return result

    def apply_actions(self, actions, email):
        """
        apply actions on emails
        """
        for action in actions:
            if action["action"] == "mark_as_read":
                self.google_email_provider.mark_as_read(email.email_provider_id)
                print(
                    f"Marked as read, {email.email_provider_id}, Subject {email.subject}"
                )
            elif action["action"] == "mark_as_unread":
                self.google_email_provider.mark_as_unread(email.email_provider_id)
                print(
                    f"Marked email as un read, {email.email_provider_id}, Subject {email.subject}"
                )
            elif action["action"] == "move_message":
                self.google_email_provider.move_to_label(
                    email.email_provider_id, action["value"]
                )
                print(
                    f"Moved email to {action['value']}, {email.email_provider_id}, Subject {email.subject} "
                )
