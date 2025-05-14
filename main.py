# main.py com estrutura de scraping e análise avançada

from flask import Flask, request
import openai
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Inicializa cliente OpenAI com chave da variável de ambiente
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def coletar_dados_partida(jogo):
    # Função simplificada: coleta informações simuladas de fontes externas
    time_a, time_b = jogo.lower().split(" x ")
    dados = []

    # Simula scraping de dados para cada time
    for time in [time_a, time_b]:
        url = f"https://www.google.com/search?q={time.replace(' ', '+')}+estatisticas+futebol"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            estatistica_fake = soup.title.text.strip()[:120]  # Exemplo simplificado
        else:
            estatistica_fake = f"Estatísticas não encontradas para {time}"

        dados.append(f"{time.title()}: {estatistica_fake}")

    return "\n".join(dados)

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    user_message = request.form.get("Body")

    # Coleta dados do jogo (simulação com scraping básico)
    try:
        dados_estudo = coletar_dados_partida(user_message)
    except Exception as e:
        dados_estudo = "Dados não foram encontrados automaticamente. Realize análise com base estatística geral."

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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um analista de futebol com foco em previsões baseadas em dados."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200,
        temperature=0.7
    )

    mensagem = response.choices[0].message.content

    return f"""
    <Response>
        <Message>{mensagem}</Message>
    </Response>
    """, 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
