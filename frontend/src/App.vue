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
    </div>
    <div class="button-container"> <!-- 添加按钮的容器 -->
      <LoginComponent :username="username" :password="password"/>
      <RegisterComponent :username="username" :password="password"/>
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
    };
  },
};
</script>

<style>
@import "./auth_forms.css";
</style>

