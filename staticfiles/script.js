function collectData() {
  return {
    video_url: document.getElementById("url").value,
    filter_query: document.getElementById("filter").value,
    resolution: document.getElementById("resolution").value,
    cookies_text: document.getElementById("cookie").value,
    proxy_url: document.getElementById("proxy").value,
    service: document.getElementById("service").value
  };
}

function startDownload(url) {
  const a = document.createElement("a");
  a.href = url;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function showLoader(show) {
  document.getElementById("loader").style.display = show ? "block" : "none";
}

function showError(message) {
  const errorBlock = document.getElementById("error");
  errorBlock.innerText = message;
  errorBlock.style.display = message ? "block" : "none";
}

function renderInfoList(dataArray) {
  const listContainer = document.getElementById("info-list");
  listContainer.innerHTML = "";

  if (!Array.isArray(dataArray) || dataArray.length === 0) {
    listContainer.innerHTML = "<p>Нет данных для отображения</p>";
    return;
  }

  const ul = document.createElement("ul");

  dataArray.forEach((data) => {
    const li = document.createElement("li");

    let text = "";

    if (data.video_codec && data.resolution) {
      text = `${data.video_codec} • ${data.resolution} • ${(data.size)}Мб`;
    } else if (data.audio_codec) {
      text = `${data.audio_codec} • ${(data.size)}Мб`;
    } else {
      text = `${(data.size)}Мб`;
    }

    li.innerHTML = `<span>${text}</span><small>${data.title || "Без названия"}</small>`;

    li.onclick = () => startDownload(data.download_url);

    ul.appendChild(li);
  });

  listContainer.appendChild(ul);
}

async function getInfo() {
  showError("");
  showLoader(true);

  try {
    const data = collectData();
    console.log("Запрос информации:", data);

    const param = new URLSearchParams();
    if (data.filter_query === "only_audio") param.append("only_audio", "True");
    else if (data.filter_query === "only_video") param.append("only_video", "True");
    else if (data.filter_query === "progressive") param.append("progressive", "True");

    if (data.resolution) param.append("resolution", data.resolution);
    if (data.proxy_url) param.append("proxy_url", data.proxy_url);

    param.append("video_url", data.video_url);
    param.append("service_name", data.service);

    const res = await fetch(`http://127.0.0.1:8000/loader/all?${param.toString()}`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: data.cookies_text
    });

    if (!res.ok) {
      const json = await res.json();
      throw new Error(json.detail || "Ошибка запроса информации");
    }

    const json = await res.json();
    console.log(json);

    renderInfoList(json); // ← Новая функция рендера
  } catch (e) {
    console.error(e);
    showError(e.message);
  } finally {
    showLoader(false);
  }
}

async function getDirect() {
  showError("");
  showLoader(true);
  let arr = [];

  try {
    const data = collectData();
    console.log("Запрос информации:", data);

    const param = new URLSearchParams();



    if (data.proxy_url) param.append("proxy_url", data.proxy_url);

    param.append("video_url", data.video_url);
    param.append("service_name", data.service);

    const res = await fetch(`http://127.0.0.1:8000/loader/fastest?${param.toString()}`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: data.cookies_text
    });

    if (!res.ok) {
      const json = await res.json();
      throw new Error(json.detail || "Ошибка запроса информации");
    }

    const json = await res.json();
    arr = [json]
    console.log(json);

    renderInfoList(arr); // ← Новая функция рендера
  } catch (e) {
    console.error(e);
    showError(e.message);
  } finally {
    showLoader(false);
  }
}

async function downloadFile() {
    showError("");
  showLoader(true);
  try {
      const data = collectData();
  console.log("Запрос скачивания:", data);

  const param = new URLSearchParams();


  if (data.resolution !== "") {
      param.append("resolution", data.resolution)
  }
  if (data.proxy_url !== "") {
      param.append("proxy_url", data.proxy_url)
  }
  param.append("video_url", data.video_url)
  param.append("proxy_url", data.proxy_url)
  param.append("service_name", data.service)



  const res = await fetch(`http://127.0.0.1:8000/loader/download?${param.toString()}`, {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
      body: data.cookies_text

  });
  if (!res.ok) {
        const json = await res.json();
        console.log(json);
        return;
    }

    const blob = await res.blob(); // читаем как файл
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;

    a.download = "video.mp4";

    document.body.appendChild(a);
    a.click();
    a.remove();

    window.URL.revokeObjectURL(url);
  }
  catch (e) {
    console.error(e);
    showError(e.message);
  } finally {
    showLoader(false);
  }

}
