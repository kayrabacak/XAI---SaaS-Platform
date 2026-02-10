import os
import io
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader

def test_pdf_generation():
    try:
        # Simulate the logic in main.py
        # Current logic:
        # env = Environment(loader=FileSystemLoader("templates"))
        
        # We need to run this from the same directory context as the app is likely running.
        # If running from backend/, cwd is backend/.
        
        print(f"Current Working Directory: {os.getcwd()}")
        
        # Try to find the templates directory as the app does
        if os.path.exists("templates"):
            print("Found 'templates' directory in CWD.")
        else:
            print("'templates' directory NOT found in CWD.")
            
        env = Environment(loader=FileSystemLoader("templates"))
        try:
            template = env.get_template("report.html")
            print("Template loaded successfully.")
        except Exception as e:
            print(f"Failed to load template: {e}")
            return

        # Dummy data
        html_content = template.render(
            task_id="test_task_123",
            date="01.01.2024 12:00",
            filename_model="model.pkl",
            filename_data="data.csv",
            ai_explanation="This is a test explanation.",
            feature_importance={"Feature A": 0.5, "Feature B": 0.3}
        )
        print("Template rendered successfully.")

        # HTML -> PDF
        pdf_file = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=pdf_file)

        if pisa_status.err:
            print("PDF generation failed.")
        else:
            print("PDF generated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_pdf_generation()
