
  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCVgXdUtPot9vEkD1Pen3_JWYLpi3udHWA",
    authDomain: "materialization-6d59d.firebaseapp.com",
    databaseURL: "https://materialization-6d59d.firebaseio.com",
    projectId: "materialization-6d59d",
    storageBucket: "materialization-6d59d.appspot.com",
    messagingSenderId: "571712754305"
  };


firebase.initializeApp(config);
const db = firebase.firestore();
const settings = {timestampsInSnapshots: true};
db.settings(settings)