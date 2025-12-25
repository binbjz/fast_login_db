<template>
  <button type="button" :disabled="loading" @click="register">
    {{ "注册" }}
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
    async register() {
      if (this.loading) return;
      if (!this.username || !this.password) {
        this.$emit('toast', { type: 'error', message: '请先输入用户名和密码' });
        return;
      }
      this.loading = true;
      try {
        const response = await axios.post(`${API_BASE_URL}/users/`, {
          username: this.username,
          password: this.password,
        });
        const payload = response?.data || {};
        this.$emit('register-success', {
          user_id: payload?.id,
          username: payload?.username || this.username,
        });
        this.$emit('toast', { type: 'success', message: '注册成功' });
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
        this.$emit('toast', { type: 'error', message: `注册失败: ${message}` });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
