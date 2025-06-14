
function getObjKeys(obj, value) {
    return Object.keys(obj).filter(key => obj[key] === value);
  }
  const firebaseConfig = {
    apiKey: "AIzaSyC0N-ADc0kZ8XqcbpVKP7C2B4kb_c5LDYc",
    authDomain: "inventorymanagementdb.firebaseapp.com",
    databaseURL: "https://inventorymanagementdb-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "inventorymanagementdb",
    storageBucket: "inventorymanagementdb.firebasestorage.app",
    messagingSenderId: "511046986981",
    appId: "1:511046986981:web:958eaab4690f6bfb9f780c"
  };

firebase.initializeApp(firebaseConfig);
var countRef = firebase.database().ref('count');

countRef.on('value', function(snapshot) {
    val = snapshot.val()
    zeros = getObjKeys(val, 0)
    count = Object.keys(val)
    // let nonzeros = count.filter(x => !zeros.includes(x));
    
    count.forEach(function (item, index) {
        value = '#' + item + '-count'
        console.log(value)
        $(value).css("color","black")
        $(value).text(val[item])
        if (val[item] < 1){
            popup_alert(value,item)
          }    
      });
      
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

function popup_alert(value,item){
    
    var newItemName = "";
  
    if (item == "BoxDrink")
    {
      newItemName = "Drink";
    }
    else if (item == "BabyPowder")
    {
      newItemName = "Powder";
    }

    note = newItemName + " stock is getting low"
    $(value).css("color","red")
    // $("#notification").text(note)
    // $("#box-notification").show()
    // sleep(3000).then(() => { $("#box-notification").fadeOut('slow'); });
}


