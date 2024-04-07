<template>
  <div class="button-container">
    <button @click="register">注册</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['username', 'password'],
  methods: {
    async register() {
      try {
        await axios.post('http://localhost:8000/users/', {
          username: this.username,
          password: this.password,
        });
        alert('注册成功');
      } catch (error) {
        alert('注册失败: ' + error.response.data.detail);
      }
    },
  },
};
</script>

