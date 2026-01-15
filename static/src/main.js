/* Global Scripts */

// Loader Spinner
window.addEventListener("load", function() {
  const loader = document.getElementById("loader-wrapper");

  setTimeout(function() {
      loader.classList.add("loader-hidden");
      setTimeout(function() {
          loader.style.display = "none";
      }, 300);

  }, 500);
});


// Unload Spinner
window.addEventListener("beforeunload", function() {
  const loader = document.getElementById("loader-wrapper");
  loader.classList.remove("fade-out");
});


// Content Spinner
window.addEventListener("load", function() {
  const loader = document.getElementById("content-loader");
  const content = document.getElementById("main-content");

  if (loader && content) {
    setTimeout(function() {
      loader.style.display = "none";
      content.classList.remove("content-hidden");

      setTimeout(() => {
        content.classList.add("content-visible");
      }, 300);
    }, 500);
  }
});


// X Message button 
var close = document.getElementsByClassName("closebtn");
var i;
for (i = 0; i < close.length; i++) {
    close[i].onclick = function(){
      var div = this.parentElement;
      div.style.opacity = "0";
      setTimeout(function(){ div.style.display = "none"; }, 600);
    }}


// Modal 
var modal = document.getElementById("myModal");
var btn = document.getElementById("myBtn");
var span = document.getElementsByClassName("close")[0];
btn.onclick = function() { modal.style.display = "block"; }
span.onclick = function() { modal.style.display = "none"; }
window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }}


// เวลาที่ส่ง
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////