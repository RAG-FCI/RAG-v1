document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        addMessage("Bem-vindo ao RAG-FCI, o que você quer saber?", "bot");
    }, 500);
});

const sendButton = document.getElementById("send-button");
const inputField = document.getElementById("user-input");
const BASE_URL = "https://rag-fci.onrender.com/"; // Alterar para o domínio do deploy depois

sendButton.addEventListener("click", sendMessage);
inputField.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
    const userInput = inputField.value.trim();

    if (userInput) {
        // Adiciona a mensagem do usuário
        addMessage(userInput, "user");

        // Limpa o campo de entrada e desativa o botão enquanto processa
        inputField.value = '';
        toggleInputState(true);

    try {
        // Chama a API para gerar a resposta do bot
        const response = await generateBotResponse(userInput);
        addMessage(response, "bot"); // Adiciona a resposta do bot ao chat
    } catch (error) {
        console.log(error); // Para depuração adicional
        addMessage(`Erro: ${error}`, "bot"); // Exibe o erro no chat
    } finally {
        toggleInputState(false); // Reativa o botão e o campo de entrada
    }
    }
}

function addMessage(message, sender) {
    const chatBox = document.getElementById("chat-box");
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("message-container", sender === "user" ? "user-container" : "bot-container");

    const messageBubble = document.createElement("div");
    messageBubble.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageBubble.textContent = message;

    messageContainer.appendChild(messageBubble);
    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight; // Rola para o final do chat
}

function toggleInputState(isDisabled) {
    sendButton.disabled = isDisabled;
    inputField.disabled = isDisabled;
}

async function generateBotResponse(input) {
    try {
        const response = await fetch(`${BASE_URL}/ragfci`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: input }),
        });

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data.resposta; // Retorna a resposta da API
    } catch (error) {
        throw new Error('Erro ao processar o prompt: ' + error.message);
    }
}
