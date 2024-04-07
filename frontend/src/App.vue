<template>
  <div class="container">
    <h1>登录|注册</h1>
    <div class="form-container">
      <div class="form-group">
        <label for="username">用户名：</label>
        <input type="text" id="username" v-model="username" placeholder="请输入用户名"/>
      </div>
      <div class="form-group">
        <label for="password">密码：</label>
        <input type="password" id="password" v-model="password" placeholder="请输入密码"/>
      </div>
      <div class="button-container">
        <button type="button" @click="login">登录</button>
        <button type="button" @click="register">注册</button>
      </div>
      <p class="result-message">{{ resultMsg }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios"
import "./auth_forms.css"

export default {
  name: "App",
  data() {
    return {
      username: "",
      password: "",
      resultMsg: "",
    }
  },
  methods: {
    async login() {
      try {
        const response = await axios.post("http://localhost:8000/login/", {
          username: this.username,
          password: this.password
        });
        this.resultMsg = `${response.data.username} ${response.data.msg}`;
      } catch (error) {
        this.resultMsg = error.response.data.detail
      }
    },
    async register() {
      try {
        const response = await axios.post("http://localhost:8000/users/", {
          username: this.username,
          password: this.password
        })
        if (response.status === 200) {
          this.resultMsg = "注册成功"
        }
      } catch (error) {
        this.resultMsg = error.response.data.detail
      }
    }
  }
}
</script>
