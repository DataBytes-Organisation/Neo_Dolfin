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

        if (this.state) {
            console.log("This is a new chat!")
            chatbox.classList.add('chatbox--active')
        } else {
            console.log("This chat is closed!")
        }
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }

        if (this.first) {
            let first_message = {
                name: "DolFine",
                message: "The AI model used by DolFin is not indicative of the actual future financial position of a user. You should not rely on this analysis and you should seek independent financial advice before making any financial decision. You hereby agree that you will not hold DolFin liable for any damages, losses, or costs arising from your reliance on the AI model's predictions. <br><br> Hello " + currentUser + ",<br> How can I help you?"
            };
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
        let text1 = textField.value;
        if (text1 === "") {
            return;
        } else {
            this.first = false;
        }

        let msg1 = {name: "User", message: text1}
        this.messages.push(msg1);

        fetch($SCRIPT_ROOT + '/chatbot', {
            method: 'POST',
            body: JSON.stringify({message: text1, input_mode: "text"}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                let msg2 = {name: "DolFine", message: r.answer};
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
    
        fetch($SCRIPT_ROOT + '/chatbot', {
            method: 'POST',
            body: JSON.stringify({input_mode: "voice"}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                if (r.answer) {
                    let msg1 = {name: "User", message: r.user_input || "Voice input"}; // Use a default message if user_input is undefined
                    let msg2 = {name: "DolFine", message: r.answer};
                    this.messages.push(msg1);
                    this.messages.push(msg2);
                    this.updateChatText(chatbox)
                } else {
                    console.error('Voice recognition failed');
                }
            }).catch((error) => {
            console.error('Error:', error);
        });
    }

    updateChatText(chatbox) {
        var html = '';
        const l = '<div class="messages__item messages__item--visitor"><small class="loading">... </small></div>'
        const chatmessage = chatbox.querySelector('.chatbox__messages');

        this.messages.slice().reverse().forEach(function (item, index) {
            if (item.name === "DolFine") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'

                setTimeout(() => {
                    chatmessage.innerHTML = html;
                }, 1300);
                chatmessage.innerHTML = l;
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
                chatmessage.innerHTML = html;
            }
        });
    }
}

const chatbox = new Chatbox();
chatbox.display();



//////old_chatbot//////

// class Chatbox {
//     constructor() {
//         this.args = {
//             openButton: document.querySelector('.chatbox__button'),
//             chatBox: document.querySelector('.chatbox__support'),
//             sendButton: document.querySelector('.send__button'),
//             voiceButton: document.querySelector('.voice__button')

//         }

//         this.state = false;
//         this.first = true;
//         this.messages = [];
//     }

//     display() {
//         const {openButton, chatBox, sendButton, voiceButton} = this.args;

//         openButton.addEventListener('click', () => this.toggleState(chatBox))

//         sendButton.addEventListener('click', () => this.onSendButton(chatBox))

//         voiceButton.addEventListener('click', () => this.onVoiceButton(chatBox))


//         const node = chatBox.querySelector('input');
//         node.addEventListener("keyup", ({key}) => {
//             if (key === "Enter") {
//                 this.onSendButton(chatBox)
//             }
//         })
//     }

    
//     newChat(chatbox) {
//         this.state = !this.state;
    
//         // show or hides the box
//         if(this.state) {
//             console.log("This is a new chat!")
//             chatbox.classList.add('chatbox--active')
//         } else {
//             // chatbox.classList.remove('chatbox--active')
//             console.log("This chat is closed!")
//         }
//     }

//     toggleState(chatbox) {
//         this.state = !this.state;

//         // show or hides the box
//         if(this.state) {
//             chatbox.classList.add('chatbox--active')
//         } else {
//             chatbox.classList.remove('chatbox--active')
//         }

//         if(this.first) {
//             let first_message = { 
//                 name: "DolFine", 
//                 message: "The AI model used by DolFin is not indicative of the actual future financial position of a user. You should not rely on this analysis and you should seek independent financial advice before making any financial decision. You hereby agree that you will not hold DolFin liable for any damages, losses, or costs arising from your reliance on the AI model's predictions. <br><br> Hello " + currentUser + ",<br> How can I help you?" 
//             };
//             this.messages.push(first_message);
//             console.log("This is the first text!");
//             var html = '';
//             html += '<div class="messages__item messages__item--visitor">' + first_message.message + '</div>'

//         const chatmessage = chatbox.querySelector('.chatbox__messages');
//         chatmessage.innerHTML = html;
//         }

//     }

//     onSendButton(chatbox) {
//         var textField = chatbox.querySelector('input');
//         let text1 = textField.value
//         if (text1 === "") {
//             return;
//         }
//         else {
//             this.first = false;
//         }

//         let msg1 = { name: "User", message: text1 }
//         this.messages.push(msg1);

//         fetch($SCRIPT_ROOT + '/chatbot', {
//             method: 'POST',
//             body: JSON.stringify({ message: text1 }),
//             mode: 'cors',
//             headers: {
//               'Content-Type': 'application/json'
//             },
//           })
//           .then(r => r.json())
//           .then(r => {
//             let msg2 = { name: "DolFine", message: r.answer };
//             this.messages.push(msg2);
//             this.updateChatText(chatbox)
//             textField.value = ''

//         }).catch((error) => {
//             console.error('Error:', error);
//             this.updateChatText(chatbox)
//             textField.value = ''
//           });
//     }

//     onVoiceButton(chatbox) {
//         console.log("Voice button clicked");
//         var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition)();
//         recognition.lang = 'en-US';
        
//         recognition.start();
        
//         recognition.onresult = (event) => {
//             const text1 = event.results[0][0].transcript;
//             console.log("Recognized Text: ", text1);
            
//             let msg1 = { name: "User", message: text1 };
//             this.messages.push(msg1);
//             console.log("User message pushed");
    
//             fetch($SCRIPT_ROOT + '/chatbot', {
//                 method: 'POST',
//                 body: JSON.stringify({ message: text1 }),
//                 mode: 'cors',
//                 headers: {
//                   'Content-Type': 'application/json'
//                 },
//               })
//               .then(r => r.json())
//               .then(r => {
//                 let msg2 = { name: "DolFine", message: r.answer };
//                 this.messages.push(msg2);
//                 this.updateChatText(chatbox)
//                 textField.value = ''
    
//             }).catch((error) => {
//                 console.error('Error:', error);
//                 this.updateChatText(chatbox)
//                 textField.value = ''
//               });
//         };
//     }



//     updateChatText(chatbox) {
//         var html = '';
//         const l = '<div class="messages__item messages__item--visitor"><small class="loading">... </small></div>'
//         const chatmessage = chatbox.querySelector('.chatbox__messages');

//         this.messages.slice().reverse().forEach(function(item, index) {
//             if (item.name === "DolFine")
//             {
//                 html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'

//                 setTimeout(() => {
//                     // chatmessage.;
//                    chatmessage.innerHTML = html;

//                 }, 1300);
//                 chatmessage.innerHTML = l;       

//             }
//             else
//             {
//                 html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
//                 chatmessage.innerHTML = html;
//             }
//           });

        
        
//     }
// }


// const chatbox = new Chatbox();
// chatbox.display();
