const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const list = document.querySelector("#todo-list");
const message = document.querySelector("#message");

function setMessage(text) {
  message.textContent = text || "";
}

async function requestJson(path, options) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail?.message || "요청을 처리하지 못했습니다.");
  }
  return body.data;
}

function render(todos) {
  list.innerHTML = "";
  if (todos.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "등록된 할 일이 없습니다.";
    list.appendChild(empty);
    return;
  }

  for (const todo of todos) {
    const item = document.createElement("li");
    item.className = todo.completed ? "done" : "";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

    const label = document.createElement("span");
    label.textContent = todo.text;

    const remove = document.createElement("button");
    remove.className = "delete";
    remove.type = "button";
    remove.textContent = "삭제";
    remove.addEventListener("click", () => deleteTodo(todo.id));

    item.append(checkbox, label, remove);
    list.appendChild(item);
  }
}

async function loadTodos() {
  try {
    render(await requestJson("/api/todos"));
    setMessage("");
  } catch (error) {
    setMessage(error.message);
  }
}

async function toggleTodo(id, completed) {
  try {
    await requestJson(`/api/todos/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    });
    await loadTodos();
  } catch (error) {
    setMessage(error.message);
  }
}

async function deleteTodo(id) {
  try {
    await requestJson(`/api/todos/${id}`, { method: "DELETE" });
    await loadTodos();
  } catch (error) {
    setMessage(error.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    setMessage("할 일을 입력하세요.");
    return;
  }

  try {
    await requestJson("/api/todos", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    input.value = "";
    await loadTodos();
  } catch (error) {
    setMessage(error.message);
  }
});

loadTodos();
