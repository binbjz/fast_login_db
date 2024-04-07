<template>
  <div class="button-container">
    <button @click="login">登录</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['username', 'password'],
  methods: {
    async login() {
      try {
        await axios.post('http://localhost:8000/login/', {
          username: this.username,
          password: this.password,
        });
        alert('登录成功');
      } catch (error) {
        alert('登录失败: ' + error.response.data.detail);
      }
    },
  },
};
</script>

