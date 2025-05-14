from flask import Flask, request
import openai
import os

app = Flask(__name__)

# Inicializa o cliente da OpenAI com a chave da variável de ambiente
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    user_message = request.form.get("Body")

    prompt = f"""
    Você é o BetBot IA, um especialista em futebol, estatísticas e apostas esportivas. 
    Responda apenas sobre futebol. Nunca fale de temas fora desse universo.

    Mensagem recebida: "{user_message}"

    Dê uma resposta clara com:
    - Palpite principal
    - 3 a 5 sugestões com estrelas de confiança (de 1 a 5)
    - Placar provável (se aplicável)
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é o BetBot IA, especialista em futebol e apostas."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
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
