<template inline-template>
  <span class="container d-inline-block">
    <!--<button type="button" class="btn btn-warning button_right" v-on:click="resetGame">Reset Game</button>
    <button type="button" class="btn btn-success button_right" v-on:click="advanceGame(default_action)">{{default_action.DisplayName}}</button>-->
    <button v-if=!target_mode type="button" class="btn btn-warning button_right" v-on:click="resetGame">Reset Game</button>
    <button v-if=target_mode type="button" class="btn btn-danger button_right" v-on:click="cancelTarget">Cancel</button>
    <button v-if=default_action type="button" class="btn btn-success button_right" v-on:click="advanceGame(default_action)">{{getDefaultButtonName(default_action)}}</button>
  </span>
</template>

<style>
ul {
  list-style-type: none;
}
.actionlist {
  display: inline-block;
  padding: 5px;
  overflow-x: auto;
}
</style>

<script>
export default {
  name: 'MainButtonPanel',
  props: {
    target_mode: Boolean,
    default_action: Object,
    state_open: Boolean,
  },
  methods: {
    resetGame() {
      this.$emit('resetGame');
    },
    cancelTarget() {
      this.$emit('cancelTarget');
    },
    advanceGame() {
      this.$emit('actionChosen', this.default_action);
    },
    getDefaultButtonName(action) {
      if (this.state_open && action.DisplayName === 'Advance') {
        return 'Resolve';
      } else {
        return action.DisplayName;
      }
    },
  },
};
</script>
