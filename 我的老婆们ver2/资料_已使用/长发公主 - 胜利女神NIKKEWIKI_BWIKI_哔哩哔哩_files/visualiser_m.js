"use strict";

const basePath = ".";

function getParams(url) {
    /*获取url的参数*/
    url = url || decodeURI(window.location.href);
    var obj = {};
    try {
        var index = url.indexOf('?');
        url = url.match(/\?([^#]+)/)[1];
        var arr = url.split('&');
        for (var i = 0; i < arr.length; i++) {
            var subArr = arr[i].split('=');
            obj[subArr[0]] = subArr[1];
        }
        return obj;
    } catch (err) {
        return obj;
    }
}

const qs = (val) =>{
      return document.querySelector(val)
}

const qsa = (val) => {
      return document.querySelectorAll(val)
}



const div = qs("#visualiserMain");


async function initJSON() {
      const response = await fetch('js/json/l2d.json');
      const json = await response.json()
      json.sort(function (a, b) {
            return a.name.localeCompare(b.name);

      })
      json.map((val) => {
            if (!RELEASED_UNITS.includes(val.name)) return false
            const liste_item = document.createElement("li");

            liste_item.innerHTML = "<img src='images/sprite/si_" + val.id + "_00_s.png'/>" + " " + val.name

            liste_item.classList.add("charDiv")

            liste_item.addEventListener("click", (e) => {
                id = val.id;
                changeSpine(val.id)
            })
            div.appendChild(liste_item) //div character list
      })

}

// initJSON()

let currentspine = "";
let currentid = ""

if (localStorage.getItem("bg_hex") === null){
      localStorage.setItem("bg_hex","#2f353a");
}

let current_color = localStorage.getItem("bg_hex") || "#2f353a"
document.body.style.backgroundColor = current_color;
let transparent = false
let skin;

let changeSpine = (id) => {

      // empties the div to clear the current spine
      // every listeners MUST be in changeSpine because
      // there aren't any spine currently, so if the listened divs
      // doesn't exist, it will break the code and nothing will work

      qs("#player-container").innerHTML = ""

      currentid = id
      
      // skin exception list , if not it'll go to default skin
      if ( skin !=="weapon_2" || id !== "c220"){
            skin = "default"
      }
      //rapi_old and shifty_old exception
      if ( id === "c010_01" || id === "c907_01"){
            skin = "00"
      } 

      if (current_l2d === "fb") {
            //if snow white or maxine > use skin acc
            if(id==="c220" || id==="c102") skin="acc"   

                  currentspine = new spine.SpinePlayer("player-container", {
                        skelUrl: basePath + "/l2d/" + id + "/" + id + "_00.skel",
                        atlasUrl: basePath + "/l2d/" + id + "/" + id + "_00.atlas",
                        animation: "idle",
                        skin: skin,
                        backgroundColor: transparent ? "#00000000" : current_color,
                        alpha: transparent ? true : false,
                        debug: false,
                        preserveDrawingBuffer:true
                  });               
      }
      if (current_l2d === "cover") {
            //if snow white and weapon_2 not selected> use weapon2
            if(id==="c220" && skin!=="weapon_2") skin="weapon_1"

                  currentspine = new spine.SpinePlayer("player-container", {
                skelUrl: basePath + "/l2d/" + id + "/cover/" + id + "_cover_00.skel",
                        atlasUrl: basePath + "/l2d/" + id + "/cover/" + id + "_cover_00.atlas",
                skin: skin,
                backgroundColor: "#2f353a",
                animation: "cover_idle",
                alpha: false,
                debug: false,
                preserveDrawingBuffer:true
        })
    } else if (current_l2d==="aim"){
        new spine.SpinePlayer("player-container", {
            skelUrl: basePath + "/l2d/" + id + "/aim/" + id + "_aim_00.skel",
            atlasUrl: basePath + "/l2d/" + id + "/aim/" + id + "_aim_00.atlas",
            skin: skin,
            animation: "aim_idle",
            backgroundColor: "#2f353a",
            alpha: false,
            debug: false,
            preserveDrawingBuffer:true
      })
    }
    
}

let current_l2d="fb"
let id = getParams().id || "c010";
changeSpine(id)



const radio_array = qsa(".form-check-input")

for (let i = 0; i < radio_array.length; i++){
    radio_array[i].addEventListener("click",(e)=>{
        current_l2d = e.target.value
        console.log(e);
        changeSpine(id)
    })
}

//skin exception checkers
document.addEventListener("click",(e)=>{
    // we need to do something special for snow white weapon_2 skin because it is too large for the container ( it'll be auto cropped)
    if(e.target.innerHTML==="weapon_2"){
          skin="weapon_2";
          changeSpine(id)
    }
    if ((e.target.innerHTML==="weapon_1" || e.target.innerHTML==="default") && skin=== "weapon_2"){
          skin="default"
          changeSpine(id)
    }
})
