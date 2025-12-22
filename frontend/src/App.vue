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
        <h1>登录 / 注册</h1>
        <p class="subtitle">快速创建账号并安全登录，清爽高效地开始使用。</p>
        <ul class="feature-list">
          <li>密码加密存储，安全可靠</li>
          <li>极速响应，体验顺滑</li>
          <li>支持 Docker 一键启动</li>
        </ul>
      </section>

      <section class="card-right">
        <div class="form-container">
          <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" v-model="username" placeholder="请输入用户名"/>
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" v-model="password" placeholder="请输入密码"/>
          </div>
        </div>
        <div class="button-container">
          <LoginComponent :username="username" :password="password" @toast="showToast"/>
          <RegisterComponent :username="username" :password="password" @toast="showToast"/>
        </div>
        <p class="helper-text">登录用于已有账号，注册用于创建新账号。</p>
      </section>
    </div>
  </div>
</template>

<script>
import LoginComponent from "./components/LoginComponent";
import RegisterComponent from "./components/RegisterComponent";

export default {
  name: "App",
  components: {
    LoginComponent,
    RegisterComponent,
  },
  data() {
    return {
      username: '',
      password: '',
      toastVisible: false,
      toastMessage: '',
      toastType: 'info',
      toastTimer: null,
    };
  },
  methods: {
    showToast({ type, message }) {
      this.toastType = type || 'info';
      this.toastMessage = message || '';
      this.toastVisible = true;
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
      }
      this.toastTimer = setTimeout(() => {
        this.toastVisible = false;
      }, 2500);
    },
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
  },
};
</script>

<style>
@import "./auth_forms.css";
</style>
