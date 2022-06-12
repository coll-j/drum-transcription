$('#exampleModal').on('shown.bs.modal', function () {
    $('#trans').trigger('focus')
})

document.querySelector("#trans").addEventListener("click", function(){
    
    var text = [
        "Processing your audio...", 
        "Detecting onsets...", 
        "Classifying onsets...",
        "Generating transcription..."];
    var counter = 0;
    var elem = document.getElementById("loading-text");
    var inst = setInterval(change, 3000);

    function change() {
    elem.innerHTML = text[counter];
    counter++;
    if (counter >= text.length) {
        counter = text.length - 1;
        // clearInterval(inst); // uncomment this if you want to stop refreshing after one cycle
    }
}
})

document.querySelector("#audio_file").addEventListener("change", function(){
    console.log('This file size is: ' + this.files[0].size / 1024 / 1024 + "MiB");
    if (this.files[0].size / 1024 / 1024 > 3.99) {
        document.getElementById("danger-text").style.display = "block";
        document.getElementById("trans").setAttribute("disabled", "");
        return;
    } else {
        document.getElementById("danger-text").style.display = "none";
        document.getElementById("trans").removeAttribute("disabled");
    }

    const reader = new FileReader();

    reader.addEventListener("load", () => {
        console.log("saving audio")
        localStorage.setItem("audio_file", reader.result);
    });

    reader.readAsDataURL(this.files[this.files.length - 1]);
})