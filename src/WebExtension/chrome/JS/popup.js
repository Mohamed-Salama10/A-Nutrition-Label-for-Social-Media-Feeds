chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sendData") {
    const receivedData = request.data;

    console.log("Data received in the popup:", receivedData);
    const div = document.createElement("div");
    div.textContent = JSON.stringify(receivedData);
    document.body.appendChild(div);
  }
});
