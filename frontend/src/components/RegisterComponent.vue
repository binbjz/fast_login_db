<template>
  <div class="button-container">
    <button @click="register">注册</button>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';

export default {
  props: ['username', 'password'],
  methods: {
    async register() {
      try {
        await axios.post(`${API_BASE_URL}/users/`, {
          username: this.username,
          password: this.password,
        });
        this.$emit('toast', { type: 'success', message: '注册成功' });
      } catch (error) {
        const message = error?.response?.data?.detail || error?.message || '请求失败';
        this.$emit('toast', { type: 'error', message: `注册失败: ${message}` });
      }
    },
  },
};
</script>
