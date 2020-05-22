<template>
  <div v-if=this.ygogame class="container-fluid">
    <topbar v-bind:game=this.ygogame></topbar>
    <div class="row">
      <div class="col-sm-4">
        <img class="highlight" v-if=highlightCard v-bind:src="require('../assets/' + highlightCard.img)">
      </div>
      <div class="col-sm-8">
        <gameboard @highlight="highlightNewCard" v-bind:game=this.ygogame v-bind:target_list=this.target_list v-bind:selected_targets=this.selectedTargets></gameboard>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-6">
        <actionbuttonpanel @actionChosen="chosenAction" v-bind:actions=this.monster_actions v-bind:target_mode=target_mode></actionbuttonpanel>
      </div>
      <div class="col-sm-6">
        <mainbuttonpanel @resetGame="resetGame" @cancelTarget="cancelTarget" @actionChosen="advanceGame" v-bind:default_action=this.default_action v-bind:target_mode=target_mode v-bind:state_open=state_open></mainbuttonpanel>
        <!--<button type="button" class="btn btn-warning button_right" v-on:click="resetGame">Reset Game</button>
        <button type="button" class="btn btn-success button_right" v-on:click="advanceGame(default_action)">{{default_action.DisplayName}}</button>-->
      </div>
    </div>
    <div class="row no-gutters">
      <div class="col-sm-5">
        <console v-bind:consoleEntries=this.ygogame.Console></console>
      </div>
      <div class="col-sm-7">
        <hand @highlight="highlightNewCard" v-bind:cards=this.ygogame.PlayerHand></hand>
      </div>
    </div>
  </div>
  <div v-else>
    <h4>ERROR!</h4>
    <p>Game unable to be created</p>
  </div>
</template>

<style>
.container {
  padding-top: 0px;
  max-height: 100%;
}
.highlight {
  width: 75%;
  height:auto;
  display: block;
  margin-left: auto;
  margin-right: auto;
  padding: 10px;
}
.button_right {
  float: right;
  padding-bottom: 10px;
}
</style>

<script>
import axios from 'axios';
import Gameboard from './Gameboard.vue';
import Console from './Console.vue';
import TopBar from './TopBar.vue';
import Hand from './Hand.vue';
import ActionButtonPanel from './ActionButtonPanel.vue';
import MainButtonPanel from './MainButtonPanel.vue';

export default {
  name: 'Game',
  components: {
    gameboard: Gameboard,
    console: Console,
    topbar: TopBar,
    hand: Hand,
    actionbuttonpanel: ActionButtonPanel,
    mainbuttonpanel: MainButtonPanel,
  },
  data() {
    return {
      ygogame: {},
      default_action: {},
      monster_actions: {},
    };
  },
  props: {
    highlightCard: Object,
    selectedTargets: [],
    state_open: Boolean,
    turn: Number,
    target_mode: Boolean,
    target_list: Array,
    target_actions: [],
  },
  methods: {
    getGame() {
      const path = 'http://localhost:5000/getgame';
      axios.get(path)
        .then((res) => {
          this.ygogame = res.data;
          this.turn = this.ygogame['Turn'];
          this.state_open = this.ygogame['StateOpen'];
          this.default_action = this.filterDefaultAction();
          this.monster_actions = this.filterAndGroup();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getConsole() {
      const path = 'http://localhost:5000/getconsole';
      axios.get(path)
        .then((res) => {
          this.ygogame.Console = res.data['ygoconsole'];
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getAdvanceGameJson(action) {
      const gameJson = {};
      if (this.turn === 1) {
        gameJson['PlayerMove'] = action;
        gameJson['OpponentMove'] = null;
      } else if (this.turn === 2) {
        gameJson['PlayerMove'] = null;
        gameJson['OpponentMove'] = action;
      }
      return gameJson;
    },
    advanceGame(action) {
      const path = 'http://localhost:5000/advancegame';
      const gameJson = this.getAdvanceGameJson(action);
      axios.post(path, gameJson)
        .then(() => {
          this.getGame();
        })
        .catch((error) => {
          console.log(error);
          this.getGame();
        });
      this.cancelTarget();
    },
    resetGame() {
      const path = 'http://localhost:5000/resetgame';
      axios.post(path, {})
        .then(() => {
          this.highlightCard = null;
          this.getGame();
        })
        .catch((error) => {
          console.log(error);
          this.highlightCard = null;
          this.getGame();
        });
    },
    cancelTarget() {
      this.target_mode = false;
      this.target_list = [];
      this.target_actions = [];
      this.selectedTargets = [];
      this.default_action = this.filterDefaultAction();
    },
    addToConsole(statement) {
      const path = 'http://localhost:5000/addtoconsole';
      const statementJson = { Statement: statement };
      axios.post(path, statementJson)
        .then(() => {
          this.getConsole();
        })
        .catch((error) => {
          console.log(error);
          this.getConsole();
        });
    },
    highlightNewCard(cardSrc) {
      this.highlightCard = cardSrc;
      if (this.target_mode) {
        const cardID = cardSrc['CardID'];
        this.selectedTargets = [cardID];
        this.default_action = this.getTargetDefaultAction(cardID);
      }
      this.monster_actions = this.filterAndGroup();
    },
    chosenAction(actionList) {
      let action = {};
      if (actionList[0]['RequiresTarget']) {
        this.toggleTargetMode(actionList);
        this.addToConsole('Select a target');
        this.target_actions = actionList;
        this.default_action = null;
      } else {
        action = actionList[0];
        this.advanceGame(action);
      }
    },
    toggleTargetMode(actionList) {
      this.target_mode = true;
      this.target_list = [];
      for (let index = 0; index < actionList.length; index += 1) {
        this.target_list.push(actionList[index]['Target']['CardID']);
      }
    },

    // Code to group the actions
    filterDefaultAction() {
      if ('PlayerActions' in this.ygogame) {
        const allActions = this.ygogame['PlayerActions'];
        for (let index = 0; index < allActions.length; index += 1) {
          const action = allActions[index];
          if (action['IsDefault'] === true) {
            return action;
          }
        }
      }
      return {};
    },
    getTargetDefaultAction(targetID) {
      for (let index = 0; index < this.target_actions.length; index += 1) {
        const action = this.target_actions[index];
        if (action['Target']['CardID'] === targetID) {
          return action;
        }
      }
      return {};
    },
    filterMonsterActions() {
      if ('PlayerActions' in this.ygogame && this.highlightCard) {
        const allActions = this.ygogame['PlayerActions'];
        const actionList = [];
        for (let index = 0; index < allActions.length; index += 1) {
          const action = allActions[index];
          if ('Monster' in action) {
            if (action['Monster']['CardID'] === this.highlightCard['CardID']) {
              actionList.push(action);
            }
          }
        }
        return actionList;
      }
      return [];
    },
    groupActions(actionList) {
      const actionObject = {};
      actionList.forEach(function (action) {
        const actionName = action['Name'];
        const actionDisplayName = action['DisplayName'];
        if (actionName in actionObject) {
          actionObject[actionDisplayName].push(action);
        } else {
          actionObject[actionDisplayName] = [action];
        }
      });
      return actionObject;
    },
    filterAndGroup() {
      const actionList = this.filterMonsterActions();
      return this.groupActions(actionList);
    },
  },
  created() {
    this.getGame();
  },
  beforeMount() {
    this.getGame();
  },
  mounted() {
    this.getGame();
  },
};

</script>
