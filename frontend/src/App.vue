<template>
  <div class="container">
    <h1>Login | Register</h1>
    <div class="form-container">
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" placeholder="Please enter your username"/>
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" placeholder="Please enter your password"/>
      </div>
      <div class="button-container">
        <button type="button" @click="login">Login</button>
        <button type="button" @click="register">Register</button>
      </div>
      <p class="result-message">{{ resultMsg }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios"
import "./shared_styles.css"

export default {
  name: "App",
  data() {
    return {
      username: "",
      password: "",
      resultMsg: ""
    }
  },
  methods: {
    async login() {
      try {
        const response = await axios.post("http://localhost:8000/login/", {
          username: this.username,
          password: this.password
        })
        this.resultMsg = response.data.msg
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
          this.resultMsg = "Registration successful"
        }
      } catch (error) {
        this.resultMsg = error.response.data.detail
      }
    }
  }
}
</script>
