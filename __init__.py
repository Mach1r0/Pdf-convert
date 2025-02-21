import os
from flask import Flask, request, jsonify
from fpdf import FPDF

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
        
    @app.route('/pdfConverter', methods=['POST'])
    def pdf_converter():
        data = request.get_json()
        app.logger.info(f"Received data: {data}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        if 'name' in data:
            pdf_name = data['name']
            app.logger.info(f"PDF name set to: {pdf_name}")
        else:
            pdf_name = 'output'
            app.logger.info("PDF name set to default: output")

        for key, value in data.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

        output_path = os.path.join(app.root_path, 'files', 'output', f'{pdf_name}.pdf')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        app.logger.info(f"PDF saved to: {output_path}")

        return jsonify({"message": "PDF created successfully", "output": output_path})

    return app