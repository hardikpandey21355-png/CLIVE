// static/js/firebase-init.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  sendPasswordResetEmail,
  deleteUser,                     
  EmailAuthProvider,               
  reauthenticateWithCredential,    
  reauthenticateWithPopup  
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import {
  getFirestore,
  doc,
  setDoc,
  getDoc,
  serverTimestamp,
  deleteDoc 
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCHm3HY1OeMID3OygGqlcsqhov0Quamyqk",
  authDomain: "clive-v1-78936.firebaseapp.com",
  projectId: "clive-v1-78936",
  storageBucket: "clive-v1-78936.firebasestorage.app",
  messagingSenderId: "607290570147",
  appId: "1:607290570147:web:2ba6e6932b0e5ae7d9d616",
  measurementId: "G-S09Y6CR9SY"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export {
  auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  sendPasswordResetEmail,
  db,
  doc,
  setDoc,
  getDoc,
  serverTimestamp,
  deleteUser,
  EmailAuthProvider,
  reauthenticateWithCredential,
  reauthenticateWithPopup,
  deleteDoc
};