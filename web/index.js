let screen = document.getElementById("screen");
const socket = io();
let isPress = false;

screen.oncontextmenu = (e) => {
  e.preventDefault();
}

function sendAction(code, e, element){
  let data = {
    action: code,
    coord: [e.offsetX, e.offsetY],
    size: [element.width, element.height]
  }

  socket.emit('action', JSON.stringify(data))
}

screen.onmousedown = (e) => {
  let code = -1;
  if(e.button == 0){ // left
    code = 0;
    isPress = true;
  }else if(e.button == 1){ // middle
    code = 4;
  }else if(e.button == 2){ // right
    code = 3;
  }

  if(code != -1){
    sendAction(code, e, screen)
  }
}

screen.onmouseup = (e) => {
  if(e.button == 0){ // left
    let code = 1;
    isPress = false;
    sendAction(code, e, screen);
  }
}

screen.onmousemove = (e) => {
  if(isPress){
    let code = 2;
    sendAction(code, e, screen);
  }
}

screen.onmouseleave = (e) => {
  if(isPress){
    isPress = false;
    let code = 1;
    sendAction(code, e, screen);
  }
}
