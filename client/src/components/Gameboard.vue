<template>
  <!--<link rel="stylesheet" href="{{ url_for('static', filename='css/gameboard.css') }}">-->
  <div class="container">
    <table>
      <tr>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
      </tr>
      <tr>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('OpponentMonster4')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('OpponentMonster2')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('OpponentMonster1')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('OpponentMonster3')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('OpponentMonster5')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
      </tr>
    </table>
    <div class="board_divider"></div>
    <table>
      <tr>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('PlayerMonster4')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('PlayerMonster2')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('PlayerMonster1')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('PlayerMonster3')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
        <td>
          <cardspace @clicked="cardSpaceClicked" v-bind:card_src="getCard('PlayerMonster5')" v-bind:target_list=this.target_list v-bind:selected_targets=this.selected_targets></cardspace>
        </td>
      </tr>
      <tr>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
        <td>
          <cardspace></cardspace>
        </td>
      </tr>
    </table>
    <div class="board_divider"></div>
  </div>
</template>

<style>
.board_divider {
  height: 30px;
  width: 100%;
}
.padding-0{
  padding-right:0;
  padding-left:0;
}
table {
  border-collapse: collapse;
}
table, th, td {
  border: 1px solid black;
}
td {
  padding: 1px;
  height: 70px;
  width: 70px;
}
</style>

<script>
import CardSpace from './CardSpace.vue';

export default {
  components: {
    cardspace: CardSpace,
  },
  props: {
    game: {},
    target_list: [],
    selected_targets: [],
  },
  methods: {
    getCard(key) {
      if (key in this.game) {
        return this.game[key];
      }
      return null;
    },
    cardSpaceClicked(cardSrc) {
      this.$emit('highlight', cardSrc);
    },
  },
};
</script>
