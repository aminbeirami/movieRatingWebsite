var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

delete_btn = document.querySelector(".delete_all").addEventListener('click', e => {
	document.querySelector('.warning_action').style.display = "block";
});
delete_btn = document.querySelector(".reject").addEventListener('click', e => {
  document.querySelector('.warning_action').style.display = "none";
});

