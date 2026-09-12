"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { user: null, users: [], requests: [], selected: null, detail: null,
    epoch: 0, listTicket: 0, detailTicket: 0, pending: false, switching: false, loading: false };
  const statuses = { submitted: "검토 대기", rejected: "반려", approved: "승인" };
  const identities = new BroadcastChannel("request-board-demo-identity");
  identities.onmessage = () => initialize();
  const sameId = (a, b) => a != null && b != null && String(a) === String(b);
  const icons = () => { if (window.lucide) window.lucide.createIcons(); };
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function badge(status) {
    return element("span", `badge ${Object.hasOwn(statuses, status) ? status : ""}`, statuses[status] || "알 수 없음");
  }
  function button(label, icon, className = "") {
    const node = element("button", className);
    node.type = "submit";
    node.title = label;
    const glyph = element("i");
    glyph.dataset.lucide = icon;
    glyph.setAttribute("aria-hidden", "true");
    node.append(glyph, element("span", "", label));
    return node;
  }
  function error(target, message = "") {
    target.textContent = message;
    target.hidden = !message;
  }
  function notice(message = "") { $("notice").textContent = message; }
  async function api(path, body) {
    const response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      credentials: "same-origin", cache: "no-store",
      headers: { Accept: "application/json", ...(state.user ? { "X-Demo-User": state.user.id } : {}),
        ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
      ...(body === undefined ? {} : { body: JSON.stringify(body) })
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const failure = new Error(data?.error?.message || `요청을 처리하지 못했습니다. (${response.status})`);
      failure.status = response.status;
      failure.code = data?.error?.code;
      throw failure;
    }
    if (data === null) throw new Error("서버 응답을 읽을 수 없습니다. 다시 시도해 주세요.");
    return data;
  }
  function message(failure) {
    return failure instanceof TypeError ? "서버에 연결할 수 없습니다. 연결을 확인하고 다시 시도해 주세요." : failure.message;
  }
  function controls() {
    const busy = state.pending || state.switching;
    $("identity").disabled = busy || !state.users.length;
    $("refresh").disabled = busy || state.loading;
    $("status-filter").disabled = busy || state.loading || !state.user;
    document.querySelectorAll("#create-form button, #create-form textarea, #detail form button, #detail form textarea, .request-item")
      .forEach((node) => { node.disabled = busy || !state.user || (state.loading && node.classList.contains("request-item")); });
    $("create-form").setAttribute("aria-busy", String(state.pending));
  }
  function clearView() {
    state.requests = [];
    state.selected = null;
    state.detail = null;
    state.listTicket++;
    state.detailTicket++;
    state.loading = false;
    $("create-form").reset();
    $("content-count").textContent = "0 / 4,000";
    error($("create-error"));
    error($("app-error"));
    notice();
    $("request-list").replaceChildren();
    $("request-list").setAttribute("aria-busy", "false");
    $("request-count").textContent = "0";
    $("detail").replaceChildren();
    $("detail-panel").setAttribute("aria-busy", "false");
    $("create-section").hidden = true;
    $("list-state").hidden = false;
    $("list-state").textContent = "테스트 계정을 선택해 주세요.";
    $("detail-state").hidden = false;
    $("detail-state").textContent = "테스트 계정을 선택해 주세요.";
  }
  function renderList() {
    $("request-count").textContent = String(state.requests.length);
    $("request-list").replaceChildren();
    $("list-state").hidden = state.requests.length > 0;
    $("list-state").textContent = "표시할 요청이 없습니다.";
    state.requests.forEach((request) => {
      const item = element("li");
      const select = element("button", "request-item");
      select.type = "button";
      select.dataset.requestId = String(request.id);
      select.setAttribute("aria-current", String(sameId(request.id, state.selected)));
      const top = element("div", "request-top");
      top.append(element("span", "request-id", `요청 #${request.id}`), badge(request.status));
      select.append(top, element("div", "request-preview", request.content), element("div", "metadata", `작성자 ${request.owner.name}`));
      select.addEventListener("click", () => { if (!state.pending && !state.switching && !state.loading) selectRequest(request.id); });
      item.append(select);
      $("request-list").append(item);
    });
    controls();
  }
  async function refresh(preferred = state.selected) {
    if (!state.user) return;
    const epoch = state.epoch;
    const ticket = ++state.listTicket;
    state.detailTicket++;
    state.detail = null;
    $("detail").replaceChildren();
    $("detail-state").hidden = false;
    $("detail-state").textContent = "상세 내용을 불러오는 중…";
    $("detail-panel").setAttribute("aria-busy", "false");
    state.loading = true;
    $("request-list").setAttribute("aria-busy", "true");
    $("list-state").hidden = false;
    $("list-state").textContent = "요청을 불러오는 중…";
    controls();
    try {
      const status = $("status-filter").value;
      const data = await api(status ? `/api/requests?status=${encodeURIComponent(status)}` : "/api/requests");
      if (epoch !== state.epoch || ticket !== state.listTicket) return;
      state.requests = data.requests;
      const desired = state.requests.find((request) => sameId(request.id, preferred));
      state.selected = desired?.id ?? state.requests[0]?.id ?? null;
      renderList();
      if (state.selected !== null) await selectRequest(state.selected);
      else {
        state.detailTicket++;
        state.detail = null;
        $("detail").replaceChildren();
        $("detail-state").hidden = false;
        $("detail-state").textContent = "표시할 요청이 없습니다.";
      }
    } catch (failure) {
      if (epoch !== state.epoch || ticket !== state.listTicket) return;
      error($("app-error"), message(failure));
      $("list-state").hidden = false;
      $("list-state").textContent = "목록을 불러오지 못했습니다. 새로고침해 주세요.";
      $("detail-state").textContent = "목록을 불러오지 못했습니다. 새로고침해 주세요.";
    } finally {
      if (epoch === state.epoch && ticket === state.listTicket) {
        state.loading = false;
        $("request-list").setAttribute("aria-busy", "false");
        controls();
      }
    }
  }
  async function selectRequest(id) {
    const epoch = state.epoch;
    const ticket = ++state.detailTicket;
    state.selected = id;
    state.detail = null;
    document.querySelectorAll(".request-item").forEach((node) => {
      node.setAttribute("aria-current", String(sameId(node.dataset.requestId, id)));
    });
    $("detail").replaceChildren();
    $("detail-state").hidden = false;
    $("detail-state").textContent = "상세 내용을 불러오는 중…";
    $("detail-panel").setAttribute("aria-busy", "true");
    try {
      const detail = await api(`/api/requests/${encodeURIComponent(id)}`);
      if (epoch !== state.epoch || ticket !== state.detailTicket) return;
      state.detail = detail;
      $("detail-state").hidden = true;
      renderDetail(detail);
    } catch (failure) {
      if (epoch !== state.epoch || ticket !== state.detailTicket) return;
      $("detail-state").textContent = [401, 403, 404].includes(failure.status)
        ? "이 요청에 접근할 수 없습니다. 계정과 요청 목록을 확인해 주세요."
        : "상세 내용을 불러오지 못했습니다. 다시 선택해 주세요.";
      error($("app-error"), message(failure));
    } finally {
      if (epoch === state.epoch && ticket === state.detailTicket) $("detail-panel").setAttribute("aria-busy", "false");
    }
  }
  function field(form, id, label, value = "") {
    const title = element("label", "", label);
    title.htmlFor = id;
    const input = element("textarea");
    input.id = id;
    input.name = id;
    input.rows = 4;
    input.maxLength = 4000;
    input.value = value;
    const feedback = element("p", "error");
    feedback.id = `${id}-error`;
    feedback.setAttribute("role", "alert");
    feedback.hidden = true;
    input.setAttribute("aria-describedby", feedback.id);
    input.addEventListener("input", () => { input.setCustomValidity(""); error(feedback); });
    form.append(title, input, feedback);
    return { input, feedback };
  }
  function valid(input, feedback) {
    if (input.value.trim().length > 0 && input.value.length <= 4000) return true;
    error(feedback, "1자 이상, 4,000자 이하로 입력해 주세요.");
    input.focus();
    return false;
  }
  function renderDetail(request) {
    const root = $("detail");
    root.replaceChildren();
    const top = element("div", "detail-title");
    top.append(element("h3", "detail-id", `요청 #${request.id}`), badge(request.status));
    root.append(top, element("p", "detail-owner", `작성자 ${request.owner.name}`), element("p", "content", request.content));
    if (request.status === "rejected" && request.reason) {
      const reason = element("section", "current-reason");
      reason.append(element("h3", "", "반려 사유"), element("p", "content", request.reason));
      root.append(reason);
    }
    const owner = sameId(request.owner.id, state.user.id);
    if (owner && request.status === "rejected") {
      const form = element("form", "actions");
      form.append(element("h3", "", "요청 보완"));
      const { input, feedback } = field(form, "amend-content", "보완 내용", request.content);
      input.required = true;
      const footer = element("div", "form-footer");
      footer.append(button("재제출", "send", "primary"));
      form.append(footer);
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (valid(input, feedback)) mutate(`/api/requests/${encodeURIComponent(request.id)}/resubmit`, { content: input.value, version: request.version }, feedback, "요청을 재제출했습니다.", request.id);
      });
      root.append(form);
    } else if (!owner && state.user.role === "reviewer" && request.status === "submitted") {
      const form = element("form", "actions");
      form.append(element("h3", "", "요청 검토"));
      const { input, feedback } = field(form, "review-reason", "반려 사유");
      const footer = element("div", "form-footer");
      const actions = element("div", "action-buttons");
      const reject = button("반려", "rotate-ccw", "reject");
      reject.value = "rejected";
      const approve = button("승인", "check", "primary");
      approve.value = "approved";
      actions.append(reject, approve);
      footer.append(actions);
      form.append(footer);
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const decision = event.submitter?.value;
        if (!["rejected", "approved"].includes(decision)) return;
        if (decision === "rejected" && !valid(input, feedback)) return;
        mutate(`/api/requests/${encodeURIComponent(request.id)}/decision`, { decision, reason: decision === "rejected" ? input.value : "", version: request.version }, feedback, decision === "approved" ? "요청을 승인했습니다." : "요청을 반려했습니다.", request.id);
      });
      root.append(form);
    }
    const history = element("section", "history");
    history.append(element("h3", "", `검토 이력 · ${request.history.length}`));
    if (!request.history.length) history.append(element("p", "empty", "아직 검토 이력이 없습니다."));
    const list = element("ol", "history-list");
    [...request.history].sort((a, b) => b.round - a.round).forEach((snapshot) => {
      const item = element("li", "history-item");
      const heading = element("div", "history-header");
      heading.append(element("h3", "", `${snapshot.round}차 검토`), badge(snapshot.decision));
      const meta = element("div", "metadata history-meta", `검토자 ${snapshot.reviewer.name}`);
      const date = new Date(snapshot.decidedAt);
      if (!Number.isNaN(date.getTime())) {
        const time = element("time", "", ` · ${date.toLocaleString("ko-KR")}`);
        time.dateTime = date.toISOString();
        meta.append(time);
      }
      item.append(heading, meta, element("p", "history-label", "당시 요청 내용"), element("p", "content", snapshot.content));
      if (snapshot.reason) item.append(element("p", "history-label", snapshot.decision === "rejected" ? "반려 사유" : "검토 사유"), element("p", "content", snapshot.reason));
      list.append(item);
    });
    history.append(list);
    root.append(history);
    icons();
    controls();
  }
  async function mutate(path, body, feedback, success, selected) {
    if (state.pending || state.switching || !state.user) return;
    const epoch = state.epoch;
    state.pending = true;
    controls();
    error(feedback);
    error($("app-error"));
    notice("처리 중…");
    try {
      const result = await api(path, body);
      if (epoch !== state.epoch) return;
      if (path === "/api/requests") {
        $("create-form").reset();
        $("content-count").textContent = "0 / 4,000";
      }
      notice(success);
      await refresh(selected ?? result.id ?? state.selected);
    } catch (failure) {
      if (epoch !== state.epoch) return;
      if (failure.code === "IDENTITY_CHANGED") {
        await initialize();
        notice("다른 탭의 계정 변경을 반영했습니다. 입력 내용은 지웠습니다.");
        return;
      }
      notice();
      error(feedback, message(failure));
      if (failure.status === 409) {
        error($("app-error"), `${message(failure)} 최신 내용을 확인한 뒤 다시 시도해 주세요.`);
        await refresh(selected);
      }
    } finally {
      if (epoch === state.epoch) { state.pending = false; controls(); }
    }
  }
  function identityOptions() {
    $("identity").replaceChildren();
    const placeholder = element("option", "", "계정 선택");
    placeholder.value = "";
    placeholder.disabled = true;
    $("identity").append(placeholder);
    state.users.forEach((user) => {
      const option = element("option", "", `${user.name} · ${user.role === "reviewer" ? "검토자" : "요청자"}`);
      option.value = String(user.id);
      $("identity").append(option);
    });
    $("identity").value = state.user ? String(state.user.id) : "";
  }
  async function switchIdentity(userId) {
    if (state.pending || state.switching) return;
    const user = state.users.find((candidate) => sameId(candidate.id, userId));
    if (!user) return;
    state.switching = true;
    const epoch = ++state.epoch;
    state.user = null;
    clearView();
    controls();
    notice("계정을 전환하는 중…");
    try {
      const data = await api("/api/demo/session", { userId: user.id });
      if (epoch !== state.epoch) return;
      state.user = data.user;
      identityOptions();
      $("create-section").hidden = !state.user;
      notice(state.user ? `${state.user.name} 계정으로 전환했습니다.` : "테스트 계정을 선택해 주세요.");
      await refresh(null);
    } catch (failure) {
      if (epoch !== state.epoch) return;
      // A failed response may still have changed the cookie; never reuse the old identity.
      state.user = null;
      $("identity").value = "";
      notice();
      error($("app-error"), `${message(failure)} 테스트 계정을 다시 선택해 주세요.`);
    } finally {
      if (epoch === state.epoch) { state.switching = false; controls(); }
      identities.postMessage("identity-changed");
    }
  }
  async function initialize() {
    state.pending = false;
    state.switching = true;
    const epoch = ++state.epoch;
    clearView();
    controls();
    $("list-state").textContent = "계정을 확인하는 중…";
    try {
      const users = await api("/api/demo/users");
      if (epoch !== state.epoch) return;
      state.users = users.users;
      identityOptions();
      const me = await api("/api/me");
      if (epoch !== state.epoch) return;
      state.user = me.user;
      identityOptions();
      $("create-section").hidden = !state.user;
      if (state.user) await refresh(null);
      else $("list-state").textContent = "테스트 계정을 선택해 주세요.";
    } catch (failure) {
      if (epoch !== state.epoch) return;
      error($("app-error"), message(failure));
      $("list-state").textContent = "계정을 확인하지 못했습니다. 새로고침해 주세요.";
    } finally {
      if (epoch === state.epoch) { state.switching = false; controls(); }
    }
  }
  $("identity").addEventListener("change", (event) => switchIdentity(event.target.value));
  $("status-filter").addEventListener("change", () => {
    error($("app-error"));
    state.requests = [];
    renderList();
    refresh();
  });
  $("refresh").addEventListener("click", () => {
    error($("app-error"));
    if (state.user) refresh(); else initialize();
  });
  $("content").setAttribute("aria-describedby", "create-error content-count");
  $("content").addEventListener("input", () => {
    $("content-count").textContent = `${$("content").value.length.toLocaleString("ko-KR")} / 4,000`;
    error($("create-error"));
  });
  $("create-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (valid($("content"), $("create-error"))) mutate("/api/requests", { content: $("content").value }, $("create-error"), "요청을 제출했습니다.", null);
  });
  icons();
  initialize();
})();
