window.onload = function(){
  var cameraInput = document.getElementById("photo");

  function getPicture() {
    var image = cameraInput.files[0];
    console.log(image);

    var reader = new FileReader();

    if(!image.type.startsWith("image")) {
      alert("must be image");
      return;
    }

    reader.addEventListener("load", function() {
      document.getElementById("image").src = reader.result;
    }, false);

    reader.readAsDataURL(image);

  }

  cameraInput.addEventListener("change", function(event){
    getPicture();
  });
}
