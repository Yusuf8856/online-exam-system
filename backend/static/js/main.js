// Function to generate random CAPTCHA
function generateCaptcha(){

let chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

let captcha = "";

for(let i=0;i<5;i++){
captcha += chars.charAt(Math.floor(Math.random()*chars.length));
}

document.getElementById("captcha").innerText = captcha;

}

// Run only after page fully loads
window.onload = function(){

generateCaptcha();

/* Check if login form exists before adding event */
let form = document.getElementById("loginForm");

if(form){

form.addEventListener("submit", function(e){

let captchaText = document.getElementById("captcha").innerText;

let userInput = document.getElementById("captchaInput").value;

if(captchaText !== userInput){

alert("Captcha Incorrect");

e.preventDefault();

}

});

}

}