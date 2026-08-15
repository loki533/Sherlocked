import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

class ReportGenerator:
    @staticmethod
    def generate(case):
        # 1. Dynamically find the absolute path to your 'templates' folder
        base_dir = Path(__file__).resolve().parent.parent
        template_dir = base_dir / "templates"
        
        # 2. Pass that absolute path string to Jinja2
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        template = env.get_template("report_template.html")
        html = template.render(case=case)
        
        output = REPORT_DIR / f"{case.case_id}_report.html"
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
            
        return output