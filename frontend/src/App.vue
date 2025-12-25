<template>
  <div class="page">
    <div
      v-if="toastVisible"
      class="toast"
      :class="toastType"
      role="status"
      aria-live="polite"
    >
      {{ toastMessage }}
    </div>

    <div class="card">
      <section class="card-left">
        <h1>{{ pageTitle }}</h1>
        <p class="subtitle">
          {{ isAuthenticated ? "当前会话有效，无需重复登录。" : "快速创建账号并安全登录，清爽高效地开始使用。" }}
        </p>
        <ul class="feature-list" v-if="!isAuthenticated">
          <li>密码加密存储，安全可靠</li>
          <li>极速响应，体验顺滑</li>
          <li>支持 Docker 一键启动</li>
        </ul>
        <ul class="feature-list" v-else>
          <li>当前账号：{{ authUser }}</li>
          <li>会话到期：{{ expiresAtText }}</li>
          <li>到期前再次访问无需重复登录</li>
        </ul>
      </section>

      <section class="card-right" v-if="!isAuthenticated">
        <div class="form-container">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              ref="usernameInput"
              type="text"
              id="username"
              v-model="username"
              placeholder="请输入用户名"
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              ref="passwordInput"
              type="password"
              id="password"
              v-model="password"
              placeholder="请输入密码"
            />
          </div>
        </div>

        <div class="button-container auth-actions">
          <LoginComponent
            :username="username"
            :password="password"
            @toast="showToast"
            @login-success="onLoginSuccess"
          />
          <RegisterComponent
            :username="username"
            :password="password"
            @toast="showToast"
            @register-success="onRegisterSuccess"
          />
        </div>

        <p class="helper-text">登录用于已有账号，注册用于创建新账号。</p>
      </section>

      <section class="card-right" v-else>
        <div class="form-container session-panel">
          <p class="session-title">已登录</p>
          <p class="session-meta">账号：{{ authUser }}</p>
          <p class="session-meta">会话到期时间：{{ expiresAtText }}</p>
        </div>

        <div class="button-container">
          <button type="button" @click="logout">退出登录</button>
        </div>
        <p class="helper-text">退出登录会彻底注销当前会话，并清空输入框。</p>
      </section>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import LoginComponent from "./components/LoginComponent.vue";
import RegisterComponent from "./components/RegisterComponent.vue";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VUE_APP_API_BASE_URL ||
  "http://localhost:8000";

const AUTH_STORAGE_KEY = "fast_login_db_auth";
const LOGIN_HISTORY_KEY = "fast_login_db_login_history";

export default {
  name: "App",
  components: {
    LoginComponent,
    RegisterComponent,
  },
  data() {
    return {
      username: "",
      password: "",
      authToken: "",
      authUser: "",
      authExpiresAt: "",
      showFirstLoginTitle: false,
      sessionTimer: null,
      toastVisible: false,
      toastMessage: "",
      toastType: "info",
      toastTimer: null,
    };
  },
  computed: {
    isAuthenticated() {
      return Boolean(this.authToken && this.authUser && this.authExpiresAt);
    },
    expiresAtText() {
      const ts = Date.parse(this.authExpiresAt || "");
      if (!Number.isFinite(ts)) return "--";
      return new Date(ts).toLocaleString();
    },
    pageTitle() {
      if (!this.isAuthenticated) return "登录 / 注册";
      return this.showFirstLoginTitle ? "登录成功" : "欢迎回来";
    },
  },
  methods: {
    readLoginHistory() {
      const raw = localStorage.getItem(LOGIN_HISTORY_KEY);
      if (!raw) return {};
      try {
        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === "object" ? parsed : {};
      } catch {
        return {};
      }
    },
    buildLoginHistoryIdentity(userId, username) {
      if (Number.isInteger(userId) && userId > 0) {
        return `id:${userId}`;
      }
      const user = String(username || "").trim();
      if (!user) return "";
      return `name:${user}`;
    },
    hasLoggedInBefore({ userId, username }) {
      const identity = this.buildLoginHistoryIdentity(userId, username);
      if (!identity) return false;
      const history = this.readLoginHistory();
      return history[identity] === true;
    },
    markUserLoggedIn({ userId, username }) {
      const identity = this.buildLoginHistoryIdentity(userId, username);
      if (!identity) return;
      const history = this.readLoginHistory();
      history[identity] = true;
      localStorage.setItem(LOGIN_HISTORY_KEY, JSON.stringify(history));
    },
    clearUserLoginHistory({ userId, username }) {
      const history = this.readLoginHistory();
      let changed = false;
      const idIdentity = this.buildLoginHistoryIdentity(userId, "");
      const nameIdentity = this.buildLoginHistoryIdentity(null, username);
      for (const identity of [idIdentity, nameIdentity]) {
        if (!identity) continue;
        if (Object.prototype.hasOwnProperty.call(history, identity)) {
          delete history[identity];
          changed = true;
        }
      }
      if (changed) {
        localStorage.setItem(LOGIN_HISTORY_KEY, JSON.stringify(history));
      }
    },
    showToast({ type, message }) {
      this.toastType = type || "info";
      this.toastMessage = message || "";
      this.toastVisible = true;
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
      }
      this.toastTimer = setTimeout(() => {
        this.toastVisible = false;
      }, 2500);
    },
    focusUsernameInput() {
      const usernameInput = this.$refs.usernameInput;
      if (usernameInput && typeof usernameInput.focus === "function") {
        usernameInput.focus();
      }
    },
    focusPasswordInput() {
      const passwordInput = this.$refs.passwordInput;
      if (passwordInput && typeof passwordInput.focus === "function") {
        passwordInput.focus();
      }
    },
    saveActiveSession() {
      if (!this.authToken || !this.authUser || !this.authExpiresAt) return;
      localStorage.setItem(
        AUTH_STORAGE_KEY,
        JSON.stringify({
          accessToken: this.authToken,
          username: this.authUser,
          expiresAt: this.authExpiresAt,
        })
      );
    },
    clearActiveSession() {
      if (this.sessionTimer) {
        clearTimeout(this.sessionTimer);
        this.sessionTimer = null;
      }
      this.authToken = "";
      this.authUser = "";
      this.authExpiresAt = "";
      localStorage.removeItem(AUTH_STORAGE_KEY);
    },
    scheduleSessionExpiry() {
      if (this.sessionTimer) {
        clearTimeout(this.sessionTimer);
        this.sessionTimer = null;
      }
      const expiresAtMs = Date.parse(this.authExpiresAt || "");
      if (!Number.isFinite(expiresAtMs)) {
        this.clearActiveSession();
        return;
      }
      const delay = expiresAtMs - Date.now();
      if (delay <= 0) {
        this.clearActiveSession();
        this.showToast({ type: "info", message: "会话已过期，请重新登录" });
        this.$nextTick(() => {
          this.focusUsernameInput();
        });
        return;
      }
      this.sessionTimer = setTimeout(() => {
        this.clearActiveSession();
        this.showToast({ type: "info", message: "会话已过期，请重新登录" });
        this.$nextTick(() => {
          this.focusUsernameInput();
        });
      }, delay);
    },
    setActiveSession({ accessToken, username, expiresAt }) {
      this.authToken = accessToken;
      this.authUser = username;
      this.authExpiresAt = expiresAt;
      this.saveActiveSession();
      this.scheduleSessionExpiry();
    },
    async fetchSessionInfo(accessToken) {
      try {
        const response = await axios.get(`${API_BASE_URL}/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        return response?.data || null;
      } catch {
        return null;
      }
    },
    onLoginSuccess(payload) {
      if (!payload?.access_token || !payload?.username || !payload?.expires_at) {
        return;
      }
      const hasLoggedInBefore = this.hasLoggedInBefore({
        userId: payload.user_id,
        username: payload.username,
      });
      this.showFirstLoginTitle = !hasLoggedInBefore;
      this.markUserLoggedIn({
        userId: payload.user_id,
        username: payload.username,
      });

      this.setActiveSession({
        accessToken: payload.access_token,
        username: payload.username,
        expiresAt: payload.expires_at,
      });
      this.username = "";
      this.password = "";
    },
    onRegisterSuccess(payload) {
      this.clearUserLoginHistory({
        userId: payload?.user_id,
        username: payload?.username || this.username,
      });
    },
    async restoreSession() {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      if (!raw) return;
      try {
        const parsed = JSON.parse(raw);
        const username = String(parsed?.username || "").trim();
        const accessToken = String(parsed?.accessToken || "").trim();
        const expiresAt = String(parsed?.expiresAt || "").trim();
        const expiresAtMs = Date.parse(expiresAt);
        if (!username || !accessToken || !Number.isFinite(expiresAtMs) || expiresAtMs <= Date.now()) {
          this.clearActiveSession();
          return;
        }

        const info = await this.fetchSessionInfo(accessToken);
        if (!info?.username || !info?.expires_at) {
          this.clearActiveSession();
          return;
        }

        this.setActiveSession({
          accessToken,
          username: info.username,
          expiresAt: info.expires_at,
        });
        this.showFirstLoginTitle = false;
        this.markUserLoggedIn({
          userId: info.user_id,
          username: info.username,
        });
      } catch {
        this.clearActiveSession();
      }
    },
    async performLogout(message) {
      const token = this.authToken;

      this.clearActiveSession();
      this.showFirstLoginTitle = false;
      this.username = "";
      this.password = "";

      if (token) {
        try {
          await axios.post(
            `${API_BASE_URL}/logout/`,
            {},
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );
        } catch {
          // Ignore logout API errors after local session is cleared.
        }
      }

      this.showToast({ type: "info", message });
      this.$nextTick(() => {
        this.focusUsernameInput();
      });
    },
    async logout() {
      await this.performLogout("已退出登录");
    },
  },
  mounted() {
    this.restoreSession();
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
    if (this.sessionTimer) {
      clearTimeout(this.sessionTimer);
    }
  },
};
</script>

<style>
@import "./auth_forms.css";
</style>
