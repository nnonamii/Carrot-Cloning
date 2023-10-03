function previewImage(event) {
  let reader = new FileReader();
  reader.onload = function () {
    let output = document.getElementById("imagePreview");
    output.src = reader.result;
    output.classList.add("img-upload-fit");
  };
  reader.readAsDataURL(event.target.files[0]);
}

function previewImage_menu(event) {
  let reader = new FileReader();
  reader.onload = function () {
    let output_menu = document.getElementById("imagePreview_menu");
    output_menu.src = reader.result;
    output_menu.classList.add("img-upload-fit");
  };
  reader.readAsDataURL(event.target.files[0]);
}
