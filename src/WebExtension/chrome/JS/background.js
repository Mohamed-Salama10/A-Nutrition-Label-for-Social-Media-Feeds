chrome.runtime.onMessage.addListener(async function (
  request,
  sender,
  sendResponse
) {
  if (request.action === "makeRequest") {
    const res = await fetch(`http://127.0.0.1:8000/nutri/createNutrition`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjVjMjlmNTI0YTExMzBjMTcxZGIyYmUyIn0.rWgmjH3VpEKZBQ2gfXGj3uJQ9zdxMIBa-kgC6qMz0kY`,
      },
      body: JSON.stringify({
        url: request.data,
      }),
    });

    const data = await res.json();
    console.log(data.hasOwnProperty("id"));
    if (data.hasOwnProperty("id")) {
      await fetch("http://127.0.0.1:8000/nutri/updatePostTime", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjVjMjlmNTI0YTExMzBjMTcxZGIyYmUyIn0.rWgmjH3VpEKZBQ2gfXGj3uJQ9zdxMIBa-kgC6qMz0kY`,
        },
        body: JSON.stringify({
          url: request.data,
          time: data.time_spent_on_post + 1.5,
        }),
      });
    }
  }
  if (request.action === "sendStats") {
    const { platform, timeSpent, scrollDistance } = request.data;
    const requests = await fetch(
      `http://127.0.0.1:8000/user/addrPlatformInfo?platform=${platform}&timeSpent=${timeSpent}&scrollDistance=${scrollDistance}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjVjMjlmNTI0YTExMzBjMTcxZGIyYmUyIn0.rWgmjH3VpEKZBQ2gfXGj3uJQ9zdxMIBa-kgC6qMz0kY`,
        },
        body: JSON.stringify({
          url: request.data,
        }),
      }
    );
  }
});
