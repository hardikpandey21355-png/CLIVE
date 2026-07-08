// static/js/auth-guard.js
import { auth, onAuthStateChanged } from "./firebase-init.js";

onAuthStateChanged(auth, (user) => {
    if (!user) {
        window.location.href = '/login';
    }
});