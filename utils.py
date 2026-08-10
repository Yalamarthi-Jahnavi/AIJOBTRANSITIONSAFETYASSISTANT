from datetime import datetime, timedelta

def calculate_notice_dates(resignation_date_str, notice_period_days):
    """
    Calculate expected last working day and employment gap based on notice period.
    """
    try:
        if not resignation_date_str:
            return None
            
        resignation_date = datetime.strptime(resignation_date_str, '%Y-%m-%d')
        try:
            days = int(notice_period_days)
        except (ValueError, TypeError):
            days = 0
            
        last_working_day = resignation_date + timedelta(days=days)
        
        return {
            'resignation_date': resignation_date.strftime('%d %b %Y'),
            'notice_period_days': days,
            'last_working_day': last_working_day.strftime('%d %b %Y'),
            'last_working_day_date': last_working_day
        }
    except Exception as e:
        print(f"Date calculation error: {e}")
        return None

def calculate_employment_gap(last_working_day_date, joining_date_str):
    """
    Calculate gap between last working day and new joining date.
    """
    try:
        if not joining_date_str or not last_working_day_date:
            return None
            
        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d')
        gap = (joining_date - last_working_day_date).days
        
        return {
            'joining_date': joining_date.strftime('%d %b %Y'),
            'gap_days': gap
        }
    except Exception as e:
        print(f"Gap calculation error: {e}")
        return None
