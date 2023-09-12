class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            voiceButton: document.querySelector('.voice__button')

        }

        this.state = false;
        this.first = true;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton, voiceButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        // openButton.addEventListener('click', () => this.newChat(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        voiceButton.addEventListener('click', () => this.onVoiceButton(chatBox))


        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    
    newChat(chatbox) {
        this.state = !this.state;
    
        // show or hides the box
        if(this.state) {
            console.log("This is a new chat!")
            chatbox.classList.add('chatbox--active')
        } else {
            // chatbox.classList.remove('chatbox--active')
            console.log("This chat is closed!")
        }
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }

        if(this.first) {
            let first_message = { name: "DolFine", message: "Hello " + currentUser + ",<br> How can I help you?" };
            this.messages.push(first_message);
            console.log("This is the first text!");
            var html = '';
            html += '<div class="messages__item messages__item--visitor">' + first_message.message + '</div>'

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
        }

    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }
        else {
            this.first = false;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch($SCRIPT_ROOT + '/chatbot', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "DolFine", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
          });
    }

    onVoiceButton(chatbox) {
        console.log("Voice button clicked");
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition)();
        recognition.lang = 'en-US';
        
        recognition.start();
        
        recognition.onresult = (event) => {
            const text1 = event.results[0][0].transcript;
            console.log("Recognized Text: ", text1);
            
            let msg1 = { name: "User", message: text1 };
            this.messages.push(msg1);
            console.log("User message pushed");
    
            fetch($SCRIPT_ROOT + '/chatbot', {
                method: 'POST',
                body: JSON.stringify({ message: text1 }),
                mode: 'cors',
                headers: {
                  'Content-Type': 'application/json'
                },
              })
              .then(r => r.json())
              .then(r => {
                let msg2 = { name: "DolFine", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textField.value = ''
    
            }).catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox)
                textField.value = ''
              });
        };
    }
    

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "DolFine")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


const chatbox = new Chatbox();
chatbox.display();
// chatbox.newChat();


// chatbot cloud

// hide the clound text
function autoAppearChatCloud() {
    // console.log("appearing")
    document.getElementById("chatbot-cloud").style.visibility = "visible";
}

// appear the cloud text
function autoDiasppearChatCloud() {
    // console.log("Diappearing")
    document.getElementById("chatbot-cloud").style.visibility = "hidden";
}

setInterval(autoAppearChatCloud, 10000)
setInterval(autoDiasppearChatCloud, 20000)


document.addEventListener("DOMContentLoaded", function () {

    const chatbotCloud = document.getElementById("chatbot-cloud");
    const chatbotButton = document.getElementsByClassName("chatbox__button")[0];
    // console.log(chatbotButton[0])
    chatbotButton.addEventListener("click", function () {
        chatbotCloud.style.display = "none";
    });
});

// greet the first message 

const openChatButton = document.querySelector('.chatbox__button');
