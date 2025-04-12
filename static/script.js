document.getElementById("classifyButton").addEventListener("click", async () => {
    const emailInput = document.getElementById("emailInput").value;
    const resultElement = document.getElementById("result");


    try {
        const response = await fetch("/classify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: emailInput }),
        });
        const data = await response.json();
        
        if (data.error) {
            resultElement.textContent = data.error;
            resultElement.className = 'error';
        } else {
            resultElement.textContent = `Prediction: ${data.classification}`;
            if (data.classification === "Spam") {
                resultElement.className = 'spam';
            } else {
                resultElement.className = 'ham';
            }
        }
    } catch (error) {
        resultElement.textContent = "Error connecting to the server.";
        resultElement.className = 'error';
    }
});
