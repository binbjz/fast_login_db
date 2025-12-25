<template>
  <button type="button" :disabled="loading" @click="login">
    {{ "登录" }}
  </button>
</template>

<script>
import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VUE_APP_API_BASE_URL ||
  'http://localhost:8000';

export default {
  props: {
    username: {
      type: String,
      default: '',
    },
    password: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    async login() {
      if (this.loading) return;
      if (!this.username || !this.password) {
        this.$emit('toast', { type: 'error', message: '请先输入用户名和密码' });
        return;
      }
      this.loading = true;
      try {
        const response = await axios.post(`${API_BASE_URL}/login/`, {
          username: this.username,
          password: this.password,
        });
        const payload = response?.data || {};
        const message = payload?.msg || '登录成功';
        this.$emit('login-success', payload);
        this.$emit('toast', { type: 'success', message });
      } catch (error) {
        const detail = error?.response?.data?.detail;
        let message = '请求失败';
        if (Array.isArray(detail)) {
          const messages = detail.map((item) => item?.msg).filter(Boolean);
          if (messages.length) {
            message = messages.join('；');
          }
        } else if (typeof detail === 'string') {
          message = detail;
        } else if (error?.message) {
          message = error.message;
        }
        this.$emit('toast', { type: 'error', message: `登录失败: ${message}` });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
