// utilities.js


// clicking on links should select their radio button
function selectRadioButton(radioButtonId, link) {
  document.getElementById(radioButtonId).checked = true;
  openPopup(link);
}


// clicking on links should create a popup window
function openPopup(link) {
  var options = "width=1000,height=600,resizable=yes";
  window.open(link, "_blank", options);
}


// text input fields should have a placeholder
function setPlaceholder(elementId, text) {
  var textarea = document.getElementById(elementId);
  if (textarea) {
      textarea.placeholder = text;
  }
}


// set placeholder text
var placeholderText = "- Stichpunktsatz 1\n- Stichpunktsatz 2\n- ...";
setPlaceholder("question_1_input", placeholderText);
setPlaceholder("question_2_input", placeholderText);
setPlaceholder("question_3_input", placeholderText);
setPlaceholder("question_4_input", placeholderText);


// at least 3 questions must be answered
document.getElementById("user_input_form").addEventListener("submit", function(event) {
  var question_1_input = document.getElementsByName("question_1_input")[0].value.trim();
  var question_2_input = document.getElementsByName("question_2_input")[0].value.trim();
  var question_3_input = document.getElementsByName("question_3_input")[0].value.trim();
  var question_4_input = document.getElementsByName("question_4_input")[0].value.trim();
  var emptyCount = 0;
  if (question_1_input === "") {
      emptyCount++;
  }
  if (question_2_input === "") {
      emptyCount++;
  }
  if (question_3_input === "") {
      emptyCount++;
  }
  if (question_4_input === "") {
      emptyCount++;
  }
  if (emptyCount > 1) {
      // trigger window alert
      alert("Bitte beantworte mindestens 3 Fragen aus Aufgabe 1.");
      event.preventDefault();
      document.getElementById("question_1_input").scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
  }
});
