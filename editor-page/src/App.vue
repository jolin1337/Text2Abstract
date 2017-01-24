<template>
  <div id="container">
    <transition name="fade" mode="out-in">
    <div class="menu-container" v-if="textItem">
      <input type="button" name="reset" class="menu-item reset-btn btn" value="Återställ" @click="resetItems">
      <input type="button" name="save" class="menu-item save-btn btn" value="Spara" @click="saveItems">
      <label class="menu-item edit-btn btn" for="editable" :class="{'editable': editable}">Redigera</label>
      <input type="checkbox" name="editable" id="editable" v-model="editable">
    </div>
    </transition>
    <text-list src="http://localhost:3000/text-analysis/result" ref="textList" query="" class="left-pannel" @focus="enlargeTextItem"></text-list>
    <div class="main-container">
      <text-details :text-item="textItem" :editable="editable">80 x 100</text-details>
    </div>
  </div>
</template>

<script>
import TextList from './TextList.vue'
import TextDetails from './TextDetails.vue'

var textDetailsItem = null;

export default {
  name: 'app',
  components: {
    "text-list": h => h(TextList),
    "text-details": h => h(TextDetails)
  },
  data: function() {
    return {
      textItem: textDetailsItem,
      editable: false
    };
  },
  methods: {
    enlargeTextItem: function(item) {
      this.textItem = item;
    },
    resetItems: function() {
      this.$refs.textList.resetItem(this.textItem);
      // this.$refs.textList.setSource();
      // this.$emit('setSource', 'test-src');
    },
    saveItems: function () {
      this.$refs.textList.saveItems();
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
#container {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

h1, h2 {
  font-weight: normal;
}

a {
  color: #42b983;
}
.left-pannel, .main-container {
  position: absolute;
  top: 0;
  height: 100%;
  display: inline-block;
  float: left;
  box-sizing: border-box;
}
.left-pannel {
  left: 0;
  width: 30%;
  background: transparent;
  border-right: 1px solid #aaa;
}
.main-container {
  left: 30%;
  width: 70%;
  background: transparent;

}


.btn {
  background: white;
  border: 1px solid #ccc;
  padding: 10px;
  margin: 3px 3px 0 0;
}
.menu-container {
  display: inline-block;
  position: absolute;
  right: 0;
  z-index: 10;
}
.menu-item {
  display: inline-block;
  vertical-align: top;
  overflow: hidden;

  background: white;
  border: 1px solid #ccc;
  padding: 10px;

  font-size: 12pt;
  color: #555;
}
.edit-btn + input {
  display: none;
}
.edit-btn.editable {
  background: #eee;
  border: 1px solid #444;
}
/*
.edit-btn:checked:before {
}*/
</style>
