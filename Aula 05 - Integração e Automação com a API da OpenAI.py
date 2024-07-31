from flask import Flask, request, jsonify
from openai import OpenAI
from docx import Document
import chardet
import json
import numpy
client = OpenAI(api_key='')
app = Flask(__name__)

def read_docx(file):
    document = Document(file)
    text = []
    for para in document.paragraphs:
        text.append(para.text)
    return '\n'.join(text)

def api_gpt(text_content):
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",  # Procure na documentação e teste com outros modelos
      response_format={ "type": "json_object" },
      messages=[
          {"role": "system", "content": "Você é especialista em extrair dados de contratos jurídicos. Para contratos de locação, preciso que me retorne os seguintes dados nesse formato: | NOME DO LOCADOR| DOCUMENTO DO LOCADOR | NOME DO LOCATÁRIO | DOCUMENTO DO LOCATÁRIO | ENDEREÇO DO IMÓVEL | VALOR DO ALUGUEL | no formato json."},
          {"role": "user", "content": f"Extraia as informações desse contrato {text_content}"}
          ],
      max_tokens=4_096)
    return jsonify(json.loads(response.choices[0].message.content))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files.get('file')
    if file.filename == '':
        return jsonify({"error": "Arquivo não selecionado"}), 400

    if file.filename.endswith('.docx'):
        text_content = read_docx(file)
        return api_gpt(text_content)
    else:
        try:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            text_content = raw_data.decode(encoding)
            return api_gpt(text_content)
        except UnicodeDecodeError:
            return jsonify({"error": "Erro de Encoding"}), 400

    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
