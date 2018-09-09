function filterNoticias(){
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var message = document.getElementById("selectFilter").value;

    /* Send an ajax request */
    $.ajax({
        type: "POST",
        url: "/noticias/",
        data: message,
        success: function(data){
            if(data["status"]=="success"){
                window.open("/noticias/filter="+data["id"],"_self")
            }
            else{
                console.log("Error sending message to server...");
            }
        },
        failure: function(data){
            console.log("Error sending message to server...");
        },
    });

};