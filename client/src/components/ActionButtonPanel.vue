<template inline-template>
  <span class="container d-inline-block">
    <ul v-if=!target_mode>
      <li class="actionlist" v-for="(value, name, index) in actions" :key=index>
        <button type="button" class="btn btn-primary button_right" v-on:click="chooseAction(name)">{{ name }}</button>
      </li>
    </ul>
  </span>
</template>

<style>
ul {
  list-style-type: none;
}
.actionlist {
  display: inline-block;
  padding: 0px;
  overflow-x: auto;
}
</style>

<script>
export default {
  name: 'ActionButtonPanel',
  props: {
    target_mode: Boolean,
    actions: Object,
  },
  methods: {
    chooseAction(actionType) {
      this.$emit('actionChosen', this.actions[actionType]);
    },
  },
};
</script>
