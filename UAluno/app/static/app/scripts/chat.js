$(document).on('click', '.panel-heading span.icon_minim', function (e) {
    var $this = $(this);
    if (!$this.hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideUp();
        $this.addClass('panel-collapsed');
        $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
    } else {
        $this.parents('.panel').find('.panel-body').slideDown();
        $this.removeClass('panel-collapsed');
        $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

$(document).on('focus', '.panel-footer input.chat_input', function (e) {
    var $this = $(this);
    if ($('#minim_chat_window').hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideDown();
        $('#minim_chat_window').removeClass('panel-collapsed');
        $('#minim_chat_window').removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

$(document).on('click', '#new_chat', function (e) {
    var size = $( ".chat-window:last-child" ).css("margin-left");
    size_total = parseInt(size) + 400;
    alert(size_total);
    var clone = $( "#chat_window_1" ).clone().appendTo( ".container" );
    clone.css("margin-left", size_total);
});

// When clicking on send button, send post to the server
$("#btn-chat").on('click', function(){
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var message = document.getElementById("btn-input").value;

    /* Send an ajax request */
    $.ajax({
        type: "POST",
        url: "/send/",
        data: message,
        success: function(data){
            if(data["status"]=="success"){

                // Create the div's and elements that create a new message
                document.getElementById("btn-input").value = "";
                var div1 = document.createElement('div');
                div1.className = 'row msg_container base_sent';
                var div2 = document.createElement('div');
                div2.className = 'col-md-10 col-xs-10 ';
                var div3 = document.createElement('div');
                div3.className = 'messages msg_sent';

                var parentdiv = document.getElementById("chat_message_div");

                var text = document.createElement('p');
                text.innerHTML = message;

                var time = document.createElement('time');
                time.innerHTML = data["name"] + " • "+data["timestamp"];

                div1.appendChild(div2);
                div2.append(div3);
                div3.append(text);
                div3.append(time);
                parentdiv.appendChild(div1);

                // Scroll down chat to the latest message
                document.getElementById("chat_message_div").scrollTo(0,document.body.scrollHeight);
            }
            else{
                console.log("Error sending message to server...");
            }
        },
        failure: function(data){
            console.log("Error sending message to server...");
        },
    });

});

// Initially scroll down chat to the latest message
document.getElementById("chat_message_div").scrollTo(0,document.body.scrollHeight);