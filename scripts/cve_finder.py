from . import scanner
from datetime import datetime
from alerts.models import CVEScans
from alerts.models import NewsArticles

def daily():
  print("CVE Finder daily running...")
  start_time = datetime.now().strftime("%H:%M:%S")
  scanner.NewCveTracker().daily_cve("pub")
  news = scanner.NewsScanner().main()
  end_time = datetime.now().strftime("%H:%M:%S")
  scan_type = "daily"
  cve_data = CVEScans(scan_type=scan_type, scan_start=start_time, scan_end=end_time)
  cve_data.save()

def weekly():
  start_time = datetime.now().strftime("%H:%M:%S")
  scanner.NewCveTracker().last_week_cve("pub")
  end_time = datetime.now().strftime("%H:%M:%S")
  scan_type = "weekly"
  insert_data = CVEScans(scan_type=scan_type, scan_start=start_time, scan_end=end_time)
  insert_data.save()