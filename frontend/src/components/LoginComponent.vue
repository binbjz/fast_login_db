<template>
  <div class="button-container">
    <button @click="login">登录</button>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';

export default {
  props: ['username', 'password'],
  methods: {
    async login() {
      try {
        const response = await axios.post(`${API_BASE_URL}/login/`, {
          username: this.username,
          password: this.password,
        });
        const message = response?.data?.msg || '登录成功';
        this.$emit('toast', { type: 'success', message });
      } catch (error) {
        const message = error?.response?.data?.detail || error?.message || '请求失败';
        this.$emit('toast', { type: 'error', message: `登录失败: ${message}` });
      }
    },
  },
};
</script>
