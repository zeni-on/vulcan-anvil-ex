const app = document.querySelector("#app");
const tokenKey = "boardSampleToken";
let cachedUser = null;

const routes = {
  signup: /^\/signup\/?$/,
  login: /^\/login\/?$/,
  posts: /^\/(?:posts)?\/?$/,
  newPost: /^\/posts\/new\/?$/,
  detail: /^\/posts\/(\d+)\/?$/,
  edit: /^\/posts\/(\d+)\/edit\/?$/,
};

function token() {
  return localStorage.getItem(tokenKey);
}

function setToken(value) {
  localStorage.setItem(tokenKey, value);
  cachedUser = null;
  updateNav();
}

function clearToken() {
  localStorage.removeItem(tokenKey);
  cachedUser = null;
  updateNav();
}

function updateNav() {
  const signedIn = Boolean(token());
  document.querySelectorAll("[data-auth-link]").forEach((node) => {
    node.hidden = !signedIn;
  });
  document.querySelectorAll("[data-guest-link]").forEach((node) => {
    node.hidden = signedIn;
  });
  document.querySelector("[data-logout]").hidden = !signedIn;
}

function shell(eyebrow, title) {
  const template = document.querySelector("#page-shell");
  const node = template.content.cloneNode(true);
  node.querySelector(".eyebrow").textContent = eyebrow;
  node.querySelector("h1").textContent = title;
  app.replaceChildren(node);
  return app.querySelector(".panel-body");
}

function messageNode() {
  const node = document.createElement("p");
  node.className = "message";
  node.setAttribute("role", "status");
  return node;
}

function setMessage(node, text, type = "") {
  node.className = `message ${type}`.trim();
  node.textContent = text;
}

async function api(path, options = {}) {
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (token()) {
    headers.Authorization = `Bearer ${token()}`;
  }
  const response = await fetch(path, {...options, headers});
  const body = await response.json();
  if (!response.ok) {
    const error = new Error(body.error?.message || "요청을 처리할 수 없습니다.");
    error.code = body.error?.code || "ERR-007";
    throw error;
  }
  return body.data;
}

async function currentUser() {
  if (!token()) return null;
  if (cachedUser) return cachedUser;
  try {
    cachedUser = await api("/api/auth/me");
    return cachedUser;
  } catch {
    clearToken();
    return null;
  }
}

function formField(labelText, name, type = "text") {
  const field = document.createElement("div");
  field.className = "field";
  const label = document.createElement("label");
  label.htmlFor = name;
  label.textContent = labelText;
  const input = type === "textarea" ? document.createElement("textarea") : document.createElement("input");
  input.id = name;
  input.name = name;
  if (type !== "textarea") input.type = type;
  input.required = true;
  field.append(label, input);
  return {field, input};
}

function submitButton(text) {
  const button = document.createElement("button");
  button.className = "button";
  button.type = "submit";
  button.textContent = text;
  return button;
}

function renderSignup() {
  const body = shell("SCR-001", "회원가입");
  const form = document.createElement("form");
  form.className = "form";
  const email = formField("이메일", "email", "email");
  const password = formField("비밀번호", "password", "password");
  const userName = formField("이름", "user_name");
  password.input.minLength = 8;
  const status = messageNode();
  form.append(email.field, password.field, userName.field, submitButton("가입"), status);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          email: email.input.value,
          password: password.input.value,
          user_name: userName.input.value,
        }),
      });
      setMessage(status, "정상 처리되었습니다.", "success");
      history.pushState(null, "", "/login");
      render();
    } catch (error) {
      setMessage(status, `${error.code}: ${error.message}`, "error");
    }
  });
  body.append(form);
}

function renderLogin() {
  const body = shell("SCR-002", "로그인");
  const form = document.createElement("form");
  form.className = "form";
  const email = formField("이메일", "email", "email");
  const password = formField("비밀번호", "password", "password");
  const status = messageNode();
  form.append(email.field, password.field, submitButton("로그인"), status);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({email: email.input.value, password: password.input.value}),
      });
      setToken(data.access_token);
      history.pushState(null, "", "/posts");
      render();
    } catch (error) {
      setMessage(status, `${error.code}: ${error.message}`, "error");
    }
  });
  body.append(form);
}

async function renderPosts() {
  const body = shell("SCR-003", "게시글 목록");
  const actions = document.createElement("div");
  actions.className = "actions";
  if (token()) {
    const newLink = document.createElement("a");
    newLink.className = "button";
    newLink.href = "/posts/new";
    newLink.textContent = "글쓰기";
    actions.append(newLink);
  }
  const list = document.createElement("div");
  list.className = "post-list";
  body.append(actions, list);
  const posts = await api("/api/posts");
  if (posts.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "등록된 게시글이 없습니다.";
    list.append(empty);
    return;
  }
  posts.forEach((post) => {
    const item = document.createElement("article");
    item.className = "post-item";
    item.innerHTML = `<h2><a href="/posts/${post.id}"></a></h2><p class="meta"></p>`;
    item.querySelector("a").textContent = post.title;
    item.querySelector(".meta").textContent = `작성자 #${post.author_id}`;
    list.append(item);
  });
}

async function renderDetail(postId) {
  const body = shell("SCR-004", "게시글 상세");
  const post = await api(`/api/posts/${postId}`);
  const user = await currentUser();
  const detail = document.createElement("div");
  detail.className = "detail";
  detail.innerHTML = `
    <h2></h2>
    <p class="meta"></p>
    <div class="content"></div>
    <div class="actions"></div>
  `;
  detail.querySelector("h2").textContent = post.title;
  detail.querySelector(".meta").textContent = `작성자 #${post.author_id}`;
  detail.querySelector(".content").textContent = post.content;
  const actions = detail.querySelector(".actions");
  const back = document.createElement("a");
  back.className = "button secondary";
  back.href = "/posts";
  back.textContent = "목록";
  actions.append(back);
  if (user && user.id === post.author_id) {
    const edit = document.createElement("a");
    edit.className = "button";
    edit.href = `/posts/${post.id}/edit`;
    edit.textContent = "수정";
    const remove = document.createElement("button");
    remove.className = "button danger";
    remove.type = "button";
    remove.textContent = "삭제";
    remove.addEventListener("click", async () => {
      await api(`/api/posts/${post.id}`, {method: "DELETE"});
      history.pushState(null, "", "/posts");
      render();
    });
    actions.append(edit, remove);
  }
  body.append(detail);
}

async function postForm({postId = null} = {}) {
  if (!token()) {
    history.replaceState(null, "", "/login");
    render();
    return;
  }
  const isEdit = Boolean(postId);
  const body = shell(isEdit ? "SCR-006" : "SCR-005", isEdit ? "게시글 수정" : "게시글 작성");
  const form = document.createElement("form");
  form.className = "form";
  const title = formField("제목", "title");
  const content = formField("본문", "content", "textarea");
  const status = messageNode();
  if (isEdit) {
    const post = await api(`/api/posts/${postId}`);
    title.input.value = post.title;
    content.input.value = post.content;
  }
  form.append(title.field, content.field, submitButton(isEdit ? "수정" : "저장"), status);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const saved = await api(isEdit ? `/api/posts/${postId}` : "/api/posts", {
        method: isEdit ? "PUT" : "POST",
        body: JSON.stringify({title: title.input.value, content: content.input.value}),
      });
      history.pushState(null, "", `/posts/${saved.id}`);
      render();
    } catch (error) {
      setMessage(status, `${error.code}: ${error.message}`, "error");
    }
  });
  body.append(form);
}

async function render() {
  updateNav();
  const path = window.location.pathname;
  try {
    if (routes.signup.test(path)) return renderSignup();
    if (routes.login.test(path)) return renderLogin();
    if (routes.newPost.test(path)) return postForm();
    const edit = path.match(routes.edit);
    if (edit) return postForm({postId: edit[1]});
    const detail = path.match(routes.detail);
    if (detail) return renderDetail(detail[1]);
    return renderPosts();
  } catch (error) {
    const body = shell("오류", "요청을 처리할 수 없습니다.");
    const status = messageNode();
    setMessage(status, `${error.code || "ERR-007"}: ${error.message}`, "error");
    body.append(status);
  }
}

document.querySelector("[data-logout]").addEventListener("click", () => {
  clearToken();
  history.pushState(null, "", "/login");
  render();
});

window.addEventListener("popstate", render);
document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href^='/']");
  if (!link) return;
  event.preventDefault();
  history.pushState(null, "", link.getAttribute("href"));
  render();
});

render();
