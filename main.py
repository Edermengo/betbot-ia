from flask import Flask, request, jsonify
import openai
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Inicializa cliente OpenAI com chave da variável de ambiente
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("A variável de ambiente 'OPENAI_API_KEY' não está configurada.")
    
openai.api_key = openai_api_key

def coletar_dados_partida(jogo):
    """
    Função que coleta informações simuladas de fontes externas sobre os times do jogo fornecido.
    """
    try:
        time_a, time_b = [time.strip() for time in jogo.lower().split(" x ")]
    except ValueError:
        raise ValueError("Formato inválido para o jogo. Use o formato 'Time A x Time B'.")
    
    dados = []

    # Simula scraping de dados para cada time
    for time in [time_a, time_b]:
        url = f"https://www.google.com/search?q={time.replace(' ', '+')}+estatisticas+futebol"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=5)
            r.raise_for_status()  # Levanta uma exceção para status de erro HTTP
        except requests.RequestException:
            estatistica_fake = f"Estatísticas não encontradas para {time}"
        else:
            soup = BeautifulSoup(r.text, "html.parser")
            estatistica_fake = soup.title.text.strip()[:120] if soup.title else f"Estatísticas não disponíveis para {time}"

        dados.append(f"{time.title()}: {estatistica_fake}")

    return "\n".join(dados)

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    """
    Endpoint para webhook do WhatsApp.
    Recebe uma mensagem do usuário e retorna uma análise com sugestões de apostas.
    """
    user_message = request.form.get("Body")
    if not user_message:
        return jsonify({"error": "Nenhuma mensagem fornecida."}), 400

    # Coleta dados do jogo
    try:
        dados_estudo = coletar_dados_partida(user_message)
    except Exception as e:
        dados_estudo = f"Erro ao coletar dados do jogo: {str(e)}. Realize análise com base estatística geral."

    prompt = f"""
Você é o BetBot IA, um analista de futebol de elite. Utilize os dados abaixo para fazer uma análise tática do jogo informado.

JOGO: {user_message}

DADOS ESTATÍSTICOS REAIS:
{dados_estudo}

Regras:
- Use linguagem clara, objetiva e com justificativas técnicas
- Dê 3 a 5 sugestões de apostas com estrelas de confiança (de 1 a 5)
- Finalize com placar provável

Gere a análise:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista de futebol com foco em previsões baseadas em dados."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        mensagem = response['choices'][0]['message']['content']
    except Exception as e:
        mensagem = f"Erro ao gerar análise com o modelo OpenAI: {str(e)}"

    # Retorna resposta no formato XML compatível com WhatsApp
    return f"""
    <Response>
        <Message>{mensagem}</Message>
    </Response>
    """, 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
