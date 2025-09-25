"""Monitor and limit token usage to control costs"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class TokenMonitor:
    def __init__(self, daily_limit=100000, cost_per_1k_tokens=0.000075):
        self.daily_limit = daily_limit
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.usage_file = Path('token_usage.json')
        self.usage = self.load_usage()

    def load_usage(self):
        """Load token usage from file"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {
            'daily': {},
            'total': 0,
            'total_cost': 0
        }

    def save_usage(self):
        """Save token usage to file"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)

    def log_usage(self, tokens_used, operation='synthesis'):
        """Log token usage for an operation"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Initialize today's entry if needed
        if today not in self.usage['daily']:
            self.usage['daily'][today] = {
                'tokens': 0,
                'operations': [],
                'cost': 0
            }

        # Add tokens
        self.usage['daily'][today]['tokens'] += tokens_used
        self.usage['total'] += tokens_used

        # Calculate cost
        cost = (tokens_used / 1000) * self.cost_per_1k_tokens
        self.usage['daily'][today]['cost'] += cost
        self.usage['total_cost'] += cost

        # Log operation
        self.usage['daily'][today]['operations'].append({
            'time': datetime.now().isoformat(),
            'operation': operation,
            'tokens': tokens_used,
            'cost': cost
        })

        self.save_usage()

    def check_daily_limit(self):
        """Check if daily limit has been reached"""
        today = datetime.now().strftime('%Y-%m-%d')

        if today in self.usage['daily']:
            daily_tokens = self.usage['daily'][today]['tokens']
            return daily_tokens < self.daily_limit

        return True

    def get_remaining_tokens(self):
        """Get remaining tokens for today"""
        today = datetime.now().strftime('%Y-%m-%d')

        if today in self.usage['daily']:
            used = self.usage['daily'][today]['tokens']
            return max(0, self.daily_limit - used)

        return self.daily_limit

    def get_usage_report(self):
        """Generate usage report"""
        today = datetime.now().strftime('%Y-%m-%d')

        report = {
            'today': {
                'date': today,
                'tokens_used': 0,
                'cost': 0,
                'operations': 0
            },
            'this_week': {
                'tokens': 0,
                'cost': 0
            },
            'this_month': {
                'tokens': 0,
                'cost': 0
            },
            'all_time': {
                'tokens': self.usage['total'],
                'cost': self.usage['total_cost']
            },
            'daily_limit': self.daily_limit,
            'remaining_today': self.get_remaining_tokens()
        }

        # Today's usage
        if today in self.usage['daily']:
            report['today']['tokens_used'] = self.usage['daily'][today]['tokens']
            report['today']['cost'] = self.usage['daily'][today]['cost']
            report['today']['operations'] = len(self.usage['daily'][today]['operations'])

        # Week and month calculations
        now = datetime.now()
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1)

        for date_str, data in self.usage['daily'].items():
            date = datetime.strptime(date_str, '%Y-%m-%d')

            # This week
            if date >= week_start:
                report['this_week']['tokens'] += data['tokens']
                report['this_week']['cost'] += data['cost']

            # This month
            if date >= month_start:
                report['this_month']['tokens'] += data['tokens']
                report['this_month']['cost'] += data['cost']

        return report

    def estimate_cost(self, num_articles):
        """Estimate cost for processing articles"""
        # Assume 4 chars per token, 250 chars per optimized article
        chars_per_article = 250
        total_chars = num_articles * chars_per_article
        estimated_tokens = total_chars / 4

        input_cost = (estimated_tokens / 1000) * self.cost_per_1k_tokens
        # Assume output is 30% of input
        output_cost = input_cost * 0.3 * 4  # Output tokens cost more

        return {
            'estimated_tokens': int(estimated_tokens),
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'within_limit': estimated_tokens <= self.get_remaining_tokens()
        }


# Integration helper
def check_token_budget(num_articles):
    """Check if operation is within token budget"""
    monitor = TokenMonitor()

    if not monitor.check_daily_limit():
        return False, "Daily token limit reached"

    estimate = monitor.estimate_cost(num_articles)

    if not estimate['within_limit']:
        remaining = monitor.get_remaining_tokens()
        return False, f"Operation would exceed daily limit. Remaining: {remaining} tokens"

    return True, f"OK - Estimated cost: ${estimate['total_cost']:.4f}"


if __name__ == "__main__":
    monitor = TokenMonitor()

    print("TOKEN USAGE MONITOR")
    print("=" * 50)

    # Get usage report
    report = monitor.get_usage_report()

    print(f"\nTODAY ({report['today']['date']}):")
    print(f"  Tokens used: {report['today']['tokens_used']:,}")
    print(f"  Cost: ${report['today']['cost']:.4f}")
    print(f"  Operations: {report['today']['operations']}")
    print(f"  Remaining: {report['remaining_today']:,} tokens")

    print(f"\nTHIS WEEK:")
    print(f"  Tokens: {report['this_week']['tokens']:,}")
    print(f"  Cost: ${report['this_week']['cost']:.2f}")

    print(f"\nTHIS MONTH:")
    print(f"  Tokens: {report['this_month']['tokens']:,}")
    print(f"  Cost: ${report['this_month']['cost']:.2f}")

    print(f"\nALL TIME:")
    print(f"  Tokens: {report['all_time']['tokens']:,}")
    print(f"  Cost: ${report['all_time']['cost']:.2f}")

    # Test estimate
    print("\n" + "=" * 50)
    print("COST ESTIMATES:")

    for num in [10, 50, 100]:
        estimate = monitor.estimate_cost(num)
        print(f"\n{num} articles:")
        print(f"  Tokens: {estimate['estimated_tokens']:,}")
        print(f"  Cost: ${estimate['total_cost']:.4f}")
        print(f"  Within limit: {estimate['within_limit']}")