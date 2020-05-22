<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <img class="center" v-bind:src="require('../assets/images/yugioh_logo.jpg')">
      </div>
    </div>
    <div class="row">
      <router-link class="center" to="/setup">New Game</router-link>
    </div>
    <div class="row">
      <router-link class="center" to="/about">About</router-link>
    </div>
  </div>
</template>

<style>
.center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}
</style>
