function showHideVerMenu(){
    body=document.querySelector('body');
    
    if (body.classList.value !==""){
        body.classList.remove("vertical-collpsed");
    }
    else{
        body.classList.add("vertical-collpsed");
    }
}