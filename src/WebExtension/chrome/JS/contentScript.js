const postElements = document.body.querySelectorAll(
  ".x78zum5.xdt5ytf.x5yr21d.xa1mljc.xh8yej3.x1bs97v6.x1q0q8m5.xso031l.x11aubdm.xnc8uc2"
);
var distanceInMeters;
let lastTime = 0;
const visiblePost = new Set();

const interactionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.intersectionRatio >= 0.7) {
        const image = entry.target.getElementsByTagName("img")[1].src;
        setInterval(() => {
          chrome.runtime.sendMessage({
            action: "makeRequest",
            data: image,
          });
        }, 1500);
      }
    });
  },
  { threshold: 0.7 }
);

const handleMutation = (mutationsList, observer) => {
  mutationsList.forEach((mutation) => {
    if (mutation.type === "childList") {
      const addedImages = Array.from(mutation.addedNodes).filter(
        (node) => node.tagName === "ARTICLE"
      );

      if (addedImages.length > 0) {
        addedImages.forEach((addedImage) => {
          setTimeout(() => {
            const imgSrc = addedImage.getAttribute("src");
            interactionObserver.observe(addedImage);
          }, 100);
        });
      }
    }
  });
};

const observerConfig = {
  attributes: true,
  childList: true,
  subtree: true,
};

postElements.forEach((div) => {
  interactionObserver.observe(div);
});

const observer = new MutationObserver(handleMutation);
postElements.forEach((div) => {
  observer.observe(div, observerConfig);
});

observer.observe(document.body, observerConfig);

// Timer for tracking user's stay on the page
let startTime;

function startTimer() {
  startTime = new Date();
}

function stopTimer() {
  const endTime = new Date();
  const elapsedTime = endTime - startTime;
  const seconds = Math.floor(elapsedTime / 1000);

  localStorage.setItem("userStayTime", seconds);
  const dataToSend = {
    platform: "Instagram",
    timeSpent: seconds,
    scrollDistance: distanceInMeters,
  };
  chrome.runtime.sendMessage({
    action: "sendStats",
    data: dataToSend,
  });
}

// Start the timer when the page loads
startTimer();

// Attach an event listener for beforeunload to stop the timer when the user leaves the page
function pixelsToMeters(pixels) {
  // Assuming a standard screen size of 96 pixels per inch
  const pixelsPerInch = 96;

  // Convert pixels to inches
  const inches = pixels / pixelsPerInch;

  // Assuming 0.0254 meters per inch
  const meters = inches * 0.0254;

  return meters;
}

// Event listener to track scrolling
window.addEventListener("scroll", () => {
  distanceInMeters = pixelsToMeters(window.scrollY);
});
window.addEventListener("beforeunload", stopTimer);
