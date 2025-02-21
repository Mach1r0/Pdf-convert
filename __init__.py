import os
import base64
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

        output_path = os.path.join(app.root_path, 'files', 'output', f'{pdf_name}_generated.pdf')

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        app.logger.info(f"PDF saved to: {output_path}")

        return jsonify({"message": "PDF created successfully", "output": output_path})

    @app.route('/pdfToBase64', methods=['POST'])
    def pdf_to_base64():
        data = request.get_json()
        pdf_name = data.get('name', 'output')
        
        possible_paths = [
            os.path.join(app.root_path, 'files', 'output', f'{pdf_name}.pdf'),
            os.path.join(app.root_path, 'files', 'output', pdf_name),
            os.path.join(app.root_path, 'files', 'output', f'{pdf_name}_generated.pdf')
        ]
        
        pdf_path = None
        for path in possible_paths:
            app.logger.info(f"Checking if PDF exists at: {path}")
            if os.path.exists(path):
                pdf_path = path
                app.logger.info(f"PDF found at: {pdf_path}")
                
                base64_path = os.path.splitext(pdf_path)[0] + "_base64.txt"
                if os.path.exists(base64_path):
                    app.logger.info(f"Base64 file already exists at: {base64_path}")
                    try:
                        with open(base64_path, "r") as base64_file:
                            encoded_string = base64_file.read()
                        return jsonify({
                            "name": pdf_name,
                            "base64": encoded_string,
                            "pdf_path": pdf_path,
                            "base64_path": base64_path,
                            "source": "cached"
                        })
                    except Exception as e:
                        app.logger.warning(f"Error reading existing base64 file, will regenerate: {str(e)}")
                break
        
        if pdf_path is None:
            pdf_path = possible_paths[0]  
            app.logger.info(f"PDF not found, creating new PDF at: {pdf_path}")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            for key, value in data.items():
                if key != 'name':
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            pdf.output(pdf_path)
            app.logger.info(f"PDF created and saved to: {pdf_path}")
        
        try:
            with open(pdf_path, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
                app.logger.info(f"Successfully converted PDF to base64")
                
                base64_path = os.path.splitext(pdf_path)[0] + "_base64.txt"
                with open(base64_path, "w") as base64_file:
                    base64_file.write(encoded_string)
                    
                app.logger.info(f"Base64 saved to: {base64_path}")
                
                return jsonify({
                    "name": pdf_name, 
                    "base64": encoded_string,
                    "pdf_path": pdf_path,
                    "base64_path": base64_path,
                    "source": "generated"
                })
        except Exception as e:
            app.logger.error(f"Error processing PDF: {str(e)}")
            return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500
    
    return app