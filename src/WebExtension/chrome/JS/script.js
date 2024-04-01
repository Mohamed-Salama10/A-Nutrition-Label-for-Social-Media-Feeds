let signinButton = document.getElementById("signin-button");
let loginWindow = document.getElementById("login-window");
let closeButtonLogin = document.getElementById("close-button-login");
let mainWindow = document.getElementById("main-window");
let additionalWindow = document.getElementById("additional-window");
let additionalInfoButton = document.getElementById("View-Infographics-button");
let backArrowAdditional = document.getElementById("back-arrow-additional");
let closeButtonAdditional = document.getElementById("close-button-additional");
let frontArrowMain = document.getElementById("front-arrow-main");
let closeButtonMain = document.getElementById("close-button-main");

const getLabels = async () => {
  try {
    const response = await fetch(
      `../JS/data.json`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjVjMjlmNTI0YTExMzBjMTcxZGIyYmUyIn0.rWgmjH3VpEKZBQ2gfXGj3uJQ9zdxMIBa-kgC6qMz0kY`,
        },
      }
    );
    const data = await response.json();

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular Labels") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 4); i++) {
          const label = keys[i];
          const elementId = `n${i + 1}-text`;
          document.getElementById(elementId).textContent = keys[i];

          const percentage = (data[category][label] * 100).toFixed(2) + "%";
          const perId = `n${i + 1}-per`;
          document.getElementById(perId).textContent =
            (data[category][label] * 100).toFixed(2) + "%";

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${label}, Percentage: ${percentage}`
          );
        }
      }
    }

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular Moods") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 3); i++) {
          const label = keys[i];
          const elementId = `n${i + 1}-m`;
          document.getElementById(elementId).textContent = keys[i];

          const percentage = (data[category][label] * 100).toFixed(2) + "%";
          const perId = `n${i + 1}-mper`;
          document.getElementById(perId).textContent =
            (data[category][label] * 100).toFixed(2) + "%";

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${label}, Percentage: ${percentage}`
          );
        }
      }
    }

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular purpose") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 3); i++) {
          const label = keys[i];
          const elementId = `n${i + 1}-p`;
          document.getElementById(elementId).textContent = keys[i];

          const percentage = (data[category][label] * 100).toFixed(2) + "%";
          const perId = `n${i + 1}-pper`;
          document.getElementById(perId).textContent =
            (data[category][label] * 100).toFixed(2) + "%";

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${label}, Percentage: ${percentage}`
          );
        }
      }
    }
  } catch (error) {
    console.error("Error fetching or parsing JSON:", error);
  }
};

const getCharts = async () => {
  try {
    const response = await fetch(
      `../JS/data.json`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjVjMjlmNTI0YTExMzBjMTcxZGIyYmUyIn0.rWgmjH3VpEKZBQ2gfXGj3uJQ9zdxMIBa-kgC6qMz0kY`,
        },
      }
    );
    const data = await response.json();

    const PopularTopics = [];
    const Moods = [];
    const Purposes = [];

    const chart1_data = [];
    const chart2_data = [];
    const chart3_data = [];

    const chart1 = document.getElementById("Ptopics-chart").getContext("2d");
    const chart2 = document.getElementById("Moods-chart").getContext("2d");
    const chart3 = document.getElementById("Purposes-chart").getContext("2d");

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular Labels") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 10); i++) {
          const label = keys[i];
          PopularTopics.push(label);

          const percentage = (data[category][label] * 100).toFixed(2);
          chart1_data.push(percentage);

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${PopularTopics}, Percentage: ${chart1_data}`
          );
        }
      }
    }

    new Chart(chart1, {
      type: "polarArea",
      data: {
        labels: PopularTopics,
        datasets: [
          {
            data: chart1_data,
          },
        ],
      },
      options: {
        scale: {
          ticks: {
            beginAtZero: true,
            max: Math.max(...chart1_data) + 10,
            fontColor: "#FFFFFF", //'#333'
          },
          pointLabels: {
            fontSize: 10,
            fontColor: "#FFFFFF", //'#333'
          },
        },
        elements: {
          line: {
            tension: 0, // Disable bezier curves
          },
        },
      },
    });

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular Moods") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 10); i++) {
          const label = keys[i];
          Moods.push(label);

          const percentage = (data[category][label] * 100).toFixed(2);
          chart2_data.push(percentage);

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${PopularTopics}, Percentage: ${chart2_data}`
          );
        }
      }
    }

    new Chart(chart2, {
      type: "polarArea",
      data: {
        labels: Moods,
        datasets: [
          {
            data: chart2_data,
          },
        ],
      },
      options: {
        scale: {
          ticks: {
            beginAtZero: true,
            max: Math.max(...chart2_data) + 10,
            fontColor: "#FFFFFF", //'#333'
          },
          pointLabels: {
            fontSize: 10,
            fontColor: "#FFFFFF", //'#333'
          },
        },
        elements: {
          line: {
            tension: 0, // Disable bezier curves
          },
        },
      },
    });

    for (const category in data) {
      if (data.hasOwnProperty(category) && category === "Popular purpose") {
        const keys = Object.keys(data[category]);

        for (let i = 0; i < Math.min(keys.length, 4); i++) {
          const label = keys[i];
          Purposes.push(label);

          const percentage = (data[category][label] * 100).toFixed(2);
          chart3_data.push(percentage);

          // Use category, label, and percentage as needed
          console.log(
            `Category: ${category}, Label: ${PopularTopics}, Percentage: ${chart2_data}`
          );
        }
      }
    }

    new Chart(chart3, {
      type: "polarArea",
      data: {
        labels: Purposes,
        datasets: [
          {
            data: chart3_data,
          },
        ],
      },
      options: {
        scale: {
          ticks: {
            beginAtZero: true,
            max: Math.max(...chart3_data) + 10,
            fontColor: "#FFFFFF", //'#333'
          },
          pointLabels: {
            fontSize: 14,
            fontColor: "#FFFFFF", //'#333'
          },
        },
        elements: {
          line: {
            tension: 0, // Disable bezier curves
          },
        },
      },
    });
  } catch (error) {
    console.error("Error fetching or parsing JSON:", error);
  }
};

function signInPressed() {
  loginWindow.hidden = true;
  mainWindow.hidden = false;
  document.addEventListener("DOMContentLoaded", getLabels);
}

closeButtonLogin.addEventListener("click", function () {
  close();
});

function additionalPressed() {
  mainWindow.hidden = true;
  additionalWindow.hidden = false;
}

function backFromAdditional() {
  mainWindow.hidden = false;
  additionalWindow.hidden = true;
  document.addEventListener("DOMContentLoaded", getLabels);
}

signinButton.addEventListener("click", function () {
  loginWindow.hidden = true;
  mainWindow.hidden = false;
  additionalWindow.hidden = true;
  getLabels();
});

additionalInfoButton.addEventListener("click", function () {
  loginWindow.hidden = true;
  mainWindow.hidden = true;
  additionalWindow.hidden = false;
  getCharts();
});

backArrowAdditional.addEventListener("click", function () {
  loginWindow.hidden = true;
  mainWindow.hidden = false;
  additionalWindow.hidden = true;
  getLabels();
});

frontArrowMain.addEventListener("click", function () {
  loginWindow.hidden = true;
  mainWindow.hidden = true;
  additionalWindow.hidden = false;
  getLabels();
});

closeButtonAdditional.addEventListener("click", function () {
  close();
});

closeButtonMain.addEventListener("click", function () {
  close();
});

loginWindow.hidden = false;
mainWindow.hidden = true;
additionalWindow.hidden = true;
